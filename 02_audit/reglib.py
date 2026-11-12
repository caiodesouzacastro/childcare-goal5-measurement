# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, os, warnings
warnings.filterwarnings("ignore")
from lib import IN
from linearmodels.panel import PanelOLS
NV=pd.read_parquet(os.path.join(IN,"nv_long.parquet"))[['norm','ano','nasc']].rename(columns={'norm':'d'})
def add_birth_lags(df, lags=range(0,5), leads=()):
    out=df.copy()
    for k in lags:
        m=NV.rename(columns={'ano':'ano_m','nasc':f'b_l{k}'}); m['ano']=m['ano_m']+k
        out=out.merge(m[['d','ano',f'b_l{k}']],on=['d','ano'],how='left')
    for k in leads:
        m=NV.rename(columns={'ano':'ano_m','nasc':f'b_f{k}'}); m['ano']=m['ano_m']-k
        out=out.merge(m[['d','ano',f'b_f{k}']],on=['d','ano'],how='left')
    return out
def panelfe(df, y, xs, entity='d', tvar='ano', cluster=True):
    d=df.dropna(subset=[y]+xs).copy()
    d=d.set_index([entity,tvar])
    import statsmodels.api as sm
    X=d[xs]
    mod=PanelOLS(d[y],X,entity_effects=True,time_effects=True,drop_absorbed=True,check_rank=False)
    res=mod.fit(cov_type='clustered',cluster_entity=True)
    return res
def show(res, xs=None):
    p=res.params; se=res.std_errors; t=res.tstats; pv=res.pvalues
    ks=xs if xs else list(p.index)
    for k in ks:
        if k in p.index:
            star=''.join(['*' for th in (.1,.05,.01) if pv[k]<th])
            print(f"  {k:16s} b={p[k]:12.5f}  se={se[k]:10.5f}  t={t[k]:7.2f}  p={pv[k]:.3f} {star}")
    print(f"  N={int(res.nobs)}  entities={res.entity_info.total}  within-R2={res.rsquared_within:.4f}")
