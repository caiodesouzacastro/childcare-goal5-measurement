# -*- coding: utf-8 -*-
# V3 FINAL (26/10/2026), decisao do autor: a serie de nascidos vivos ajustada aos Censos de 2010 e 2022 passa a ser a
# leitura principal do braco A; SEADE sai como principal (erro de 14,4% em 2022); linear vira robustez.
# (a) Deriva da SEADE contra os Censos (2010 e 2022) e contra a serie ajustada nos anos 2010-2018 (anos da secao 4).
# (b) A secao 4 usa SEADE? Nao: a cobertura compara dois registros; as parcelas por coorte usam nascidos vivos (SINASC)
#     da coorte. Sensibilidade: parcelas por coorte reescaladas pela razao nascidos/Censo (fator r(k) interpolado),
#     aplicada aos valores congelados (NUMEROS_V3); o que muda e o que nao muda.
# (c) Tabela 5 nova (C_arms_v3_body.tex): bracos com a serie ajustada como principal, 2010-2025.
# Entradas: 03_build/build22/robustez_R1_bracoA.csv (pool de nascidos, matriculas, Censo), 03_build/build20/bracos_ano.csv.
# Saidas: 03_build/build23/denominador.log (via tee), denominador_serie.csv, 04_paper/assets/tables/c/C_arms_v3_body.tex
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os; sys.stdout.reconfigure(encoding="utf-8")
import numpy as np, pandas as pd
ROOT = (NE_ROOT + "/"); OUT = ROOT + "03_build/build23/"; os.makedirs(OUT, exist_ok=True)
pd.set_option("display.width", 250)
R = pd.read_csv(ROOT + "03_build/build22/robustez_R1_bracoA.csv")
B = pd.read_csv(ROOT + "03_build/build20/bracos_ano.csv")
c10, c22 = 564210, 464826
r10 = R.loc[R.ano == 2010, "pool_nv_maio"].iloc[0] / c10; r22 = R.loc[R.ano == 2022, "pool_nv_maio"].iloc[0] / c22
R["r"] = np.where(R.ano.between(2010, 2022), r10 + (R.ano - 2010) / 12 * (r22 - r10), np.nan)
R["pop_main"] = R.pool_nv_maio / R.r
R["A_stage"] = 100 * R.matA_total / R.pop_main; R["A_age"] = 100 * R.matA_idade_total / R.pop_main; R["A_mun"] = 100 * R.matA_munconv / R.pop_main
R["seade_err"] = 100 * (R.pop_0a3 / R.pop_main - 1)
print("=" * 20, "(a) deriva da SEADE")
print(f"SEADE/Censo - 1: 2010 {100 * (R.loc[R.ano == 2010, 'pop_0a3'].iloc[0] / c10 - 1):+.1f}% | 2022 {100 * (R.loc[R.ano == 2022, 'pop_0a3'].iloc[0] / c22 - 1):+.1f}%")
print(R[R.ano.between(2010, 2022)][["ano", "pop_0a3", "pop_main", "seade_err", "r"]].to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
print("anos da secao 4 (2010-2018): erro da SEADE contra a serie ajustada, de", round(R[R.ano.between(2010, 2018)].seade_err.min(), 1), "a", round(R[R.ano.between(2010, 2018)].seade_err.max(), 1), "%")
print("=" * 20, "(b) secao 4: sensibilidade das parcelas por coorte ao ajuste nascidos/Censo")
r = dict(zip(R.ano, R.r))
V = {"matriculados <24m, registro de pedidos": {2010: 7.4, 2011: 22.8, 2012: 33.2, 2016: 53.8},
     "matriculados <24m, registros de matricula (EOL)": {2010: 25.1, 2011: 28.3, 2012: 31.9, 2016: 53.2},
     "registrados <12m": {2010: 11.0, 2012: 38.3, 2016: 50.1},
     "registrados <47m (coortes 2012-2014)": {2012: 79.4, 2013: 81.5, 2014: 83.7}}
for k, d in V.items():
    print(k, {y: (v, round(v * r[y], 1)) for y, v in d.items()}, "| (observado, reescalado)")
a = V["matriculados <24m, registro de pedidos"]; e = V["matriculados <24m, registros de matricula (EOL)"]
for lab, f in (("observado", lambda y, v: v), ("reescalado", lambda y, v: v * r[y])):
    ra = f(2016, a[2016]) - f(2010, a[2010]); re_ = f(2016, e[2016]) - f(2010, e[2010])
    print(f"  artefato <24m 2010->2016 ({lab}): pedidos {ra:.1f} p.p., EOL {re_:.1f} p.p., parcela de cobertura {100 * (1 - re_ / ra):.1f}%")
g = V["registrados <12m"]
for lab, f in (("observado", lambda y, v: v), ("reescalado", lambda y, v: v * r[y])):
    print(f"  registro <12m 2012->2016 ({lab}): {f(2016, g[2016]) - f(2012, g[2012]):.1f} p.p.")
print("  fator r de 2010 a 2016:", {y: round(r[y], 3) for y in range(2010, 2017)}, "| variacao relativa 2010->2016:", f"{100 * (r[2016] / r[2010] - 1):.1f}%")
print("  razoes que nao dependem do denominador: cobertura de entrantes (pedidos/EOL), completude por semestre, encaminhamento entre solicitantes")
R.to_csv(OUT + "denominador_serie.csv", index=False); assert len(pd.read_csv(OUT + "denominador_serie.csv")) == len(R); print("[gravado e relido] denominador_serie.csv")
print("=" * 20, "(c) bracos com a serie ajustada (principal)")
M = R.merge(B[["ano", "B_set", "B_dez", "conf_reportado", "cumpre_conf_set", "cumpre_conf_dez"]], on="ano", how="left")  # tentativa 2: exigB_dez e dem_dez ja estao em R
M["AB"] = 0.75 * M.pop_main / M.exigB_dez
M["obriga"] = np.where(M.AB.notna(), np.where(M.AB > 1, "A", "B"), "--")
assert set(range(2010, 2026)) <= set(M.ano)
show = ["ano", "pop_main", "A_stage", "A_age", "A_mun", "B_set", "B_dez", "AB", "obriga", "conf_reportado"]
print(M[M.ano.between(2010, 2025)][show].to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
s = M[M.ano.between(2010, 2022)]
print("A (etapa) >= 75 em:", s[s.A_stage >= 75].ano.astype(int).tolist(), "| B obriga em:", s[s.obriga == "B"].ano.astype(int).tolist(),
      "| A obriga e A >= 75 em:", s[(s.obriga == "A") & (s.A_stage >= 75)].ano.astype(int).tolist(), "| min A/B quando A obriga:", round(s[s.obriga == "A"].AB.min(), 2), "max:", round(s.AB.max(), 2))
BS = chr(92)
def f1(v): return "--" if pd.isna(v) else f"{v:.1f}"
def yn(v): return "--" if pd.isna(v) else ("yes" if bool(v) else "no")
# tentativa 3: coluna municipal + conveniada. Correcao de 27/10/2026 (INDETERMINACAO): o comentario desta linha ficava
# dentro da lista e engolia BS + "toprule"; a celula Law passa a '--' nos anos sem populacao (2023-2025), como na edicao a mao.
L = ["% Gerado por 02_audit/build23_denominador.py (V3 FINAL, 26/10/2026; corrigido em 27/10/2026). Nao editar a mao.", BS + "footnotesize", BS + "setlength{" + BS + "tabcolsep}{3.5pt}", BS + "fitbox{%",
     BS + "begin{tabular}{l r rrr rr r c r ccc}", BS + "toprule",
     " & & " + BS + "multicolumn{3}{c}{Arm A: per cent of children 0--3} & " + BS + "multicolumn{2}{c}{Arm B: per cent of registered served} & & Binding & Review & " + BS + "multicolumn{3}{c}{Goal met?} " + BS + BS,
     BS + "cmidrule(lr){3-5}" + BS + "cmidrule(lr){6-7}" + BS + "cmidrule(lr){11-13}",
     "Year & Pop. 0--3 (000) & Stage & Age & Mun.\\ and partner & Sep. & Dec. & A / B Dec. & arm & reported & Law & Review, Sep. & Review, Dec. " + BS + BS, BS + "midrule"]
for _, x in M[M.ano.between(2010, 2025)].iterrows():
    L.append(f"{int(x.ano)} & {'--' if pd.isna(x.pop_main) else int(round(x.pop_main / 1000))} & {f1(x.A_stage)} & {f1(x.A_age)} & {f1(x.A_mun)} & {f1(x.B_set)} & {f1(x.B_dez)} & "
             f"{'--' if pd.isna(x.AB) else f'{x.AB:.2f}'} & {x.obriga if isinstance(x.obriga, str) else '--'} & {'--' if pd.isna(x.conf_reportado) else f'{x.conf_reportado:.2f}'} & "
             f"{'--' if pd.isna(x.pop_main) else 'no'} & {yn(x.cumpre_conf_set)} & {yn(x.cumpre_conf_dez)} " + BS + BS)
L += [BS + "bottomrule", BS + "end{tabular}}"]
open(ROOT + "04_paper/assets/tables/c/C_arms_v3_body.tex", "w", encoding="utf-8").write(chr(10).join(L) + chr(10)); print("[gravado] C_arms_v3_body.tex", len(L), "linhas")
