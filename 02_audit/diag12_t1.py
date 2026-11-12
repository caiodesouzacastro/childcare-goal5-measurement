# -*- coding: utf-8 -*-
import os as _os_ne  # pacote de replicacao (R3): raiz unica, variavel NE_ROOT ou a pasta acima de 02_audit
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
# DIAG12 TESTE 1 - degraus da formula de repasse (Portaria SME 5.272/2007).
# Base: parc_parcerias032023.csv (5.926 registros). Bunching de vagas_contratadas
# em 60/90/120 e quebra de inclinacao do repasse per capita.
import sys; sys.stdout.reconfigure(encoding="utf-8")
import numpy as np, csv, os, glob, collections
np.random.seed(20260722)
SRC=NE_ROOT + r"\01_dados_publicos"
OUT=NE_ROOT + r"\03_build\build01\_staging"; os.makedirs(OUT,exist_ok=True)
def rd(fn):
    rows=[]
    with open(os.path.join(SRC,fn),encoding="latin-1") as f:
        for r in csv.DictReader(f,delimiter=";"):
            rows.append({(k or "").strip().lower().lstrip("﻿"):v for k,v in r.items()})
    return rows
def fnum(x):
    try: return float(str(x).replace(",",".").replace("R$","").strip())
    except: return None

P=rd("parc_parcerias032023.csv")
vc=[]; vm=[]; vb=[]
for r in P:
    a=fnum(r.get("vagas_contratadas")); v=fnum(r.get("valor_mensal")); b=fnum(r.get("vagas_bercario_contratadas"))
    if a and a>0:
        vc.append(a); vm.append(v if v else np.nan); vb.append(b if b else 0.0)
vc=np.array(vc); vm=np.array(vm); vb=np.array(vb)
print(f"N contratos com vagas>0: {len(vc)}")

# ---------- T1a: histograma resolucao 1, 30-200 ----------
cnt=collections.Counter(int(round(x)) for x in vc)
print("\n### T1a: contagens exatas ###")
for lo,hi,thr in [(55,65,60),(85,95,90),(115,125,120)]:
    seg=" ".join(f"{v}:{cnt.get(v,0)}" for v in range(lo,hi+1))
    print(f"  em torno de {thr}: {seg}")
