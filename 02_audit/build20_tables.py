# -*- coding: utf-8 -*-
# SAIDA C, escrita (26/10/2026): tabelas do manuscrito da Saida C, a partir das saidas de build19 (nada recalculado).
#   C_series_body.tex   estoque publicado em mar/jun/set/dez, 2007-2025, queda set->dez e dez/media do ano
#   C_stab_body.tex     variacao 2014->2017 do estoque e dos indicadores de fluxo, por mes final (nucleo_E_fluxos.csv)
#   C_recon_body.tex    estoque reconstruido / publicado, fim de trimestre, 2010-2018 (nucleo_D_reconstruido.csv)
#   C_dates_body.tex    data de extracao das edicoes de dezembro (datas_extracao.csv)
# Copia tambem a figura fig_meta5_mes.pdf para assets/figures/C_fig_goal.pdf.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, shutil; sys.stdout.reconfigure(encoding="utf-8")
import numpy as np, pandas as pd
ROOT = (NE_ROOT + "/"); B19 = ROOT + "03_build/build19/"; T = ROOT + "04_paper/assets/tables/c/"
BS = chr(92); NL = chr(10)
def fmt(v): return "--" if pd.isna(v) else f"{int(round(v)):,}"
def f1(v): return "--" if pd.isna(v) else f"{v:.1f}"
def write(name, L):
    p = T + name; open(p, "w", encoding="utf-8").write(NL.join(L) + NL); assert open(p, encoding="utf-8").read().count(NL) == len(L); print("[gravado e relido]", p, len(L), "linhas")
head = lambda cols: ["% Gerado por 02_audit/build20_tables.py (26/10/2026). Nao editar a mao.", BS + "footnotesize", BS + "fitbox{%", BS + "begin{tabular}{" + cols + "}", BS + "toprule"]
tail = [BS + "bottomrule", BS + "end{tabular}}"]
# (1) serie
S = pd.read_csv(B19 + "serie_publicada_completa.csv")
W = S.pivot(index="ano", columns="mes", values="dem_total")
L = head("lrrrrrrr") + ["Year & March & June & September & December & " + BS + "shortstack[r]{Sep.--Dec.\\\\fall (" + BS + "%)} & " + BS + "shortstack[r]{December / mean\\\\of the year} & " + BS + "shortstack[r]{December\\\\enrolment} " + BS + BS, BS + "midrule"]
for y in range(2007, 2026):
    r = W.loc[y]; full = r.dropna()
    fall = 100 * (r.get(9) - r.get(12)) / r.get(9) if pd.notna(r.get(9)) and pd.notna(r.get(12)) else np.nan
    ratio = r.get(12) / full.mean() if pd.notna(r.get(12)) and len(full) >= 4 else np.nan
    enr = S[(S.ano == y) & (S.mes == 12)].matric_creche
    L.append(f"{y} & {fmt(r.get(3))} & {fmt(r.get(6))} & {fmt(r.get(9))} & {fmt(r.get(12))} & {f1(fall)} & {'--' if pd.isna(ratio) else f'{ratio:.2f}'} & {fmt(enr.iloc[0]) if len(enr) else '--'} " + BS + BS)
write("C_series_body.tex", L + tail)
# (2) estabilidade
E = pd.read_csv(B19 + "nucleo_E_fluxos.csv"); A = W
Q = {3: "March", 6: "June", 9: "September", 12: "December"}
# tentativa 3: acrescenta a coluna "Dec./Sep." (variacao medida em dezembro / variacao medida em setembro)
L = head("lrrrrr") + ["Measure, change 2014 to 2017 & March & June & September & December & Dec./Sep. " + BS + BS, BS + "midrule"]
P = {c: E.pivot(index="ano", columns="mes", values=c) for c in ("fluxo", "idade_mediana_m", "enc365")}
def linha(lab, ch, fmt):
    L.append(f"{lab} & " + " & ".join(fmt(ch[m]).replace("-", "$-$").replace("+", "$+$") for m in Q) + f" & {ch[12] / ch[9]:.2f} " + BS + BS)  # tentativa 4 (FUSAO): sinal de menos tipografico
    print("estabilidade |", lab, "|", {m: round(ch[m], 3) for m in Q}, "| dez/set", round(ch[12] / ch[9], 3))
linha("Registered demand, snapshot at month end (" + BS + "%)", {m: 100 * (A.loc[2017, m] - A.loc[2014, m]) / A.loc[2014, m] for m in Q}, lambda v: f"{v:+.1f}")
linha("New first requests, 12 months to month end (" + BS + "%)", {m: 100 * (P['fluxo'].loc[2017, m] - P['fluxo'].loc[2014, m]) / P['fluxo'].loc[2014, m] for m in Q}, lambda v: f"{v:+.1f}")
linha("Median age at first request, same window (months)", {m: P['idade_mediana_m'].loc[2017, m] - P['idade_mediana_m'].loc[2014, m] for m in Q}, lambda v: f"{v:+.1f}")
linha("Referred within 365 days, same window (share)", {m: P['enc365'].loc[2017, m] - P['enc365'].loc[2014, m] for m in Q}, lambda v: f"{v:+.3f}")
write("C_stab_body.tex", L + tail)
# (3) reconstrucao
D = pd.read_csv(B19 + "nucleo_D_reconstruido.csv"); D = D[D.ano <= 2018]
L = head("lrrrr") + ["Year & March & June & September & December " + BS + BS, BS + "midrule"]
for y, g in D.groupby("ano"):
    g = g.set_index("mes"); L.append(f"{y} & " + " & ".join("--" if m not in g.index else f"{g.loc[m, 'razao_rec_pub']:.2f}" for m in Q) + " " + BS + BS)
write("C_recon_body.tex", L + tail)
# (4) datas de extracao (dezembro)
X = pd.read_csv(B19 + "datas_extracao.csv"); X = X[X.mes == 12]
L = head("lll") + ["Year & Extraction date printed & Note " + BS + BS, BS + "midrule"]
for _, r in X.iterrows():
    d = pd.to_datetime(r.data_extracao, format="%d/%m/%Y").strftime("%d %B %Y").lstrip("0") if isinstance(r.data_extracao, str) and r.data_extracao else "not printed"  # tentativa 4 (FUSAO): data por extenso
    nota = "marked " + chr(96) * 2 + "Ajustado" + chr(39) * 2 + " (adjusted)" if r.ajustado else ""
    L.append(f"{int(r.ano)} & {d} & {nota} " + BS + BS)
write("C_dates_body.tex", L + tail)
src = B19 + "fig_meta5_mes.pdf"; dst = ROOT + "04_paper/assets/figures/C_fig_goal.pdf"
shutil.copyfile(src, dst); assert os.path.getsize(dst) == os.path.getsize(src); print("[copiado]", dst)
