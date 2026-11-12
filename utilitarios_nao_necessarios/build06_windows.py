# -*- coding: utf-8 -*-
# BUILD06 - tabela S3decomp: FUSAO de S3a (medias por coorte) e S3windows (tres
# janelas, duas definicoes) numa unica tabela de dois paineis. Descritivo.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import os, csv
ROOT=NE_ROOT
TAB=os.path.join(ROOT,r"03_build\build03\tables")
STG=os.path.join(ROOT,r"03_build\build03\_staging")

# ---- Panel A: medias por coorte (le S3a_decomp.csv) ----
rowsA=[]
with open(os.path.join(STG,"S3a_decomp.csv"),encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rowsA.append([str(int(float(r["coorte_nasc"]))),
                      f"{int(float(r['N'])):,}",
                      f"{float(r['idade_sol']):.2f}",
                      f"{float(r['espera']):.2f}",
                      f"{float(r['idade_ent']):.2f}"])

# ---- Panel B: tres janelas, duas definicoes ----
rowsB=[
 ["Year of application, 2010--2018", "$-19.09$","80\\%","20\\%", "$-20.52$","79\\%","21\\%"],
 ["Year of application, 2010--2016 (full 730-day follow-up)", "$-15.11$","99\\%","1\\%", "$-16.41$","93\\%","8\\%"],
 ["Birth cohort, 2010--2014 (entry at or before 48 months)", "$-9.37$","93\\%","7\\%", "$-9.62$","87\\%","13\\%"],
]
h1=["", "\\multicolumn{3}{c}{Interval to enrolment}", "\\multicolumn{3}{c}{Interval to referral}"]
h2=["Unit and window", "Change (mo.)","Share appl.","Share wait", "Change (mo.)","Share appl.","Share wait"]

cap=("Decomposing the fall in age at entry: cohort means and three observation windows")
note=("Panel A gives the underlying means, in months since birth, for the paper's preferred window "
      "(enrolled children entering at or before 48 months, birth cohorts 2010--2014); the identity age at "
      "entry $=$ age at application $+$ wait holds in means with a residual below 0.04 months. Panel B "
      "reports the change in age at entry and the share attributable to earlier application and to shorter "
      "waiting, under three windows and two definitions of the interval. Under \\emph{Enrolment} the "
      "interval is application to enrolment (the headline); under \\emph{Referral} it is application to first "
      "referral, which precedes enrolment by a median of five to seven days. Both figures are conditional on "
      "eventual entry within the common window. Descriptive.")

L=["% requer booktabs. Descritivo (fusao S3a + S3windows).",
   "\\begin{table}[htbp]\\centering",
   f"\\caption{{{cap}}}","\\label{tab:S3decomp}","\\small",
   # Panel A
   "\\textbf{Panel A. Mean age at application, wait, and age at entry by birth cohort}\\\\[3pt]",
   "\\begin{tabular}{lrrrr}","\\toprule",
   "Birth cohort & N & Age at application & Wait & Age at entry \\\\","\\midrule"]
for r in rowsA: L.append(" & ".join(r)+" \\\\")
L+=["\\bottomrule","\\end{tabular}","",
   "\\vspace{7pt}",
   "\\textbf{Panel B. Change in age at entry and the share from each margin}\\\\[3pt]",
   "\\setlength{\\tabcolsep}{4pt}",
   "\\begin{tabular}{p{4.6cm}rrrrrr}","\\toprule",
   " & ".join(h1)+" \\\\","\\cmidrule(lr){2-4}\\cmidrule(lr){5-7}",
   " & ".join(h2)+" \\\\","\\midrule"]
for r in rowsB: L.append(" & ".join(r)+" \\\\")
L+=["\\bottomrule","\\end{tabular}",
    f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
open(os.path.join(TAB,"S3decomp.tex"),"w",encoding="utf-8").write("\n".join(L)+"\n")
print("tex: S3decomp (fusao S3a + S3windows)")
