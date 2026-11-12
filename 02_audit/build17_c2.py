# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# FATAIS, Etapa 2 (26/10/2026): C2, completude do registro indexada pela DATA DE SOLICITACAO (nao pelo ano de entrada).
# Duas medidas, ambas usando o EOL (registro de matricula, independente da fila) como referencia:
#  (a) completude das solicitacoes do semestre P: R(P) / (R(P) + M(P)), em que
#      R(P) = entrantes em creche no EOL (2010-2018) cuja 1a solicitacao registrada cai em P e antecede a entrada;
#      M(P) = entrantes SEM solicitacao registrada antes da entrada, distribuidos pelos semestres em que teriam solicitado
#             segundo a distribuicao da defasagem entrada - solicitacao observada nos entrantes cobertos de 2014-2017
#             (separada para entrada em fevereiro e nos demais meses). Supoe que a defasagem dos ausentes e a dos cobertos
#             e que a completude e a mesma entre quem entra e quem nunca entra (o EOL so ve quem entra).
#  (b) completude do DESFECHO: entre solicitantes de P que entraram em creche no EOL depois de solicitar, a parcela com
#      encaminhamento registrado na fila ate 60 dias apos a entrada, e com matricula na fila a ate 60 dias da entrada.
# Regra de corte fixada ANTES de ver o resultado: o semestre P e "completo" se (a) e (b, encaminhamento) ficam a no maximo
# 2 p.p. abaixo da media de 2014S1-2016S2. A janela comeca no primeiro semestre a partir do qual todos sao completos.
# Descritivo; nao escreve em 04_paper. Saidas: 03_build/build17_fatais/c2_*.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, numpy as np, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; OUT = os.path.join(ROOT, r"03_build\build17_fatais"); os.makedirs(OUT, exist_ok=True)
PANEL = pd.Timestamp("2019-11-28"); EMAX = pd.Timestamp("2019-01-01")
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
def save(df, name):
    p = os.path.join(OUT, name); df.to_csv(p, index=False); chk = pd.read_csv(p)
    assert len(chk) == len(df), name; print(f"[gravado e relido] {p} ({len(chk)} linhas)")
def key(s): return pd.to_numeric(s, errors="coerce").astype("Int64")
def sem(d): return d.dt.year.astype("Int64") * 10 + np.where(d.dt.month <= 6, 1, 2)
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"),
                     columns=["cd_aluno_sme", "ano_nasc", "d_sol1", "d_enc1", "d_mat1", "d_age47"])
sp["id"] = key(sp.cd_aluno_sme)
e = pd.read_parquet(os.path.join(ROOT, r"03_build\build14_cobertura\eol_creche.parquet"), columns=["CD_ALUNO_SME", "AN_LETIVO", "DT_IN_MAT"])
e["id"] = key(e.CD_ALUNO_SME); e["an"] = pd.to_numeric(e.AN_LETIVO, errors="coerce"); e["dt"] = pd.to_datetime(e.DT_IN_MAT.str[:19], errors="coerce")
first = e.dropna(subset=["id", "dt"]).sort_values(["id", "an", "dt"]).groupby("id").first()[["dt"]]
x = first.join(sp.set_index("id")[["d_sol1", "d_enc1", "d_mat1"]], how="left")
x = x[(x.dt >= "2010-01-01") & (x.dt < EMAX)]
x["cov"] = x.d_sol1.notna() & (x.d_sol1 < x.dt); x["fev"] = x.dt.dt.month == 2
print(f"entrantes 2010-2018: {len(x):,} | com solicitacao anterior a entrada: {100 * x['cov'].mean():.1f}%")
# --- distribuicao da defasagem (dias) nos entrantes cobertos de 2014-2017
base = x[x["cov"] & (x.dt >= "2014-01-01") & (x.dt < "2018-01-01")]
lags = {f: np.sort((g.dt - g.d_sol1).dt.total_seconds().values / 86400) for f, g in base.groupby("fev")}
print("defasagem entrada - solicitacao, entrantes cobertos 2014-2017, mediana (dias): fev", round(np.median(lags[True]), 1), "| outros meses", round(np.median(lags[False]), 1))
sems = [y * 10 + s for y in range(2006, 2019) for s in (1, 2)]
def bounds(s):
    y, h = divmod(s, 10); return (pd.Timestamp(y, 1, 1), pd.Timestamp(y, 7, 1)) if h == 1 else (pd.Timestamp(y, 7, 1), pd.Timestamp(y + 1, 1, 1))
