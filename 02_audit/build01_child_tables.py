# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD01 - calcula T1, T3, T4, T5 a partir de child_master.feather. So descritivo.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
STG=(NE_ROOT + r"\03_build\build01\_staging")
b=pd.read_feather(os.path.join(STG,"child_master.feather"))
YEARS=list(range(2010,2019))
AGR_LAB={"BERC1":"Bercario I","BERC2":"Bercario II","MINI1":"Mini Grupo I","MINI2":"Mini Grupo II"}
def w(df,name): df.to_csv(os.path.join(STG,name),index=False); print("escrita",name)

# modalidade (3 vias) da escola de matricula, via perfil
pt=pd.read_csv(os.path.join(STG,"perfil_turma.csv"))
def modal3(t):
    t=str(t).upper()
    if "DIRET" in t or "CEU CEI" in t or "CEMEI" in t or "CECI" in t or "CCI" in t: return "Direta"
    if "INDIR" in t: return "Indireta"
    if "CONV" in t or "CR.P" in t: return "Conveniada"
    return "Outra"
pt["m3"]=pt["tipoesc"].map(modal3)
# modalidade modal por codesc
esc_mod=(pt.groupby("codesc")["m3"].agg(lambda s:s.value_counts().index[0]))
esc_mod.index=esc_mod.index.astype(str)
b["esc_mat_str"]=b["cd_esc_matricula"].apply(lambda x: str(int(x)) if pd.notna(x) else np.nan)
b["modal_mat"]=b["esc_mat_str"].map(esc_mod)

# ================= T1 =================
def col_stats(d):
    n=len(d)
    return {
        "N solicitacoes":n,
        "% feminino":100*d["fem"].mean(),
        "% Branca":100*(d["raca"]=="Branca").mean(),
        "% Preta":100*(d["raca"]=="Preta").mean(),
        "% Parda":100*(d["raca"]=="Parda").mean(),
        "% Amarela":100*(d["raca"]=="Amarela").mean(),
        "% Indigena":100*(d["raca"]=="Indigena").mean(),
        "% Outra/ND":100*(d["raca"]=="Outra/ND").mean(),
        "Idade mediana solic. (meses)":d["idade_sol"].median(),
        "% com prioridade":100*d["prio"].mean(),
        "Renda mediana do CEP (R$)":d["renda"].median(),
        "N mediano de CEIs <=2km":d["nelig"].median(),
        "% matriculado em 365d":100*d["mat365"].mean(),
        "% nunca matriculado":100*d["nunca"].mean(),
    }
rows=[]
order=["N solicitacoes","% feminino","% Branca","% Preta","% Parda","% Amarela","% Indigena",
       "% Outra/ND","Idade mediana solic. (meses)","% com prioridade","Renda mediana do CEP (R$)",
       "N mediano de CEIs <=2km","% matriculado em 365d","% nunca matriculado"]
cols={}
for y in YEARS: cols[str(y)]=col_stats(b[b["ano_sol"]==y])
cols["Total"]=col_stats(b)
T1=pd.DataFrame({"metrica":order})
for c in [str(y) for y in YEARS]+["Total"]:
    T1[c]=[cols[c][m] for m in order]
w(T1,"T1_fila.csv")

# ================= T3 =================
m=b[b["ever_mat"]==1].copy()
def decomp(d):
    return pd.Series({"N":len(d),"idade_sol":d["idade_sol"].mean(),"espera":d["espera_m"].mean(),
                      "idade_ent":d["idade_ent"].mean()})
g=m[m["ano_sol"].isin(YEARS)].groupby("ano_sol").apply(decomp).reset_index()
g["check"]=g["idade_sol"]+g["espera"]-g["idade_ent"]
w(g,"T3_decomp.csv")
# medianas (painel de referencia)
gm=m[m["ano_sol"].isin(YEARS)].groupby("ano_sol").agg(
    idade_sol=("idade_sol","median"),espera=("espera_m","median"),idade_ent=("idade_ent","median")).reset_index()
w(gm,"T3_medianas.csv")
# T3b: variacao acumulada desde 2010 e fracao atribuida
base=g[g["ano_sol"]==2010].iloc[0]
tb=g.copy()
for c in ["idade_sol","espera","idade_ent"]: tb["d_"+c]=tb[c]-base[c]
tb["frac_idade_sol"]=tb["d_idade_sol"]/tb["d_idade_ent"]
tb["frac_espera"]=tb["d_espera"]/tb["d_idade_ent"]
w(tb[["ano_sol","d_idade_sol","d_espera","d_idade_ent","frac_idade_sol","frac_espera"]],"T3b_cumulativa.csv")
# T3c: por quartil de renda
gc=m[m["ano_sol"].isin(YEARS)&m["rq"].notna()].groupby(["rq","ano_sol"]).apply(decomp).reset_index()
gc["check"]=gc["idade_sol"]+gc["espera"]-gc["idade_ent"]
w(gc,"T3c_renda.csv")
# T3d: por agrupamento solicitado (creche)
gd=m[m["ano_sol"].isin(YEARS)&m["agrup_sol"].notna()].groupby(["agrup_sol","ano_sol"]).apply(decomp).reset_index()
gd["check"]=gd["idade_sol"]+gd["espera"]-gd["idade_ent"]
w(gd,"T3d_agrup.csv")

