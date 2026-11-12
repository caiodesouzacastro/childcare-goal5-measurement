# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# SAIDA C, etapa 2 (26/10/2026): nucleo empirico. Descritivo; nenhuma estimativa causal.
# Entradas: 03_build/build19/serie_publicada_completa.csv (build19_confere_pdf.py; dados abertos 2006-2016 + XLS SME 2017-2026)
#           03_build/build10/_staging/spine.parquet (1a solicitacao por crianca)
# (A) tabela ano x mes de referencia (mar/jun/set/dez) e variacao entre anos por mes, com sinal
# (B) queda set->dez (e pico->dez) no mesmo ano, por ano; tendencia
# (C) simulacao da Meta 5: "demanda atendida" = matric/(matric+demanda) no mes da publicacao (formula inferida; confere
#     contra os valores da Conferencia 2023), criterio da Conferencia (>=75%) e criterio literal (demanda = 0); e o
#     componente "sem opcao por unidade especifica, mais de 30 dias" (indicador da Meta 77), quando publicado
# (D) estoque reconstruido do registro (spine) no fim de mar/jun/set/dez, 2010-2019, e razao com o publicado
# (E) indicadores de fluxo em janelas moveis de 12 meses terminando em mar/jun/set/dez (registro a partir de jul/2012):
#     numero de 1as solicitacoes, idade mediana na solicitacao, encaminhamento em 365 dias; variacao 2013->2017 por mes final
# Saidas: 03_build/build19/nucleo_*.csv e nucleo.log (via tee)
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, itertools; sys.stdout.reconfigure(encoding="utf-8")
import numpy as np, pandas as pd
ROOT = NE_ROOT; OUT = os.path.join(ROOT, r"03_build\build19")
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
def save(df, n):
    p = os.path.join(OUT, n); df.to_csv(p, index=False); assert len(pd.read_csv(p)) == len(df); print("[gravado e relido]", p)
S = pd.read_csv(os.path.join(OUT, "serie_publicada_completa.csv"))
Q = {3: "mar", 6: "jun", 9: "set", 12: "dez"}

# ---------------- (A)
print("=" * 30, "(A) estoque publicado, ano x mes")
A = S[S.mes.isin(Q)].pivot(index="ano", columns="mes", values="dem_total").rename(columns=Q)
print(A.to_string(float_format=lambda v: f"{v:,.0f}"))
save(A.reset_index(), "nucleo_A_tabela.csv")
def pch(a, b, m):
    x, y = A.loc[a, m] if a in A.index else np.nan, A.loc[b, m] if b in A.index else np.nan
    return 100 * (y - x) / x
rows = []
for m in Q.values():
    s = A[m].dropna(); a, b = s.index.min(), s.index.max()
    rows.append(dict(janela=f"serie inteira do mes ({a}-{b})", mes=m, ano_ini=a, ano_fim=b, v_ini=s[a], v_fim=s[b], var_pct=round(100 * (s[b] - s[a]) / s[a], 1)))
JAN = [(2007, 2017), (2007, 2019), (2010, 2017), (2011, 2019), (2012, 2016), (2013, 2017), (2013, 2019), (2015, 2019), (2016, 2019), (2020, 2022)]
for a, b in JAN:
    for m in Q.values():
        rows.append(dict(janela=f"{a}-{b}", mes=m, ano_ini=a, ano_fim=b, v_ini=A.loc[a, m], v_fim=A.loc[b, m], var_pct=round(pch(a, b, m), 1)))
V = pd.DataFrame(rows); V["sinal"] = np.sign(V.var_pct).map({1.0: "+", -1.0: "-", 0.0: "0"})
print(V.to_string(index=False)); save(V, "nucleo_A_variacoes.csv")
# todos os pares de anos 2007-2019: em quantos o sinal de set difere do de dez
P = []
for a, b in itertools.combinations(range(2007, 2020), 2):
    vs, vd = pch(a, b, "set"), pch(a, b, "dez")
    P.append(dict(a=a, b=b, set=vs, dez=vd, difere=np.sign(vs) != np.sign(vd)))
P = pd.DataFrame(P)
print(f"pares de anos 2007-2019: {len(P)}; sinal set != sinal dez em {int(P.difere.sum())} ({100 * P.difere.mean():.1f}%)")
for lo in (2007, 2011):
    p2 = P[(P.a >= lo)]
    print(f"  pares com ano inicial >= {lo}: {len(p2)}; difere em {int(p2.difere.sum())}")
print("pares em que difere:", P[P.difere][["a", "b"]].astype(str).agg("-".join, axis=1).tolist())
save(P, "nucleo_A_pares.csv")

