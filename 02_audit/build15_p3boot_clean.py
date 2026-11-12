# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# GERADO por build15_make_p3boot.py a partir de build_p3boot.py (25/10/2026). Nao editar a mao.
# -*- coding: utf-8 -*-
# BLOCO F (revisao r1 / referee). Bootstrap do Delta padronizado 2010->2016 da CIF
# de referral em 365 dias (Aalen-Johansen, saida por idade = evento competitivo),
# reponderando cada coorte a composicao de SOLICITANTE de 2013.
#
# Reaproveita exatamente as definicoes de build_p3.py:
#   - mesma spine (build10/_staging/spine.parquet), mesmo PANEL,
#   - mesma celula principal: idade(bins 6/12/24/36) x prio x rq x distrito x semestre,
#   - mesmo alvo (coorte 2013), mesmo trimming de pesos (1o/99o percentil),
#   - mesma cif365 (aqui vetorizada; validada contra a estimativa pontual +0.387).
# A unica adicao e o bootstrap: reamostragem com reposicao DENTRO de cada coorte
# (2010, 2016 e tambem 2013, que fornece a composicao alvo), recalculando os pesos
# de padronizacao em cada replica.
#
# Saida: 03_build/build11/tables/P3_boot.tex  (label tab:P3boot)
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os, unicodedata, time