# ================= T4 =================
def inc(d):
    mm=d[d["ever_mat"]==1]
    return pd.Series({"N":len(d),
        "espera_med_dias":mm["espera_d"].median() if len(mm) else np.nan,
        "p180":100*d["mat180"].mean(),"p365":100*d["mat365"].mean(),
        "pnunca":100*d["nunca"].mean()})
def by_group(gvar,fname,label):
    d=b[b["ano_sol"].isin(YEARS)&b[gvar].notna()]
    t=d.groupby([gvar,"ano_sol"]).apply(inc).reset_index()
    w(t,fname)
by_group("rq","T4a_renda.csv","quartil renda")
by_group("ipvs_q","T4b_ipvs.csv","quartil IPVS")
by_group("nelig_dec","T4c_nelig.csv","decil nelig")
# T4d: nunca-matriculados vs resto
nev=b["ever_mat"]==0
def ms(v):
    x=b.loc[nev,v].astype(float); y=b.loc[~nev,v].astype(float)
    mx,my=x.mean(),y.mean();
    se=np.sqrt(x.var(ddof=1)/x.notna().sum()+y.var(ddof=1)/y.notna().sum())
    return mx,my,mx-my,se
metrs=[("idade_sol","Idade na solicitacao (meses)"),("renda","Renda do CEP (R$)"),
       ("ipvs_grupo","Grupo IPVS (1-6)"),("nelig","N de CEIs <=2km"),
       ("dist_nearest","Dist. ao CEI mais proximo (km)"),("prio","% com prioridade"),
       ("ano_sol","Ano de solicitacao")]
rows=[]
for v,lab in metrs:
    mx,my,dif,se=ms(v)
    if v=="prio": mx,my,dif,se=mx*100,my*100,dif*100,se*100
    rows.append({"variavel":lab,"nunca_mat":mx,"matriculou":my,"diferenca":dif,"ep":se})
w(pd.DataFrame(rows),"T4d_never.csv")

# ================= T5 =================
mm=b[b["ever_mat"]==1].copy()
mm["rankcat"]=np.where(mm["rank_assigned"].isna(),"fora (>2km / s coord)",
              np.where(mm["rank_assigned"]<=5,mm["rank_assigned"].fillna(0).astype("Int64").astype(str),"6+"))
# T5a: distribuicao do rank por ano
cats=["1","2","3","4","5","6+","fora (>2km / s coord)"]
rowsa=[]
for cat in cats:
    r={"rank":cat}
    for y in YEARS:
        d=mm[mm["ano_sol"]==y]
        r[str(y)]=100*(d["rankcat"]==cat).mean()
    d=mm; r["Total"]=100*(mm["rankcat"]==cat).mean()
    rowsa.append(r)
w(pd.DataFrame(rowsa),"T5a_rank.csv")
# T5b: distancia mediana ao CEI de matricula por ano e por quartil renda
t5b_y=mm[mm["ano_sol"].isin(YEARS)].groupby("ano_sol")["dist_assigned"].median().reset_index().rename(columns={"dist_assigned":"dist_med_km"})
w(t5b_y,"T5b_dist_ano.csv")
t5b_r=mm[mm["rq"].notna()].groupby("rq")["dist_assigned"].median().reset_index().rename(columns={"dist_assigned":"dist_med_km"})
w(t5b_r,"T5b_dist_renda.csv")
# T5c: % por modalidade da escola de matricula, por ano
def modshare(d):
    tot=d["modal_mat"].isin(["Direta","Indireta","Conveniada"]).sum()
    return pd.Series({mm_:100*(d["modal_mat"]==mm_).sum()/tot if tot else np.nan
                      for mm_ in ["Direta","Indireta","Conveniada"]})
t5c_y=mm[mm["ano_sol"].isin(YEARS)].groupby("ano_sol").apply(modshare).reset_index()
w(t5c_y,"T5c_modal_ano.csv")
t5c_r=mm[mm["rq"].notna()].groupby("rq").apply(modshare).reset_index()
w(t5c_r,"T5c_modal_renda.csv")
print("OK child_tables")
