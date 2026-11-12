# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
import os as _os_ne  # pacote de replicacao (R3): raiz unica, variavel NE_ROOT ou a pasta acima de 02_audit
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
# DIAG12 TESTE 2 - CEIs pivotais: a diluicao (1 de ~33) mata o primeiro estagio?
# Concentracao do conjunto elegivel (share do maior CEI, HHI) e primeiro estagio
# do DIAG11 D1/D2 por quartil de concentracao (absorb setor#semestre, cluster CEI).
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
AUD=NE_ROOT + r"\02_audit"
STG=NE_ROOT + r"\03_build\build01\_staging"

# ---------- concentracao por crianca (child_cei: cd_aluno_sme, ceicode, capb) ----------
agg={}
for ch in pd.read_stata(os.path.join(AUD,"child_cei.dta"),columns=["cd_aluno_sme","capb"],chunksize=1_000_000):
    ch["capb"]=ch["capb"].fillna(0.0)
    ch["capb2"]=ch["capb"]**2
    g=ch.groupby("cd_aluno_sme").agg(tot=("capb","sum"),ss=("capb2","sum"),mx=("capb","max"),n=("capb","size"))
    for cid,row in zip(g.index,g.itertuples(index=False)):
        if cid in agg:
            a=agg[cid]; a[0]+=row.tot; a[1]+=row.ss; a[2]=max(a[2],row.mx); a[3]+=row.n
        else:
            agg[cid]=[row.tot,row.ss,row.mx,row.n]
C=pd.DataFrame([(k,v[0],v[1],v[2],v[3]) for k,v in agg.items()],
               columns=["cd_aluno_sme","tot","ss","mx","nelig_c"])
C=C[C["tot"]>0].copy()
C["share_max"]=C["mx"]/C["tot"]
C["hhi"]=C["ss"]/C["tot"]**2
print("### T2a: concentracao do conjunto elegivel ###")
for v in ["share_max","hhi","nelig_c"]:
    q=C[v].quantile([.1,.25,.5,.75,.9])
    print(f"  {v}: p10={q[.1]:.3f} p25={q[.25]:.3f} p50={q[.5]:.3f} p75={q[.75]:.3f} p90={q[.9]:.3f} media={C[v].mean():.3f}")

# ---------- design + setor + ceicode mais proximo ----------
b=pd.read_stata(os.path.join(AUD,"berc_design.dta"),
    columns=["cd_aluno_sme","cep","sol_sidx","espera","enc180","idade_entrada","mat365",
             "choque_neg","choque_pos","choque_pre","cap_base"])
b=b.merge(C[["cd_aluno_sme","share_max","hhi","nelig_c"]],on="cd_aluno_sme",how="left")
# ceicode mais proximo por cep + setor
pairs=pd.read_stata(os.path.join(AUD,"cep_cei_pairs_novo.dta"),columns=["cep","ceicode","dist_km"])
pairs=pairs.sort_values(["cep","dist_km"]).drop_duplicates("cep")
capf=pd.read_stata(os.path.join(AUD,"cap_full.dta"),columns=["codesc","setor"]).drop_duplicates("codesc")
capf=capf.rename(columns={"codesc":"ceicode"})
near=pairs.merge(capf,on="ceicode",how="left")[["cep","ceicode","setor"]]
b=b.merge(near,on="cep",how="left")
b=b.dropna(subset=["setor","share_max"]).copy()
for v in ["choque_neg","choque_pos","choque_pre","cap_base"]: b[v+"100"]=b[v]/100
b["ssem"]=b["setor"].astype(str)+"_"+b["sol_sidx"].astype(str)
# quartil de concentracao (share_max)
b["cq"]=pd.qcut(b["share_max"],4,labels=[1,2,3,4])
print("N design com concentracao e setor:",len(b))

# ---------- primeiro estagio com absorb(setor#semestre) e cluster(ceicode) ----------
def within(df,cols,by):
    out=df[cols].copy().astype(float)
    grp=df.groupby(by)
    return out - grp[cols].transform("mean")
