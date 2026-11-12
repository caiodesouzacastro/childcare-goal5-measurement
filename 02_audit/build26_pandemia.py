# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# build26_pandemia.py -- FINAL (27/10/2026), objecao 10 (pandemia). Descritivo; nenhuma estimacao causal.
# Pergunta: a fila zerada de dezembro de 2020-2022 e as combinacoes "cumprida" de 2019-2022 refletem queda de procura?
# (a) novos pedidos por ano: registro individual (1o pedido por crianca, 2013-2018; o registro termina em dez/2018);
#     de 2019 em diante nao ha serie publicada de entradas; usa-se um limite inferior: contagem maxima do ano menos a
#     contagem de dezembro anterior (entradas liquidas de saidas ate o pico), calibrado em 2013-2018 contra o registro.
# (b) matricula: SME (mesma publicacao da fila) e Censo Escolar por rede (maio); nascidos vivos (SINASC/CEInfo).
# (c) identidade contabil: fila = (matricula + fila) - matricula, em setembro (pico) e dezembro.
# Entradas: 03_build/build19/serie_publicada_completa.csv; 03_build/build10/_staging/spine.parquet;
#           03_build/build20/creche_mat_sp_2007_2024.csv; 01_dados_publicos/ceinfo/sinasc_nv_distrito_2006_2026.csv;
#           03_build/build22/robustez_R1_bracoA.csv (pool de nascidos de maio).
# Saidas: 03_build/build26/pandemia_anual.csv, pandemia.log (via tee).
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import os
import numpy as np
import pandas as pd

ROOT = NE_ROOT
OUT = os.path.join(ROOT, r"03_build\build26")
os.makedirs(OUT, exist_ok=True)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)

S = pd.read_csv(os.path.join(ROOT, r"03_build\build19\serie_publicada_completa.csv"))
S = S[S.ano >= 2012].copy()

# ---------- (a) entradas
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"), columns=["d_sol1"])
d = pd.to_datetime(sp.d_sol1)
novos = d.dt.year.value_counts().sort_index()
novos_jan_pico = d[d.dt.month <= 9].dt.year.value_counts().sort_index()

rows = []
for y in range(2013, 2026):
    s = S[S.ano == y]; sp_ = S[(S.ano == y - 1) & (S.mes == 12)]
    dez_prev = int(sp_.dem_total.iloc[0])
    # pico: maior contagem publicada de jan a out (set ate 2022; ago/out a partir de 2023)
    s_pico = s[s.mes <= 10]
    i = s_pico.dem_total.idxmax()
    dez = s[s.mes == 12]
    mes_set = 9 if (s.mes == 9).any() else 8      # sem setembro a partir de 2023: agosto
    st = s[s.mes == mes_set].iloc[0]
    rows.append(dict(
        ano=y,
        novos_registro=int(novos.get(y, 0)) if y <= 2018 else np.nan,
        novos_registro_jan_set=int(novos_jan_pico.get(y, 0)) if y <= 2018 else np.nan,
        dem_dez_ant=dez_prev, mes_pico=int(S.loc[i, "mes"]), dem_pico=int(S.loc[i, "dem_total"]),
        entradas_lim_inf=int(S.loc[i, "dem_total"]) - dez_prev,
        mes_set=mes_set, dem_set=int(st.dem_total), mat_sme_set=int(st.matric_creche),
        dem_dez=int(dez.dem_total.iloc[0]) if len(dez) else np.nan,
        dem1_dez=dez.dem_1.iloc[0] if len(dez) else np.nan,
        mat_sme_dez=int(dez.matric_creche.iloc[0]) if len(dez) else np.nan,
        dem_media=s.dem_total.mean(), mat_sme_media=s.matric_creche.mean(), n_contagens=len(s)))
A = pd.DataFrame(rows)
A["calib_lim_inf_sobre_registro"] = A.entradas_lim_inf / A.novos_registro
A["soma_set"] = A.mat_sme_set + A.dem_set
A["soma_dez"] = A.mat_sme_dez + A.dem_dez
A["soma_media"] = A.mat_sme_media + A.dem_media

# ---------- (b) nascidos e Censo Escolar
nv = pd.read_csv(os.path.join(ROOT, r"01_dados_publicos\ceinfo\sinasc_nv_distrito_2006_2026.csv"), sep=";", encoding="latin-1")
nv = nv[nv.iloc[:, 0] == "Total"].iloc[0]
NV = {int(c): int(nv[c]) for c in nv.index[1:] if c.isdigit()}
A["nascidos"] = A.ano.map(NV)
R = pd.read_csv(os.path.join(ROOT, r"03_build\build22\robustez_R1_bracoA.csv"))[["ano", "pool_nv_maio"]]
A = A.merge(R, on="ano", how="left")
A["soma_set_sobre_pool"] = A.soma_set / A.pool_nv_maio
A["soma_media_sobre_pool"] = A.soma_media / A.pool_nv_maio
C = pd.read_csv(os.path.join(ROOT, r"03_build\build20\creche_mat_sp_2007_2024.csv"))
P = C.pivot_table(index="ano", columns="rede", values="QT_MAT_INF_CRE", aggfunc="sum")
cen = pd.DataFrame({"ano": P.index,
                    "censo_total": P.sum(axis=1, min_count=1).values,
                    "censo_mun_conv": (P["municipal_direta"] + P["privada_conveniada_municipal"]).values,
                    "censo_privada_nc": P["privada_nao_conveniada"].values})
