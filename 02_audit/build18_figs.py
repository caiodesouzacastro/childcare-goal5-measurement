# -*- coding: utf-8 -*-
# MANHA, etapa 1.5 (26/10/2026): figuras do corpo com a janela a partir de jul./2012. So le saidas ja geradas:
#   V2_coverage.tex (Paineis A e B), build17_fatais/c2_completude_semestre.csv, build14_cobertura/janela_cif.csv,
#   build18/nivel_corrigido.csv. Preto e branco, como build16_figs.py: series por marcador e estilo de linha.
# Saidas: 04_paper/assets/figures/V3_fig_coverage.pdf, V3_fig_naive.pdf (refeita, fora do corpo), V3_fig_level.pdf; PNGs em 03_build/build18
# figs-geradores-1 (09/11/2026, pedido do autor): rotulo de painel so com a letra, no canto superior esquerdo do painel, e titulo descritivo fora da imagem (OUP); a chave fica; "enrolment" nos eixos. Versao anterior em build18_figs.py.bak-2026-11-09-figs-geradores-1.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import os, re, sys, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; FIG = os.path.join(ROOT, r"04_paper\assets\figures"); OUT = os.path.join(ROOT, r"03_build\build18")
plt.rcParams.update({"font.family": "serif", "font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6, "legend.frameon": False, "pdf.fonttype": 42})
INK, MID, LIGHT = "#000000", "#555555", "#e6e6e6"
t = open(os.path.join(ROOT, r"04_paper\assets\tables\v2\V2_coverage.tex"), encoding="utf-8").read()
pA, pB = t.split("Panel B.")
def rows(s): return [[c.strip().rstrip("\\").strip() for c in l.split("&")] for l in s.splitlines() if re.match(r"^\s*20\d\d\s*&", l)]
A = pd.DataFrame([[int(r[0]), float(r[2]), float(r[3]), (float(r[4]) if r[4] != "--" else None)] for r in rows(pA)], columns=["ano", "todos", "fev", "outros"])
B = pd.DataFrame([[int(r[0]), float(r[1]), float(r[2])] for r in rows(pB)], columns=["coorte", "fila", "eol"])
S = pd.read_csv(os.path.join(ROOT, r"03_build\build17_fatais\c2_completude_semestre.csv")); S = S[S.semestre <= "2017S2"].reset_index(drop=True)
S["x"] = S.semestre.str[:4].astype(int) + (S.semestre.str[-1] == "2") * 0.5
ref = S[S.semestre.str[:4].astype(int).between(2014, 2016)]; thr = ref.completude_solicitacao.mean() - 2
C = pd.read_csv(os.path.join(ROOT, r"03_build\build14_cobertura\janela_cif.csv")); C = C[C.serie == "coorte"].copy(); C["coorte"] = C.grupo.astype(int)
L = pd.read_csv(os.path.join(OUT, "nivel_corrigido.csv"))
for d, n in ((A, "fig_A"), (S, "fig_S"), (B, "fig_B"), (C, "fig_C"), (L, "fig_L")): d.to_csv(os.path.join(OUT, n + ".csv"), index=False)
def shade(ax, x0, x1, label, y):
    ax.axvspan(x0, x1, color=LIGHT, zorder=0, lw=0); ax.text((x0 + x1) / 2, y, label, ha="center", va="top", fontsize=7, color=MID, style="italic")
def grid(ax): ax.grid(axis="y", color="#d0d0d0", lw=0.4); ax.set_axisbelow(True)
def letras(pares, fs):  # figs-geradores-1: letra no canto superior esquerdo de cada painel (borda esquerda do rotulo do eixo y), todas na mesma altura, acima do painel mais alto
    fig = pares[0][0].figure; bb = [ax.get_tightbbox().transformed(fig.transFigure.inverted()) for ax, _ in pares]; y = max(b.y1 for b in bb)
    for (ax, l), b in zip(pares, bb): fig.text(b.x0, y, l, fontsize=fs, fontweight="bold", ha="left", va="bottom")
# ---------- Figura 1: cobertura, tres paineis ----------
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(7.4, 2.75), gridspec_kw=dict(wspace=0.45))
shade(a1, 2009.6, 2012.5, "incomplete", 90)
a1.plot(A.ano, A.todos, color=INK, lw=1.4, marker="o", ms=4, label="All entrants")
f = A[A.ano >= 2012]
a1.plot(f.ano, f.fev, color=INK, lw=1.1, ls="--", marker="s", ms=4, mfc="white", label="February")
a1.plot(f.ano, f.outros, color=MID, lw=1.1, ls=":", marker="^", ms=4, mfc="white", label="Other months")
a1.set_ylim(30, 102); a1.set_xlim(2009.6, 2018.4); a1.set_xticks(range(2010, 2019, 2))
a1.set_xlabel("Year of first childcare enrolment"); a1.set_ylabel("Entrants found in the record (%)")
a1.legend(loc="lower right", fontsize=6.6, handlelength=2.2)
shade(a2, 2009.85, 2012.35, "incomplete", 16)
a2.axhline(thr, color=MID, lw=0.7, ls="--"); a2.text(2017.9, thr - 2.5, f"rule: {thr:.1f}", ha="right", va="top", fontsize=6.6, color=MID)
a2.plot(S.x, S.completude_solicitacao, color=INK, lw=1.4, marker="o", ms=3.6)
a2.set_ylim(10, 102); a2.set_xlim(2009.85, 2018.1); a2.set_xticks(range(2010, 2019, 2))
a2.set_xlabel("Semester of first application"); a2.set_ylabel("Completeness of requests (%)")
shade(a3, 2009.6, 2011.5, "incomplete", 4)
a3.plot(B.coorte, B.eol, color=INK, lw=1.1, ls="--", marker="s", ms=4, mfc="white", label="Enrolment records")
a3.plot(B.coorte, B.fila, color=INK, lw=1.4, marker="o", ms=4, label="Request record")
a3.set_ylim(0, 60); a3.set_xlim(2009.6, 2016.4); a3.set_xticks(range(2010, 2017, 2))
a3.set_xlabel("Birth cohort"); a3.set_ylabel("Enrolled before 24 months (% of births)")
a3.legend(loc="upper left", fontsize=6.6, handlelength=2.4)
for ax in (a1, a2, a3): grid(ax)
letras(((a1, "A"), (a2, "B"), (a3, "C")), 8.2)
fig.savefig(os.path.join(FIG, "V3_fig_coverage.pdf"), bbox_inches="tight"); fig.savefig(os.path.join(OUT, "V3_fig_coverage.png"), dpi=170, bbox_inches="tight"); plt.close(fig)
# ---------- Figura 2 refeita: extrato completo x janela (2012-2016) ----------
fig, ax = plt.subplots(figsize=(5.2, 3.0))
shade(ax, 2009.6, 2011.5, "incomplete\ncoverage", 0.935)
ax.plot(C.coorte, C.ref365, color=MID, lw=1.1, ls="--", marker="o", ms=4.5, mfc="white", label="Full extract, 2010–2016")
cl = C[C.coorte >= 2012]
ax.plot(cl.coorte, cl.ref365, color=INK, lw=1.8, marker="o", ms=5, label="Window of complete coverage, 2012–2016")
v10, v12, v16 = (float(C.set_index("coorte").ref365[k]) for k in (2010, 2012, 2016))
def bracket(x, y0, y1, txt):
    ax.annotate("", xy=(x, y1), xytext=(x, y0), arrowprops=dict(arrowstyle="-", lw=0.8, color=INK, shrinkA=0, shrinkB=0))
    for y in (y0, y1): ax.plot([x - 0.06, x], [y, y], color=INK, lw=0.8)
    ax.text(x + 0.1, (y0 + y1) / 2, txt, va="center", fontsize=7.5)
ax.plot([2010, 2016.3], [v10, v10], color=MID, lw=0.5, ls=":"); ax.plot([2012, 2017.25], [v12, v12], color=INK, lw=0.5, ls=":")
ax.plot([2016, 2017.25], [v16, v16], color=INK, lw=0.5, ls=":")
bracket(2016.3, v10, v16, f"{v16 - v10:+.3f}\nfull extract"); bracket(2017.25, v12, v16, f"{v16 - v12:+.3f}\ncomplete\ncoverage")
ax.set_xlim(2009.6, 2018.4); ax.set_ylim(0.45, 0.95); ax.set_xticks(range(2010, 2017))
ax.set_xlabel("Birth cohort"); ax.set_ylabel("Probability of referral within one year")
ax.legend(loc="lower right", bbox_to_anchor=(0.86, 0.02), fontsize=7.2, handlelength=2.6); grid(ax)
fig.savefig(os.path.join(FIG, "V3_fig_naive.pdf"), bbox_inches="tight"); fig.savefig(os.path.join(OUT, "V3_fig_naive.png"), dpi=170, bbox_inches="tight"); plt.close(fig)
# ---------- Figura 2 alternativa: nivel observado e corrigido ----------
fig, (b1, b2) = plt.subplots(1, 2, figsize=(6.6, 2.8), gridspec_kw=dict(wspace=0.32))
P = []  # figs-geradores-1: paineis e letras da A2, desenhadas depois do laco
for ax, obs, lo, hi, r1, r2, yl, ttl, ylim, ytxt in (
        (b1, "ref_obs", "ref_inf", "ref_sup", "ref_R1", "ref_R2", "Probability of referral within one year", "A", (0.3, 0.95), 0.94),
        (b2, "reg12_obs", None, "reg12_sup", "reg12_R1", "reg12_R2", "Registered before 12 months (% of births)", "B", (0, 55), 54)):
    shade(ax, 2009.6, 2011.5, "incomplete\ncoverage", ytxt)
    lo_v = L[lo] if lo else L[obs]
    ax.vlines(L.coorte, lo_v, L[hi], color=MID, lw=0.8, zorder=2)
    for x, a, b in zip(L.coorte, lo_v, L[hi]):
        ax.plot([x - 0.08, x + 0.08], [a, a], color=MID, lw=0.8); ax.plot([x - 0.08, x + 0.08], [b, b], color=MID, lw=0.8)
    ax.vlines(L.coorte + 0.001, L[[r1, r2]].min(axis=1), L[[r1, r2]].max(axis=1), color=INK, lw=3.2, zorder=3)
    ax.plot(L.coorte, L[[r1, r2]].mean(axis=1), color=INK, lw=0, marker="D", ms=3.6, mfc="white", zorder=4, label="Corrected (two imputations)")
    ax.plot(L.coorte, L[obs], color=INK, lw=1.3, marker="o", ms=4.2, zorder=5, label="Observed")
    ax.plot([], [], color=MID, lw=0.8, label="Bounds" if lo else "Observed to maximum")
    ax.set_xlim(2009.6, 2016.4); ax.set_ylim(*ylim); ax.set_xticks(range(2010, 2017)); ax.tick_params(axis="x", labelsize=7.2, rotation=45)
    ax.set_xlabel("Birth cohort"); ax.set_ylabel(yl); grid(ax); P.append((ax, ttl))
    ax.legend(loc="lower right", fontsize=6.4, handlelength=2.0)
letras(P, 8.5)
fig.savefig(os.path.join(FIG, "V3_fig_level.pdf"), bbox_inches="tight"); fig.savefig(os.path.join(OUT, "V3_fig_level.png"), dpi=170, bbox_inches="tight"); plt.close(fig)
for n in ("V3_fig_coverage.pdf", "V3_fig_naive.pdf", "V3_fig_level.pdf"):
    p = os.path.join(FIG, n); assert os.path.getsize(p) > 5000, n; print("gravado:", p, os.path.getsize(p))
