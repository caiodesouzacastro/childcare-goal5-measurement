# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# FATAIS, Etapas 2.4-2.6 e 3 (26/10/2026): ganho por data de inicio da janela e series por semestre, com o mesmo
# estimador do paper (cif365 de build14_janela.py, que reproduz a Tabela 1 e a A20). Descritivo; nao escreve em 04_paper.
# Saidas: 03_build/build17_fatais/c2_inicio_janela.csv, c3x_series_semestre.csv, c2_coorte_semestres.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, numpy as np, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; OUT = os.path.join(ROOT, r"03_build\build17_fatais")
PANEL = pd.Timestamp("2019-11-28")
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
def save(df, name):
    p = os.path.join(OUT, name); df.to_csv(p, index=False); chk = pd.read_csv(p)
    assert len(chk) == len(df), name; print(f"[gravado e relido] {p} ({len(chk)} linhas)")
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"),
                     columns=["cd_aluno_sme", "ano_nasc", "mes_nasc", "d_sol1", "d_enc1", "d_mat1", "d_age47", "d_birth"])
def cif365(df, t1):   # identico a build14_janela.py
    df = df[df.d_sol1 <= df.d_age47]
    tr = (df[t1] - df.d_sol1).dt.days.where(df[t1] >= df.d_sol1); ta = (df.d_age47 - df.d_sol1).dt.days; tc = (PANEL - df.d_sol1).dt.days
    T = np.fmin(np.fmin(tr.fillna(np.inf), ta), tc).values
    ev = np.where(tr.fillna(np.inf).values <= np.minimum(ta, tc).values, 1, np.where(ta.values <= tc.values, 2, 0))
    o = np.argsort(T, kind="mergesort"); T, ev = T[o], ev[o]; n = len(T); S = 1.0; c = 0.0; i = 0
    while i < n and T[i] <= 365:
        j = i
        while j < n and T[j] == T[i]: j += 1
        d1 = (ev[i:j] == 1).sum(); d2 = (ev[i:j] == 2).sum(); r = n - i; c += S * d1 / r; S *= 1 - (d1 + d2) / r; i = j
    return c, len(df)
comp = pd.read_csv(os.path.join(OUT, "c2_completude_semestre.csv")).set_index("semestre").completude_solicitacao
sp["s"] = sp.d_sol1.dt.year.astype(str) + np.where(sp.d_sol1.dt.month <= 6, "S1", "S2")
# validacao contra a Tabela 1 / A20
v = {co: round(cif365(sp[sp.ano_nasc == co], "d_enc1")[0], 3) for co in range(2010, 2017)}
print("validacao coorte (Tabela 1: 0.563 0.530 0.631 0.753 0.761 0.814 0.876):", v)
# ---------- composicao da coorte por semestre de solicitacao, e completude implicada ----------
rows = []
for co in range(2010, 2017):
    g = sp[sp.ano_nasc == co]; sh = g.s.value_counts(normalize=True)
    w = sum(sh.get(k, 0) * comp.get(k, 100.0 if k >= "2019" else np.nan) for k in sh.index if k >= "2010")
    pre = g.d_sol1 < "2010-01-01"
    rows.append(dict(coorte=co, solicitantes=len(g), pct_sol_antes_2012S2=round(100 * (g.d_sol1 < "2012-07-01").mean(), 1),
                     pct_sol_2012S1=round(100 * (g.s == "2012S1").mean(), 1), completude_ponderada=round(w / sh[sh.index >= "2010"].sum(), 1)))
