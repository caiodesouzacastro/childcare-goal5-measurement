# -*- coding: utf-8 -*-
# INDETERMINACAO (27/10/2026), decisao do autor: o paper passa a ser sobre a indeterminacao da Meta 5. Descritivo.
# Estende a matriz do build24 a todas as escolhas que a lei deixa abertas e gera a TABELA CENTRAL do corpo.
# Dimensoes (2 x 3 x 3 x 2 x 2 x 2 = 144 combinacoes, anos 2010-2022):
#   fila: total publicado | sem pedido por unidade especifica (set./2019 em diante; em 2019 e a coluna (1), de 2020 em
#         diante e total - coluna (3)). CORRIGE o build24, que pulava set. e dez. de 2019 nessa definicao.
#   data da contagem: dezembro | setembro | media das contagens publicadas no ano (as quatro trimestrais ate 2022;
#         a media da fila sem unidade especifica so existe quando todas as contagens do ano trazem a divisao).
#   populacao: principal (nascidos ajustados aos Censos) | SEADE | linear entre os Censos.
#   fonte da matricula no braco B: SME (mesma publicacao da fila; na media, media das contagens) | Censo Escolar,
#         municipal + conveniada, maio (ate 2021).
#   rede no braco A: todas as redes | municipal + conveniada (ate 2021).
#   leitura da clausula: so o braco maior conta | fila vazia exigida sempre.
# Linha de referencia: indicador da revisao (parcela atendida >= 75%), por data.
# Entradas: 03_build/build23/denominador_serie.csv, 03_build/build19/serie_publicada_completa.csv
# Saidas: 03_build/build25/combinacoes.csv, indeterminacia.log (via tee), 04_paper/assets/tables/c/C_indet_body.tex
#   (corpo) e C_indet_full_body.tex (apendice, as 144). RETOMADA (27/10/2026): tabelas por build25_tabelas.py.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, itertools; sys.stdout.reconfigure(encoding="utf-8")
import numpy as np, pandas as pd
import m3_registro; m3_registro.registra(__file__, "analise")
ROOT = (NE_ROOT + "/"); OUT = ROOT + "03_build/build25/"; os.makedirs(OUT, exist_ok=True)
D = pd.read_csv(ROOT + "03_build/build23/denominador_serie.csv")
S = pd.read_csv(ROOT + "03_build/build19/serie_publicada_completa.csv").drop_duplicates(["ano", "mes"])
c10, c22 = 564210, 464826
D["pop_linear"] = np.where(D.ano.between(2010, 2022), c10 + (D.ano - 2010) / 12 * (c22 - c10), np.nan)
POP = {"principal": "pop_main", "SEADE": "pop_0a3", "linear": "pop_linear"}
NET = {"todas": "matA_total", "municipal": "matA_munconv"}

def narrow(s):  # fila sem pedido por unidade especifica numa contagem; NaN quando a publicacao nao traz a divisao
    if s.ano == 2019 and not pd.isna(s.dem_1): return s.dem_1          # 2019: (1) sem opcao por unidade especifica
    if not pd.isna(s.dem_3): return s.dem_total - s.dem_3               # 2020+: (3) com opcao por unidade especifica
    if s.ano == 2020 and not pd.isna(s.dem_1): return s.dem_1           # mar. e jun. de 2020: mesma divisao de 2019
    return np.nan
S["dem_narrow"] = S.apply(narrow, axis=1)

def count(y, data, fila):  # (demanda, matricula SME) para o ano y na data escolhida
    s = S[S.ano == y]
    col = "dem_total" if fila == "total" else "dem_narrow"
    if data in (12, 9):
        s = s[s.mes == data]
        if not len(s) or pd.isna(s[col].iloc[0]): return np.nan, np.nan
        return s[col].iloc[0], s.matric_creche.iloc[0]
    if len(s) < 4 or s[col].isna().any(): return np.nan, np.nan
    return s[col].mean(), s.matric_creche.mean()

