# -*- coding: utf-8 -*-
# BUILD04 - F10 (estoque da fila x matriculas em creche, municipio, 2006-2017) e T11.
# Fonte: open data PMSP "Demanda Registrada e Matriculas" (serie 2006-2017). Descritivo.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":11,"figure.dpi":120})
ROOT=NE_ROOT
TAB=os.path.join(ROOT,r"03_build\build04\tables"); FIG=os.path.join(ROOT,r"03_build\build04\figures")
os.makedirs(FIG,exist_ok=True)
d=pd.read_csv(os.path.join(TAB,"D15_E_anual_dez.csv"))

# ---------- F10 (merge of old F10 + F13): enrolment (annual) + registered
#            demand (quarterly). Two stacked panels, shared x-axis. ----------
EXT=os.path.join(ROOT,r"03_build\build04\_ext\evolucaodemanda.csv")
MES={"jan":1,"fev":2,"mar":3,"abr":4,"mai":5,"jun":6,"jul":7,"ago":8,"set":9,"out":10,"nov":11,"dez":12}
evd=pd.read_csv(EXT,sep=";",thousands=".",dtype={"MES_ANO_REF":str})
evd["ano"]=evd.MES_ANO_REF.str[-2:].astype(int)+2000; evd["mes"]=evd.MES_ANO_REF.str[:3].map(MES)
evd["DEM_CRECHE"]=pd.to_numeric(evd.DEM_CRECHE,errors="coerce")
q=evd.groupby(["ano","mes"]).DEM_CRECHE.sum().reset_index()
piv=q.pivot(index="ano",columns="mes",values="DEM_CRECHE")[[3,6,9,12]]; piv=piv.loc[2006:2017]

fig,(axT,axB)=plt.subplots(2,1,sharex=True,figsize=(7.2,6.2),
                           gridspec_kw={"hspace":0.14})
axT.plot(d.ano,d.mat/1000,"-o",color="#1b7837")
axT.set_ylabel("Enrolment\n(thousands)"); axT.grid(True,alpha=.3)
axT.set_title("Childcare enrolment (annual) and registered demand (by quarter), 2006–2017")
for m,lab,c in [(9,"September","#c0392b"),(6,"June","#e67e22"),(3,"March","#2980b9"),(12,"December","#1b7837")]:
    axB.plot(piv.index,piv[m]/1000,"-o",ms=3,label=lab,color=c)
axB.set_ylabel("Registered demand\n(thousands)"); axB.grid(True,alpha=.3)
axB.set_xlabel("Year"); axB.set_xticks(range(2006,2018,2))
axB.legend(title="Quarter",fontsize=8,ncol=2,loc="upper right")
fig.savefig(os.path.join(FIG,"F10_estoque_matricula.pdf"),bbox_inches="tight"); plt.close(fig)
d[["ano","mat","dem","dem_total"]].to_csv(os.path.join(FIG,"F10_data.csv"),index=False)
piv.reset_index().to_csv(os.path.join(FIG,"F10_quarterly.csv"),index=False)
print("fig F10 (merged with quarterly demand) + data")

# ---------- T11 ----------
def nf(x):
    try: return f"{float(x):,.0f}"
    except: return str(x)
body=[]
for _,r in d.iterrows():
    cr=f"{r.mat_cresc_pct:+.1f}" if pd.notna(r.mat_cresc_pct) else "--"
    body.append([str(int(r.ano)),nf(r.mat),cr,nf(r.dem),nf(r.dem_total)])
cap="Childcare enrolment and registered demand (queue stock) in the municipality of S\\~ao Paulo, 2006--2017"
note=("Open data of the municipality (``Demanda Registrada e Matriculas'', historical series 2006--2017), "
      "summed over 96 districts, December snapshot of each year. Enrolment = childcare (creche) enrolment (MAT\\_CRECHE); "
      "registered demand = the stock of children on the waiting list for a childcare place (DEM\\_CRECHE); demand "
      "incl.\\ preferential adds preferential demand (DEM\\_PREF\\_CRECHE). The 2013 enrolment (214,460) matches the "
      "offered-places series used in the paper (VAGOFER 2013S1, 214,561). Source: Portal de Dados Abertos PMSP.")
L=["% requer booktabs. Descritivo.","\\begin{table}[htbp]\\centering",f"\\caption{{{cap}}}",
   "\\label{tab:T11}","\\small","\\begin{tabular}{lrrrr}","\\toprule",
   "Year & Enrolment & Growth \\% & Registered demand & Demand incl.\\ pref. \\\\","\\midrule"]
for b in body: L.append(" & ".join(b)+" \\\\")
L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
open(os.path.join(TAB,"T11_estoque_demanda.tex"),"w",encoding="utf-8").write("\n".join(L)+"\n")
d[["ano","mat","mat_cresc_pct","dem","dem_total"]].to_csv(os.path.join(TAB,"T11_estoque_demanda.csv"),index=False)
print("T11_estoque_demanda.tex + .csv")
print("\n== serie anual (dez), municipio ==")
print("ano   MAT(creche)  DEM(fila)   DEM+pref")
for _,r in d.iterrows(): print(f"{int(r.ano)}   {int(r.mat):>9,}   {int(r.dem):>8,}   {int(r.dem_total):>8,}")
