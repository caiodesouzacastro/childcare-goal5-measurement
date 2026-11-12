# -*- coding: utf-8 -*-
# DIAG15 Parte E - estender a serie para tras (2006-2017) com o open data da PMSP.
# Fonte: Portal de Dados Abertos SP, "Demanda Registrada e Matriculas" (serie 2006-2017),
#   arquivo evolucaodemanda.csv (distrito x trimestre). Descritivo.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
ROOT=NE_ROOT
EXT=os.path.join(ROOT,r"03_build\build04\_ext\evolucaodemanda.csv")
TAB=os.path.join(ROOT,r"03_build\build04\tables")
SUM=[]
def S(x): SUM.append(x); print(x)
MES={"jan":1,"fev":2,"mar":3,"abr":4,"mai":5,"jun":6,"jul":7,"ago":8,"set":9,"out":10,"nov":11,"dez":12}
df=pd.read_csv(EXT,sep=";",thousands=".",dtype={"DISTRITO":str,"MES_ANO_REF":str})
def to_period(s):
    m,a=s.split("-"); return pd.Timestamp(2000+int(a),MES[m],1)
df["data"]=df.MES_ANO_REF.map(to_period); df["ano"]=df.data.dt.year; df["mes"]=df.data.dt.month
for c in ["MAT_CRECHE","DEM_CRECHE","DEM_PREF_CRECHE","MAT_PROC_CRECHE"]:
    df[c]=pd.to_numeric(df[c],errors="coerce")
S(f"# Parte E: open data PMSP, {df.DISTRITO.nunique()} distritos x {df.MES_ANO_REF.nunique()} trimestres (jun/2006-dez/2017).")
S("# MAT_CRECHE=matriculas creche; DEM_CRECHE=demanda registrada (fila) creche; DEM_PREF_CRECHE=demanda preferencial.")

# ---- municipio por trimestre ----
mun=df.groupby("data").agg(mat=("MAT_CRECHE","sum"),dem=("DEM_CRECHE","sum"),
    dem_pref=("DEM_PREF_CRECHE","sum"),mat_proc=("MAT_PROC_CRECHE","sum")).reset_index()
mun["dem_total"]=mun.dem+mun.dem_pref.fillna(0)
mun.to_csv(os.path.join(TAB,"D15_E_serie_trimestral.csv"),index=False)

# ---- snapshot anual: dezembro (ou ultimo trimestre do ano) ----
dez=df[df.mes==12].groupby("ano").agg(mat=("MAT_CRECHE","sum"),dem=("DEM_CRECHE","sum"),
    dem_pref=("DEM_PREF_CRECHE","sum")).reset_index()
dez["dem_total"]=dez.dem+dez.dem_pref.fillna(0)
dez["mat_cresc_pct"]=100*dez.mat.pct_change()
dez.to_csv(os.path.join(TAB,"D15_E_anual_dez.csv"),index=False)
S("\nE2/E3: matriculas em creche (MAT) e demanda registrada/fila (DEM) no MUNICIPIO, snapshot dezembro:")
S("  ano   MAT_creche   cresc%   DEM_creche   DEM_total(+pref)")
for _,r in dez.iterrows():
    cr=f"{r.mat_cresc_pct:+.1f}" if pd.notna(r.mat_cresc_pct) else "  -- "
    S(f"  {int(r.ano)}   {int(r.mat):>9,}   {cr:>6}   {int(r.dem):>9,}   {int(r.dem_total):>9,}")

def g(y0,y1,col="mat"):
    a=dez[dez.ano==y0][col].values[0]; b=dez[dez.ano==y1][col].values[0]
    return a,b,100*(b/a-1),100*((b/a)**(1/(y1-y0))-1)
S("\nE2 crescimento de MATRICULAS em creche (municipio, dez):")
for lab,y0,y1 in [("2006->2012",2006,2012),("2010->2012",2010,2012),("2013->2017",2013,2017),("2006->2017",2006,2017)]:
    a,b,tot,cagr=g(y0,y1,"mat"); S(f"  {lab}: {int(a):,} -> {int(b):,}  (+{tot:.1f}% total; {cagr:.1f}%/ano)")
S("\nE3 crescimento da DEMANDA registrada em creche (fila, municipio, dez):")
for lab,y0,y1 in [("2006->2012",2006,2012),("2010->2012",2010,2012),("2013->2017",2013,2017)]:
    a,b,tot,cagr=g(y0,y1,"dem"); S(f"  {lab}: {int(a):,} -> {int(b):,}  (+{tot:.1f}% total; {cagr:.1f}%/ano)")
S(f"\nE3 pico da fila (DEM_creche, dez): {int(dez.dem.max()):,} em {int(dez.loc[dez.dem.idxmax(),'ano'])}; "
  f"minimo {int(dez.dem.min()):,} em {int(dez.loc[dez.dem.idxmin(),'ano'])}.")

# sanity: MAT_creche 2013 vs VAGOFER perfil 2013 (~214.561)
S(f"\nsanidade: MAT_creche(dez2013)={int(dez[dez.ano==2013].mat.values[0]):,} vs VAGOFER perfil 2013s1~214.561 (ordens de grandeza compativeis).")

with open(os.path.join(TAB,"_DIAG15_E_resumo.txt"),"w",encoding="utf-8") as f: f.write("\n".join(SUM))
print("\nOK build04_diag15E (Parte E)")