rows = []
for y in range(2010, 2023):
    d = D[D.ano == y].iloc[0]
    for fila, data, pl, fonte, rede, clausula in itertools.product(("total", "sem_unid_especifica"), (12, 9, "media"), POP, ("SME", "Censo"),
                                                                 NET, ("so_maior", "fila_sempre")):
        dem, mat_sme = count(y, data, fila)
        pop = d[POP[pl]]; matA = d[NET[rede]]; mat = mat_sme if fonte == "SME" else d.matA_munconv
        ok = not any(pd.isna(v) for v in (dem, pop, matA, mat))
        r = dict(ano=y, fila=fila, data=str(data), pop=pl, fonte_B=fonte, rede_A=rede, clausula=clausula, avaliavel=ok)
        if ok:
            A = 100 * matA / pop; reqA = 0.75 * pop; reqB = mat + dem; a_obriga = reqA > reqB
            if clausula == "so_maior": met = (A >= 75) if a_obriga else (dem == 0)
            else: met = (dem == 0) and (A >= 75 or not a_obriga)
            r.update(A=round(A, 1), AB=round(reqA / reqB, 3), obriga="A" if a_obriga else "B", dem=round(dem, 1), cumpre=bool(met))
        rows.append(r)
R = pd.DataFrame(rows); R.to_csv(OUT + "combinacoes.csv", index=False); assert len(pd.read_csv(OUT + "combinacoes.csv")) == len(R)
print("[gravado e relido] combinacoes.csv", len(R), "linhas;", R.groupby(["fila", "data", "pop", "fonte_B", "rede_A", "clausula"]).ngroups, "combinacoes")
K = ["fila", "data", "pop", "fonte_B", "rede_A", "clausula"]
def pattern(g):
    ev = g[g.avaliavel]; yrs = ev[ev.cumpre].ano.astype(int).tolist()
    return pd.Series(dict(anos=yrs, primeiro_avaliavel=int(ev.ano.min()) if len(ev) else None, ultimo_avaliavel=int(ev.ano.max()) if len(ev) else None,
                          n_aval=len(ev), monotona=(not yrs) or yrs == list(range(yrs[0], int(ev.ano.max()) + 1))))
P = R.groupby(K).apply(pattern).reset_index()
P["anos_s"] = P.anos.apply(lambda v: ",".join(map(str, v)) if v else "nunca")
print("=== todas as combinacoes (anos cumpridos | anos avaliaveis)")
for _, p in P.iterrows(): print(tuple(p[K]), "|", p.anos_s, "|", p.primeiro_avaliavel, "-", p.ultimo_avaliavel, "| monotona:", p.monotona)
print("=== distribuicao dos padroes:", len(P), "combinacoes")
print(P.anos_s.value_counts().to_string())
print("combinacoes com algum ano cumprido:", int((P.anos_s != "nunca").sum()), "| nunca:", int((P.anos_s == "nunca").sum()))
print("combinacoes nao monotonas (cumpre e depois deixa de cumprir dentro dos anos avaliaveis):", int((~P.monotona).sum()))
print(P[~P.monotona][K + ["anos_s", "ultimo_avaliavel"]].to_string(index=False))
print("primeiro ano cumprido, por combinacao com algum ano:", P[P.anos_s != "nunca"].anos.apply(lambda v: v[0]).value_counts().sort_index().to_dict())
for k in K:
    print(f"  por {k}:", P.groupby(k).apply(lambda g: f"{int((g.anos_s != 'nunca').sum())} de {len(g)} com algum ano").to_dict())
print("=== diferenca contra o build24 (fila sem unidade especifica, 2019):")
print(R[(R.ano == 2019) & (R.fila == "sem_unid_especifica") & (R.rede_A == "todas") & (R.clausula == "so_maior") & R.data.isin(["12", "9"])][["data", "pop", "fonte_B", "A", "AB", "obriga", "dem", "cumpre"]].to_string(index=False))
print("=== media anual (fila total, SME, principal):")
print(R[(R.data == "media") & (R.fila == "total") & (R.fonte_B == "SME") & (R["pop"] == "principal") & (R.rede_A == "todas") & (R.clausula == "so_maior")][["ano", "A", "AB", "obriga", "dem", "cumpre"]].to_string(index=False))
# indicador da revisao: parcela atendida = matricula / (matricula + fila), mesma publicacao, limiar 75%
REV = {}
for data in (12, 9, "media"):
    yrs = []
    for y in range(2010, 2023):
        dem, mat = count(y, data, "total")
        if not pd.isna(dem) and 100 * mat / (mat + dem) >= 75: yrs.append(y)
    REV[str(data)] = yrs
