# -*- coding: utf-8 -*-
# NOTAS (27/10/2026), pedido do autor (item 1.2): a Lei 16.271/2015 nao governa a serie de populacao (o art. 4o fala dos
# censos da educacao basica e superior; nenhum outro artigo trata de populacao). Material para tratar a populacao como
# mais uma dimensao indefinida: o que cada serie produz na meta, ano a ano, e o que muda na Tabela 1. Descritivo.
# Repete a logica do build25_indeterminacia.py (mesmas entradas, mesma regra de cumprimento) com seis series:
#   principal (nascidos ajustados aos Censos), linear (entre os Censos), SEADE (projecao interpolada) -> as tres da A13;
#   SEADE_ancorada (SEADE reescalada pela razao Censo/SEADE de 2022; calculada no build22, fora da A13);
#   censo2010_fixo (564.210 em todos os anos: o Censo disponivel na data da lei);
#   nascidos (pool de nascidos sem ajuste; nao e contagem de populacao, so referencia).
# Checagem embutida: para as tres series da A13, cada linha tem de reproduzir 03_build/build25/combinacoes.csv.
# Entradas: 03_build/build23/denominador_serie.csv, 03_build/build19/serie_publicada_completa.csv, 03_build/build25/combinacoes.csv
# Saidas: 03_build/build27/populacao_series.csv, combinacoes_pop6.csv, populacao.log (via tee). Nao grava nada em 04_paper.
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, itertools; sys.stdout.reconfigure(encoding="utf-8")
import numpy as np, pandas as pd
import m3_registro; m3_registro.registra(__file__, "analise")
ROOT = (NE_ROOT + "/"); OUT = ROOT + "03_build/build27/"; os.makedirs(OUT, exist_ok=True)
D = pd.read_csv(ROOT + "03_build/build23/denominador_serie.csv")
S = pd.read_csv(ROOT + "03_build/build19/serie_publicada_completa.csv").drop_duplicates(["ano", "mes"])
C25 = pd.read_csv(ROOT + "03_build/build25/combinacoes.csv", dtype={"data": str})
c10, c22 = 564210, 464826
D["pop_linear"] = np.where(D.ano.between(2010, 2022), c10 + (D.ano - 2010) / 12 * (c22 - c10), np.nan)
D["pop_c10"] = np.where(D.ano.between(2010, 2022), float(c10), np.nan)
D["pop_anc"] = np.where(D.ano.between(2007, 2024), D.pop_ancorada_c22, np.nan)
POP = {"principal": "pop_main", "SEADE": "pop_0a3", "linear": "pop_linear",
       "SEADE_ancorada": "pop_anc", "censo2010_fixo": "pop_c10", "nascidos": "pool_nv_maio"}
NET = {"todas": "matA_total", "municipal": "matA_munconv"}


def narrow(s):  # identica ao build25
    if s.ano == 2019 and not pd.isna(s.dem_1): return s.dem_1
    if not pd.isna(s.dem_3): return s.dem_total - s.dem_3
    if s.ano == 2020 and not pd.isna(s.dem_1): return s.dem_1
    return np.nan
S["dem_narrow"] = S.apply(narrow, axis=1)


def count(y, data, fila):  # identica ao build25
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
R = pd.DataFrame(rows)
R.to_csv(OUT + "combinacoes_pop6.csv", index=False); assert len(pd.read_csv(OUT + "combinacoes_pop6.csv")) == len(R)
print("[gravado e relido] combinacoes_pop6.csv", len(R), "linhas")

# ---- checagem: as tres series da A13 reproduzem o build25 linha a linha
K = ["ano", "fila", "data", "pop", "fonte_B", "rede_A", "clausula"]
V = ["avaliavel", "A", "AB", "obriga", "dem", "cumpre"]
m = R[R["pop"].isin(["principal", "SEADE", "linear"])].merge(C25, on=K, suffixes=("", "_25"), how="outer", indicator=True)
assert (m._merge == "both").all() and len(m) == len(C25) == 1872, "linhas nao casam com o build25"
for v in V:
    a, b = m[v], m[v + "_25"]
    iguais = (a == b) | (a.isna() & b.isna())
    if v == "cumpre": iguais = (a.fillna(-1).astype(str) == b.fillna(-1).astype(str))
    assert iguais.all(), f"coluna {v} diverge do build25 em {int((~iguais).sum())} linhas"
print("CHECAGEM: principal, SEADE e linear reproduzem 03_build/build25/combinacoes.csv nas 1.872 linhas (", ", ".join(V), ")")

# ---- (1) series ano a ano: populacao, braco A (etapa, todas as redes), exigencias de dezembro (lista publicada, SME)
L = []
for y in range(2010, 2023):
    d = D[D.ano == y].iloc[0]
    for pl, col in POP.items():
        p = d[col]
        L.append(dict(ano=y, serie=pl, pop=p, A_etapa=100 * d.matA_total / p, A_idade=100 * d.matA_idade_total / p,
                      exigA=0.75 * p, exigB_dez=d.exigB_dez, AB=0.75 * p / d.exigB_dez,
                      var_pop_para_75=100 * (d.matA_total / (0.75 * p) - 1), sobre_principal=100 * (p / d.pop_main - 1)))
