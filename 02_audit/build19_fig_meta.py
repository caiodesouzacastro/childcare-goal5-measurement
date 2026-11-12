# -*- coding: utf-8 -*-
# SAIDA C (26/10/2026): figura candidata do paper. TRIAGEM (26/10): sem nota embutida, titulos alinhados ao texto, rotulo do limiar deslocado. "Demanda atendida" de creche (formula inferida, que reproduz 6 dos 8
# valores da Conferencia 2023) por ano, medida em marco, junho, setembro e dezembro; linha do criterio de 75% usado pela
# Conferencia. Painel B: estoque publicado nos mesmos meses (escala log). Preto e branco. Descritivo.
# Entrada: 03_build/build19/nucleo_C_meta.csv. Saida: 03_build/build19/fig_meta5_mes.pdf/.png
# figs-geradores-1 (09/11/2026, pedido do autor): rotulo de painel so com a letra, no canto superior esquerdo do painel, e titulo descritivo fora da imagem (OUP); a chave fica; "enrolment" nos eixos. Versao anterior em build19_fig_meta.py.bak-2026-11-09-figs-geradores-1.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import os, sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT = (NE_ROOT + r"\03_build\build19")
C = pd.read_csv(os.path.join(OUT, "nucleo_C_meta.csv")); C = C[(C.ano >= 2007) & (C.ano <= 2022)]
Q = [(3, "March", "o", ":"), (6, "June", "s", "-."), (9, "September", "^", "--"), (12, "December", "D", "-")]
plt.rcParams.update({"font.size": 10, "font.family": "serif"})
fig, ax = plt.subplots(1, 2, figsize=(10, 4.2))
for m, lab, mk, ls in Q:
    d = C[C.mes == m]
    ax[0].plot(d.ano, d.atendida_pct, ls=ls, marker=mk, ms=4, color="black", mfc="white" if m != 12 else "black", lw=1.1, label=lab)
    ax[1].plot(d.ano, d.dem_total / 1000, ls=ls, marker=mk, ms=4, color="black", mfc="white" if m != 12 else "black", lw=1.1, label=lab)
ax[0].axhline(75, color="gray", lw=0.8); ax[0].text(2007.2, 76.5, "75% threshold (2023 review)", fontsize=8, color="gray")  # tentativa 4 (FUSAO, autorizada): rotulo curto, termina antes do marcador de dez./2015
ax[0].axvspan(2014.5, 2017.5, color="0.9", zorder=0)
ax[0].set_ylabel("Enrolment / (enrolment + registered demand), %")
ax[1].set_yscale("log"); ax[1].set_ylabel("Registered demand (thousands, log scale)")
for a in ax: a.set_xticks(range(2007, 2023, 3)); a.set_xlabel("Year"); a.spines[["top", "right"]].set_visible(False)
ax[0].legend(frameon=False, fontsize=8, loc="lower right")
fig.tight_layout()
bb = [a.get_tightbbox().transformed(fig.transFigure.inverted()) for a in ax]; y = max(b.y1 for b in bb)  # figs-geradores-1: letra no canto superior esquerdo de cada painel (borda esquerda do rotulo do eixo y), as duas na mesma altura, acima do painel mais alto
for b, l in zip(bb, "AB"): fig.text(b.x0, y, l, fontsize=10, fontweight="bold", ha="left", va="bottom")
for ext in ("pdf", "png"):
    p = os.path.join(OUT, f"fig_meta5_mes.{ext}"); fig.savefig(p, dpi=150, bbox_inches="tight"); assert os.path.getsize(p) > 0; print("[gravado]", p)