print("=== indicador da revisao (parcela atendida >= 75%), anos:", REV)

# ---------------- Tabela 1 em dois niveis (RETOMADA, 27/10/2026, decisao D2 do autor). Corpo (C_indet_body.tex):
# so as leituras que o texto sustenta (braco A em todas as redes, so o braco maior exigido, populacao principal ou
# linear). Apendice (C_indet_full_body.tex): as 144. Formatacao em build25_tabelas.py, testada por
# test_build25_tabelas.py antes desta execucao; o rotulo "of which" (OQ-107) sai do modulo, nao de edicao a mao.
import build25_tabelas as T25
P25 = T25.padroes(R)
assert (P25.set_index(K).anos_s.sort_index() == P.set_index(K).anos_s.sort_index()).all()  # mesma leitura do pattern() acima
for nome, linhas in (("C_indet_body.tex", T25.corpo(P25, REV, "02_audit/build25_indeterminacia.py")),
                     ("C_indet_full_body.tex", T25.apendice(P25, "02_audit/build25_indeterminacia.py"))):
    open(ROOT + "04_paper/assets/tables/c/" + nome, "w", encoding="utf-8").write(chr(10).join(linhas) + chr(10))
    print("[gravado]", nome, len(linhas), "linhas")
print("nucleo do corpo:", T25.resumo(T25.nucleo(P25)))
print("todas as 144:", T25.resumo(P25))
print("anos avaliaveis por (fila, data, fonte):")
print(P[(P.rede_A == "todas") & (P.clausula == "so_maior") & (P["pop"] == "principal")][["fila", "data", "fonte_B", "primeiro_avaliavel", "ultimo_avaliavel", "anos_s"]].to_string(index=False))

# ---------------- tentativa 3: objecao 6 (teste de estabilidade) e objecao 3 (margens da populacao)
print("=== objecao 6: estoque de um dia contra media movel das quatro contagens dos 12 meses que terminam no mes (publicado)")
Q4 = S[S.ano.between(2006, 2022) & S.mes.isin([3, 6, 9, 12])].sort_values(["ano", "mes"]).reset_index(drop=True)
Q4["roll4"] = Q4.dem_total.rolling(4).mean()
res = {}
for m in (3, 6, 9, 12):
    a = Q4[(Q4.ano == 2014) & (Q4.mes == m)].iloc[0]; b = Q4[(Q4.ano == 2017) & (Q4.mes == m)].iloc[0]
    one = 100 * (b.dem_total / a.dem_total - 1); roll = 100 * (b.roll4 / a.roll4 - 1); res[m] = (one, roll)
    print(f"  mes {m:2d}: contagem do dia {one:.1f}% | media das 4 contagens ate o mes {roll:.1f}%")
print(f"  razao dez./set.: contagem do dia {res[12][0] / res[9][0]:.2f} | media movel {res[12][1] / res[9][1]:.2f}")
print("=== objecao 3: quanto a populacao principal precisaria mudar para o braco A cruzar 75% (A / 75 - 1)")
for y in (2019, 2020, 2021, 2022):
    d = D[D.ano == y].iloc[0]; A = 100 * d.matA_total / d.pop_main
    s = S[(S.ano == y) & (S.mes == 12)].iloc[0]; reqB = s.matric_creche + s.dem_total
    pop_lim = d.matA_total / 0.75; ab_lim = 0.75 * pop_lim / reqB
    print(f"  {y}: A {A:.1f}% | populacao no limiar {pop_lim:,.0f} ({100 * (pop_lim / d.pop_main - 1):+.1f}% da serie principal) | A/B dez. no limiar {ab_lim:.3f} ({'A' if ab_lim > 1 else 'B'} obriga)")