ROOT = os.environ.get("NE_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STG  = os.path.join(ROOT, r"03_build\build10\_staging")
OUT  = os.path.join(ROOT, r"03_build\build15"); os.makedirs(OUT, exist_ok=True)
CEPRENDA = os.path.join(os.environ.get("NE_DADOS_SME", os.path.join(ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")), r"processados\bases_analise\cep_renda_pop_2010.dta")

PANEL  = pd.Timestamp("2019-11-28")
SEED   = 20260726          # semente fixa, reportada na tabela e no texto
NREP   = 1000              # >= 500 exigidas
TRIM   = (1.0, 99.0)
COH    = [2013, 2016]
BASE   = 2013
TARGET = 2013

LOG = []
def S(x):
    LOG.append(str(x)); print(x, flush=True)

# ------------------------------------------------------------------ dados
S("carregando spine...")
sp = pd.read_parquet(os.path.join(STG, "spine.parquet"),
     columns=["d_sol1","d_enc1","d_age47","idade_sol","prio","rq","cep_aluno","ano_nasc"])
d = sp[sp.ano_nasc.isin(COH)].copy()
d["d_sol"]   = d["d_sol1"]
d["sem_sol"] = np.where(d.d_sol.dt.month <= 6, 1, 2)
d["cep_i"]   = pd.to_numeric(d.cep_aluno, errors="coerce")

def nz(s):
    return "".join(c for c in unicodedata.normalize("NFD", str(s).strip().upper())
                   if unicodedata.category(c) != "Mn")
rd = pd.read_stata(CEPRENDA, columns=["cep","nm_distrit"])
cep2d = {int(c): nz(x) for c, x in zip(rd.cep, rd.nm_distrit)}
d["distrito"] = d["cep_i"].map(cep2d)
S(f"  N={len(d):,} nas coortes {COH}. distrito ok={d.distrito.notna().mean():.2f}")

# celula PRINCIPAL de build_p3.py: idade(5 faixas) x prio x rq x distrito x semestre
abin = np.digitize(d.idade_sol.values, [6,12,24,36]).astype(str)
pcol = d.prio.fillna(0).astype(int).clip(0,1).astype(str).values
qcol = d.rq.fillna(0).astype(int).astype(str).values
dcol = d.distrito.fillna("NA").astype(str).values
scol = d.sem_sol.astype(str).values
cell = np.array(["|".join(t) for t in zip(abin, pcol, qcol, dcol, scol)])
codes, _ = pd.factorize(cell)
NCELL = int(codes.max()) + 1
S(f"  celulas distintas (3 coortes) = {NCELL:,}")

# tempo e tipo de evento, identicos a cif365() de build_p3.py
tr = np.where(d.d_enc1.notna(), (d.d_enc1 - d.d_sol).dt.days, np.inf).astype(float)
ta = (d.d_age47 - d.d_sol).dt.days.values.astype(float)
tp = (PANEL - d.d_sol).dt.days.values.astype(float)
time_all = np.minimum.reduce([np.where(np.isfinite(tr), tr, 1e9), ta, tp])
ev = np.zeros(len(d), int)
r1 = (tr <= np.minimum(ta, tp)) & np.isfinite(tr) & (tr >= 0)
a1 = (~r1) & (ta <= tp)
ev[r1] = 1; ev[a1] = 2
okv = np.isfinite(time_all) & (time_all >= 0)
S(f"  linhas com tempo valido (entram na CIF): {okv.sum():,} de {len(d):,}")
S("  (as demais permanecem no calculo das FREQUENCIAS de celula, como em build_p3.py,")
S("   onde os pesos sao construidos sobre a coorte inteira e a CIF descarta o invalido)")

coh_arr = d.ano_nasc.values

# ------------------------------- pre-computo por coorte, ordem de tempo fixa
class C: pass
CO = {}
for c in COH:
    m = (coh_arr == c)
    o = C()
    o.n   = int(m.sum())
    tk    = np.where(okv[m], time_all[m], np.inf)      # invalidos vao para o fim
    order = np.argsort(tk, kind="mergesort")
    o.ord = order
    o.t   = tk[order]
    o.k   = codes[m][order]
    okc   = okv[m][order]
    o.is1 = ((ev[m][order] == 1) & okc).astype(float)
    o.is2 = ((ev[m][order] == 2) & okc).astype(float)
    o.ok  = okc.astype(float)                          # invalidos: peso zerado na CIF
    uniq, starts = np.unique(o.t, return_index=True)
    o.uniq = uniq; o.starts = starts
    o.le365 = uniq <= 365
    CO[c] = o
    S(f"  coorte {c}: n={o.n:,}  validos={int(okc.sum()):,}  tempos distintos={len(uniq):,}  "
      f"referral={int(o.is1.sum()):,}  aging-out={int(o.is2.sum()):,}")

def cif365_w(o, w):
    """CIF de referral em 365d (Aalen--Johansen ponderado); w na ordem de o.t."""
    w = w * o.ok
    d1 = np.add.reduceat(w * o.is1, o.starts)
    d2 = np.add.reduceat(w * o.is2, o.starts)
    dl = np.add.reduceat(w,          o.starts)
    ar = dl.sum() - np.concatenate(([0.0], np.cumsum(dl)[:-1]))   # em risco antes de cada t
    good = ar > 0
    haz = np.zeros_like(ar); haz[good] = (d1[good] + d2[good]) / ar[good]
    Sp  = np.concatenate(([1.0], np.cumprod(1.0 - haz)[:-1]))
    sel = good & o.le365
    return float((Sp[sel] * d1[sel] / ar[sel]).sum())

def wpct(x, cnt, qs):
    """Percentis do vetor x replicado cnt vezes cada, com a interpolacao 'linear'
    do numpy. Com cnt==1 em todo lugar, reproduz np.percentile(x, qs) exatamente."""
    o  = np.argsort(x, kind="mergesort")
    xs = x[o]; cs = np.cumsum(cnt[o])
    N  = cs[-1]
    out = []
    for qq in qs:
        pos = (N - 1.0) * qq / 100.0
        il  = int(np.floor(pos)); ih = min(il + 1, int(N) - 1); fr = pos - il
        jl  = min(int(np.searchsorted(cs, il, side="right")), len(xs) - 1)
        jh  = min(int(np.searchsorted(cs, ih, side="right")), len(xs) - 1)
        out.append(xs[jl] * (1.0 - fr) + xs[jh] * fr)
    return out

def std_delta(counts):
    """Delta padronizado (2016-2010) reponderado a composicao de solicitante de 2013."""
    tr_ = np.bincount(CO[TARGET].k, weights=counts[TARGET], minlength=NCELL)
    tgt = tr_ / tr_.sum()
    vals = {}
    for c in (BASE, 2016):
        o = CO[c]; cnt = counts[c]
        fr_ = np.bincount(o.k, weights=cnt, minlength=NCELL)
        fre = fr_ / fr_.sum()
        wmap = np.zeros(NCELL)
        hit = (fre > 0) & (tgt > 0)
        wmap[hit] = tgt[hit] / fre[hit]
        wrow = wmap[o.k]
        keep = (wrow > 0) & (cnt > 0)        # celula presente em 2013 (senao: NaN -> dropado)
        lo, hi = wpct(wrow[keep], cnt[keep], TRIM)
        w = np.where(keep, np.clip(wrow, lo, hi) * cnt, 0.0)
        vals[c] = cif365_w(o, w)
    return vals[2016] - vals[BASE], vals

def raw_delta(counts):
    v = {c: cif365_w(CO[c], counts[c].astype(float)) for c in (BASE, 2016)}
    return v[2016] - v[BASE], v

# ------------------------------------------------------------ estimativa pontual
ones = {c: np.ones(CO[c].n) for c in COH}
d_std, v_std = std_delta(ones)
d_raw, v_raw = raw_delta(ones)
S("")
S("## estimativa pontual (contagens = 1; deve reproduzir build_p3.py)")
S(f"  Raw           : 2013={v_raw[BASE]:.3f} 2016={v_raw[2016]:.3f}  Delta={d_raw:+.4f}  (esperado +0.123 = 0.876-0.753, tab:P3series)")
S(f"  Applicant std : 2013={v_std[BASE]:.3f} 2016={v_std[2016]:.3f}  Delta={d_std:+.4f}  (esperado +0.132 = 0.885-0.753, tab:P3series)")
if abs(d_std - 0.132) > 0.002 or abs(d_raw - 0.123) > 0.002:
    S("  !! ATENCAO: estimativa pontual nao reproduz build_p3.py -- NAO usar o IC.")

# ------------------------------------------------------------------- bootstrap
rng = np.random.default_rng(SEED)
bs_std = np.empty(NREP); bs_raw = np.empty(NREP)
t0 = time.time()
for b in range(NREP):
    cnt = {}
    for c in COH:
        n = CO[c].n
        cnt[c] = np.bincount(rng.integers(0, n, size=n), minlength=n).astype(float)
    bs_std[b], _ = std_delta(cnt)
    bs_raw[b], _ = raw_delta(cnt)
    if (b + 1) % 50 == 0:
        el = time.time() - t0
        S(f"  rep {b+1}/{NREP}  ({el:.0f}s, {el/(b+1):.2f}s/rep)  media std={bs_std[:b+1].mean():+.4f}")

lo_s, hi_s = np.percentile(bs_std, [2.5, 97.5])
lo_r, hi_r = np.percentile(bs_raw, [2.5, 97.5])
se_s = bs_std.std(ddof=1); se_r = bs_raw.std(ddof=1)
S("")
S(f"## BOOTSTRAP  seed={SEED}  reps={NREP}")
S(f"  Raw           Delta={d_raw:+.4f}  se={se_r:.4f}  IC95=[{lo_r:+.4f}, {hi_r:+.4f}]")
S(f"  Applicant std Delta={d_std:+.4f}  se={se_s:.4f}  IC95=[{lo_s:+.4f}, {hi_s:+.4f}]")

np.savetxt(os.path.join(OUT, "P3_boot_reps_2013_2016.csv"),
           np.column_stack([bs_raw, bs_std]), delimiter=",",
           header="delta_raw,delta_applicant_std", comments="")

# --------------------------------------------------------------------- tabela
def f3(x): return f"{x:+.3f}"
rows = [
  ["Raw (unweighted)", f3(d_raw), f"{se_r:.3f}", f"[{f3(lo_r)}, {f3(hi_r)}]"],
  ["Applicant composition (2013 target)", f3(d_std), f"{se_s:.3f}", f"[{f3(lo_s)}, {f3(hi_s)}]"],
]
note = (
 "Bootstrap of the 2013--2016 change in the one-year cumulative incidence of referral "
 "(Aalen--Johansen, aging out of eligibility treated as a competing event), for the "
 "unweighted series and for the series reweighted to the 2013 cohort's joint distribution "
 "of applicant attributes---age at application, priority, postcode income quartile, "
 "district and semester of application. These are the first two rows of "
 f"Table~\\ref{{tab:P3series}}. {NREP} replications; children are resampled with "
 "replacement within each of the 2010 and 2016 cohorts and within the 2013 cohort, the "
 "last included because it supplies the target composition, and the standardization "
 "weights (including the 1st/99th percentile trimming) are recomputed in every "
 f"replication. Percentile interval; random seed {SEED}. The interval describes sampling "
 "variability in a reweighted descriptive difference; it is not a confidence interval for "
 "a causal quantity."
)
L = ["% BLOCO F (revisao r1). Bootstrap do Delta padronizado.",
     "\\begin{table}[htbp]\\centering",
     "\\caption{Bootstrap interval for the 2013--2016 change in one-year referral incidence}",
     "\\label{tab:P3boot}", "\\footnotesize", "\\setlength{\\tabcolsep}{6pt}",
     "\\begin{tabular}{lrrc}", "\\toprule",
     "Series & $\\Delta$ (2016$-$2013) & Bootstrap s.e. & 95\\% CI \\\\", "\\midrule"]
for r in rows: L.append(" & ".join(r) + " \\\\")
L += ["\\bottomrule", "\\end{tabular}",
      f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}", "\\end{table}"]
open(os.path.join(OUT, "P3_boot_2013_2016.tex"), "w", encoding="utf-8").write("\n".join(L) + "\n")
S("tex: P3_boot")

with open(os.path.join(OUT, "p3boot_2013_2016.log"), "w", encoding="utf-8") as f:
    f.write("\n".join(LOG))
S("\nOK P3 bootstrap")
