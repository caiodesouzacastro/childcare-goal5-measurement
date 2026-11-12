# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD03 - contexto demografico (S6). Descritivo. Nascidos vivos (SINASC/CEInfo) e
# razao capacidade autorizada de creche / pool 0-3. Capacidade = VAGOFER (perfil).
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os, csv, unicodedata, re
B1=(NE_ROOT + r"\03_build\build01\_staging")
STG=(NE_ROOT + r"\03_build\build03\_staging")
SIN=(NE_ROOT + r"\01_dados_publicos\ceinfo\sinasc_nv_distrito_2006_2026.csv")
BA=NE_ROOT + r"\dados_restritos\Ciro\01_dados\processados\bases_analise\cep_renda_pop_2010.dta"
def w(df,n): df.to_csv(os.path.join(STG,n),index=False); print("  ->",n)
def fixhex(s): return re.sub(r'<([0-9a-fA-F]{2})>', lambda m: bytes([int(m.group(1),16)]).decode('latin-1'), str(s))
def norm(s): s=fixhex(s); return "".join(c for c in unicodedata.normalize("NFD",str(s).strip().upper()) if unicodedata.category(c)!="Mn")

# ---------- nascidos vivos por distrito e ano (SINASC, UTF-8, excl Ignorado/Total, sem 2026) ----------
rows=list(csv.reader(open(SIN,encoding="utf-8"),delimiter=";"))
hdr=rows[0]; yidx={int(hdr[i]):i for i in range(1,len(hdr)) if hdr[i].isdigit() and int(hdr[i])!=2026}
births_d={}  # (distrito_norm, year) -> n
for r in rows[1:]:
    nm=r[0].strip()
    if nm in ("Ignorado","Total"): continue
    dn=norm(nm)
    for y,i in yidx.items():
        try: births_d[(dn,y)]=int(r[i])
        except: pass
distritos=sorted(set(d for d,_ in births_d))
YRS=sorted(yidx)
print(f"distritos={len(distritos)} anos={min(YRS)}-{max(YRS)}")
def births_mun(y): return sum(births_d.get((d,y),0) for d in distritos)

# ---------- renda por distrito (cep_renda; ponderada pela populacao) ----------
rd=pd.read_stata(BA,columns=["nm_distrit","renda","populacao","massa_renda"])
rd["dn"]=rd["nm_distrit"].map(norm)
g=rd.groupby("dn").agg(massa=("massa_renda","sum"),pop=("populacao","sum")).reset_index()
g["renda_distrito"]=g["massa"]/g["pop"]
g=g[g["dn"].isin(distritos)].copy()
g["rq"]=pd.qcut(g["renda_distrito"],4,labels=[1,2,3,4])
dist_rq=dict(zip(g["dn"],g["rq"]))
print("distritos com renda+quartil:",g["rq"].notna().sum(),"/",len(distritos))

# ================= S6a: nascidos vivos municipio por ano 2006-2018 =================
S6a=pd.DataFrame({"ano":[y for y in YRS if 2006<=y<=2018]})
S6a["nascidos_vivos"]=S6a["ano"].map(births_mun)
peak=S6a.loc[S6a["nascidos_vivos"].idxmax()]
S6a["var_pct_vs_2018"]=100*(S6a["nascidos_vivos"]/S6a[S6a.ano==2018]["nascidos_vivos"].iloc[0]-1)
w(S6a,"S6a_nascidos_municipio.csv")
n2018=S6a[S6a.ano==2018]["nascidos_vivos"].iloc[0]
print(f"S6a: pico {int(peak['nascidos_vivos'])} em {int(peak['ano'])}; 2018={int(n2018)}; queda pico->2018 = {100*(n2018/peak['nascidos_vivos']-1):.1f}%")

# ================= S6b: nascidos por quartil de renda do distrito =================
def births_q(q,y): return sum(births_d.get((d,y),0) for d in distritos if dist_rq.get(d)==q)
rows_b=[]
for y in [yy for yy in YRS if 2006<=yy<=2018]:
    row={"ano":y}
    for q in [1,2,3,4]: row[f"Q{q}"]=births_q(q,y)
    rows_b.append(row)
S6b=pd.DataFrame(rows_b); w(S6b,"S6b_nascidos_renda.csv")
# variacao pico->2018 por quartil
qchg={}
for q in [1,2,3,4]:
    ser=S6b[f"Q{q}"]; qchg[q]=100*(ser.iloc[-1]/ser.max()-1)
print("S6b queda pico->2018 por quartil (Q1 pobre..Q4 rico):",{q:round(v,1) for q,v in qchg.items()})

# ================= S6c: razao capacidade / pool 0-3 =================
# capacidade autorizada de creche (VAGOFER, sem1) por distrito e ano, do perfil
pt=pd.read_csv(os.path.join(B1,"perfil_turma.csv"))
pt["dn"]=pt["distrito"].map(norm)
cap=pt[pt["sem"]==1].groupby(["dn","ano"])["vagofer"].sum().reset_index()
cap_d={(r.dn,int(r.ano)):r.vagofer for r in cap.itertuples()}
def cap_mun(y): return sum(v for (d,yy),v in cap_d.items() if yy==y)
def cap_q(q,y): return sum(v for (d,yy),v in cap_d.items() if yy==y and dist_rq.get(d)==q)
def pool_d(d,y): return sum(births_d.get((d,y-k),0) for k in range(0,4))   # Y..Y-3 (0-3 anos)
def pool_mun(y): return sum(pool_d(d,y) for d in distritos)
def pool_q(q,y): return sum(pool_d(d,y) for d in distritos if dist_rq.get(d)==q)
rows_c=[]
for y in range(2013,2020):
    row={"ano":y,"capacidade_mun":cap_mun(y),"pool_0_3_mun":pool_mun(y),
         "cobertura_mun":cap_mun(y)/pool_mun(y) if pool_mun(y) else np.nan}
    for q in [1,2,3,4]:
        pq=pool_q(q,y); row[f"cobertura_Q{q}"]=cap_q(q,y)/pq if pq else np.nan
    rows_c.append(row)
S6c=pd.DataFrame(rows_c); w(S6c,"S6c_cobertura.csv")
print("S6c cobertura municipio 2013->2019:",round(S6c.iloc[0]["cobertura_mun"],3),"->",round(S6c.iloc[-1]["cobertura_mun"],3))

# ================= S6d: decomposicao do ganho de cobertura 2013->2019 =================
cap13,cap19=cap_mun(2013),cap_mun(2019); pool13,pool19=pool_mun(2013),pool_mun(2019)
cov13,cov19=cap13/pool13,cap19/pool19
comp_cap=(cap19-cap13)/pool13                 # crescimento da capacidade (pool fixo 2013)
comp_pool=cap19*(1/pool19-1/pool13)           # contracao do pool (capacidade em 2019)
S6d=pd.DataFrame([{"cobertura_2013":cov13,"cobertura_2019":cov19,"ganho_total":cov19-cov13,
    "comp_crescimento_capacidade":comp_cap,"comp_contracao_pool":comp_pool,
    "frac_capacidade":comp_cap/(cov19-cov13),"frac_pool":comp_pool/(cov19-cov13),
    "cap_2013":cap13,"cap_2019":cap19,"pool_2013":pool13,"pool_2019":pool19}])
w(S6d,"S6d_decomp.csv")
print(f"S6d: ganho={cov19-cov13:.3f} | capacidade {comp_cap:.3f} ({comp_cap/(cov19-cov13):.0%}) | pool {comp_pool:.3f} ({comp_pool/(cov19-cov13):.0%})")
print("OK build03_demog")
