# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding="utf-8")
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
import pandas as pd, numpy as np, os
from lib import norm, rd, IN

# ---------- 1. BIRTHS ----------
nv=pd.read_parquet(os.path.join(IN,"nv_long.parquet"))[['norm','ano','nasc']].rename(columns={'norm':'d','nasc':'births'})

# ---------- 2. CEP -> district bridge + district covariates ----------
ren=rd("cep_renda_pop_2010.dta",usecols=['cep','nm_distrit','populacao','renda','cod_setor'])
ren['d']=ren['nm_distrit'].map(norm); ren['cep']=ren['cep'].astype('int64')
# district total population (unique setor) and pop-weighted renda
setor=ren.drop_duplicates('cod_setor')
pop_d=setor.groupby('d')['populacao'].sum().rename('pop_tot')
# pop-weighted mean renda by district (weight = setor pop, using unique setor)
sd=setor.dropna(subset=['renda','populacao'])
renda_d=(sd.assign(w=sd['populacao']).groupby('d').apply(lambda g: np.average(g['renda'],weights=g['w']))).rename('renda')
# IPVS from cep_covars merged by cep -> district (modal/mean)
cc=pd.read_csv(os.path.join(IN,"cep_covars.csv")); cc['cep']=cc['cep'].astype('int64')
cep2d=ren[['cep','d']].drop_duplicates('cep')
ccd=cc.merge(cep2d,on='cep',how='inner')
ipvs_d=ccd.groupby('d')['ipvs_grupo'].mean().rename('ipvs_mean')
covars=pd.concat([pop_d,renda_d,ipvs_d],axis=1).reset_index()
print("covars districts:",covars['d'].nunique(),"| pop_tot sum:",int(covars['pop_tot'].sum()))

# ---------- 3. FILA solicitations + matriculas from B_novo ----------
b=rd("B_novo.dta",usecols=['cep_aluno','ano_sol','ever_mat','dt_mat_first'])
b['cep_aluno']=b['cep_aluno'].astype('int64')
b=b.merge(cep2d.rename(columns={'cep':'cep_aluno'}),on='cep_aluno',how='left')
sol=b.dropna(subset=['d']).groupby(['d','ano_sol']).size().rename('solic').reset_index().rename(columns={'ano_sol':'ano'})
# matriculas by year of dt_mat_first
b['mat_year']=pd.to_datetime(pd.to_numeric(b['dt_mat_first'],errors='coerce'),unit='D',origin='1960-01-01',errors='coerce').dt.year
mat=b.dropna(subset=['d','mat_year']).groupby(['d','mat_year']).size().rename('matric').reset_index().rename(columns={'mat_year':'ano'})
mat['ano']=mat['ano'].astype(int)

# ---------- 4. CAPACITY (VAGOFER) by district-year, agrup, rede ----------
pc=pd.read_csv(os.path.join(IN,"perfil_panel_creche.csv"))
pc['d']=pc['distrito'].map(norm)
# year-end snapshot: sem==2; for 2019 only sem1 exists -> use max sem available per year
def yearend(df):
    idx=df.groupby(['ano'])['sem'].transform('max')
    return df[df['sem']==idx]
pcye=yearend(pc)
cap_tot=pcye.groupby(['d','ano'])['cap_vagofer'].sum().rename('cap').reset_index()
cap_rede=pcye.groupby(['d','ano','rede'])['cap_vagofer'].sum().unstack('rede').add_prefix('cap_').reset_index()
cap_agr=pcye.groupby(['d','ano','agrup'])['cap_vagofer'].sum().unstack('agrup').add_prefix('cap_').reset_index()
# n CEIs in operation (distinct codesc with cap>0) by rede, year-end
op=pcye[pcye['cap_vagofer']>0]
nceis=op.groupby(['d','ano'])['codesc'].nunique().rename('n_cei').reset_index()
nceis_rede=op.groupby(['d','ano','rede'])['codesc'].nunique().unstack('rede').add_prefix('ncei_').reset_index()
print("cap years:",sorted(cap_tot['ano'].unique()))

# ---------- 5. ASSEMBLE district x year panel ----------
years=list(range(2007,2020))
dists=sorted(nv['d'].dropna().unique())
grid=pd.MultiIndex.from_product([dists,years],names=['d','ano']).to_frame(index=False)
P=grid.merge(nv,on=['d','ano'],how='left') \
      .merge(sol,on=['d','ano'],how='left') \
      .merge(mat,on=['d','ano'],how='left') \
      .merge(cap_tot,on=['d','ano'],how='left') \
      .merge(cap_rede,on=['d','ano'],how='left') \
      .merge(cap_agr,on=['d','ano'],how='left') \
      .merge(nceis,on=['d','ano'],how='left') \
      .merge(nceis_rede,on=['d','ano'],how='left') \
      .merge(covars,on='d',how='left')
for c in ['solic','matric','cap','n_cei']:
    if c in P: P[c]=P[c]
P=P.sort_values(['d','ano']).reset_index(drop=True)
P.to_parquet(os.path.join(IN,"panel_d.parquet"))
print("\nPANEL shape:",P.shape,"| districts:",P['d'].nunique(),"years:",P['ano'].min(),P['ano'].max())
print("cols:",list(P.columns))
print("\nnonmissing counts:"); print(P[['births','solic','matric','cap']].notna().sum())
