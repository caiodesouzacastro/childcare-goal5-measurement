# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD03 - correcao de truncamento na analise por COORTE DE NASCIMENTO (S1-S5).
# Descritivo. Painel de solicitacoes: jan/2010 a dez/2018. Denominador de coorte =
# nascidos vivos (SINASC). Reaproveita child_master (BUILD01), child_dtenc (BUILD02).
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os, csv
B1=(NE_ROOT + r"\03_build\build01\_staging")
B2=(NE_ROOT + r"\03_build\build02\_staging")
STG=(NE_ROOT + r"\03_build\build03\_staging")
SIN=NE_ROOT + r"\dados_externos\sinasc_nv_distrito_2006_2026.csv"
EP=pd.Timestamp("1960-01-01"); PANEL_ENC=pd.Timestamp("2019-11-28")
os.makedirs(STG,exist_ok=True)
def w(df,n): df.to_csv(os.path.join(STG,n),index=False); print("  ->",n)

# ---------- nascidos vivos por ano (municipio) ----------
rows=list(csv.reader(open(SIN,encoding="latin-1"),delimiter=";"))
hdr=rows[0]; years=[c for c in hdr[1:] if c.isdigit()]
excl={"Ignorado","Total"}
births={}
ndist=0
for r in rows[1:]:
    nm=r[0].strip()
    if nm in excl: continue
    ndist+=1
    for i,y in enumerate(hdr[1:],start=1):
        if y.isdigit():
            try: births[int(y)]=births.get(int(y),0)+int(r[i])
            except: pass
births={y:v for y,v in births.items() if y!=2026}   # 2026 parcial descartado
print(f"SINASC: {ndist} distritos validos (excl Ignorado+Total); nascidos 2010={births.get(2010)}")

# ---------- child_master ----------
cm=pd.read_feather(os.path.join(B1,"child_master.feather"))
cm["d_sol_ts"]=EP+pd.to_timedelta(cm["dt_sol"],unit="D")
enc=pd.read_feather(os.path.join(B2,"child_dtenc.feather"))
cm=cm.merge(enc,on="cd_aluno_sme",how="left")
cm["esp_enc"]=(cm["dt_enc"]-cm["d_sol_ts"]).dt.days
cm.loc[cm["esp_enc"]<0,"esp_enc"]=np.nan
cm["enc_event"]=cm["dt_enc"].notna() & cm["esp_enc"].notna()
cm["fu_enc"]=(PANEL_ENC-cm["d_sol_ts"]).dt.days

# ================= S1: janelas de observabilidade =================
# painel jan/2010-dez/2018. coorte c (nasc jan c .. dez c):
#   idade minima plenamente observavel = max(0,(2010-c)*12); idade maxima = (2018-c)*12
rows_s1=[]
for c in range(2008,2019):
    amin=max(0,(2010-c)*12); amax=(2018-c)*12
    rows_s1.append({"coorte_nasc":c,"idade_min_obs_meses":amin,"idade_max_obs_meses":amax,
                    "plena_0_24":int(amin==0 and amax>=24),"plena_0_36":int(amin==0 and amax>=36)})
S1=pd.DataFrame(rows_s1); w(S1,"S1a_janelas.csv")
OBS24=[c for c in range(2008,2019) if S1[S1.coorte_nasc==c]["plena_0_24"].iloc[0]==1]
OBS36=[c for c in range(2008,2019) if S1[S1.coorte_nasc==c]["plena_0_36"].iloc[0]==1]
print("plenamente observaveis 0-24:",OBS24," ; 0-36:",OBS36)

# ================= S2: estatistica limpa (denominador = nascidos) =================
def frac_before(cohorts, marks):
    out=[]
    for c in cohorts:
        d=cm[cm["ano_nasc"]==c]; b=births.get(c,np.nan)
        row={"coorte_nasc":c,"nascidos":b,"solicitantes":len(d)}
        for X in marks:
            n=(d["idade_sol"]<X).sum()
            row[f"frac_ate{X}m"]=100*n/b if b else np.nan
        out.append(row)
    return pd.DataFrame(out)
S2a=frac_before(OBS24,[6,12,18,24]); w(S2a,"S2a_frac_0_24.csv")
S2b=frac_before(OBS36,[6,12,18,24,36]); w(S2b,"S2b_frac_0_36.csv")
# S2c: idade media/mediana condicional a <24m, por coorte 0-24
rows_s2c=[]
for c in OBS24:
    d=cm[(cm["ano_nasc"]==c)&(cm["idade_sol"]<24)]
    rows_s2c.append({"coorte_nasc":c,"N_cond":len(d),
        "idade_media":d["idade_sol"].mean(),"idade_mediana":d["idade_sol"].median()})