U = x[~x["cov"]].groupby([x.dt.dt.normalize(), "fev"]).size()
M = {s: 0.0 for s in sems}
for (E, f), n in U.items():
    L = lags[f]; nL = len(L)
    for s in sems:
        a, b = bounds(s)
        if a >= E: continue
        lo = (E - min(b, E)).total_seconds() / 86400; hi = (E - a).total_seconds() / 86400   # defasagem em (lo, hi]
        M[s] += n * (np.searchsorted(L, hi, "right") - np.searchsorted(L, lo, "right")) / nL
cv = x[x["cov"]]; R = sem(cv.d_sol1).value_counts()
# --- (b) completude do desfecho, por semestre da 1a solicitacao
z = sp.set_index("id")[["d_sol1", "d_enc1", "d_mat1"]].join(first, how="left")
z = z[z.dt.notna() & (z.dt >= z.d_sol1) & (z.dt < EMAX)]
z["s"] = sem(z.d_sol1)
z["enc_ok"] = z.d_enc1.notna() & (z.d_enc1 <= z.dt + pd.Timedelta(days=60))
z["mat_ok"] = z.d_mat1.notna() & ((z.d_mat1 - z.dt).abs() <= pd.Timedelta(days=60))
ob = z.groupby("s").agg(N_out=("enc_ok", "size"), enc_ok=("enc_ok", "mean"), mat_ok=("mat_ok", "mean"))
rows = []
for s in [y * 10 + h for y in range(2010, 2019) for h in (1, 2)]:
    r_ = float(R.get(s, 0)); m_ = M[s]
    rows.append(dict(semestre=f"{s // 10}S{s % 10}", R_registradas_que_entraram=int(r_), M_ausentes_estimadas=round(m_),
                     completude_solicitacao=round(100 * r_ / (r_ + m_), 1) if r_ + m_ else np.nan,
                     N_desfecho=int(ob.N_out.get(s, 0)), enc_registrado=round(100 * ob.enc_ok.get(s, np.nan), 1), mat_registrada=round(100 * ob.mat_ok.get(s, np.nan), 1)))
C = pd.DataFrame(rows)
ref = C[C.semestre.str[:4].astype(int).between(2014, 2016)]
thr_a = ref.completude_solicitacao.mean() - 2; thr_b = ref.enc_registrado.mean() - 2
C["completo"] = (C.completude_solicitacao >= thr_a) & (C.enc_registrado >= thr_b)
print(f"\nlimiar (a) {thr_a:.1f}  (b) {thr_b:.1f}  (media 2014S1-2016S2 menos 2 p.p.)")
print(C.to_string(index=False)); save(C, "c2_completude_semestre.csv")
ok = C.completo.values; start = next(i for i in range(len(ok)) if ok[i:].all() or ok[i:-3].all())
print("primeiro semestre a partir do qual todos sao completos (ignorando 2017S2-2018S2, cortados pelo fim do EOL):", C.semestre[start])
# sensibilidade de (a) a defasagem: so entrantes de 2014 / so de 2016-2017
for lo_, hi_ in (("2014-01-01", "2015-01-01"), ("2016-01-01", "2018-01-01")):
    b2 = x[x["cov"] & (x.dt >= lo_) & (x.dt < hi_)]; L2 = {f: np.sort((g.dt - g.d_sol1).dt.total_seconds().values / 86400) for f, g in b2.groupby("fev")}
    out = []
    for s in (20111, 20112, 20121, 20122, 20131, 20132):
        a, b = bounds(s); m_ = 0.0
        for (E, f), n in U.items():
            if a >= E: continue
            L = L2[f]; lo = (E - min(b, E)).total_seconds() / 86400; hi = (E - a).total_seconds() / 86400
            m_ += n * (np.searchsorted(L, hi, "right") - np.searchsorted(L, lo, "right")) / len(L)
        r_ = float(R.get(s, 0)); out.append(f"{s // 10}S{s % 10}: {100 * r_ / (r_ + m_):.1f}")
    print(f"sensibilidade, defasagem dos entrantes {lo_[:4]}-{int(hi_[:4]) - 1}:", " | ".join(out))
# entrantes de 2012 no registro: a solicitacao antecede a entrada?
g12 = x[(x.dt.dt.year == 2012)]
for f, g in g12.groupby("fev"):
    print(f"entrantes 2012 {'fev' if f else 'outros meses'}: N={len(g):,} | no registro {100 * g.d_sol1.notna().mean():.1f}% | solicitacao antes da entrada {100 * g['cov'].mean():.1f}%")