cen.loc[cen.ano >= 2022, ["censo_mun_conv", "censo_privada_nc"]] = np.nan   # 2022+: conveniada nao separavel (objecao 13)
A = A.merge(cen, on="ano", how="left")

print("=" * 30, "(a) entradas na fila por ano")
print(A[["ano", "nascidos", "novos_registro", "novos_registro_jan_set", "dem_dez_ant", "mes_pico", "dem_pico",
         "entradas_lim_inf", "calib_lim_inf_sobre_registro"]].to_string(index=False))
cal = A.loc[A.ano <= 2018, "calib_lim_inf_sobre_registro"]
print(f"calibracao 2013-2018: limite inferior / 1os pedidos do registro: min {cal.min():.3f} max {cal.max():.3f} media {cal.mean():.3f}")
for y in (2020, 2021, 2022):
    print(f"limite inferior {y} vs 2019: {A.loc[A.ano == y, 'entradas_lim_inf'].iloc[0]:,} vs "
          f"{A.loc[A.ano == 2019, 'entradas_lim_inf'].iloc[0]:,} ({100 * (A.loc[A.ano == y, 'entradas_lim_inf'].iloc[0] / A.loc[A.ano == 2019, 'entradas_lim_inf'].iloc[0] - 1):+.1f}%)")
for y in (2020, 2021, 2022, 2023, 2024):
    print(f"nascidos {y} vs 2019: {NV[y]:,} vs {NV[2019]:,} ({100 * (NV[y] / NV[2019] - 1):+.1f}%)")

print("=" * 30, "(b) matricula e fila")
print(A[["ano", "mes_set", "dem_set", "mat_sme_set", "soma_set", "dem_dez", "dem1_dez", "mat_sme_dez", "soma_dez",
         "n_contagens", "soma_media", "pool_nv_maio", "soma_set_sobre_pool", "soma_media_sobre_pool",
         "censo_total", "censo_mun_conv", "censo_privada_nc"]].to_string(index=False))

print("=" * 30, "(c) identidade: d(fila) = d(matricula + fila) - d(matricula)")
def dec(col_dem, col_mat, y0, y1):
    a, b = A[A.ano == y0].iloc[0], A[A.ano == y1].iloc[0]
    dd, dm = b[col_dem] - a[col_dem], b[col_mat] - a[col_mat]
    print(f"{col_dem} {y0}->{y1}: fila {a[col_dem]:,.0f} -> {b[col_dem]:,.0f} (d {dd:+,.0f}); matricula {a[col_mat]:,.0f} -> "
          f"{b[col_mat]:,.0f} (d {dm:+,.0f}); soma d {dd + dm:+,.0f} ({100 * (dd + dm) / (a[col_dem] + a[col_mat]):+.1f}%)")
for y1 in (2020, 2021, 2022):
    dec("dem_set", "mat_sme_set", 2019, y1)
for y1 in (2020, 2021, 2022, 2023, 2024, 2025):
    dec("dem_dez", "mat_sme_dez", 2019, y1)
for y0, y1 in ((2020, 2021), (2021, 2022), (2022, 2023), (2023, 2024), (2024, 2025)):
    dec("dem_dez", "mat_sme_dez", y0, y1)
for y1 in (2020, 2021, 2022):
    a, b = A[A.ano == 2019].iloc[0], A[A.ano == y1].iloc[0]
    print(f"pool de nascidos (maio) 2019->{y1}: {a.pool_nv_maio:,.0f} -> {b.pool_nv_maio:,.0f} ({100 * (b.pool_nv_maio / a.pool_nv_maio - 1):+.1f}%); "
          f"soma set {100 * (b.soma_set / a.soma_set - 1):+.1f}%; soma media {100 * (b.soma_media / a.soma_media - 1):+.1f}%")
a, b = A[A.ano == 2019].iloc[0], A[A.ano == 2021].iloc[0]
print(f"Censo 2019->2021: total {a.censo_total:,.0f} -> {b.censo_total:,.0f} ({b.censo_total - a.censo_total:+,.0f}); municipal+conveniada "
      f"{a.censo_mun_conv:,.0f} -> {b.censo_mun_conv:,.0f} ({b.censo_mun_conv - a.censo_mun_conv:+,.0f}); privada nao conveniada "
      f"{a.censo_privada_nc:,.0f} -> {b.censo_privada_nc:,.0f} ({b.censo_privada_nc - a.censo_privada_nc:+,.0f})")