S2c=pd.DataFrame(rows_s2c); w(S2c,"S2c_cond24.csv")
# S2d: Kaplan-Meier nascimento->1a solicitacao (nao-solicitantes censurados)
# risco = nascidos(c); eventos = idade_sol; para coortes plena 0-24 nao ha censura antes de 24
def km_birth(cohorts,horizons=(6,12,18,24)):
    out=[]
    for c in cohorts:
        d=cm[cm["ano_nasc"]==c]; b=births.get(c,None)
        if not b: continue
        row={"coorte_nasc":c}
        for h in horizons:
            F=(d["idade_sol"]<h).sum()/b     # fracao ja solicitada ate h (sem censura <=24)
            row[f"S{h}"]=1-F
        # mediana KM: menor idade com S<=0.5 (dentro da janela plena)
        med=np.nan
        for a in range(0,int(S1[S1.coorte_nasc==c]["idade_max_obs_meses"].iloc[0])+1):
            if 1-(d["idade_sol"]<a).sum()/b <= 0.5: med=a; break
        row["mediana_KM_meses"]=med
        out.append(row)
    return pd.DataFrame(out)
S2d=km_birth(OBS24); w(S2d,"S2d_km.csv")

# ================= S3: decomposicao refeita (coortes plena p/ ENTRADA) =================
# entrada = solicitacao + espera (meses desde nascimento). Para observar a entrada ate
# ~48m sem truncamento: (2018-c)*12>=48 -> c<=2014, e c>=2010. Janela fixa idade_ent<=48.
S3COH=[c for c in range(2010,2015)]  # 2010-2014 (entrada plena a 48m)
m=cm[(cm["ever_mat"]==1)&(cm["ano_nasc"].isin(S3COH))&(cm["idade_ent"]<=48)].copy()
def dec(d): return pd.Series({"N":len(d),"idade_sol":d["idade_sol"].mean(),
    "espera":d["espera_m"].mean(),"idade_ent":d["idade_ent"].mean()})
S3=m.groupby("ano_nasc").apply(dec).reset_index().rename(columns={"ano_nasc":"coorte_nasc"})
S3["check"]=S3["idade_sol"]+S3["espera"]-S3["idade_ent"]
w(S3,"S3a_decomp.csv")
b0=S3.iloc[0]; b1=S3.iloc[-1]
d_ent=b1["idade_ent"]-b0["idade_ent"]; d_sol=b1["idade_sol"]-b0["idade_sol"]; d_esp=b1["espera"]-b0["espera"]
S3b=pd.DataFrame([{"periodo":f"coortes {S3COH[0]}-{S3COH[-1]}","d_idade_entrada":d_ent,
    "d_idade_sol":d_sol,"d_espera":d_esp,"frac_sol":d_sol/d_ent,"frac_espera":d_esp/d_ent}])
w(S3b,"S3b_split.csv")
print(f"S3: d_ent={d_ent:.2f} sol={d_sol:.2f}({d_sol/d_ent:.0%}) espera={d_esp:.2f}({d_esp/d_ent:.0%})")

# ================= S4: espera (KM) por coorte de NASCIMENTO =================
def km_wait(sub,horizons=None):
    t=np.where(sub["enc_event"],sub["esp_enc"],sub["fu_enc"]).astype(float)
    e=sub["enc_event"].astype(int).values
    ok=t>=0; t=t[ok]; e=e[ok]
    order=np.argsort(t); t=t[order]; e=e[order]; n=len(t); cur=1.0; sc=[(0,1.0)]; nat=n; j=0
    while j<n:
        tj=t[j]; d=0; k=j
        while k<n and t[k]==tj:
            if e[k]==1: d+=1
            k+=1
        if d>0: cur*=(1-d/nat)
        nat-=(k-j); sc.append((tj,cur)); j=k
    med=np.nan
    for tj,cv in sc:
        if cv<=0.5: med=tj; break
    return med
rows_s4=[]
for c in OBS24:
    med=km_wait(cm[cm["ano_nasc"]==c])
    rows_s4.append({"coorte_nasc":c,"espera_mediana_KM_dias":med,"N":int((cm["ano_nasc"]==c).sum())})
S4a=pd.DataFrame(rows_s4); w(S4a,"S4a_espera_coorte.csv")
rows_s4b=[]
for c in OBS24:
    row={"coorte_nasc":c}
    for q in [1,2,3,4]:
        sub=cm[(cm["ano_nasc"]==c)&(cm["rq"]==q)]
        row[f"Q{q}"]=km_wait(sub) if len(sub)>20 else np.nan
    rows_s4b.append(row)
S4b=pd.DataFrame(rows_s4b); w(S4b,"S4b_espera_renda.csv")
print("OK build03_cohort")
