# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
from lib import IN
from reglib import add_birth_lags, panelfe, show
P=pd.read_parquet(os.path.join(IN,"panel_d.parquet")).sort_values(['d','ano'])
# capacity deltas
P['dcap']=P.groupby('d')['cap'].diff()
P['dncei']=P.groupby('d')['n_cei'].diff()
P['logcap']=np.log(P['cap'])
# per-capita (per 1000 residents)
P['dcap_pc']=P['dcap']/P['pop_tot']*1000
D=add_birth_lags(P,lags=range(0,5),leads=(1,2))
for k in range(0,5): D[f'bpc_l{k}']=D[f'b_l{k}']/D['pop_tot']*1000
for k in (1,2):     D[f'bpc_f{k}']=D[f'b_f{k}']/D['pop_tot']*1000
for k in range(0,5): D[f'lb_l{k}']=np.log(D[f'b_l{k}'])
LAGS=[f'b_l{k}' for k in range(5)]; LAGSpc=[f'bpc_l{k}' for k in range(5)]; LLAGS=[f'lb_l{k}' for k in range(5)]

print("======================= PART C1: REACTION FUNCTION =======================")
print("Δcapacity(d,t) ~ births(t..t-4), FE district+year, cluster district\n")
print("### V1 RAW: Δcap ~ births lags (levels) ###")
show(panelfe(D,'dcap',LAGS),LAGS)
print("\n### V2 PER-CAPITA: Δcap per 1000 pop ~ births per 1000 pop lags ###")
show(panelfe(D,'dcap_pc',LAGSpc),LAGSpc)
print("\n### V3 LOG-LEVEL (elasticity): log(cap) ~ log(births) lags ###")
show(panelfe(D,'logcap',LLAGS),LLAGS)

print("\n======================= PART C2: LEADS (placebo) =======================")
print("Δcap ~ births(t..t-4) + births(t+1)+births(t+2); capacity must NOT move before births\n")
res=panelfe(D,'dcap',LAGS+['b_f1','b_f2'])
show(res,LAGS+['b_f1','b_f2'])
# joint test leads=0
from numpy.linalg import inv
try:
    import numpy as np
    R=res.params.index
    lead_names=[x for x in ['b_f1','b_f2'] if x in R]
    wt=res.wald_test(formula=" = 0, ".join(lead_names)+" = 0")
    print(f"\n  Joint Wald test (b_f1=b_f2=0): stat={wt.stat:.3f}  p={wt.pval:.4f}")
except Exception as e:
    print("  leads joint test err:",str(e)[:120])

print("\n======================= PART C3: LEVELS & N_CEI =======================")
print("### cap LEVEL ~ births lags ###")
show(panelfe(D,'cap',LAGS),LAGS)
print("\n### n_cei ~ births lags ###")
show(panelfe(D,'n_cei',LAGS),LAGS)
print("### Δn_cei ~ births lags ###")
show(panelfe(D,'dncei',LAGS),LAGS)
