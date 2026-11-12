# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# FATAIS, Etapa 3 (26/10/2026): C1. (i) tres normalizacoes do ganho (bruta, por passo, nivel no ponto de partida);
# (ii) teste de linearidade das series; (iii) limites para o nivel das coortes de cobertura incompleta, somando os
# entrantes do EOL sem solicitacao anterior a entrada. So aritmetica sobre series ja calculadas (janela_cif.csv,
# S2a_frac_0_24.csv, V2_coverage Panel B, c3x_series_semestre.csv) e uma contagem no EOL. Descritivo.
# Saidas: 03_build/build17_fatais/c1_*.csv. Corrigido em 26/10 (MANHA 1.4): entradas ate 2018. O nivel corrigido usado no paper
# esta em 03_build/build18/nivel_corrigido.csv (build18_nivel.py), que tambem remove a dupla contagem dos ausentes ja no N.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, numpy as np, pandas as pd; from scipy import stats; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; OUT = os.path.join(ROOT, r"03_build\build17_fatais")
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
def save(df, name):
    p = os.path.join(OUT, name); df.to_csv(p, index=False); chk = pd.read_csv(p)
    assert len(chk) == len(df), name; print(f"[gravado e relido] {p} ({len(chk)} linhas)")
jc = pd.read_csv(os.path.join(ROOT, r"03_build\build14_cobertura\janela_cif.csv"))
co = jc[jc.serie == "coorte"].assign(g=lambda d: d.grupo.astype(int)).set_index("g")
ay = jc[(jc.serie == "ano_solicitacao") & jc.grupo.str.isdigit()].assign(g=lambda d: d.grupo.astype(int)).set_index("g")
r12 = pd.read_csv(os.path.join(ROOT, r"03_build\build03\_staging\S2a_frac_0_24.csv")).set_index("coorte_nasc")
# Tabela 1 / V2_coverage Panel B (registro x EOL, % nascidos matriculados antes de 24 meses)
rec24 = pd.Series([7.4, 22.8, 33.2, 43.4, 44.1, 46.6, 53.8], index=range(2010, 2017)); eol24 = pd.Series([25.1, 28.3, 31.9, 42.9, 43.2, 45.6, 53.2], index=range(2010, 2017))
S = {  # nome: (serie, N por ponto, escala)
    "registro antes de 12 meses (% nascidos), coorte": (r12.frac_ate12m.round(1), r12.nascidos, 100),
    "encaminhamento 1 ano, coorte": (co.ref365, co.N, 1),
    "matricula 1 ano, coorte": (co.mat365, co.N, 1),
    "encaminhamento 1 ano, ano de solicitacao": (ay.ref365, ay.N, 1),
    "matriculado antes de 24 meses (% nascidos), registro": (rec24, r12.nascidos, 100),
    "matriculado antes de 24 meses (% nascidos), EOL": (eol24, r12.nascidos, 100),
}
STD = {"full": (0.498, 0.885), 2013: (0.753, 0.885)}   # composicao fixa em 2013 (V2_naive); serie anual nao recalculada
rows = []
for nm, (s, N, sc) in S.items():
    f0 = 2010; f1 = 2017 if "ano de solicitacao" in nm else 2016
    for w0 in (2012, 2013):
        full = s[f1] - s[f0]; win = s[f1] - s[w0]; pre = s[w0] - s[f0]
        rows.append(dict(medida=nm, inicio_janela=w0, completo=f"{s[f0]:g}->{s[f1]:g}", janela=f"{s[w0]:g}->{s[f1]:g}",
                         a_ganho_completo=round(full, 3), a_ganho_janela=round(win, 3), a_razao=round(win / full, 2),
                         b_passo_completo=round(full / (f1 - f0), 4), b_passo_janela=round(win / (f1 - w0), 4), b_razao=round((win / (f1 - w0)) / (full / (f1 - f0)), 2),
                         c_subida_antes_da_janela=round(pre, 3), c_parcela_do_ganho_antes_da_janela=round(pre / full, 2)))
for w0 in (2013,):
    a0, a1 = STD["full"]; b0, b1 = STD[w0]
    rows.append(dict(medida="encaminhamento 1 ano, coorte, composicao fixa em 2013", inicio_janela=w0, completo=f"{a0}->{a1}", janela=f"{b0}->{b1}",
                     a_ganho_completo=round(a1 - a0, 3), a_ganho_janela=round(b1 - b0, 3), a_razao=round((b1 - b0) / (a1 - a0), 2),
                     b_passo_completo=round((a1 - a0) / 6, 4), b_passo_janela=round((b1 - b0) / 3, 4), b_razao=round(((b1 - b0) / 3) / ((a1 - a0) / 6), 2),
                     c_subida_antes_da_janela=round(b0 - a0, 3), c_parcela_do_ganho_antes_da_janela=round((b0 - a0) / (a1 - a0), 2)))
T = pd.DataFrame(rows); print(T.to_string(index=False)); save(T, "c1_normalizacoes.csv")

