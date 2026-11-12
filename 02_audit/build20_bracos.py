# -*- coding: utf-8 -*-
# SAIDA C, escrita (26/10/2026): os dois bracos da Meta 5 do PME (Lei 16.271/2015):
#   "atendimento para 75% das criancas de zero a 3 anos e 11 meses ou 100% da demanda registrada, o que for maior".
# BRACO A: matricula em creche / populacao 0-3 (SEADE), mesmo metodo da secao de cobertura (sec2_setting.tex, nota 1):
#   numerador Censo Escolar, etapa creche (todas as redes; e municipal direta + conveniada municipal); denominador projecao
#   SEADE "populacao em idade escolar" 0-3, publicada para 2005/2010/2015/2020/2025 e interpolada linearmente nos demais anos.
#   Robustez: contagem por idade (QT_MAT_BAS_0_3) e matricula municipal de dezembro da publicacao da SME (EOL).
# BRACO B: matricula municipal / (matricula municipal + demanda registrada), mesma publicacao da SME, em setembro e dezembro.
# CLAUSULA DO MAIOR: em numero de criancas, exigencia A = 0,75 x populacao; exigencia B = matricula + demanda registrada.
# CONFERENCIA 2023: valores reportados (p. 41-42 do relatorio), comparados com a formula inferida (matric/(matric+demanda), dez.).
# Descritivo. Saidas: 03_build/build20/bracos_ano.csv, bracos_tabela.tex (tabela central), bracos.log (via tee)
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os; sys.stdout.reconfigure(encoding="utf-8")
import numpy as np, pandas as pd
ROOT = (NE_ROOT + "/"); OUT = ROOT + "03_build/build20/"
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
# populacao
pj = pd.read_csv(ROOT + "03_build/build13_coverage/seade_raw/pop_idade_escolar-2000a2050_esp.csv", sep=";", encoding="latin-1", dtype=str)
pj.columns = [c.strip() for c in pj.columns]
pj = pj[pj.cod_ibge == "3550308"].set_index("ano")["00_03anos"].str.replace(".", "", regex=False).astype(int)
pj.index = pj.index.astype(int)
anos = range(2007, 2026)
pop = pd.Series(np.interp(list(anos), pj.index, pj.values), index=anos).round()
pop_pub = {y: (y in pj.index) for y in anos}
print("SEADE 0-3 publicado:", {y: int(pj[y]) for y in pj.index if 2005 <= y <= 2025})
# censo escolar
m = pd.read_csv(OUT + "creche_mat_sp_2007_2024.csv")
mc = m[m.rede.isin(["municipal_direta", "privada_conveniada_municipal"])].groupby("ano")[["QT_MAT_INF_CRE", "QT_MAT_BAS_0_3"]].sum()
mt = m.groupby("ano")[["QT_MAT_INF_CRE", "QT_MAT_BAS_0_3"]].sum()
# rede municipal+conveniada nao e identificavel em 2007 (2.245 conveniadas sem TP_CONVENIO) nem em 2022-2024 (colunas de
# convenio ausentes em 2023-2024; em 2022 a classificacao cai de 345.974 para 53.417): ver build20/censo.log
mc.loc[mc.index.isin([2007, 2022, 2023, 2024])] = np.nan
# publicacao SME
S = pd.read_csv(ROOT + "03_build/build19/serie_publicada_completa.csv")
def pub(y, mes, col):
    r = S[(S.ano == y) & (S.mes == mes)]
    return float(r.iloc[0][col]) if len(r) else np.nan
conf = {2015: 77.62, 2016: 81.38, 2017: 87.05, 2018: 94.43, 2019: 96.31, 2020: 99.86, 2021: 99.85, 2022: 99.99}
conf_dem = {2015: 75194, 2016: 65040, 2017: 44092, 2018: 19697, 2019: 9670, 2020: 540, 2021: 595, 2022: 699}
R = []
for y in anos:
    r = dict(ano=y, pop_0a3=int(pop[y]), pop_publicada=pop_pub[y])
    r["matA_total"] = mt.QT_MAT_INF_CRE.get(y, np.nan); r["matA_munconv"] = mc.QT_MAT_INF_CRE.get(y, np.nan)
    r["matA_idade_total"] = mt.QT_MAT_BAS_0_3.get(y, np.nan)
    r["A_total"] = 100 * r["matA_total"] / pop[y]; r["A_munconv"] = 100 * r["matA_munconv"] / pop[y]
    r["A_idade_total"] = 100 * r["matA_idade_total"] / pop[y]
    r["mat_eol_dez"] = pub(y, 12, "matric_creche"); r["A_eol_dez"] = 100 * r["mat_eol_dez"] / pop[y]
    for lab, mes in (("set", 9), ("dez", 12), ("out", 10)):
        mt_, dm = pub(y, mes, "matric_creche"), pub(y, mes, "dem_total")
        r[f"mat_{lab}"] = mt_; r[f"dem_{lab}"] = dm; r[f"B_{lab}"] = 100 * mt_ / (mt_ + dm)
        r[f"exigB_{lab}"] = mt_ + dm
    r["exigA"] = 0.75 * pop[y]
    r["obriga_dez"] = "A" if r["exigA"] > r["exigB_dez"] else ("B" if r["exigB_dez"] > r["exigA"] else np.nan)
    r["obriga_set"] = ("A" if r["exigA"] > r["exigB_set"] else "B") if not np.isnan(r["exigB_set"]) else np.nan
    r["exigA_sobre_exigB_dez"] = r["exigA"] / r["exigB_dez"]
    r["conf_reportado"] = conf.get(y, np.nan); r["conf_dem"] = conf_dem.get(y, np.nan)
    # leituras
    r["cumpre_lei_A_total"] = r["A_total"] >= 75 if not np.isnan(r["A_total"]) else np.nan
    r["cumpre_lei_A_munconv"] = r["A_munconv"] >= 75 if not np.isnan(r["A_munconv"]) else np.nan
    r["cumpre_lei_B_dez"] = r["dem_dez"] == 0 if not np.isnan(r["dem_dez"]) else np.nan
    r["cumpre_conf_dez"] = r["B_dez"] >= 75 if not np.isnan(r["B_dez"]) else np.nan
    r["cumpre_conf_set"] = r["B_set"] >= 75 if not np.isnan(r["B_set"]) else np.nan
    R.append(r)
