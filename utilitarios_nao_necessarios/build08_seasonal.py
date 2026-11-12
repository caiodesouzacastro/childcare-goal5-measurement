# -*- coding: utf-8 -*-
# BUILD08 - sazonalidade do DEM_CRECHE (T12, F13). Parsing CORRETO (thousands="."; ver DIAG16).
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":11,"figure.dpi":120})
ROOT=NE_ROOT
EXT=os.path.join(ROOT,r"03_build\build04\_ext\evolucaodemanda.csv")
TAB=os.path.join(ROOT,r"03_build\build04\tables"); FIG=os.path.join(ROOT,r"03_build\build04\figures")
MES={"jan":1,"fev":2,"mar":3,"abr":4,"mai":5,"jun":6,"jul":7,"ago":8,"set":9,"out":10,"nov":11,"dez":12}
df=pd.read_csv(EXT,sep=";",thousands=".",dtype={"MES_ANO_REF":str})
df["ano"]=df.MES_ANO_REF.str[-2:].astype(int)+2000; df["mes"]=df.MES_ANO_REF.str[:3].map(MES)
df["DEM_CRECHE"]=pd.to_numeric(df.DEM_CRECHE,errors="coerce")
mun=df.groupby(["ano","mes"]).DEM_CRECHE.sum().reset_index()
piv=mun.pivot(index="ano",columns="mes",values="DEM_CRECHE")[[3,6,9,12]]
piv.columns=["mar","jun","set","dez"]
piv=piv.loc[2006:2017]
piv.reset_index().to_csv(os.path.join(TAB,"T12_sazonalidade.csv"),index=False)

def nf(x):
    try:
        x=float(x)
        return "--" if pd.isna(x) else f"{x:,.0f}"
    except: return "--"
cap="Registered childcare demand by quarter, municipality of S\\~ao Paulo"
note=("The series is strongly seasonal: registered demand peaks in September and falls in December, after the "
      "enrolment round. Comparisons across years use the December snapshot throughout.")
L=["% requer booktabs. Descritivo.","\\begin{table}[htbp]\\centering",f"\\caption{{{cap}}}",
   "\\label{tab:T12}","\\small","\\setlength{\\tabcolsep}{5pt}","\\begin{tabular}{lrrrr}","\\toprule",
   "Year & March & June & September & December \\\\","\\midrule"]
for y,r in piv.iterrows(): L.append(f"{int(y)} & {nf(r['mar'])} & {nf(r['jun'])} & {nf(r['set'])} & {nf(r['dez'])} \\\\")
L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
open(os.path.join(TAB,"T12_sazonalidade.tex"),"w",encoding="utf-8").write("\n".join(L)+"\n")
print("tex: T12_sazonalidade")

# F13
fig,ax=plt.subplots(figsize=(7.2,4.4))
for q,lab,c in [("set","September","#c0392b"),("jun","June","#e67e22"),("mar","March","#2980b9"),("dez","December","#1b7837")]:
    ax.plot(piv.index,piv[q]/1000,"-o",ms=4,label=lab,color=c)
ax.set_xlabel("Year"); ax.set_ylabel("Registered demand (thousands)")
ax.set_title("Registered childcare demand by quarter, 2006–2017")
ax.legend(title="Quarter"); ax.grid(True,alpha=.3); ax.set_xticks(range(2006,2018,2)); fig.tight_layout()
fig.savefig(os.path.join(FIG,"F13_sazonalidade.pdf")); plt.close(fig)
piv.reset_index().to_csv(os.path.join(FIG,"F13_data.csv"),index=False)
print("fig F13")
print("\nDEM_CRECHE municipal por trimestre (2006-2017):")
print(piv.to_string(float_format=lambda x:f"{x:,.0f}"))
