# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
import os as _os_ne  # pacote de replicacao (R3): raiz unica, variavel NE_ROOT ou a pasta acima de 02_audit
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
# DIAG12 TESTE 4 - reforma de julho/2016 e endereco-base. Serie mensal 2014-2018
# da atribuicao (encaminhamento) e teste de quebra em jul/2016; decomposicao dos
# 39,5% atribuidos a >2km / sem coordenada.
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
AUD=NE_ROOT + r"\02_audit"
STG=NE_ROOT + r"\03_build\build01\_staging"
FILA=NE_ROOT + r"\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
def dp(s): return pd.to_datetime(s,format="%d/%m/%Y %H:%M:%S",errors="coerce")

# ---------- eventos de encaminhamento 2014-2018 ----------
print("lendo Fila1018 (eventos de encaminhamento)...")
ev=[]
for ch in pd.read_stata(FILA,columns=["cd_aluno_sme","dt_solicitacao","dt_encaminhamento",
        "cd_esc_encaminhamento","cep_aluno"],chunksize=400000):
    ch["denc"]=dp(ch["dt_encaminhamento"]); ch["dsol"]=dp(ch["dt_solicitacao"])
    e=ch.dropna(subset=["denc","cd_esc_encaminhamento"]).copy()
    e=e[(e["denc"]>=pd.Timestamp("2014-01-01"))&(e["denc"]<=pd.Timestamp("2018-12-31"))]
    e["espera"]=(e["denc"]-e["dsol"]).dt.days
    ev.append(e[["cd_aluno_sme","cep_aluno","denc","cd_esc_encaminhamento","espera"]])
E=pd.concat(ev,ignore_index=True)
E["ym"]=E["denc"].dt.to_period("M").astype(str)
E["mes"]=E["denc"].dt.month
E["esc"]=E["cd_esc_encaminhamento"].astype("Int64")
print("eventos de encaminhamento 2014-2018:",len(E))

# distancia CEP -> CEI atribuido
pairs=pd.read_stata(os.path.join(AUD,"cep_cei_pairs_novo.dta"),columns=["cep","ceicode","dist_km"])
pr=pairs.rename(columns={"ceicode":"esc","dist_km":"dist"})
E=E.merge(pr,left_on=["cep_aluno","esc"],right_on=["cep","esc"],how="left")
E["le2"]=(E["dist"]<=2).astype(float)
print("cobertura de distancia (par existe):",round(E["dist"].notna().mean(),3))

# distrito por CEP (via CEI mais proximo)
near=pairs.sort_values(["cep","dist_km"]).drop_duplicates("cep")
capf=pd.read_stata(os.path.join(AUD,"cap_full.dta"),columns=["codesc","distrito","setor"]).drop_duplicates("codesc")
near=near.merge(capf.rename(columns={"codesc":"ceicode"}),on="ceicode",how="left")
E=E.merge(near[["cep","distrito"]].rename(columns={"cep":"cep_aluno"}),on="cep_aluno",how="left")

# ---------- T4a: serie mensal ----------
# n escolas distintas por CEP-mes
nesc=E.groupby(["cep_aluno","ym"])["esc"].nunique().reset_index(name="nesc")
nesc_m=nesc.groupby("ym")["nesc"].median()
ser=E.groupby("ym").agg(dist_med=("dist","median"),pct_le2=("le2","mean"),
                        espera_med=("espera","median"),n=("esc","size")).reset_index()
ser["nesc_med_por_cep"]=ser["ym"].map(nesc_m)
ser.to_csv(os.path.join(STG,"t4_serie_mensal.csv"),index=False)
print("\n### T4a: serie mensal (amostra jul/2015-set/2016) ###")
for _,r in ser[(ser["ym"]>="2015-07")&(ser["ym"]<="2016-12")].iterrows():
    print(f"  {r['ym']}: dist_med={r['dist_med']:.3f} %<=2km={100*r['pct_le2']:.1f} espera_med={r['espera_med']:.0f} nesc/cep={r['nesc_med_por_cep']:.1f} n={int(r['n'])}")

# ---------- T4b: regressao de quebra (child-event level) ----------
E["post16"]=(E["denc"]>=pd.Timestamp("2016-07-01")).astype(float)
E["trend"]=(E["denc"].dt.year-2014)*12+(E["denc"].dt.month-1)
def breakreg(df,dep,postvar,extra_trend="trend"):
    d=df.dropna(subset=[dep,postvar,extra_trend,"mes","distrito"]).copy()
    moy=pd.get_dummies(d["mes"],prefix="m",drop_first=True).astype(float)
    dist=pd.get_dummies(d["distrito"],prefix="d",drop_first=True).astype(float)
    X=np.column_stack([np.ones(len(d)),d[postvar].values,d[extra_trend].values,moy.values,dist.values])
    y=d[dep].values.astype(float)
    XtXi=np.linalg.inv(X.T@X); beta=XtXi@(X.T@y); resid=y-X@beta
    # cluster por ym
    cl=d["ym"].values if "ym" in d else d[extra_trend].values
    order=np.argsort(cl); Xo=X[order]; ro=resid[order]; clo=cl[order]
    idx=np.unique(clo,return_index=True)[1]; splits=np.split(np.arange(len(clo)),idx[1:])
    meat=np.zeros((X.shape[1],X.shape[1]))
    for s in splits: sc=Xo[s].T@ro[s]; meat+=np.outer(sc,sc)
    G=len(splits); n=len(y); k=X.shape[1]; adj=(G/(G-1))*((n-1)/(n-k))
    V=XtXi@meat@XtXi*adj
    return beta[1],np.sqrt(V[1,1]),n
