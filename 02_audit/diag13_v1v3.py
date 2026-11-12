# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
import os as _os_ne  # pacote de replicacao (R3): raiz unica, variavel NE_ROOT ou a pasta acima de 02_audit
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
# DIAG13 - validade do desenho de Maimonides. V1 (direcao da causalidade), V2 (de
# onde vem a massa acima do limiar), V3 (balanco em torno do limiar).
# Painel escola x agrupamento x semestre do perfil (BUILD01). M = modulo legal.
# Capacidade = VAGOFER (autorizada); N = matricula (forcing var), nunca capacidade.
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
AUD=NE_ROOT + r"\02_audit"
STG=NE_ROOT + r"\03_build\build01\_staging"
M={"BERC1":7,"BERC2":9,"MINI1":12,"MINI2":25}
LAB={"BERC1":"Bercario I","BERC2":"Bercario II","MINI1":"Mini Grupo I","MINI2":"Mini Grupo II"}

pt=pd.read_csv(os.path.join(STG,"perfil_turma.csv"))
g=pt.groupby(["codesc","agrup","sidx"]).agg(
    N=("matric","sum"),VAG=("vagofer","sum"),CAP=("capreal","sum"),
    nt=("matric","size"),rede=("rede","first"),setor=("setor","first"),
    distrito=("distrito","first")).reset_index()
g=g[g["N"]>0].copy()
g["M"]=g["agrup"].map(M)
g["pred_turmas"]=np.ceil(g["N"]/g["M"])
g["aut_turmas"]=np.ceil(g["VAG"]/g["M"])
g=g.sort_values(["codesc","agrup","sidx"])
# lags/leads dentro de escola x agrup, so semestres consecutivos
grp=g.groupby(["codesc","agrup"])
g["sidx_lag"]=grp["sidx"].shift(1); g["N_lag"]=grp["N"].shift(1)
g["VAG_lag"]=grp["VAG"].shift(1); g["pred_lag"]=grp["pred_turmas"].shift(1)
g["VAG_lead"]=grp["VAG"].shift(-1); g["sidx_lead"]=grp["sidx"].shift(-1)
g["cons_back"]=(g["sidx"]-g["sidx_lag"]==1)
g["cons_fwd"]=(g["sidx_lead"]-g["sidx"]==1)
# CRUZAMENTO entrando em t: pred_turmas sobe (uma turma a mais exigida)
g["cross"]=((g["pred_turmas"]>g["pred_lag"])&(g["cons_back"])).astype(float)
print("unidades:",len(g)," cruzamentos:",int(g["cross"].sum()))

# ================= V1a: tempo relativo da mudanca de VAGOFER =================
cr=g[g["cross"]==1].copy()
cr["dVAG_now"]=cr["VAG"]-cr["VAG_lag"]                       # t-1 -> t
cr["dVAG_lead"]=cr["VAG_lead"]-cr["VAG"]                     # t -> t+1
# mudanca em t-1 (antes): precisa de VAG em t-2
g2=g.set_index(["codesc","agrup","sidx"])
def vaglag2(row):
    key=(row["codesc"],row["agrup"],row["sidx_lag"]-1)
    return g2["VAG"].get(key,np.nan) if pd.notna(row["sidx_lag"]) else np.nan
cr["VAG_lag2"]=cr.apply(vaglag2,axis=1)
cr["dVAG_pre"]=cr["VAG_lag"]-cr["VAG_lag2"]                  # t-2 -> t-1 (antes do cruzamento)
print("\n### V1a: mudanca de VAGOFER em torno do cruzamento de kM ###")
for lab,col in [("t-1 (antes)","dVAG_pre"),("t (junto)","dVAG_now"),("t+1 (depois)","dVAG_lead")]:
    x=cr[col].dropna()
    print(f"  {lab}: dVAG medio={x.mean():+.1f}  %subiu(>0)={100*(x>0).mean():.1f}  %ja subiu em t ou antes: n={len(x)}")

