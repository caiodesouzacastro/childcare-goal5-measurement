# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# DIAG15 - emite as tabelas-chave em .tex (booktabs, descritivo, ingles) a partir dos .csv.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, os
TAB=(NE_ROOT + r"\03_build\build04\tables")
def nf(x,d=1):
    try: x=float(x)
    except: return str(x)
    return f"{x:,.0f}" if d==0 else f"{x:,.{d}f}"
def emit(name,cap,note,cols,header,body):
    L=["% requer booktabs. Diagnostico descritivo.","\\begin{table}[htbp]\\centering",
       f"\\caption{{{cap}}}",f"\\label{{tab:{name}}}","\\small",f"\\begin{{tabular}}{{{cols}}}","\\toprule",
       " & ".join(header)+" \\\\","\\midrule"]
    for r in body: L.append("\\midrule" if r=="MID" else " & ".join(r)+" \\\\")
    L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
    open(os.path.join(TAB,name+".tex"),"w",encoding="utf-8").write("\n".join(L)+"\n"); print("tex:",name)
def rd(f): return pd.read_csv(os.path.join(TAB,f))

# B1 batch share
d=rd("D15_B1_lote_share.csv")
emit("D15_B1_lote_share","Share of first applications carrying a timestamp shared with other children, by year",
 "Each child's first application is dated to the second (day and hour:minute:second) in the raw queue register. Columns give the share of first applications whose exact timestamp is shared by at least 2, 10, 50 or 100 children. Batch (bulk) registration would show a high share sharing a timestamp; individual online applications do not. Source: build04\\_diag15.py (Fila1018).",
 "lrrrrr",["Year","N","$\\geq$2","$\\geq$10","$\\geq$50","$\\geq$100"],
 [[str(int(r.asol)),nf(r.N,0),nf(r.frac_sh2),nf(r.frac_sh10),nf(r.frac_sh50),nf(r.frac_sh100)] for r in d.itertuples()])

# B4 cohort with/without batches
d=rd("D15_B4_coorte_sem_lote.csv")
emit("D15_B4_coorte_sem_lote","Share of the birth cohort with a first application before 12 months, with and without batch registrations",
 "Denominator: live births (SINASC). Numerator: children of the cohort whose first application occurs before age 12 months. The last column excludes children whose first-application timestamp is shared by 10 or more children (a batch). Source: build04\\_diag15.py.",
 "lrrrr",["Birth cohort","Live births","Full (\\%)","Excl.\\ batches (\\%)","\\% batch in cohort"],
 [[str(int(r.coorte)),nf(r.nascidos,0),nf(r.frac12_full),nf(r.frac12_sem_lote10),nf(r.frac_lote10_na_coorte)] for r in d.itertuples()])

# C markers
d=rd("D15_C_marcadores.csv")
emit("D15_C_marcadores","Administrative completeness markers, by year of first application",
 "Share of first applications with each field present: taxpayer id of the guardian (CPF); sex; postcode matched to a census tract; race declared (categories 1--5, excluding not-declared); a priority code. Rising completeness would mark a change of form or registration system. Source: build04\\_diag15.py.",
 "lrrrrrr",["Year","N","CPF","Sex","Postcode","Race decl.","Priority"],
 [[str(int(r.asol)),nf(r.N,0),nf(r.frac_cpf),nf(r.frac_sexo),nf(r.frac_cep),nf(r.frac_raca_decl),nf(r.frac_prio)] for r in d.itertuples()])

# E annual series
d=rd("D15_E_anual_dez.csv")
emit("D15_E_anual_dez","Childcare enrolment and registered demand in the municipality of S\\~ao Paulo, December snapshot, 2006--2017",
 "Open data of the municipality (``Demanda Registrada e Matriculas'', historical series 2006--2017), summed over 96 districts, December of each year. MAT = childcare (creche) enrolment; DEM = registered childcare demand (the queue stock); DEM total adds preferential demand. The 2013 enrolment (214,460) matches the offered-places series used in the paper (VAGOFER 2013S1, 214,561). Source: build04\\_diag15E.py; Portal de Dados Abertos PMSP.",
 "lrrrr",["Year","Enrolment","Growth \\%","Demand (queue)","Demand total"],
 [[str(int(r.ano)),nf(r.mat,0),(nf(r.mat_cresc_pct) if pd.notna(r.mat_cresc_pct) else "--"),nf(r.dem,0),nf(r.dem_total,0)] for r in d.itertuples()])
print("OK tex DIAG15")
