# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# PLANO_V2 (25/10/2026), item 6: numeros do texto que nao estao em tabela por coorte 2013-2016 e precisam de recalculo.
# Cada bloco REPRODUZ o valor publicado (coluna 'validacao') e calcula a janela limpa. Descritivo.
# Saida: 03_build/build14_cobertura/v2nums.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, csv, numpy as np, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; OUT = os.path.join(ROOT, r"03_build\build14_cobertura")
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"))
cm = pd.read_feather(os.path.join(ROOT, r"03_build\build01\_staging\child_master.feather"),
                     columns=["cd_aluno_sme", "ano_sol", "nunca", "idade_sol", "prio", "renda", "ever_mat"])
rows = []
def add(item, valor_publicado, recalc_publicado, janela_limpa, nota=""):
    rows.append(dict(item=item, publicado=valor_publicado, reproduzido=recalc_publicado, janela_limpa=janela_limpa, nota=nota))
# nascidos vivos (SINASC, linha Total) -- mesma fonte do paper
r = list(csv.reader(open(os.path.join(ROOT, r"01_dados_publicos\ceinfo\sinasc_nv_distrito_2006_2026.csv"), encoding="utf-8"), delimiter=";"))
hdr = r[0]; tot = [x for x in r if x and x[0].strip() == "Total"][0]; B = {int(h): int(tot[i]) for i, h in enumerate(hdr) if h.isdigit()}
# o paper soma os 96 distritos (exclui Ignorado e Total); reconstruir assim
dist = [x for x in r[1:] if x and x[0].strip() not in ("Ignorado", "Total")]
Bd = {int(h): sum(int(x[i]) for x in dist) for i, h in enumerate(hdr) if h.isdigit()}
def frac(co, X): s = sp[sp.ano_nasc == co]; return round(100 * (s.idade_sol < X).sum() / Bd[co], 1)
def kmmed(co):
    s = sp[sp.ano_nasc == co]
    for a in range(0, 120):
        if (s.idade_sol < a).sum() / Bd[co] >= 0.5: return a
add("registro antes de 6 meses (% nascidos)", "4.2 -> 33.4 (2010->2016)", f"{frac(2010, 6)} -> {frac(2016, 6)}", f"{frac(2013, 6)} -> {frac(2016, 6)} (2013->2016)")
add("registro antes de 12 meses (% nascidos)", "11.0 -> 50.1", f"{frac(2010, 12)} -> {frac(2016, 12)}", f"{frac(2013, 12)} -> {frac(2016, 12)}")
add("registro antes de 24 meses (% nascidos)", "33.7 -> 70.9", f"{frac(2010, 24)} -> {frac(2016, 24)}", f"{frac(2013, 24)} -> {frac(2016, 24)}")
add("mediana nascimento->1a solicitacao (meses)", "36 -> 12", f"{kmmed(2010)} -> {kmmed(2016)}", f"{kmmed(2013)} -> {kmmed(2016)}")
# faixa pedida x faixa corrente (V8)
SER = {1: 1, 4: 2, 27: 3, 28: 4}
sp["band_req"] = pd.to_numeric(sp.serie_sol1, errors="coerce").map(SER)
sp["band_cur"] = np.select([sp.idade_sol < 14, sp.idade_sol < 23, sp.idade_sol < 35, sp.idade_sol < 47], [1, 2, 3, 4], 5)
def fcur(co): d = sp[(sp.ano_nasc == co) & (sp.band_req == sp.band_cur)]; return round(100 * (d.idade_sol < 12).sum() / Bd[co], 1)
add("<12m restrito a faixa corrente (% nascidos)", "11.0 -> 49.0", f"{fcur(2010)} -> {fcur(2016)}", f"{fcur(2013)} -> {fcur(2016)}")
cr = sp[sp.band_req.notna()]; crc = cr[cr.d_sol1 >= "2013-01-01"]
add("faixa pedida = faixa corrente (% solicitacoes de creche)", "83", f"{100 * (cr.band_req == cr.band_cur).mean():.0f}", f"{100 * (crc.band_req == crc.band_cur).mean():.0f} (solicitacoes 2013+)")
add("faixa pedida futura (%)", "1", f"{100 * (cr.band_req > cr.band_cur).mean():.1f}", f"{100 * (crc.band_req > crc.band_cur).mean():.1f}")
y0 = sp[sp.idade_sol.between(0, 5) & sp.band_req.notna()]; y0c = y0[y0.d_sol1 >= "2013-01-01"]
add("0-5 meses pedindo Bercario I (%)", "100", f"{100 * (y0.band_req == 1).mean():.1f}", f"{100 * (y0c.band_req == 1).mean():.1f}")
# mediana mensal da idade na 1a solicitacao (Figura A3)
mm = sp.groupby(sp.d_sol1.dt.to_period("M")).idade_sol.median()
add("mediana mensal idade na 1a solicitacao (meses)", "46 (jan/2010) -> 13 (dez/2018)", f"{mm[pd.Period('2010-01')]:.0f} -> {mm[pd.Period('2018-12')]:.0f}",
    f"{mm[pd.Period('2013-01')]:.0f} (jan/2013) -> {mm[pd.Period('2018-12')]:.0f} (dez/2018)")
