# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
from lib import IN
from reglib import add_birth_lags, panelfe, show
P=pd.read_parquet(os.path.join(IN,"panel_d.parquet"))
pd.set_option('display.width',160)
print("=======================  PART B2: DESCRIPTIVES  =======================")
cols=['births','solic','matric','cap','cap_DIR','cap_CON','n_cei','renda','ipvs_mean','pop_tot']
desc=P[cols].describe(percentiles=[.5]).T[['count','mean','std','min','50%','max']]
print(desc.to_string(float_format=lambda x:f'{x:,.1f}'))
print("\n-- capacity present only 2013-2019; solic 2007-2018; matric 2009-2017 --")
print("\n== B2 contemporaneous correlation (births, solic, cap) 2013-2018 ==")
sub=P[(P['ano'].between(2013,2018))][['births','solic','cap','matric','n_cei']]
print(sub.corr().round(3).to_string())

print("\n=======================  PART B3: DEMAND VALIDATION  =======================")
print("Do births(t-k) predict solicitations(t)?  FE district + FE year, cluster district")
D=add_birth_lags(P)
for k in range(0,4):
    print(f"\n-- lag k={k}: solic ~ b_l{k} --")
    try: show(panelfe(D,'solic',[f'b_l{k}']),[f'b_l{k}'])
    except Exception as e: print("  ERR",str(e)[:90])
print("\n-- distributed lag: solic ~ b_l0..b_l3 jointly --")
try: show(panelfe(D,'solic',['b_l0','b_l1','b_l2','b_l3']),['b_l0','b_l1','b_l2','b_l3'])
except Exception as e: print("  ERR",str(e)[:90])
for lo,hi in [(2009,2013),(2014,2018)]:
    print(f"\n-- period {lo}-{hi}: solic ~ b_l0..b_l3 --")
    sub=D[D['ano'].between(lo,hi)]
    try: show(panelfe(sub,'solic',['b_l0','b_l1','b_l2','b_l3']),['b_l0','b_l1','b_l2','b_l3'])
    except Exception as e: print("  ERR",str(e)[:90])