# ---------- linearidade ----------
def lin(y, n, sc, label):
    x = np.array(y.index, float); p = y.values / sc; v = p * (1 - p) / n.reindex(y.index).values   # variancia binomial (aproximacao)
    w = 1 / v; X = np.c_[np.ones_like(x), x]; b = np.linalg.solve(X.T @ (w[:, None] * X), X.T @ (w * p)); res = p - X @ b
    chi = float((w * res ** 2).sum()); df = len(x) - 2; steps = np.diff(p); gain = p[-1] - p[0]
    return dict(serie=label, pontos=len(x), passos=" ".join(f"{sc * d:+.3g}" for d in steps), ganho=round(sc * gain, 3),
                maior_passo_pct_do_ganho=round(100 * steps.max() / gain, 0), menor_passo_pct_do_ganho=round(100 * steps.min() / gain, 0),
                residuo_max_pct_do_ganho=round(100 * np.abs(res).max() / abs(gain), 0), chi2=round(chi, 1), gl=df, p=f"{stats.chi2.sf(chi, df):.1e}")
L = []
for nm, (s, N, sc) in S.items():
    f1 = 2017 if "ano de solicitacao" in nm else 2016
    for w0 in (2010, 2012, 2013):
        L.append(lin(s.loc[w0:f1], N, sc, f"{nm}, {w0}-{f1}"))
ss = pd.read_csv(os.path.join(OUT, "c3x_series_semestre.csv"))
for ser, w0, w1 in (("coorte_semestre", "2013S1", "2016S2"), ("coorte_semestre", "2012S1", "2016S2")):
    g = ss[(ss.serie == ser) & (ss.periodo >= w0) & (ss.periodo <= w1)].reset_index(drop=True)
    g.index = np.arange(len(g)) / 2.0
    L.append(lin(g.ref365, g.N.set_axis(g.index), 1, f"encaminhamento 1 ano, coorte por semestre de nascimento, {w0}-{w1}"))
for h in ("S1", "S2"):
    g = ss[(ss.serie == "ano_solicitacao") & ss.periodo.str.endswith(h) & (ss.periodo >= "2013") & (ss.periodo < "2018")].reset_index(drop=True)
    g.index = np.arange(len(g)).astype(float)
    L.append(lin(g.ref365, g.N.set_axis(g.index), 1, f"encaminhamento 1 ano, solicitacoes do {h}, 2013-2017"))
LL = pd.DataFrame(L); print("\nlinearidade (passos na escala da medida; qui-quadrado de WLS com variancia binomial):"); print(LL.to_string(index=False))
save(LL, "c1_linearidade.csv")

# ---------- limites para o nivel nas coortes de cobertura incompleta ----------
key = lambda s: pd.to_numeric(s, errors="coerce").astype("Int64")
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"), columns=["cd_aluno_sme", "ano_nasc", "d_sol1"])
sp["id"] = key(sp.cd_aluno_sme)
e = pd.read_parquet(os.path.join(ROOT, r"03_build\build14_cobertura\eol_creche.parquet"), columns=["CD_ALUNO_SME", "AN_LETIVO", "DT_IN_MAT", "ANO_NASC_ALUNO", "MES_NASC_ALUNO"])
e["id"] = key(e.CD_ALUNO_SME); e["an"] = pd.to_numeric(e.AN_LETIVO, errors="coerce"); e["dt"] = pd.to_datetime(e.DT_IN_MAT.str[:19], errors="coerce")
f = e.dropna(subset=["id", "dt"]).sort_values(["id", "an", "dt"]).groupby("id").first()
f["an_n"] = pd.to_numeric(f.ANO_NASC_ALUNO, errors="coerce"); f["me_n"] = pd.to_numeric(f.MES_NASC_ALUNO, errors="coerce")
f["idade"] = (f.dt.dt.year - f.an_n) * 12 + (f.dt.dt.month - f.me_n)
f = f[f.dt < "2019-01-01"]   # MANHA 1.4 (26/10/2026): so entradas ate dez./2018; antes entravam os entrantes de 2019 (falha F2 do FATAIS)
f = f.join(sp.set_index("id")[["d_sol1"]], how="left"); f["semsol"] = ~(f.d_sol1.notna() & (f.d_sol1 < f.dt))
B = []
for c in range(2010, 2017):
    g = f[(f.an_n == c) & f.idade.between(0, 46)]; M = int(g.semsol.sum()); N = int(co.N[c]); p = co.ref365[c]; q = co.mat365[c]
    nasc = r12.nascidos[c]; m12 = int((g.semsol & (g.idade < 24)).sum())
    B.append(dict(coorte=c, N_solicitantes_elegiveis=N, entrantes_sem_solicitacao_previa=M, pct_de_N=round(100 * M / N, 1),
                  ref365=p, ref365_lim_inf=round(p * N / (N + M), 3), ref365_lim_sup=round((p * N + M) / (N + M), 3),
                  mat365=q, mat365_lim_inf=round(q * N / (N + M), 3), mat365_lim_sup=round((q * N + M) / (N + M), 3),
                  reg12m=round(r12.frac_ate12m[c], 1), reg12m_lim_sup=round(r12.frac_ate12m[c] + 100 * M / nasc, 1),
                  reg12m_lim_sup_so_entrantes_antes_24m=round(r12.frac_ate12m[c] + 100 * m12 / nasc, 1)))
BB = pd.DataFrame(B); print("\nlimites (ver nota no FATAIS.md: o limite inferior supoe que nenhum ausente foi encaminhado em 1 ano; o superior, que todos foram):")
print(BB.to_string(index=False)); save(BB, "c1_limites_nivel.csv")