# ---------------- (B)
print("=" * 30, "(B) queda no mesmo ano")
B = A.copy()
B["queda_set_dez_pct"] = 100 * (B.set - B.dez) / B.set
B["set_sobre_dez"] = B.set / B.dez
W = S.pivot(index="ano", columns="mes", values="dem_total")
B["max_ano"] = W.max(axis=1); B["mes_max"] = W.idxmax(axis=1)
B["queda_max_dez_pct"] = 100 * (B.max_ano - B.dez) / B.max_ano
print(B[["set", "dez", "queda_set_dez_pct", "set_sobre_dez", "max_ano", "mes_max", "queda_max_dez_pct"]].to_string(float_format=lambda v: f"{v:,.1f}"))
b = B.loc[2007:2019, "queda_set_dez_pct"].dropna()
sl = np.polyfit(b.index, b.values, 1)[0]
print(f"queda set->dez 2007-2019: min {b.min():.1f} ({b.idxmin()}), max {b.max():.1f} ({b.idxmax()}), media {b.mean():.1f}; "
      f"inclinacao OLS {sl:+.2f} p.p./ano; corr com ano {np.corrcoef(b.index, b.values)[0, 1]:+.2f}")
for lo, hi in ((2007, 2012), (2013, 2019), (2013, 2017)):
    bb = B.loc[lo:hi, "queda_set_dez_pct"].dropna(); print(f"  {lo}-{hi}: min {bb.min():.1f}, max {bb.max():.1f}, media {bb.mean():.1f}")
bq = B.loc[2020:2026, ["queda_max_dez_pct", "mes_max"]]; print("2020-2026, queda do maximo do ano ate dez:\n", bq.to_string())
save(B.reset_index(), "nucleo_B_queda.csv")

# ---------------- (C)
print("=" * 30, "(C) Meta 5 simulada")
C = S.copy()
C["atendida_pct"] = 100 * C.matric_creche / (C.matric_creche + C.dem_total)
C["crit_conf_75"] = C.atendida_pct >= 75
C["crit_literal_100"] = C.dem_total == 0
# componente da Meta 77: sem opcao por unidade especifica ha mais de 30 dias (publicado desde set/2020, coluna (2));
# set/2019-jun/2020: so ha "sem opcao" (sem corte de 30 dias), coluna (1)
C["sem_opcao_mais30"] = np.where(C.ano * 100 + C.mes >= 202009, C.dem_2, np.nan)
C["sem_opcao_total"] = np.where(C.ano * 100 + C.mes >= 202009, C.dem_1 + C.dem_2, np.where(C.ano * 100 + C.mes >= 201909, C.dem_1, np.nan))
conf = {2015: 77.62, 2016: 81.38, 2017: 87.05, 2018: 94.43, 2019: 96.31, 2020: 99.86, 2021: 99.85, 2022: 99.99}
conf_dem = {2015: 75194, 2016: 65040, 2017: 44092, 2018: 19697, 2019: 9670, 2020: 540, 2021: 595, 2022: 699}
d = C[C.mes == 12].set_index("ano")
print("Conferencia 2023 vs publicacao de dezembro (formula inferida matric/(matric+demanda)):")
ok = 0
for y in conf:
    calc = round(d.loc[y, "atendida_pct"], 2); bate = abs(calc - conf[y]) < 0.005; ok += bate
    print(f"  {y}: Conferencia {conf[y]:.2f} | calculado {calc:.2f} | {'BATE' if bate else 'NAO BATE'} | demanda conf {conf_dem[y]:,} vs publicada {int(d.loc[y, 'dem_total']):,}")