R = pd.DataFrame(R)
show = ["ano", "pop_0a3", "pop_publicada", "matA_total", "A_total", "matA_munconv", "A_munconv", "A_idade_total", "A_eol_dez",
        "B_set", "B_dez", "B_out", "exigA", "exigB_dez", "obriga_dez", "obriga_set", "exigA_sobre_exigB_dez", "conf_reportado"]
print(R[show].to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
p = OUT + "bracos_ano.csv"; R.to_csv(p, index=False); assert len(pd.read_csv(p)) == len(R); print("[gravado e relido]", p)
# respostas
def primeiro(col):
    s = R[R[col] == True]; return int(s.ano.min()) if len(s) else None
print("\nBRACO A (>=75%): 1o ano cumprido | total:", primeiro("cumpre_lei_A_total"), "| mun+conv:", primeiro("cumpre_lei_A_munconv"))
for c in ("A_total", "A_munconv", "A_idade_total", "A_eol_dez"):
    s = R.dropna(subset=[c]); i = s[c].idxmax(); print(f"  {c}: de {s[c].iloc[0]:.1f} ({int(s.ano.iloc[0])}) a {s[c].iloc[-1]:.1f} ({int(s.ano.iloc[-1])}); maximo {s.loc[i, c]:.1f} em {int(s.loc[i, 'ano'])}")
allB = S.assign(B=100 * S.matric_creche / (S.matric_creche + S.dem_total))
i = allB.B.idxmax()
print(f"BRACO B (=100%): fotos com demanda zero: {(allB.dem_total == 0).sum()} de {len(allB)}; maximo {allB.loc[i, 'B']:.3f}% em {int(allB.loc[i, 'mes'])}/{int(allB.loc[i, 'ano'])} (demanda {int(allB.loc[i, 'dem_total'])})")
for mes in (9, 12):
    s = allB[allB.mes == mes]; j = s.B.idxmax(); print(f"  mes {mes}: maximo {s.loc[j, 'B']:.3f}% em {int(s.loc[j, 'ano'])}; menor demanda {int(s.dem_total.min())}")
print("CLAUSULA: anos em que A obriga (dez):", R[R.obriga_dez == "A"].ano.tolist(), "| B obriga (dez):", R[R.obriga_dez == "B"].ano.tolist())
print("  razao exigA/exigB_dez: min", round(R.exigA_sobre_exigB_dez.min(), 3), "max", round(R.exigA_sobre_exigB_dez.max(), 3))
print("  anos em que B obriga (set):", R[R.obriga_set == "B"].ano.tolist())
print("CONFERENCIA: 1o ano >=75% dez:", primeiro("cumpre_conf_dez"), "| set:", primeiro("cumpre_conf_set"))
# tabela central (LaTeX), 2010-2025 (tentativa 2: arquivo .tex completo em 04_paper/assets/tables/c/)
def f1(v): return "--" if pd.isna(v) else f"{v:.1f}"
def yn(v): return "--" if pd.isna(v) else ("yes" if v else "no")
BS = chr(92)
L = ["% Gerado por 02_audit/build20_bracos.py. Nao editar a mao. Entra em assets/tables/c/C_arms.tex.",
     BS + "footnotesize", BS + "setlength{" + BS + "tabcolsep}{3.5pt}", BS + "fitbox{%",
     BS + "begin{tabular}{l r rr rr c r ccc}", BS + "toprule",
     " & & " + BS + "multicolumn{2}{c}{Arm A: percent of children 0--3} & " + BS + "multicolumn{2}{c}{Arm B: percent of registered served} & Binding & Review & " + BS + "multicolumn{3}{c}{Goal met?} " + BS + BS,
     BS + "cmidrule(lr){3-4}" + BS + "cmidrule(lr){5-6}" + BS + "cmidrule(lr){9-11}",
     "Year & Pop. 0--3 (000) & Stage & Age & Sep. & Dec. & arm & reported & Law & Review, Sep. & Review, Dec. " + BS + BS, BS + "midrule"]
for _, r in R[R.ano.between(2010, 2025)].iterrows():
    L.append(f"{int(r.ano)} & {int(round(r.pop_0a3/1000))} & {f1(r.A_total)} & {f1(r.A_idade_total)} & {f1(r.B_set)} & {f1(r.B_dez)} & "
             f"{r.obriga_dez if isinstance(r.obriga_dez, str) else '--'} & {'--' if pd.isna(r.conf_reportado) else f'{r.conf_reportado:.2f}'} & "
             f"{yn(r.cumpre_lei_A_total)} & {yn(r.cumpre_conf_set)} & {yn(r.cumpre_conf_dez)} " + BS + BS)
L += [BS + "bottomrule", BS + "end{tabular}}"]
open(ROOT + "04_paper/assets/tables/c/C_arms_body.tex", "w", encoding="utf-8").write(chr(10).join(L) + chr(10)); print("[gravado] C_arms_body.tex", len(L), "linhas")
