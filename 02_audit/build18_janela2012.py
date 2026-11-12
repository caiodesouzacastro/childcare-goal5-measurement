# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# MANHA, etapa 1.1 (26/10/2026): numeros do texto que mudam com a janela a partir de jul./2012 (coortes 2012-2016)
# e que nao estao em tabela existente. Cada bloco reproduz primeiro o valor publicado da coorte de 2013 (validacao).
# Descritivo. Saida: 03_build/build18/janela2012_nums.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, csv, numpy as np, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; OUT = os.path.join(ROOT, r"03_build\build18"); os.makedirs(OUT, exist_ok=True)
PANEL = pd.Timestamp("2019-11-28")
rows = []
def add(item, valor, validacao=""): rows.append(dict(item=item, valor=valor, validacao=validacao)); print(f"{item}: {valor}   [{validacao}]")
rr = list(csv.reader(open(os.path.join(ROOT, r"01_dados_publicos\ceinfo\sinasc_nv_distrito_2006_2026.csv"), encoding="utf-8"), delimiter=";"))
Bd = {int(h): sum(int(x[i]) for x in rr[1:] if x and x[0].strip() not in ("Ignorado", "Total")) for i, h in enumerate(rr[0]) if h.isdigit()}
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"))
def cif365(df, t1="d_enc1"):   # identico a build14_janela.py
    df = df[df.d_sol1 <= df.d_age47]
    tr = (df[t1] - df.d_sol1).dt.days.where(df[t1] >= df.d_sol1); ta = (df.d_age47 - df.d_sol1).dt.days; tc = (PANEL - df.d_sol1).dt.days
    T = np.fmin(np.fmin(tr.fillna(np.inf), ta), tc).values
    ev = np.where(tr.fillna(np.inf).values <= np.minimum(ta, tc).values, 1, np.where(ta.values <= tc.values, 2, 0))
    o = np.argsort(T, kind="mergesort"); T, ev = T[o], ev[o]; n = len(T); S = 1.0; c = 0.0; i = 0
    while i < n and T[i] <= 365:
        j = i
        while j < n and T[j] == T[i]: j += 1
        d1 = (ev[i:j] == 1).sum(); d2 = (ev[i:j] == 2).sum(); r = n - i; c += S * d1 / r; S *= 1 - (d1 + d2) / r; i = j
    return round(c, 3), len(df)
# --- timing por coorte (% dos nascidos, 96 distritos) ---
def frac(co, X): s = sp[sp.ano_nasc == co]; return round(100 * (s.idade_sol < X).sum() / Bd[co], 1)
for co in (2012, 2013):
    add(f"registro <6/<12/<24 meses (% nascidos), coorte {co}", f"{frac(co, 6)} / {frac(co, 12)} / {frac(co, 24)}", "2013 publicado: 26.1 / 41.5 / 62.3")
def kmmed(co):
    s = sp[sp.ano_nasc == co]
    for a in range(0, 120):
        if (s.idade_sol < a).sum() / Bd[co] >= 0.5: return a
add("mediana nascimento -> 1a solicitacao (meses), coortes 2012 / 2013 / 2016", f"{kmmed(2012)} / {kmmed(2013)} / {kmmed(2016)}", "publicado: 2013 = 17, 2016 = 12")
SER = {1: 1, 4: 2, 27: 3, 28: 4}
sp["band_req"] = pd.to_numeric(sp.serie_sol1, errors="coerce").map(SER)
sp["band_cur"] = np.select([sp.idade_sol < 14, sp.idade_sol < 23, sp.idade_sol < 35, sp.idade_sol < 47], [1, 2, 3, 4], 5)
def fcur(co): d = sp[(sp.ano_nasc == co) & (sp.band_req == sp.band_cur)]; return round(100 * (d.idade_sol < 12).sum() / Bd[co], 1)
add("<12m restrito a faixa corrente (% nascidos), coortes 2012 / 2013 / 2016", f"{fcur(2012)} / {fcur(2013)} / {fcur(2016)}", "publicado: 41.5 -> 49.0")
cr = sp[sp.band_req.notna()]; crc = cr[cr.d_sol1 >= "2012-07-01"]
add("faixa pedida = faixa corrente; faixa futura (% solicitacoes de creche a partir de jul./2012)",
    f"{100 * (crc.band_req == crc.band_cur).mean():.1f} / {100 * (crc.band_req > crc.band_cur).mean():.1f}", "2013+: 89.4 / 1.7")
