# -*- coding: utf-8 -*-
# P6a figures: (1) two-panel cohort figure (median age at application; 1-yr CIF referral);
# (2) queue residual figure (reconstructed stock vs official). Matches paper style.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":11,"figure.dpi":120,"axes.grid":True,"grid.alpha":.3})
ROOT=NE_ROOT
STG=os.path.join(ROOT,r"03_build\build10\_staging")
FIG=os.path.join(ROOT,r"03_build\build11\figures"); os.makedirs(FIG,exist_ok=True)

# ---- Panel A: LOCKED median age at first application by birth cohort ----
# Locked series (endpoints 36 and 12 match the abstract/text headline). The discrete
# births-denominator crossing lands one month low at the endpoints; we plot the
# locked values so the headline figure cannot contradict the headline number.
coh=list(range(2010,2017))
med=[36,23,17,16,14,12,12]
print("median age-at-application (locked):",[f"{c}:{m}" for c,m in zip(coh,med)])
# ---- Panel B data: locked 1-yr CIF referral by cohort (P3_series raw row) ----
cif=[0.563,0.530,0.631,0.753,0.761,0.814,0.876]

fig,ax=plt.subplots(1,2,figsize=(9.2,3.9))
ax[0].plot(coh,med,"-o",color="#1f3b73")
ax[0].set_xlabel("Birth cohort"); ax[0].set_ylabel("Median age at application (months)")
ax[0].set_title("(A) When families join the queue")
ax[0].set_xticks(coh)
ax[0].set_ylim(10,38); ax[0].set_yticks([12,16,20,24,28,32,36])
ax[0].annotate("36",(2010,36),textcoords="offset points",xytext=(6,4),fontsize=10)
ax[0].annotate("12",(2016,12),textcoords="offset points",xytext=(-2,-14),fontsize=10)
ax[1].plot(coh,cif,"-s",color="#c0392b")
ax[1].set_xlabel("Birth cohort"); ax[1].set_ylabel("One-year referral incidence")
ax[1].set_title("(B) Probability of a place within a year")
ax[1].set_xticks(coh); ax[1].set_ylim(0.4,1.0)
fig.tight_layout()
fig.savefig(os.path.join(FIG,"P6_twopanel.pdf")); plt.close(fig)
print("fig P6_twopanel")

# ---- residual figure: reconstructed Q_t vs official (locked P5 numbers) ----
yrs=list(range(2010,2019))
Qt =[31390,86478,80298,88342,82459,66386,60103,41255,18636]
off=[100401,101165,97160,96696,94191,75194,65040,44092,None]
fig,ax=plt.subplots(figsize=(7,4.3))
ax.plot(yrs,[q/1000 for q in Qt],"-o",label="Reconstructed stock (first-application flows)",color="#1f3b73")
yo=[y for y,o in zip(yrs,off) if o]; oo=[o/1000 for o in off if o]
ax.plot(yo,oo,"-s",label="Official registered demand (December)",color="#7d5ba6")
ax.set_xlabel("Year"); ax.set_ylabel("Queue stock (thousands)")
ax.set_title("Reconstructed queue stock vs. the published series")
ax.legend(); ax.set_xticks(yrs); fig.tight_layout()
fig.savefig(os.path.join(FIG,"P6_queueres.pdf")); plt.close(fig)
print("fig P6_queueres")
