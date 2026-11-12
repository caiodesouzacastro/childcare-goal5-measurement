# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
from lib import IN
from reglib import add_birth_lags, panelfe, show
P=pd.read_parquet(os.path.join(IN,"panel_d.parquet")).sort_values(['d','ano'])
AGR={'BERC1':'0-13m (expect t/t-1)','BERC2':'14-22m (expect t-1)','MINI1':'23-34m (expect t-2)','MINI2':'35-46m (expect t-3)'}
for a in AGR: P[f'd_{a}']=P.groupby('d')[f'cap_{a}'].diff()
D=add_birth_lags(P,lags=range(0,5))
LAGS=[f'b_l{k}' for k in range(5)]

print("===== PART D: LAG STRUCTURE BY AGRUPAMENTO (age) =====")
print("Δcap_agrup ~ births(t..t-4), FE district+year, cluster district")
peak={}
for a,lbl in AGR.items():
    print(f"\n### {a}  [{lbl}] ###")
    try:
        res=panelfe(D,f'd_{a}',LAGS); show(res,LAGS)
        p=res.params[LAGS]; pv=res.pvalues[LAGS]
        # peak lag = largest positive significant; else largest |t|
        sig=[(k,p[f'b_l{k}'],pv[f'b_l{k}']) for k in range(5)]
        pospos=[(k,b) for k,b,pp in sig if b>0 and pp<0.10]
        pk = max(pospos,key=lambda x:x[1])[0] if pospos else max(range(5),key=lambda k:abs(res.tstats[f'b_l{k}']))
        peak[a]=pk
    except Exception as e: print("  ERR",str(e)[:90]); peak[a]='ERR'
print("\n== D2 PEAK LAG BY AGRUPAMENTO ==")
print("  agrup   expected_peak         observed_peak_lag")
exp={'BERC1':'0-1','BERC2':'1','MINI1':'2','MINI2':'3'}
for a in AGR: print(f"  {a:6s}  {exp[a]:18s}  t-{peak[a]}")

print("\n===== POWER / WITHIN-VARIATION DIAGNOSTIC (F4) =====")
# fraction of births variance that is within-district
b=P.dropna(subset=['births']).copy()
import statsmodels.formula.api as smf
tot=b['births'].var()
wdm=b['births']-b.groupby('d')['births'].transform('mean')
within_sd=wdm.std(); 
# residual within-district AND within-year (two-way)
bym=b['births']-b.groupby('ano')['births'].transform('mean')
b['bw']=b['births']-b.groupby('d')['births'].transform('mean')-b.groupby('ano')['births'].transform('mean')+b['births'].mean()
print(f"births: overall SD={b['births'].std():.0f}; within-district SD={within_sd:.0f}; two-way residual SD={b['bw'].std():.1f}")
print(f"  within-district birth variation is {within_sd/b['births'].std()*100:.1f}% of overall; two-way residual {b['bw'].std()/b['births'].std()*100:.1f}%")
# restrict to capacity years 2013-2019
b2=b[b['ano'].between(2013,2019)].copy()
b2['bw']=b2['births']-b2.groupby('d')['births'].transform('mean')-b2.groupby('ano')['births'].transform('mean')+b2['births'].mean()
print(f"  2013-2019 two-way residual births SD = {b2['bw'].std():.1f} (this is the identifying variation for C1)")
# MDE for C1 dcap ~ births: se of b_l0 was ~0.58 (raw). MDE ~ 2.8*se
se_bl0=0.579
print(f"\nC1 raw: SE(b_l0)~{se_bl0}; MDE (80% power, 5%) ~ 2.8*SE = {2.8*se_bl0:.2f} vagas per extra birth")
print(f"  i.e. can only detect responses larger than ~{2.8*se_bl0:.1f} authorized vagas created per additional birth within a district-year.")