def feols_cluster(df,dep,regs,by,cluster):
    d=df.dropna(subset=[dep]+regs+[by,cluster]).copy()
    cols=[dep]+regs
    dem=within(d,cols,by)
    y=dem[dep].values; X=dem[regs].values
    XtX=X.T@X
    try: XtXi=np.linalg.inv(XtX)
    except: return None
    beta=XtXi@(X.T@y); resid=y-X@beta
    # cluster-robust
    meat=np.zeros((X.shape[1],X.shape[1]))
    cl=d[cluster].values
    order=np.argsort(cl); Xo=X[order]; ro=resid[order]; clo=cl[order]
    idx=np.unique(clo,return_index=True)[1]; splits=np.split(np.arange(len(clo)),idx[1:])
    for s in splits:
        Xg=Xo[s]; ug=ro[s]; sc=Xg.T@ug; meat+=np.outer(sc,sc)
    G=len(splits); n=len(y); k=X.shape[1]
    adj=(G/(G-1))*((n-1)/(n-k))
    V=XtXi@meat@XtXi*adj
    se=np.sqrt(np.diag(V))
    return beta,se,n,G
DEPS=["espera","enc180","idade_entrada","mat365"]
print("\n### T2b: primeiro estagio (choque_neg100) por quartil de concentracao, absorb setor#sem ###")
t2b=[]
for q in [1,2,3,4]:
    dq=b[b["cq"]==q]
    line=f"  Q{q} (share_max mediana {dq['share_max'].median():.2f}, N{len(dq)}): "
    for dep in DEPS:
        r=feols_cluster(dq,dep,["choque_neg100","choque_pos100","cap_base100"],"ssem","ceicode")
        if r:
            beta,se,n,G=r; line+=f"{dep} b={beta[0]:+.4f}(se{se[0]:.4f}) "
            t2b.append((q,dep,beta[0],se[0],n))
    print(line)
print("\n### T2c: placebo pre-solicitacao (choque_pre100) por quartil de concentracao ###")
t2c=[]
for q in [1,2,3,4]:
    dq=b[b["cq"]==q]
    line=f"  Q{q}: "
    for dep in ["espera","idade_entrada"]:
        r=feols_cluster(dq,dep,["choque_pre100","choque_pos100","cap_base100"],"ssem","ceicode")
        if r:
            beta,se,n,G=r; line+=f"{dep} bPRE={beta[0]:+.4f}(se{se[0]:.4f}) "
            t2c.append((q,dep,beta[0],se[0]))
    print(line)

# ---------- T2d: caracterizar quartil mais concentrado ----------
cov=pd.read_csv(os.path.join(STG,"cep_covars.csv"))
b=b.merge(cov,left_on="cep",right_on="cep",how="left")
cen=pd.read_stata(NE_ROOT + r"\dados_restritos\Ciro\01_dados\brutos\fila_espera\cepcen.dta")
cen["dist_centro"]=np.sqrt((cen["latitude"]-(-23.55052))**2+(cen["longitude"]-(-46.63331))**2)*111.0
b=b.merge(cen[["cep","dist_centro"]],on="cep",how="left")
print("\n### T2d: quartil mais concentrado (Q4) vs demais ###")
top=b["cq"]==4; rest=b["cq"].isin([1,2,3])
for v,lab in [("renda","Renda CEP"),("ipvs_grupo","IPVS"),("nelig_c","N CEIs elegiveis"),
              ("dist_centro","Dist. ao centro (km)"),("share_max","Share do maior CEI")]:
    x=b.loc[top,v].astype(float); y=b.loc[rest,v].astype(float)
    dif=x.mean()-y.mean(); se=np.sqrt(x.var()/x.notna().sum()+y.var()/y.notna().sum())
    print(f"  {lab}: Q4={x.mean():.2f} demais={y.mean():.2f} dif={dif:+.2f} (EP {se:.3f})")
print("\nOK diag12_t2")
