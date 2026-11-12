# -*- coding: utf-8 -*-
# NOITE (26/10/2026), etapa 1: figuras do corpo sob a tese da cobertura. So le saidas ja geradas:
#   - 04_paper/assets/tables/v2/V2_coverage.tex (Paineis A e B, gerados por build15_tables.py)
#   - 03_build/build14_cobertura/janela_cif.csv (encaminhamento em 1 ano por coorte; validado contra a Tabela 1)
# Preto e branco: series distinguidas por marcador e estilo de linha, nunca por cor; rotulos diretos + legenda.
# Saidas: 04_paper/assets/figures/V2_fig_coverage.pdf, V2_fig_naive.pdf; 03_build/build16/fig_dados.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import os, re, sys, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; FIG = os.path.join(ROOT, r"04_paper\assets\figures"); OUT = os.path.join(ROOT, r"03_build\build16"); os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "serif", "font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6, "legend.frameon": False, "pdf.fonttype": 42})
INK, MID, LIGHT = "#000000", "#555555", "#e6e6e6"
# ---------- dados ----------
t = open(os.path.join(ROOT, r"04_paper\assets\tables\v2\V2_coverage.tex"), encoding="utf-8").read()
pA, pB = t.split("Panel B.")
def rows(s): return [[c.strip().rstrip("\\").strip() for c in l.split("&")] for l in s.splitlines() if re.match(r"^\s*20\d\d\s*&", l)]
A = pd.DataFrame([[int(r[0]), float(r[2]), float(r[3]), (float(r[4]) if r[4] != "--" else None)] for r in rows(pA)], columns=["ano", "todos", "fev", "outros"])
B = pd.DataFrame([[int(r[0]), float(r[1]), float(r[2])] for r in rows(pB)], columns=["coorte", "fila", "eol"])
C = pd.read_csv(os.path.join(ROOT, r"03_build\build14_cobertura\janela_cif.csv")); C = C[C.serie == "coorte"].copy(); C["coorte"] = C.grupo.astype(int)
A.to_csv(os.path.join(OUT, "fig1A.csv"), index=False); B.to_csv(os.path.join(OUT, "fig1B.csv"), index=False); C[["coorte", "N", "ref365"]].to_csv(os.path.join(OUT, "fig2.csv"), index=False)
print(A.to_string(index=False)); print(B.to_string(index=False)); print(C[["coorte", "ref365"]].to_string(index=False))
def shade(ax, x0, x1, label, y):
    ax.axvspan(x0, x1, color=LIGHT, zorder=0, lw=0); ax.text((x0 + x1) / 2, y, label, ha="center", va="top", fontsize=7.5, color=MID, style="italic")
# ---------- Figura 1: cobertura ----------
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.5, 2.8), gridspec_kw=dict(wspace=0.32))
shade(a1, 2009.6, 2012.5, "incomplete\ncoverage", 92)
a1.plot(A.ano, A.todos, color=INK, lw=1.4, marker="o", ms=4.5, label="All entrants")
f = A[A.ano >= 2012]
a1.plot(f.ano, f.fev, color=INK, lw=1.1, ls="--", marker="s", ms=4.5, mfc="white", label="February")
a1.plot(f.ano, f.outros, color=MID, lw=1.1, ls=":", marker="^", ms=4.5, mfc="white", label="Other months")
a1.set_ylim(30, 102); a1.set_xlim(2009.6, 2018.4); a1.set_xticks(range(2010, 2019)); a1.tick_params(axis="x", labelsize=7.2, rotation=45)
a1.set_xlabel("Year of first childcare enrollment"); a1.set_ylabel("Entrants found in the request record (%)")
a1.set_title("A. Coverage of entrants, by year", loc="left", fontsize=8.5)
a1.legend(loc="lower right", bbox_to_anchor=(1.0, 0.04), fontsize=7.2, handlelength=2.4)
shade(a2, 2009.6, 2012.5, "incomplete\ncoverage", 58)
a2.plot(B.coorte, B.eol, color=INK, lw=1.1, ls="--", marker="s", ms=4.5, mfc="white", label="Enrollment records")
a2.plot(B.coorte, B.fila, color=INK, lw=1.4, marker="o", ms=4.5, label="Request record")
a2.set_ylim(0, 60); a2.set_xlim(2009.6, 2016.4); a2.set_xticks(range(2010, 2017)); a2.tick_params(axis="x", labelsize=7.2, rotation=45)
a2.set_xlabel("Birth cohort"); a2.set_ylabel("Enrolled before 24 months (% of live births)")
a2.set_title("B. The same cohort statistic from two records", loc="left", fontsize=8.5)
a2.legend(loc="lower right", fontsize=7.2, handlelength=2.6)
for ax in (a1, a2): ax.grid(axis="y", color="#d0d0d0", lw=0.4); ax.set_axisbelow(True)
fig.savefig(os.path.join(FIG, "V2_fig_coverage.pdf"), bbox_inches="tight"); fig.savefig(os.path.join(OUT, "V2_fig_coverage.png"), dpi=170, bbox_inches="tight"); plt.close(fig)
# ---------- Figura 2: extrato completo x janela limpa ----------
fig, ax = plt.subplots(figsize=(5.2, 3.0))
shade(ax, 2009.6, 2012.5, "incomplete\ncoverage", 0.935)
ax.plot(C.coorte, C.ref365, color=MID, lw=1.1, ls="--", marker="o", ms=4.5, mfc="white", label="Full extract, 2010–2016")
cl = C[C.coorte >= 2013]
ax.plot(cl.coorte, cl.ref365, color=INK, lw=1.8, marker="o", ms=5, label="Window of complete coverage, 2013–2016")
v10, v13, v16 = (float(C.set_index("coorte").ref365[k]) for k in (2010, 2013, 2016))
def bracket(x, y0, y1, txt):
    ax.annotate("", xy=(x, y1), xytext=(x, y0), arrowprops=dict(arrowstyle="-", lw=0.8, color=INK, shrinkA=0, shrinkB=0))
    for y in (y0, y1): ax.plot([x - 0.06, x], [y, y], color=INK, lw=0.8)
    ax.text(x + 0.1, (y0 + y1) / 2, txt, va="center", fontsize=7.5)
ax.plot([2010, 2016.35], [v10, v10], color=MID, lw=0.5, ls=":"); ax.plot([2013, 2016.85], [v13, v13], color=INK, lw=0.5, ls=":")
ax.plot([2016, 2016.85], [v16, v16], color=INK, lw=0.5, ls=":")
bracket(2016.35, v10, v16, f"{v16 - v10:+.3f}\nfull extract".replace("+", "+")); bracket(2016.85, v13, v16, f"{v16 - v13:+.3f}\ncomplete\ncoverage")
ax.set_xlim(2009.6, 2018.0); ax.set_ylim(0.45, 0.95); ax.set_xticks(range(2010, 2017))
ax.set_xlabel("Birth cohort"); ax.set_ylabel("Probability of referral within one year")
ax.legend(loc="lower right", bbox_to_anchor=(0.86, 0.02), fontsize=7.2, handlelength=2.6)
ax.grid(axis="y", color="#d0d0d0", lw=0.4); ax.set_axisbelow(True)
fig.savefig(os.path.join(FIG, "V2_fig_naive.pdf"), bbox_inches="tight"); fig.savefig(os.path.join(OUT, "V2_fig_naive.png"), dpi=170, bbox_inches="tight"); plt.close(fig)
print("ok: V2_fig_coverage.pdf, V2_fig_naive.pdf")
