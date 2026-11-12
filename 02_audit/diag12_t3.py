# -*- coding: utf-8 -*-
import os as _os_ne  # pacote de replicacao (R3): raiz unica, variavel NE_ROOT ou a pasta acima de 02_audit
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
# DIAG12 TESTE 3 - Maimonides feito corretamente. Unidade = escola x agrupamento x
# semestre (perfil 2013-2019). N = matricula efetiva; M = modulo legal (7/9/12/25).
# Regra: turmas = ceil(N/M); tamanho previsto = N/ceil(N/M). Capacidade (M) e legal,
# nunca derivada de matricula; N (matricula) e o forcing var do desenho Maimonides.
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os, math
STG=NE_ROOT + r"\03_build\build01\_staging"
M={"BERC1":7,"BERC2":9,"MINI1":12,"MINI2":25}
LAB={"BERC1":"Bercario I","BERC2":"Bercario II","MINI1":"Mini Grupo I","MINI2":"Mini Grupo II"}

pt=pd.read_csv(os.path.join(STG,"perfil_turma.csv"))
pt=pt[pt["matric"]>=0].copy()
# agrega escola x agrup x semestre
g=pt.groupby(["codesc","agrup","sidx"]).agg(N=("matric","sum"),nturmas=("matric","size")).reset_index()
g=g[g["N"]>0].copy()
g["M"]=g["agrup"].map(M)
g["real_size"]=g["N"]/g["nturmas"]
g["pred_turmas"]=np.ceil(g["N"]/g["M"])
g["pred_size"]=g["N"]/g["pred_turmas"]
print("unidades escola x agrup x semestre:",len(g))

# ---------- T3a: histograma de N por agrupamento (exporta) + regioes de kM ----------
for a in ["BERC1","BERC2","MINI1","MINI2"]:
    sub=g[g["agrup"]==a]
    vc=sub["N"].value_counts()
    hist=pd.DataFrame({"N":range(1,5*M[a]+1)})
    hist["n"]=hist["N"].map(vc).fillna(0).astype(int)
    hist.to_csv(os.path.join(STG,f"t3_hist_{a}.csv"),index=False)

# ---------- T3b: suporte acima do limiar kM, kM+1, kM+2, kM+3 ----------
print("\n### T3b: contagem em kM, kM+1, kM+2, kM+3 (tabela decisiva) ###")
t3b=[]
for a in ["BERC1","BERC2","MINI1","MINI2"]:
    sub=g[g["agrup"]==a]; vc=sub["N"].value_counts()
    print(f"  {LAB[a]} (M={M[a]}, N unid={len(sub)}):")
    for k in range(1,6):
        base=k*M[a]
        cnts=[int(vc.get(base+j,0)) for j in range(0,4)]
        print(f"    k={k}: {base}:{cnts[0]}  {base+1}:{cnts[1]}  {base+2}:{cnts[2]}  {base+3}:{cnts[3]}")
        t3b.append((a,k,base,*cnts))

# ---------- T3c: n turmas vs N (salto em kM+1?) ----------
print("\n### T3c: n medio de turmas logo abaixo/acima de kM ###")
for a in ["BERC1","BERC2","MINI1","MINI2"]:
    sub=g[g["agrup"]==a]
    parts=[]
    for k in range(1,5):
        base=k*M[a]
        lo=sub[(sub["N"]>=base-2)&(sub["N"]<=base)]["nturmas"].mean()
        hi=sub[(sub["N"]>=base+1)&(sub["N"]<=base+3)]["nturmas"].mean()
        parts.append(f"kM={base}: abaixo={lo:.2f} acima={hi:.2f}")
    print(f"  {LAB[a]}: "+" | ".join(parts))

# ---------- T3d: tamanho real vs N e vs previsto ----------
print("\n### T3d: tamanho real medio vs previsto (Maimonides) ###")
for a in ["BERC1","BERC2","MINI1","MINI2"]:
    sub=g[g["agrup"]==a]
    corr=np.corrcoef(sub["real_size"],sub["pred_size"])[0,1]
    print(f"  {LAB[a]}: real medio={sub['real_size'].mean():.2f} previsto medio={sub['pred_size'].mean():.2f} corr(real,previsto)={corr:.3f}")

# ---------- T3e: primeiro estagio Maimonides ----------
# real_size = pred_size + N + N^2 + FE escola + FE semestre. F sobre pred_size.
def twoway_fe(df,dep,regs,unit,time):
    d=df.dropna(subset=[dep]+regs+[unit,time]).copy()
    cols=[dep]+regs
    # demean por escola (unit)
    dem=d[cols]-d.groupby(unit)[cols].transform("mean")
    # dummies de semestre
    tt=pd.get_dummies(d[time],prefix="t",drop_first=True).astype(float)
    tt=tt-tt.mean()
    X=np.column_stack([dem[regs].values, tt.values])
    y=dem[dep].values
    XtX=X.T@X; XtXi=np.linalg.inv(XtX)
    beta=XtXi@(X.T@y); resid=y-X@beta
    n=len(y); k=X.shape[1]
    # cluster por escola
    cl=d[unit].values; order=np.argsort(cl)
    Xo=X[order]; ro=resid[order]; clo=cl[order]
    idx=np.unique(clo,return_index=True)[1]; splits=np.split(np.arange(len(clo)),idx[1:])
    meat=np.zeros((k,k))
    for s in splits:
        sc=Xo[s].T@ro[s]; meat+=np.outer(sc,sc)
    G=len(splits); adj=(G/(G-1))*((n-1)/(n-k))
    V=XtXi@meat@XtXi*adj; se=np.sqrt(np.diag(V))
    return beta,se,n,G
print("\n### T3e: primeiro estagio (tamanho_real ~ tamanho_previsto + N + N^2 + FE esc + FE sem) ###")
g["N2"]=g["N"]**2/1000
t3e=[]
for a in ["BERC1","BERC2","MINI1","MINI2"]:
    sub=g[g["agrup"]==a].copy()
    beta,se,n,G=twoway_fe(sub,"real_size",["pred_size","N","N2"],"codesc","sidx")
    F=(beta[0]/se[0])**2
    print(f"  {LAB[a]}: b(previsto)={beta[0]:.3f} (se {se[0]:.3f}) F={F:.1f}  N={n} escolas={G}")
    t3e.append((a,beta[0],se[0],F,n))
pd.DataFrame(t3e,columns=["agrup","b_pred","se","F","N"]).to_csv(os.path.join(STG,"t3e_firststage.csv"),index=False)
print("\nOK diag12_t3")