# exporta histograma 30-200
with open(os.path.join(OUT,"t1_hist.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["vagas","n"])
    for v in range(30,201): w.writerow([v,cnt.get(v,0)])

# ---------- T1b: bunching / excesso de massa ----------
xs=np.arange(30,201)
ys=np.array([cnt.get(v,0) for v in xs],dtype=float)
def excess_mass(thr, win=3, exclude=(-3,2), deg=5, nboot=500):
    # ajusta polinomio excluindo janela [thr+exclude0, thr+exclude1]; contrafactual
    ex_lo,ex_hi=thr+exclude[0],thr+exclude[1]
    mask=~((xs>=ex_lo)&(xs<=ex_hi))
    coef=np.polyfit(xs[mask],ys[mask],deg)
    cf=np.polyval(coef,xs)
    # excesso just-below: [thr-3, thr]
    below=(xs>=thr-3)&(xs<=thr)
    obs_b=ys[below].sum(); cf_b=cf[below].sum()
    B=(obs_b-cf_b)/ (cf_b/ (below.sum())) if cf_b>0 else np.nan  # excesso normalizado (n bins)
    # bootstrap: reamostra Poisson dos contrafactuais
    bs=[]
    for _ in range(nboot):
        yb=np.random.poisson(np.clip(cf,0,None))
        m2=~((xs>=ex_lo)&(xs<=ex_hi))
        c2=np.polyfit(xs[m2],yb[m2],deg); cf2=np.polyval(c2,xs)
        ob=yb[below].sum(); cb=cf2[below].sum()
        bs.append((ob-cb)/(cb/below.sum()) if cb>0 else np.nan)
    return B, np.nanstd(bs), obs_b, cf_b
print("\n### T1b: excesso de massa logo abaixo do limiar ###")
t1b_rows=[]
for thr in [60,90,120]:
    B,se,ob,cf=excess_mass(thr)
    print(f"  limiar {thr}: obs[thr-3,thr]={ob:.0f} contrafactual={cf:.1f} excesso(bins)={B:.2f} (EP boot {se:.2f})")
    t1b_rows.append((thr,ob,cf,B,se))

# ---------- T1c: repasse per capita vs vagas; quebra de inclinacao ----------
pc=vm/vc
def band(a):
    return "<=60" if a<=60 else "61-90" if a<=90 else "91-120" if a<=120 else ">120"
bands=np.array([band(a) for a in vc])
print("\n### T1c: repasse per capita medio por faixa ###")
t1c_rows=[]
for bnd in ["<=60","61-90","91-120",">120"]:
    m=(bands==bnd)&np.isfinite(pc)
    print(f"  {bnd}: n={m.sum()} media pc={np.nanmean(pc[m]):.1f} mediana={np.nanmedian(pc[m]):.1f}")
    t1c_rows.append((bnd,int(m.sum()),float(np.nanmean(pc[m])),float(np.nanmedian(pc[m]))))
# quebra de inclinacao: spline linear com nos em 60/90/120 sobre valor_mensal ~ vagas
ok=np.isfinite(vm)&np.isfinite(vc)
X=np.column_stack([np.ones(ok.sum()),vc[ok],
    np.clip(vc[ok]-60,0,None),np.clip(vc[ok]-90,0,None),np.clip(vc[ok]-120,0,None)])
beta,_,_,_=np.linalg.lstsq(X,vm[ok],rcond=None)
print("\n  spline valor_mensal ~ vagas (inclinacao marginal por R$/vaga):")
print(f"    <=60: {beta[1]:.1f} ; 61-90: {beta[1]+beta[2]:.1f} ; 91-120: {beta[1]+beta[2]+beta[3]:.1f} ; >120: {beta[1]+beta[2]+beta[3]+beta[4]:.1f}")
print(f"    quebras (delta inclinacao) em 60/90/120: {beta[2]:.1f} / {beta[3]:.1f} / {beta[4]:.1f}")

# ---------- T1d: adicional de bercario ----------
print("\n### T1d: repasse per capita por bercario>0 vs =0, controlando faixa ###")
for bnd in ["<=60","61-90","91-120",">120"]:
    m=(bands==bnd)&np.isfinite(pc)
    b1=m&(vb>0); b0=m&(vb==0)
    if b1.sum()>5 and b0.sum()>5:
        print(f"  {bnd}: berc>0 pc={np.nanmean(pc[b1]):.1f} (n{b1.sum()}) | berc=0 pc={np.nanmean(pc[b0]):.1f} (n{b0.sum()}) | dif={np.nanmean(pc[b1])-np.nanmean(pc[b0]):.1f}")
    else:
        print(f"  {bnd}: n insuficiente (berc>0 n{b1.sum()}, berc=0 n{b0.sum()})")

# ---------- T1e: serie do repasse per capita medio por faixa e ano ----------
print("\n### T1e: repasse per capita medio por faixa, por snapshot ###")
snaps=[("032018","2018-03"),("032019","2019-03"),("032020","2020-03"),("032021","2021-03"),
       ("092022","2022-09"),("032023","2023-03")]
t1e_rows=[]
for key,lab in snaps:
    cand=[f for f in glob.glob(os.path.join(SRC,f"parc_*{key}*.csv"))]
    if not cand: print(f"  {lab}: arquivo nao encontrado"); continue
    R=rd(os.path.basename(cand[0]))
    aa=[];vv=[]
    for r in R:
        a=fnum(r.get("vagas_contratadas")); v=fnum(r.get("valor_mensal"))
        if a and a>0 and v: aa.append(a); vv.append(v)
    aa=np.array(aa); vv=np.array(vv); ppc=vv/aa; bb=np.array([band(a) for a in aa])
    means={bnd:float(np.nanmean(ppc[bb==bnd])) for bnd in ["<=60","61-90","91-120",">120"]}
    print(f"  {lab} (n{len(aa)}): "+" ".join(f"{k}={means[k]:.0f}" for k in means))
    t1e_rows.append((lab,len(aa),means))
print("\nOK diag12_t1")
