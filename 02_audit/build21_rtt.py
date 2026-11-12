# -*- coding: utf-8 -*-
# FECHAMENTO C (26/10/2026): NHS England RTT, percent of incomplete pathways waiting under 18 weeks, monthly.
# Input: referee_EE_2026-10/fontes_saidaC/transfer/nhs_rtt/rtt_pct18_monthly.csv (built by build_rtt_series.py from the
# time-series tables printed in official RTT statistical press notices; see TRANSFER.md). Descriptive.
# Output: 03_build/build21/rtt.log (via tee), rtt_stats.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd
SRC = (NE_ROOT + r"\04_paper\referee_EE_2026-10\fontes_saidaC\transfer\nhs_rtt\rtt_pct18_monthly.csv")
OUT = (NE_ROOT + r"\03_build\build21"); os.makedirs(OUT, exist_ok=True)
d = pd.read_csv(SRC).sort_values("date"); d = d[d.date >= "2016-04-01"].reset_index(drop=True)
d["ch"] = d.pct_within_18wk.diff()
print("meses abr/2016-ago/2026:", len(d), "| primeiro", d.date.iloc[0], "ultimo", d.date.iloc[-1])
for lab, lo, hi in (("sem 2020-2021", "2020-01-01", "2021-12-31"), ("sem mar/2020-jun/2021", "2020-03-01", "2021-06-30")):
    x = d[~d.date.between(lo, hi)].dropna(subset=["ch"])
    r = x.ch.rank(ascending=False, method="min")
    i = x.index[x.date == "2026-03-01"][0]
    print(f"{lab}: variacoes mensais {len(x)}; media |var| {x.ch.abs().mean():.2f} p.p.; fev->mar/2026 {x.loc[i, 'ch']:+.1f} p.p., posto {int(r[i])}; "
          f"maiores: {x.sort_values('ch', ascending=False).head(3)[['date', 'ch']].values.tolist()}")
v = d.set_index("date").pct_within_18wk
print("fev/2026", v["2026-02-01"], "| mar/2026", v["2026-03-01"], "| abr-ago/2026", v["2026-04-01":"2026-08-01"].tolist())
fy = d[(d.date >= "2025-04-01") & (d.date <= "2026-03-01")]
print("ano fiscal abr/2025-mar/2026: media dos 11 meses antes de marco", round(fy[fy.date < "2026-03-01"].pct_within_18wk.mean(), 1),
      "| max antes de marco", fy[fy.date < "2026-03-01"].pct_within_18wk.max())
pd.DataFrame({"stat": ["fevmar2026_pp"], "valor": [round(v["2026-03-01"] - v["2026-02-01"], 1)]}).to_csv(os.path.join(OUT, "rtt_stats.csv"), index=False)