# ================= V1b: lead-lag =================
# VAG_t ~ cross(t+1)=lead + cross(t)=now + cross(t-1)=lag + FE escola + FE sem
g["cross_lead"]=grp["cross"].shift(-1).fillna(0)
g["cross_lag"]=grp["cross"].shift(1).fillna(0)
def twfe(df,dep,regs,unit,time):
    d=df.dropna(subset=[dep]+regs).copy()
    cols=[dep]+regs
    dem=d[cols]-d.groupby(unit)[cols].transform("mean")
    tt=pd.get_dummies(d[time],prefix="t",drop_first=True).astype(float); tt=tt-tt.mean()
    X=np.column_stack([dem[regs].values,tt.values]); y=dem[dep].values
    XtXi=np.linalg.inv(X.T@X); beta=XtXi@(X.T@y); resid=y-X@beta
    cl=d[unit].values; order=np.argsort(cl); Xo=X[order]; ro=resid[order]; clo=cl[order]
    idx=np.unique(clo,return_index=True)[1]; splits=np.split(np.arange(len(clo)),idx[1:])
    meat=np.zeros((X.shape[1],X.shape[1]))
    for s in splits: sc=Xo[s].T@ro[s]; meat+=np.outer(sc,sc)
    G=len(splits); n=len(y); k=X.shape[1]; adj=(G/(G-1))*((n-1)/(n-k))
    V=XtXi@meat@XtXi*adj; se=np.sqrt(np.diag(V))
    return dict(zip(regs,beta[:len(regs)])),dict(zip(regs,se[:len(regs)])),n,G
g["uid"]=g["codesc"].astype(str)+"_"+g["agrup"]
b,se,n,G=twfe(g,"VAG",["cross_lead","cross","cross_lag"],"uid","sidx")
print("\n### V1b: VAGOFER_t ~ cruzamento(lead/now/lag) + FE escola-agrup + FE sem ###")
for r in ["cross_lead","cross","cross_lag"]:
    print(f"  {r}: {b[r]:+.2f} (EP {se[r]:.2f})")
print(f"  N={n} unidades(FE)={G}")

# ================= V1c: turma extra ja autorizada =================
print("\n### V1c: unidades com N>kM que ja tem VAGOFER>kM no mesmo semestre ###")
for a in ["BERC1","BERC2","MINI1","MINI2"]:
    sub=g[(g["agrup"]==a)&(g["pred_turmas"]>=2)].copy()  # N excede 1 modulo
    # o kM relevante = (pred_turmas-1)*M ; VAG>kM?
    kM=(sub["pred_turmas"]-1)*M[a]
    frac=(sub["VAG"]>kM).mean()
    fracN=(sub["nt"]>=sub["pred_turmas"]).mean()
    print(f"  {LAB[a]}: VAGOFER>kM em {100*frac:.1f}% ; turmas reais>=previstas em {100*fracN:.1f}% (n={len(sub)})")

# ================= V2a: a massa vem de poucas escolas? =================
print("\n### V2a: escolas que geram a massa em [kM+1, kM+3] ###")
def above(a):
    sub=g[g["agrup"]==a]
    mask=np.zeros(len(sub),bool)
    for k in range(1,8):
        base=k*M[a]; mask |= (sub["N"]>=base+1)&(sub["N"]<=base+3)
    return sub[mask]
for a in ["BERC1","BERC2","MINI1","MINI2"]:
    ab=above(a); nsc=ab["codesc"].nunique()
    ap=ab["codesc"].value_counts()
    print(f"  {LAB[a]}: {len(ab)} unidades de {nsc} escolas distintas; aparicoes/escola: mediana={ap.median():.0f} p90={ap.quantile(.9):.0f} max={ap.max()}")

# ================= V2b: diferem das de N=kM? =================
# setor -> renda media (via child_master + cep_setor)
cm=pd.read_feather(os.path.join(STG,"child_master.feather"))[["cep_aluno","renda"]]
cs=pd.read_stata(os.path.join(AUD,"cep_setor.dta"),columns=["cep","setor_cep"]).drop_duplicates("cep")
cm=cm.merge(cs,left_on="cep_aluno",right_on="cep",how="left")
setren=cm.groupby("setor_cep")["renda"].mean().rename("renda_setor")
g["renda_setor"]=g["setor"].map(setren)
g["is_kM"]=False; g["is_above"]=False
for a in ["BERC1","BERC2","MINI1","MINI2"]:
    m=M[a]; ga=g["agrup"]==a
    onk=np.zeros(len(g),bool); ab=np.zeros(len(g),bool)
    for k in range(1,8):
        onk |= ga.values&(g["N"].values==k*m)
        ab  |= ga.values&(g["N"].values>=k*m+1)&(g["N"].values<=k*m+3)
    g.loc[onk,"is_kM"]=True; g.loc[ab,"is_above"]=True