print(f"  formula reproduz {ok} de {len(conf)} anos")
print(C[["ano", "mes", "matric_creche", "dem_total", "atendida_pct", "crit_conf_75", "crit_literal_100", "sem_opcao_total", "sem_opcao_mais30"]].to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
save(C, "nucleo_C_meta.csv")
G = C[C.mes.isin(Q)].pivot(index="ano", columns="mes", values="atendida_pct").rename(columns=Q)
print("demanda atendida (%), ano x mes:\n", G.to_string(float_format=lambda v: f"{v:.1f}"))
H = C[C.mes.isin(Q)].pivot(index="ano", columns="mes", values="crit_conf_75").rename(columns=Q)
anos_div = [y for y in H.index if H.loc[y].dropna().nunique() > 1]
print("anos em que o criterio >=75% depende do mes:", anos_div)
for y in anos_div: print("  ", y, {m: bool(H.loc[y, m]) for m in H.columns if pd.notna(H.loc[y, m])}, {m: round(G.loc[y, m], 1) for m in G.columns if pd.notna(G.loc[y, m])})
print("1o ano em que >=75% vale em dezembro:", H.index[H.dez.fillna(False).astype(bool)].min(),
      "| 1o ano em que vale em setembro:", H.index[H.set.fillna(False).astype(bool)].min(),
      "| 1o ano em que vale nos 4 meses:", [y for y in H.index if H.loc[y].dropna().all() and H.loc[y].notna().sum() == 4][:1])
save(G.reset_index(), "nucleo_C_atendida_anoxmes.csv")

# ---------------- (D)
print("=" * 30, "(D) estoque reconstruido")
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"), columns=["d_sol1", "d_enc1", "d_age47", "d_des1"])
R = []
for y in range(2010, 2020):
    for m in (3, 6, 9, 12):
        t = pd.Timestamp(y, m, 1) + pd.offsets.MonthEnd(0) + pd.Timedelta(hours=23, minutes=59, seconds=59)
        if t > pd.Timestamp(2019, 11, 28): continue
        q = (sp.d_sol1 <= t) & ~(sp.d_enc1 <= t) & (sp.d_age47 > t) & ~(sp.d_des1 <= t)
        R.append(dict(ano=y, mes=m, reconstruido=int(q.sum())))
R = pd.DataFrame(R).merge(S[["ano", "mes", "dem_total"]], on=["ano", "mes"], how="left")
R["razao_rec_pub"] = R.reconstruido / R.dem_total
print(R.to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
RR = R.pivot(index="ano", columns="mes", values="reconstruido").rename(columns=Q)
for a, b2 in ((2013, 2017), (2013, 2018), (2014, 2018)):
    print(f"reconstruido {a}->{b2}: " + ", ".join(f"{m} {100 * (RR.loc[b2, m] - RR.loc[a, m]) / RR.loc[a, m]:+.0f}%" for m in Q.values()))
RB = RR.copy(); RB["queda_set_dez_pct"] = 100 * (RB.set - RB.dez) / RB.set
print("reconstruido, queda set->dez no mesmo ano:", RB.queda_set_dez_pct.round(1).to_dict())
save(R, "nucleo_D_reconstruido.csv")

# ---------------- (E)
print("=" * 30, "(E) indicadores de fluxo, janelas moveis de 12 meses")
sp2 = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"), columns=["d_sol1", "d_enc1", "d_birth"])
sp2 = sp2[sp2.d_sol1 >= pd.Timestamp(2012, 7, 1)].copy()
sp2["idade_m"] = (sp2.d_sol1 - sp2.d_birth).dt.days / 30.4375
sp2["enc365"] = (sp2.d_enc1 - sp2.d_sol1).dt.days.le(365) & sp2.d_enc1.notna()
E = []
for y in range(2013, 2019):
    for m in (3, 6, 9, 12):
        fim = pd.Timestamp(y, m, 1) + pd.offsets.MonthEnd(0) + pd.Timedelta(hours=23, minutes=59, seconds=59)
        ini = fim - pd.DateOffset(years=1)
        w = sp2[(sp2.d_sol1 > ini) & (sp2.d_sol1 <= fim)]
        seg = fim + pd.Timedelta(days=365) <= pd.Timestamp(2019, 11, 28)
        # tentativa 2: janela so conta se comecar depois de 30/6/2012 (registro completo); antes era truncada
        compl = ini >= pd.Timestamp(2012, 6, 30, 23, 59, 59)
        E.append(dict(ano=y, mes=m, janela_completa=compl, fluxo=len(w) if compl else np.nan,
                      idade_mediana_m=round(w.idade_m.median(), 1) if compl else np.nan,
                      enc365=round(w.enc365.mean(), 3) if (seg and compl) else np.nan))
E = pd.DataFrame(E); print(E.to_string(index=False))
for col in ("fluxo", "idade_mediana_m", "enc365"):
    P2 = E.pivot(index="ano", columns="mes", values=col).rename(columns=Q)
    for a, b2 in ((2014, 2017), (2014, 2018)):
        if b2 not in P2.index or P2.loc[b2].isna().all(): continue
        ch = {m: (P2.loc[b2, m] - P2.loc[a, m]) / P2.loc[a, m] * 100 if col == "fluxo" else P2.loc[b2, m] - P2.loc[a, m] for m in Q.values() if pd.notna(P2.loc[b2, m])}
        unid = "%" if col == "fluxo" else ("meses" if col == "idade_mediana_m" else "p.p./100")
        print(f"{col} {a}->{b2} por mes final da janela ({unid}): " + ", ".join(f"{m} {v:+.3f}" for m, v in ch.items())
              + f" | amplitude entre meses {max(ch.values()) - min(ch.values()):.3f}")
save(E, "nucleo_E_fluxos.csv")
