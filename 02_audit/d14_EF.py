# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
from lib import IN, rd, norm
from reglib import add_birth_lags, panelfe, show, NV
from linearmodels.iv import IV2SLS
P=pd.read_parquet(os.path.join(IN,"panel_d.parquet")).sort_values(['d','ano'])
P['dcap']=P.groupby('d')['cap'].diff()
P['dcap_DIR']=P.groupby('d')['cap_DIR'].diff()
P['dcap_CON']=P.groupby('d')['cap_CON'].diff()
D=add_birth_lags(P,lags=range(0,5))
LAGS=[f'b_l{k}' for k in range(5)]

print("===== PART C4: IV (capacity ~ solic, instrument solic with lagged births) =====")
def twoway_demean(df,cols):
    d=df.copy()
    for c in cols:
        d[c]=d[c]-d.groupby('d')[c].transform('mean')-d.groupby('ano')[c].transform('mean')+d[c].mean()
    return d
iv=D.dropna(subset=['cap','solic','b_l1','b_l2','b_l3']).copy()
ivd=twoway_demean(iv,['cap','solic','b_l1','b_l2','b_l3'])
# first stage
import statsmodels.api as sm
fs=sm.OLS(ivd['solic'],sm.add_constant(ivd[['b_l1','b_l2','b_l3']])).fit(cov_type='cluster',cov_kwds={'groups':iv['d']})
print("First stage solic ~ b_l1..b_l3 (two-way demeaned):")
print(f"  b_l1={fs.params['b_l1']:.3f} b_l2={fs.params['b_l2']:.3f} b_l3={fs.params['b_l3']:.3f}  F={fs.fvalue:.2f}")
try:
    res=IV2SLS(ivd['cap'],None,ivd[['solic']],ivd[['b_l1','b_l2','b_l3']]).fit(cov_type='clustered',clusters=iv['d'])
    print(f"Second stage: cap ~ solic(IV):  b={res.params['solic']:.4f}  se={res.std_errors['solic']:.4f}  p={res.pvalues['solic']:.3f}")
except Exception as e: print("  IV err",str(e)[:100])

print("\n===== PART E1: DIR vs CON reaction (Δcap by rede ~ births lags) =====")
for lab,y in [('DIRETA','dcap_DIR'),('CONVENIADA','dcap_CON')]:
    print(f"### {lab} ###")
    try: show(panelfe(D,y,LAGS),LAGS)
    except Exception as e: print("  ERR",str(e)[:80])

print("\n===== PART E2/E4: heterogeneity by income quartile (Δcap ~ births×quartile) =====")
q=P.groupby('d')['renda'].first().rank(pct=True)
P['rq']=P['d'].map((q*4).apply(np.ceil).clip(1,4))
D=add_birth_lags(P,lags=range(0,5))
# conversion rate: total Δcap per total births by quartile and period
for lo,hi,lab in [(2013,2015,'2013-2015'),(2016,2019,'2016-2019')]:
    print(f"\n-- conversion Δvagas per birth, {lab} --")
    s=P[P['ano'].between(lo,hi)]
    for qq in [1,2,3,4]:
        ss=s[s['rq']==qq]
        conv=ss['dcap'].sum()/ss['births'].sum()
        print(f"  Q{qq} renda: Σdcap={ss['dcap'].sum():.0f}  Σbirths={ss['births'].sum():.0f}  vagas/birth={conv:.4f}")

print("\n===== PART F2: PLACEBO — EMEF openings ~ births lags =====")
es=rd("escolas_parsed.dta",usecols=['tipoesc','distrito','dt_ini_func_d'])
es['d']=es['distrito'].map(norm)
es['fy']=pd.to_datetime(es['dt_ini_func_d'],errors='coerce').dt.year
def open_panel(mask,name):
    sub=es[mask].dropna(subset=['d','fy'])
    op=sub.groupby(['d','fy']).size().rename(name).reset_index().rename(columns={'fy':'ano'})
    return op
emef=open_panel(es['tipoesc'].astype(str).str.contains('EMEF',na=False),'emef_open')
cei =open_panel(es['tipoesc'].astype(str).str.contains('CEI|CR.P|CEMEI|CCI',na=False,regex=True),'cei_open')
G=P[['d','ano','births','pop_tot']].merge(emef,on=['d','ano'],how='left').merge(cei,on=['d','ano'],how='left')
G['emef_open']=G['emef_open'].fillna(0); G['cei_open']=G['cei_open'].fillna(0)
G=add_birth_lags(G,lags=range(0,5))
print("### CEI openings ~ births lags (should respond if design valid) ###")
try: show(panelfe(G[G['ano'].between(2008,2019)],'cei_open',LAGS),LAGS)
except Exception as e: print("  ERR",str(e)[:80])
print("### EMEF openings ~ births lags (placebo; if same pattern -> general public investment) ###")
try: show(panelfe(G[G['ano'].between(2008,2019)],'emef_open',LAGS),LAGS)
except Exception as e: print("  ERR",str(e)[:80])

print("\n===== PART F3: reaction function by administration =====")
for lo,hi,lab in [(2013,2016,'Haddad 2013-2016'),(2017,2019,'Doria/Covas 2017-2019')]:
    print(f"-- {lab}: Δcap ~ births lags --")
    try: show(panelfe(D[D['ano'].between(lo,hi)],'dcap',LAGS),LAGS)
    except Exception as e: print("  ERR",str(e)[:80])