print("\n### V2b: unidades [kM+1,kM+3] vs N=kM (diferenca de medias) ###")
A=g[g["is_above"]]; K=g[g["is_kM"]]
for v,lab in [("VAG","VAGOFER"),("nt","n turmas"),("CAP","CAPREAL"),("renda_setor","Renda setor")]:
    x=A[v].astype(float); y=K[v].astype(float)
    d=x.mean()-y.mean(); s=np.sqrt(x.var()/x.notna().sum()+y.var()/y.notna().sum())
    print(f"  {lab}: acima={x.mean():.1f} kM={y.mean():.1f} dif={d:+.2f} (EP {s:.3f})")
print("  modalidade (%%CON): acima=%.1f kM=%.1f"%(100*(A["rede"]=="CON").mean(),100*(K["rede"]=="CON").mean()))

# ================= V2c: N > VAGOFER (irregular)? =================
print("\n### V2c: fracao com N>VAGOFER (matricula acima da capacidade autorizada) ###")
for a in ["BERC1","BERC2","MINI1","MINI2"]:
    ab=above(a); fr=(ab["N"]>ab["VAG"]).mean()
    frall=(g[g["agrup"]==a]["N"]>g[g["agrup"]==a]["VAG"]).mean()
    print(f"  {LAB[a]}: em [kM+1,kM+3] N>VAGOFER={100*fr:.1f}% ; no geral={100*frall:.1f}%")

# ================= V3a: balanco em torno do limiar =================
print("\n### V3a: balanco em [kM-3,kM+3], 1[N>kM] (cross-section + FE semestre) ###")
win=[]
for a in ["BERC1","BERC2","MINI1","MINI2"]:
    m=M[a]; ga=g[g["agrup"]==a].copy()
    keep=np.zeros(len(ga),bool); abv=np.zeros(len(ga),bool)
    for k in range(1,8):
        near=(ga["N"]>=k*m-3)&(ga["N"]<=k*m+3); keep|=near.values
        abv|=near.values&(ga["N"].values>k*m)
    ga=ga[keep].copy(); ga["above"]=abv[keep].astype(float); win.append(ga)
W=pd.concat(win)
for v,lab in [("VAG","VAGOFER"),("CAP","CAPREAL"),("nt","n turmas"),("renda_setor","Renda setor")]:
    d=W.dropna(subset=[v]).copy()
    tt=pd.get_dummies(d["sidx"],prefix="s",drop_first=True).astype(float)
    X=np.column_stack([np.ones(len(d)),d["above"].values,tt.values]); y=d[v].values.astype(float)
    XtXi=np.linalg.inv(X.T@X); beta=XtXi@(X.T@y); resid=y-X@beta
    sig2=(resid@resid)/(len(y)-X.shape[1]); se=np.sqrt(np.diag(XtXi)*sig2)
    print(f"  {lab}: coef 1[N>kM]={beta[1]:+.3f} (EP {se[1]:.3f})")
print("  modalidade %%CON: acima=%.1f abaixo=%.1f"%(100*(W[W.above==1]["rede"]=="CON").mean(),100*(W[W.above==0]["rede"]=="CON").mean()))

# ================= V3b: bunching/McCrary de N em torno de kM =================
print("\n### V3b: densidade (bunching) de N em torno de kM ###")
for a in ["BERC1","BERC2","MINI1","MINI2"]:
    m=M[a]; sub=g[g["agrup"]==a]; vc=sub["N"].value_counts()
    ratios=[]
    for k in range(1,6):
        base=k*m
        at=vc.get(base,0); above1=vc.get(base+1,0)
        ratios.append(f"{base}:{at}/{base+1}:{above1}")
    tot=len(sub); atkm=sum(vc.get(k*m,0) for k in range(1,9))
    print(f"  {LAB[a]}: massa exatamente em multiplos de M = {100*atkm/tot:.1f}% do total | "+" ".join(ratios[:3]))
print("\nOK diag13_v1v3")