y0 = sp[sp.idade_sol.between(0, 5) & sp.band_req.notna() & (sp.d_sol1 >= "2012-07-01")]
add("0-5 meses pedindo Bercario I (%, a partir de jul./2012)", f"{100 * (y0.band_req == 1).mean():.1f}", "2013+: 100")
# --- distritos 2012-2016 ---
pan = pd.read_parquet(os.path.join(ROOT, r"03_build\build05\_panel_criancas.parquet"), columns=["cd_aluno_sme", "distrito"])
pan["cd_aluno_sme"] = pan.cd_aluno_sme.astype(str); z = sp[["cd_aluno_sme", "ano_nasc", "idade_sol"]].assign(cd_aluno_sme=lambda d: d.cd_aluno_sme.astype(str)).merge(pan, on="cd_aluno_sme", how="left")
z = z[(z.idade_sol < 24) & z.distrito.notna()]; z["lt12"] = (z.idade_sol < 12).astype(int)
for a, b in ((2013, 2016), (2012, 2016)):
    g = z[z.ano_nasc.isin([a, b])].groupby(["distrito", "ano_nasc"]).lt12.mean().unstack(); d = (g[b] - g[a]).dropna()
    add(f"distritos {a}-{b}: N / sobe / mediana / min / max", f"{len(d)} / {int((d > 0).sum())} / {d.median():+.3f} / {d.min():+.3f} / {d.max():+.3f}", "2013-2016 publicado: 96 / 85 / +0.042 / -0.060 / +0.171")
# --- coorte 2012: composicao no tempo ---
for co in (2012, 2013):
    s = sp[(sp.ano_nasc == co) & (sp.d_sol1 <= sp.d_age47)]; t = sp[sp.ano_nasc == co]
    add(f"coorte {co} elegivel: solicitou a partir de jul./2016 (%)", f"{100 * (s.d_sol1 >= '2016-07-01').mean():.1f}", "2013 publicado: 8.2")
    add(f"coorte {co} elegivel: solicitou antes de jul./2012 (%)", f"{100 * (s.d_sol1 < '2012-07-01').mean():.1f}")
    add(f"coorte {co} elegivel: solicitou em jul./2012-dez./2013 (%)", f"{100 * ((s.d_sol1 >= '2012-07-01') & (s.d_sol1 < '2014-01-01')).mean():.1f}", "2013 publicado: 29.8")
    add(f"coorte {co}: solicitou depois do limite de elegibilidade, por dia (% de todos os solicitantes)", f"{100 * (t.d_sol1 > t.d_age47).mean():.1f} (N={len(t):,})", "2013 publicado: 8.0")
# coorte 2012 so com solicitacoes a partir de jul./2012 (sensibilidade da janela)
s12 = sp[(sp.ano_nasc == 2012) & (sp.d_sol1 >= "2012-07-01")]
a, n = cif365(s12); b, _ = cif365(s12, "d_mat1")
add("coorte 2012, so solicitacoes a partir de jul./2012: ref365 / mat365 / N", f"{a:.3f} / {b:.3f} / {n:,}", "FATAIS: 0.607")
# --- semestre 2012S2 ---
s = sp[(sp.d_sol1 >= "2012-07-01") & (sp.d_sol1 < "2013-01-01")]; a, n = cif365(s); b, _ = cif365(s, "d_mat1")
add("solicitacoes 2012S2: ref365 / mat365 / N", f"{a:.3f} / {b:.3f} / {n:,}", "c3x: 0.562")
s = sp[(sp.d_sol1 >= "2013-01-01") & (sp.d_sol1 < "2013-07-01")]; a, n = cif365(s)
add("validacao 2013S1 ref365", f"{a:.3f}", "reforma_semestral: 0.707")
# --- primeiras solicitacoes na janela; serie analoga a Soares (todos os solicitantes) ---
add("1as solicitacoes a partir de 1/7/2012", f"{(sp.d_sol1 >= '2012-07-01').sum():,}", "a partir de 2013: 1,047,288")
cm = pd.read_feather(os.path.join(ROOT, r"03_build\build01\_staging\child_master.feather"), columns=["cd_aluno_sme", "ano_sol", "idade_sol"])
m = cm.groupby("ano_sol").idade_sol.mean()
cm2 = cm.merge(sp[["cd_aluno_sme", "d_sol1"]], on="cd_aluno_sme", how="left")
m12s2 = cm2[(cm2.d_sol1 >= "2012-07-01") & (cm2.d_sol1 < "2013-01-01")].idade_sol.mean()
add("idade media na 1a solicitacao (meses), todos: 2010 / 2012S2 / 2013 / 2018", f"{m[2010]:.2f} / {m12s2:.2f} / {m[2013]:.2f} / {m[2018]:.2f}", "publicado: 35.64 / - / 24.35 / 16.78")
R = pd.DataFrame(rows); p = os.path.join(OUT, "janela2012_nums.csv"); R.to_csv(p, index=False); assert len(pd.read_csv(p)) == len(R); print("[gravado e relido]", p, len(R))