T = pd.DataFrame(L); T.to_csv(OUT + "populacao_series.csv", index=False); assert len(pd.read_csv(OUT + "populacao_series.csv")) == len(T)
print("[gravado e relido] populacao_series.csv", len(T), "linhas")
print("=== (1a) populacao 0-3 por serie (milhares)")
print(T.pivot(index="ano", columns="serie", values="pop").div(1000).round(1)[list(POP)].to_string())
print("=== (1b) braco A, etapa, todas as redes (%), por serie")
print(T.pivot(index="ano", columns="serie", values="A_etapa").round(1)[list(POP)].to_string())
print("=== (1c) braco A, idade (0-3 em qualquer etapa) (%), por serie")
print(T.pivot(index="ano", columns="serie", values="A_idade").round(1)[list(POP)].to_string())
print("=== (1d) A/B em dezembro (75% da populacao / matricula SME + lista publicada); > 1: A e o maior")
print(T.pivot(index="ano", columns="serie", values="AB").round(3)[list(POP)].to_string())
print("=== (1e) variacao da populacao que levaria o braco A (etapa, todas as redes) a 75% (%); negativo: a populacao teria de ser menor")
print(T.pivot(index="ano", columns="serie", values="var_pop_para_75").round(1)[list(POP)].to_string())
print("=== (1f) serie sobre a principal (%)")
print(T.pivot(index="ano", columns="serie", values="sobre_principal").round(1)[list(POP)].to_string())
print("anos com braco A (etapa, todas) >= 75, por serie:", {pl: T[(T.serie == pl) & (T.A_etapa >= 75)].ano.tolist() for pl in POP})
print("maximo do braco A (etapa, todas) 2010-2022, por serie:", {pl: round(T[T.serie == pl].A_etapa.max(), 1) for pl in POP})
print("SEADE_ancorada contra o Censo 2010:", f"{100 * (D.loc[D.ano == 2010, 'pop_anc'].iloc[0] / c10 - 1):+.1f}%",
      "| SEADE contra o Censo 2010:", f"{100 * (D.loc[D.ano == 2010, 'pop_0a3'].iloc[0] / c10 - 1):+.1f}%")
print("SEADE 2025 na serie do projeto:", int(D.loc[D.ano == 2025, "pop_0a3"].iloc[0]), "| SME, noticia de 11/08/2025: '566 mil criancas (dados do SEADE)'",
      f"| razao 566.000 / serie = {566000 / D.loc[D.ano == 2025, 'pop_0a3'].iloc[0]:.3f}")


# ---- (2) Tabela 1 (31/12, todas as redes em A, so o braco maior) com as seis series
def pattern(g):
    ev = g[g.avaliavel]; yrs = ev[ev.cumpre == True].ano.astype(int).tolist()
    return pd.Series(dict(anos=",".join(map(str, yrs)) if yrs else "nunca", aval=f"{int(ev.ano.min())}-{int(ev.ano.max())}" if len(ev) else "-",
                          monotona=(not yrs) or yrs == list(range(yrs[0], int(ev.ano.max()) + 1))))
K6 = ["fila", "data", "pop", "fonte_B", "rede_A", "clausula"]
P = R.groupby(K6).apply(pattern).reset_index()
t1 = P[(P.data == "12") & (P.rede_A == "todas") & (P.clausula == "so_maior")]
print("=== (2) Tabela 1 com as seis series (31/12; braco A todas as redes; so o braco maior): anos cumpridos | anos avaliaveis")
print(t1[["pop", "fila", "fonte_B", "anos", "aval", "monotona"]].sort_values(["pop", "fila", "fonte_B"]).to_string(index=False))
for conj, nome in ((["principal", "linear"], "Tabela 1 hoje (principal, linear)"), (["principal", "linear", "SEADE"], "com a SEADE"),
                   (["principal", "linear", "SEADE", "SEADE_ancorada", "censo2010_fixo"], "com as cinco series de populacao")):
    s = t1[t1["pop"].isin(conj)]
    prim = s[s.anos != "nunca"].anos.str[:4].value_counts().sort_index().to_dict()
    print(f"  {nome}: {len(s)} combinacoes; com algum ano {int((s.anos != 'nunca').sum())}; nunca {int((s.anos == 'nunca').sum())};",
          f"primeiro ano {prim}; nao monotonas {int((~s.monotona).sum())}; conjuntos distintos {s.anos.nunique()}")

# ---- (3) as 48 combinacoes de cada serie (estrutura da A13): com algum ano; e quantas cumprem em cada ano
print("=== (3) por serie, nas 48 combinacoes da estrutura da A13 (fila x data x matricula em B x rede em A x clausula)")
for pl in POP:
    s = P[P["pop"] == pl]
    print(f"  {pl}: {int((s.anos != 'nunca').sum())} de {len(s)} com algum ano")
Y = R[R.avaliavel & (R.cumpre == True)].groupby(["pop", "ano"]).size().unstack(fill_value=0).reindex(list(POP)).fillna(0).astype(int)
print("combinacoes (de 48) cumpridas em cada ano, por serie:")
print(Y.to_string())
print("combinacoes avaliaveis em cada ano (iguais para toda serie com populacao no ano):")
print(R[R.avaliavel & (R["pop"] == "principal")].groupby("ano").size().to_string())