print("\n### T4b: coef 1[pos-jul/2016] (trend + FE mes-do-ano + FE distrito) ###")
for dep,lab in [("dist","dist. ao CEI (km)"),("le2","<=2km (0/1)"),("espera","espera (dias)")]:
    b,se,n=breakreg(E,dep,"post16")
    print(f"  {lab}: {b:+.4f} (EP {se:.4f}) N={n}")

# ---------- T4c: placebos jul/2014 e jul/2015 ----------
print("\n### T4c: placebos ###")
for py,cut in [("2014-07-01","jul/2014 (dados 2014-2015)"),("2015-07-01","jul/2015 (dados 2015-jun2016)")]:
    if "2014" in py: sub=E[E["denc"]<pd.Timestamp("2016-01-01")].copy()
    else: sub=E[(E["denc"]>=pd.Timestamp("2015-01-01"))&(E["denc"]<pd.Timestamp("2016-07-01"))].copy()
    sub["postp"]=(sub["denc"]>=pd.Timestamp(py)).astype(float)
    for dep,lab in [("dist","dist"),("le2","<=2km")]:
        try:
            b,se,n=breakreg(sub,dep,"postp"); print(f"  {cut} [{lab}]: {b:+.4f} (EP {se:.4f}) N={n}")
        except Exception as e: print(f"  {cut} [{lab}]: erro {str(e)[:40]}")

# ---------- T4d: decomposicao dos atribuidos a >2km / sem coordenada ----------
# usa child_master (escola de matricula) do BUILD01
b=pd.read_feather(os.path.join(STG,"child_master.feather"))
mm=b[b["ever_mat"]==1].copy()
mm["esc"]=mm["cd_esc_matricula"]
ceiset=set(pairs["ceicode"].unique())
mm["esc_known"]=mm["esc"].apply(lambda x: (int(x) in ceiset) if pd.notna(x) else False)
mm["has_dist"]=mm["dist_assigned"].notna()
sem_coord=(~mm["esc_known"])
coord_far=mm["esc_known"]&(~mm["has_dist"])   # e CEI conhecido mas par ausente (>raio)
# distancia calculada para pares existentes (todas <=~raio); para >2km reais preciso dist bruta.
# distancia bruta CEP->escola de matricula via merge amplo (todos os pares)
allpairs=pairs.rename(columns={"ceicode":"esc","dist_km":"dist_full"})
mm2=mm.merge(allpairs,left_on=["cep_aluno","esc"],right_on=["cep","esc"],how="left")
far=mm2[(mm2["dist_full"].notna())&(mm2["dist_full"]>2)]
print("\n### T4d: decomposicao dos atribuidos fora do conjunto <=2km ###")
tot=len(mm)
print(f"  total matriculados: {tot}")
print(f"  (i) escola sem coordenada no cadastro: {sem_coord.sum()} ({100*sem_coord.mean():.1f}%)")
print(f"  (ii) escola com coordenada e dist>2km: {len(far)} ({100*len(far)/tot:.1f}%)")
if len(far):
    q=far["dist_full"].quantile([.5,.75,.9,.95,.99])
    print(f"      dist>2km: mediana={q[.5]:.2f} p75={q[.75]:.2f} p90={q[.9]:.2f} p95={q[.95]:.2f} p99={q[.99]:.2f} max={far['dist_full'].max():.1f}")
    print(f"      fracao dessas com dist<=3km (erro de medida?): {100*(far['dist_full']<=3).mean():.1f}%  ; >5km: {100*(far['dist_full']>5).mean():.1f}%")

# ---------- T4e: essas criancas diferem? ----------
sib=pd.read_stata(os.path.join(AUD,"sibmat.dta"))
mm2=mm2.merge(sib,on="cd_aluno_sme",how="left")
mm2["fora"]=((~mm2["esc_known"]) | (mm2["dist_full"]>2)).astype(int)
print("\n### T4e: fora do conjunto <=2km vs dentro ###")
for v,lab in [("renda","Renda CEP"),("prio","% prioridade"),("ano_sol","Ano solic."),("sib_mat","% irmao matriculado")]:
    if v not in mm2: print(f"  {lab}: n/d"); continue
    x=mm2.loc[mm2["fora"]==1,v].astype(float); y=mm2.loc[mm2["fora"]==0,v].astype(float)
    mult=100 if v in ("prio","sib_mat") else 1
    dif=(x.mean()-y.mean())*mult; se=np.sqrt(x.var()/x.notna().sum()+y.var()/y.notna().sum())*mult
    print(f"  {lab}: fora={x.mean()*mult:.2f} dentro={y.mean()*mult:.2f} dif={dif:+.2f} (EP {se:.3f})")
print("\nOK diag12_t4")