# C4: matricula apos encaminhamento por celula
q = sp.copy(); q["esp"] = (q.d_enc1 - q.d_sol1).dt.days; q["refd"] = q.d_enc1.notna() & (q.esp >= 0)
q["mat_after"] = q.d_mat1.notna() & q.refd & (q.d_mat1 >= q.d_enc1)
def c4(df):
    out = []
    for alo, ahi in ((0, 5), (6, 11), (12, 23), (24, 999)):
        for slo, shi in ((0, 30), (31, 90), (91, 180), (181, 10 ** 9)):
            s = df[df.refd & df.idade_sol.between(alo, ahi) & df.esp.between(slo, shi)]
            rr = s[s.d_rec1.notna()]
            out.append((len(s), 100 * s.mat_after.mean(), 100 * (rr.n_enc_after_rec > 0).mean() if len(rr) else np.nan))
    return out
a = c4(q); b = c4(q[q.d_sol1 >= "2013-01-01"])
add("C4 celula 0-5m e 0-30d: N / % matricula", "25,297 / 94.5", f"{a[0][0]:,} / {a[0][1]:.1f}", f"{b[0][0]:,} / {b[0][1]:.1f}")
add("C4 faixa da taxa de matricula entre celulas (%)", "82-95", f"{min(x[1] for x in a):.1f}-{max(x[1] for x in a):.1f}", f"{min(x[1] for x in b):.1f}-{max(x[1] for x in b):.1f}")
add("C4 faixa de re-encaminhamento apos recusa (%)", "53-87", f"{np.nanmin([x[2] for x in a]):.1f}-{np.nanmax([x[2] for x in a]):.1f}", f"{np.nanmin([x[2] for x in b]):.1f}-{np.nanmax([x[2] for x in b]):.1f}")
# nunca matriculados (T1/T4d)
c = cm.copy(); cc = c[c.ano_sol.between(2013, 2017)]
add("nunca matriculados, % de todos", "13.4 (1,524,560)", f"{100 * c.nunca.mean():.1f}", f"{100 * cc.nunca.mean():.1f} (solicitacoes 2013-2017, N={len(cc):,})")
for v, lab, pub in (("idade_sol", "idade media na solicitacao, nunca vs matriculados", "29.2 vs 21.4"), ("prio", "% com prioridade, nunca vs matriculados", "4.0 vs 16.1"),
                     ("renda", "renda media do CEP, nunca vs matriculados", "1295 vs 1201")):
    k = 100 if v == "prio" else 1
    add(lab, pub, f"{k * c[c.nunca == 1][v].mean():.1f} vs {k * c[c.nunca == 0][v].mean():.1f}", f"{k * cc[cc.nunca == 1][v].mean():.1f} vs {k * cc[cc.nunca == 0][v].mean():.1f}")
# primeiras solicitacoes no universo na janela
add("1as solicitacoes na janela (2013-2018)", "1,524,560 (2006-2018)", f"{len(sp):,}", f"{(sp.d_sol1 >= '2013-01-01').sum():,}")
R = pd.DataFrame(rows); R.to_csv(os.path.join(OUT, "v2nums.csv"), index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60); print(R.to_string(index=False))
