# -*- coding: utf-8 -*-
# Etapa 6 (26/10/2026): regenera F6 e F7 do apendice com os MESMOS dados do build03_tex.py (03_build/build03/_staging),
# corrigindo o que a revisao (REVIEW_V2, agentes 1 e 5) apontou: legenda errada da F7 ("Population aged 0-3" para uma
# soma de nascidos vivos), titulos dentro do grafico duplicando a legenda, series so distinguiveis por cor, hifen em
# intervalo. Nenhum valor muda. Saida: 04_paper/assets/figures/F6_solicitacao_precoce.pdf, F7_capacidade_pool.pdf
# (o .bak-2026-10-26-e6 dos PDFs anteriores fica ao lado).
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import os, shutil, pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = NE_ROOT; STG = os.path.join(R, r"03_build\build03\_staging"); FIG = os.path.join(R, r"04_paper\assets\figures")
plt.rcParams.update({"font.family": "serif", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
def save(fig, name):
    p = os.path.join(FIG, name)
    if not os.path.exists(p + ".bak-2026-10-26-e6"): shutil.copy2(p, p + ".bak-2026-10-26-e6")
    fig.savefig(p); plt.close(fig); print("ok", name, os.path.getsize(p))
d = pd.read_csv(os.path.join(STG, "S2a_frac_0_24.csv"))
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.plot(d.coorte_nasc, d.frac_ate12m, "-o", color="black", label="Applied before 12 months")
ax.plot(d.coorte_nasc, d.frac_ate24m, "--s", color="0.45", mfc="white", label="Applied before 24 months")
ax.set_xlabel("Birth cohort"); ax.set_ylabel("Percent of the birth cohort (live births)")
ax.set_xticks(range(2010, 2017)); ax.legend(frameon=False); ax.grid(axis="y", color="0.9"); fig.tight_layout()
save(fig, "F6_solicitacao_precoce.pdf")
d = pd.read_csv(os.path.join(STG, "S6c_cobertura.csv"))
fig, ax = plt.subplots(figsize=(6.5, 4))
ax.plot(d.ano, d.capacidade_mun / 1000, "-o", color="black", label="Authorized places")
ax.plot(d.ano, d.pool_0_3_mun / 1000, "--s", color="0.45", mfc="white", label="Eligible pool (live births, current and three preceding years)")
ax.set_xlabel("Year"); ax.set_ylabel("Thousands"); ax.set_xticks(range(2013, 2020))
ax.legend(frameon=False, loc="center right"); ax.grid(axis="y", color="0.9"); fig.tight_layout()
save(fig, "F7_capacidade_pool.pdf")
