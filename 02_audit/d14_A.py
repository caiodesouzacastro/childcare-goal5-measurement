# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, unicodedata, os, re, pyreadstat
AUD=(NE_ROOT + r"\_audit")
BA=NE_ROOT + r"\dados_restritos\Ciro\01_dados\processados\bases_analise"
def _detok(s):  # Stata <c1> hex tokens -> latin1 char
    return re.sub(r'<([0-9a-fA-F]{2})>', lambda m: bytes([int(m.group(1),16)]).decode('latin1'), str(s))
def norm(s):
    if pd.isna(s): return s
    s=_detok(s).strip().upper()
    s=''.join(c for c in unicodedata.normalize('NFKD',s) if not unicodedata.combining(c))
    s=re.sub(r"[^A-Z0-9 ]","",s); s=re.sub(r'\s+',' ',s).strip()
    return s

nv=pd.read_csv(os.path.join(AUD,"sinasc_nv_distrito_2006_2026.csv"),sep=';',encoding='utf-8',quotechar='"')
nv=nv.rename(columns={nv.columns[0]:'distrito'})
nv=nv[nv['distrito']!='Total'].copy()
yrs=[c for c in nv.columns if c.isdigit()]
for c in yrs: nv[c]=pd.to_numeric(nv[c],errors='coerce')
nv_dist=nv[nv['distrito']!='Ignorado'].copy()
nv_dist['norm']=nv_dist['distrito'].map(norm)
print("SINASC districts:", nv_dist['norm'].nunique())

def dnames(path,col,ba=False):
    p=os.path.join(BA if ba else AUD,path)
    d,_=pyreadstat.read_dta(p,usecols=[col])
    return set(d[col].dropna().map(norm).unique())
R=dnames("cep_renda_pop_2010.dta","nm_distrit",ba=True)
C=dnames("cap_full.dta","distrito")
E=dnames("escolas_parsed.dta","distrito")
S=set(nv_dist['norm'])
print("cep_renda:",len(R),"cap_full:",len(C),"escolassite:",len(E))
print("\n== A4 (normalized: detok+upper+deaccent) ==")
print("SINASC∩cep_renda:",len(S&R),"| S−R:",sorted(S-R),"| R−S:",sorted(R-S))
print("SINASC∩cap_full :",len(S&C),"| S−C:",sorted(S-C),"| C−S:",sorted(C-S))
print("SINASC∩escola   :",len(S&E),"| S−E:",sorted(S-E),"| E−S:",sorted(E-S))

# A3: top/bottom 5 by total births 2010-2018 (analysis window)
win=[str(y) for y in range(2010,2019)]
nv_dist['tot1018']=nv_dist[win].sum(axis=1)
top=nv_dist.nlargest(5,'tot1018')[['distrito','tot1018']]
bot=nv_dist.nsmallest(5,'tot1018')[['distrito','tot1018']]
print("\n== A3 top5 births (sum 2010-2018) =="); print(top.to_string(index=False))
print("== A3 bottom5 =="); print(bot.to_string(index=False))
# Ignorado share
ig=nv[nv['distrito']=='Ignorado'][yrs].iloc[0]
tot=nv[nv['distrito']=='Total'][yrs].iloc[0] if (nv['distrito']=='Total').any() else nv_dist[yrs].sum()
print("\n== Ignorado share by year =="); 
for y in yrs: print(f"  {y}: {ig[y]/ (nv_dist[y].sum()+ig[y]) *100:.2f}%  (n={int(ig[y])})")
nvl=nv_dist.melt(id_vars=['distrito','norm'],value_vars=yrs,var_name='ano',value_name='nasc')
nvl['ano']=nvl['ano'].astype(int)
nvl.to_parquet(os.path.join(AUD,"nv_long.parquet"))
print("\nsaved nv_long.parquet",nvl.shape)