CC = pd.DataFrame(rows); print("\ncoortes: parcela das solicitacoes antes de jul/2012 e completude ponderada pelos semestres de solicitacao (%):"); print(CC.to_string(index=False))
save(CC, "c2_coorte_semestres.csv")
# ---------- ganho por inicio da janela ----------
r12 = pd.read_csv(os.path.join(ROOT, r"03_build\build03\_staging\S2a_frac_0_24.csv")).set_index("coorte_nasc").frac_ate12m
cy = {co: cif365(sp[sp.ano_nasc == co], "d_enc1") for co in range(2010, 2017)}
cm = {co: cif365(sp[sp.ano_nasc == co], "d_mat1")[0] for co in range(2010, 2017)}
yy = {y: cif365(sp[sp.d_sol1.dt.year == y], "d_enc1") for y in range(2010, 2018)}
rows = []
for st in (2010, 2011, 2012, 2013, 2014):
    rows.append(dict(serie="encaminhamento 1 ano, por coorte", inicio=st, fim=2016, passos=2016 - st, N=sum(cy[c][1] for c in range(st, 2017)),
                     valor_inicio=round(cy[st][0], 3), valor_fim=round(cy[2016][0], 3), ganho=round(cy[2016][0] - cy[st][0], 3), completude_inicio=CC.set_index("coorte").completude_ponderada[st]))
    rows.append(dict(serie="matricula 1 ano, por coorte", inicio=st, fim=2016, passos=2016 - st, N=sum(cy[c][1] for c in range(st, 2017)),
                     valor_inicio=round(cm[st], 3), valor_fim=round(cm[2016], 3), ganho=round(cm[2016] - cm[st], 3), completude_inicio=CC.set_index("coorte").completude_ponderada[st]))
    rows.append(dict(serie="registro antes de 12 meses (% nascidos), por coorte", inicio=st, fim=2016, passos=2016 - st, N=np.nan,
                     valor_inicio=round(r12[st], 1), valor_fim=round(r12[2016], 1), ganho=round(r12[2016] - r12[st], 1), completude_inicio=CC.set_index("coorte").completude_ponderada[st]))
    rows.append(dict(serie="encaminhamento 1 ano, por ano de solicitacao", inicio=st, fim=2017, passos=2017 - st, N=sum(yy[y][1] for y in range(st, 2018)),
                     valor_inicio=round(yy[st][0], 3), valor_fim=round(yy[2017][0], 3), ganho=round(yy[2017][0] - yy[st][0], 3),
                     completude_inicio=round(comp[[f"{st}S1", f"{st}S2"]].mean(), 1)))
a, n = cif365(sp[(sp.d_sol1 >= "2012-07-01") & (sp.d_sol1 < "2013-01-01")], "d_enc1")
rows.append(dict(serie="encaminhamento 1 ano, por ano de solicitacao", inicio="2012S2", fim=2017, passos=4.5, N=n + sum(yy[y][1] for y in range(2013, 2018)),
                 valor_inicio=round(a, 3), valor_fim=round(yy[2017][0], 3), ganho=round(yy[2017][0] - a, 3), completude_inicio=comp["2012S2"]))
G = pd.DataFrame(rows).sort_values(["serie", "inicio"], key=lambda s: s.astype(str)); print("\nganho por inicio da janela:"); print(G.to_string(index=False))
save(G, "c2_inicio_janela.csv")
# coorte 2012 restrita a solicitacoes a partir de jul/2012 (sensibilidade; amostra selecionada, so para limitar o vies)
a, n = cif365(sp[(sp.ano_nasc == 2012) & (sp.d_sol1 >= "2012-07-01")], "d_enc1")
print(f"\ncoorte 2012, so solicitacoes a partir de jul/2012: {a:.3f} (N={n:,}) contra {cy[2012][0]:.3f} na coorte inteira")
# ---------- series por semestre (para a Etapa 3: linearidade) ----------
rows = []
for y in range(2010, 2019):
    for h, (m0, m1) in (("S1", (1, 6)), ("S2", (7, 12))):
        g = sp[(sp.d_sol1.dt.year == y) & sp.d_sol1.dt.month.between(m0, m1)]
        a, n = cif365(g, "d_enc1"); b, _ = cif365(g, "d_mat1")
        rows.append(dict(serie="ano_solicitacao", periodo=f"{y}{h}", N=n, ref365=round(a, 4), mat365=round(b, 4)))
for co in range(2010, 2017):
    for h, (m0, m1) in (("S1", (1, 6)), ("S2", (7, 12))):
        g = sp[(sp.ano_nasc == co) & sp.mes_nasc.between(m0, m1)]
        a, n = cif365(g, "d_enc1"); b, _ = cif365(g, "d_mat1")
        age = ((g.d_sol1 - g.d_birth).dt.days / 30.4375)
        # registro antes de 12 meses, % dos solicitantes do semestre de nascimento (nascidos vivos por semestre nao disponiveis)
        rows.append(dict(serie="coorte_semestre", periodo=f"{co}{h}", N=n, ref365=round(a, 4), mat365=round(b, 4),
                         sol_antes_12m_pct_solicitantes=round(100 * (age < 12).mean(), 2), N_solicitantes=len(g)))
S = pd.DataFrame(rows); print(S.to_string(index=False)); save(S, "c3x_series_semestre.csv")