print("=" * 30, "(d) combinacoes de build25 que cumprem a meta: em que anos e por qual braco")
M = pd.read_csv(os.path.join(ROOT, r"03_build\build25\combinacoes.csv"))
M = M[M.avaliavel.astype(str) == "True"].copy(); M["cumpre"] = M.cumpre.astype(str) == "True"
k = ["fila", "data", "pop", "fonte_B", "rede_A", "clausula"]
G = M[M.cumpre].groupby(k).ano.apply(lambda s: tuple(sorted(s))).reset_index()
print(G.to_string(index=False))
print("combinacoes com algum ano cumprido:", len(G))
so_pand = G.ano.apply(lambda t: set(t) <= {2020, 2021}).sum()
com19 = G.ano.apply(lambda t: 2019 in t).sum(); com22 = G.ano.apply(lambda t: 2022 in t).sum()
print(f"cumpridas apenas em anos de 2020-2021: {so_pand}; com 2019: {com19}; com 2022: {com22}")
print("cumprimentos (combinacao-ano) por ano, data e braco que obriga:")
print(M[M.cumpre].groupby(["ano", "data", "obriga"]).size().unstack(fill_value=0).to_string())
for c in k: M[c] = M[c].astype(str)
x = M[(M.data == "9") & (M["pop"] == "linear") & (M.rede_A == "todas") & (M.clausula == "so_maior") & M.ano.isin([2019, 2020, 2021])]
print("setembro, populacao linear, por fila e fonte da matricula:"); print(x[k + ["ano", "A", "AB", "obriga", "dem", "cumpre"]].to_string(index=False))

print("=" * 30, "(e) execucao 3 (triagem REVIEW_V4): truncamento em 2021, anos <= 2018, janela fixa, matriculas em processo")
anos_av = M.groupby(k).ano.apply(lambda s: tuple(sorted(s))).rename("anos_avaliaveis").reset_index()
G2 = G.copy()
for c in k: G2[c] = G2[c].astype(str)
G2 = G2.merge(anos_av, on=k, how="left")
G2["av_2022"] = G2.anos_avaliaveis.apply(lambda t: 2022 in t)
G2["so_pand"] = G2.ano.apply(lambda t: set(t) <= {2020, 2021})
print(G2[k + ["ano", "anos_avaliaveis", "av_2022", "so_pand"]].to_string(index=False))
print(f"das {int(G2.so_pand.sum())} cumpridas so em 2020-2021, avaliaveis em 2022: {int((G2.so_pand & G2.av_2022).sum())}")
print(f"combinacoes avaliaveis em 2022 com algum ano cumprido: {int(G2.av_2022.sum())}; destas, so em 2020-2021: {int((G2.so_pand & G2.av_2022).sum())}; "
      f"cumpridas em 2022: {int(G2[G2.av_2022].ano.apply(lambda t: 2022 in t).sum())}")
print("combinacoes-ano cumpridas em anos <= 2018:", int(M[M.cumpre & (M.ano <= 2018)].shape[0]),
      "| combinacoes avaliaveis em algum ano 2010-2018:", int(M[M.ano <= 2018].groupby(k).ngroups))
print("--- limite inferior em janela fixa: contagem de junho menos dezembro anterior")
jj = []
nj = d[d.dt.month <= 6].dt.year.value_counts()
for y in range(2013, 2026):
    jun = S[(S.ano == y) & (S.mes == 6)].dem_total; dz = S[(S.ano == y - 1) & (S.mes == 12)].dem_total
    if len(jun) and len(dz):
        lb = int(jun.iloc[0]) - int(dz.iloc[0]); reg = int(nj.get(y, 0)) if y <= 2018 else np.nan
        jj.append(dict(ano=y, jun=int(jun.iloc[0]), dez_ant=int(dz.iloc[0]), lim_inf_jun=lb, registro_jan_jun=reg,
                       calib=lb / reg if y <= 2018 else np.nan))
J = pd.DataFrame(jj); print(J.to_string(index=False))
b19 = J.loc[J.ano == 2019, "lim_inf_jun"].iloc[0]
for y in (2020, 2021, 2022):
    v = J.loc[J.ano == y, "lim_inf_jun"].iloc[0]; print(f"janela fixa {y} vs 2019: {v:,} vs {b19:,} ({100 * (v / b19 - 1):+.1f}%)")
print("--- matriculas em processo (alocadas aguardando confirmacao), dezembro, e parcela atendida contando-as como espera")
for y in (2015, 2016, 2017):
    r = S[(S.ano == y) & (S.mes == 12)].iloc[0]
    e, l, p_ = r.matric_creche, r.dem_total, r.mat_processo_creche
    print(f"{y}: em processo {p_:,.0f}; atendida {100 * e / (e + l):.2f}%; contando em processo como espera {100 * e / (e + l + p_):.2f}%; "
          f"como atendidas {100 * (e + p_) / (e + l + p_):.2f}%")

p = os.path.join(OUT, "pandemia_anual.csv"); A.to_csv(p, index=False)
assert len(pd.read_csv(p)) == len(A); print("[gravado e relido]", p, len(A), "linhas")
