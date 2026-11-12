# -*- coding: utf-8 -*-
# SAIDA C (26/10/2026): corpo LaTeX da tabela central (tab:arms) a partir de 03_build/build20/bracos_ano.csv.
# Substitui o bloco de tabela de build20_bracos.py, cujo cabecalho desalinhava as colunas; nao recalcula nada.
# Saida: 04_paper/assets/tables/c/C_arms_body.tex
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd
ROOT = (NE_ROOT + "/")
R = pd.read_csv(ROOT + "03_build/build20/bracos_ano.csv")
BS = chr(92); NL = chr(10)
def f1(v): return "--" if pd.isna(v) else f"{v:.1f}"
def yn(v): return "--" if pd.isna(v) else ("yes" if bool(v) else "no")
ss = lambda a, b: BS + "shortstack{" + a + BS + BS + b + "}"
L = ["% Gerado por 02_audit/build20_arms_tex.py a partir de bracos_ano.csv (build20_bracos.py). Nao editar a mao.",
     BS + "footnotesize", BS + "setlength{" + BS + "tabcolsep}{4pt}", BS + "fitbox{%",
     BS + "begin{tabular}{lrrrrrrrcrccc}", BS + "toprule",
     " & & " + BS + "multicolumn{3}{c}{Arm A (" + BS + "%)} & " + BS + "multicolumn{2}{c}{Arm B (" + BS + "%)} & & & & " + BS + "multicolumn{3}{c}{Goal met?} " + BS + BS,
     BS + "cmidrule(lr){3-5}" + BS + "cmidrule(lr){6-7}" + BS + "cmidrule(lr){11-13}",
     "Year & " + ss("Pop.\\ 0--3", "(000)") + " & Stage & Age & " + ss("Mun. and", "partner") + " & Sep. & Dec. & " + ss("A / B", "Dec.") + " & " + ss("Binding", "arm") + " & " + ss("Review", "reported") +
     " & Law & " + ss("Review,", "Sep.") + " & " + ss("Review,", "Dec.") + " " + BS + BS, BS + "midrule"]
L[-2] = L[-2].replace("\\\\ 0--3", BS + " 0--3")
f2 = lambda v: "--" if pd.isna(v) else f"{v:.2f}"
# triagem (26/10/2026): 2007-2025; coluna municipal + conveniada; razao exigencia A / exigencia B em dezembro; Arm B dez. com 2 casas
for _, r in R[R.ano.between(2007, 2025)].iterrows():
    L.append(f"{int(r.ano)} & {int(round(r.pop_0a3 / 1000))} & {f1(r.A_total)} & {f1(r.A_idade_total)} & {f1(r.A_munconv)} & {f1(r.B_set)} & {f2(r.B_dez)} & {f2(r.exigA_sobre_exigB_dez)} & "
             f"{r.obriga_dez if isinstance(r.obriga_dez, str) else '--'} & {'--' if pd.isna(r.conf_reportado) else f'{r.conf_reportado:.2f}'} & "
             f"{yn(r.cumpre_lei_A_total)} & {yn(r.cumpre_conf_set)} & {yn(r.cumpre_conf_dez)} " + BS + BS)
L += [BS + "bottomrule", BS + "end{tabular}}"]
p = ROOT + "04_paper/assets/tables/c/C_arms_body.tex"
open(p, "w", encoding="utf-8").write(NL.join(L) + NL)
assert open(p, encoding="utf-8").read().count(NL) == len(L); print("[gravado e relido]", p, len(L), "linhas")
print(NL.join(L[4:12]))
