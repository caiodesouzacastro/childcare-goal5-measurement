# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# MANHA, etapa 2 (26/10/2026): verificacoes para a SAIDA C (o indicador da Meta 5 do PME). Descritivo.
# (1) Serie publicada (T12_sazonalidade.tex, dados abertos PMSP): queda setembro -> dezembro no mesmo ano, por ano, e
#     variacao entre anos medida em cada mes de referencia (serie completa 2006-2017 e anos 2013-2017).
# (2) Mesmo exercicio com o estoque reconstruido do registro de solicitacoes (spine): criancas com 1a solicitacao ate a data,
#     ainda sem encaminhamento, sem aging out e sem desistencia registrada, em 30/set e 31/dez de 2010-2018.
# Saidas: 03_build/build18/saidaC_publicado.csv, saidaC_reconstruido.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, re, numpy as np, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; OUT = os.path.join(ROOT, r"03_build\build18")
pd.set_option("display.width", 220)
def save(df, n):
    p = os.path.join(OUT, n); df.to_csv(p, index=False); assert len(pd.read_csv(p)) == len(df); print("[gravado e relido]", p)
s = open(os.path.join(ROOT, r"04_paper\assets\tables\T12_sazonalidade.tex"), encoding="utf-8").read()
rows = [[c.strip().rstrip("\\").strip().replace(",", "") for c in l.split("&")] for l in s.splitlines() if re.match(r"^\s*20\d\d\s*&", l)]
P = pd.DataFrame([[int(r[0])] + [float(x) if x not in ("--", "") else np.nan for x in r[1:5]] for r in rows], columns=["ano", "mar", "jun", "set", "dez"])
P["queda_set_dez_pct"] = (100 * (P.set - P.dez) / P.set).round(1); P["dez_sobre_set_pct"] = (100 * P.dez / P.set).round(0)
P["pico_sobre_vale"] = (P[["mar", "jun", "set", "dez"]].max(axis=1) / P[["mar", "jun", "set", "dez"]].min(axis=1)).round(2)
print(P.to_string(index=False)); save(P, "saidaC_publicado.csv")
def var(a, b):
    x, y = P.set_index("ano").loc[a], P.set_index("ano").loc[b]
    return {m: round(100 * (y[m] - x[m]) / x[m], 0) for m in ("mar", "jun", "set", "dez")}
for a, b in ((2013, 2017), (2007, 2017), (2010, 2017), (2013, 2016), (2014, 2017)):
    print(f"variacao {a}->{b} (%), por mes de referencia:", var(a, b))
w = P[P.ano.between(2013, 2017)]
print(f"queda set->dez no mesmo ano, 2013-2017: de {w.queda_set_dez_pct.min()} a {w.queda_set_dez_pct.max()}% (media {w.queda_set_dez_pct.mean():.1f}); "
      f"serie completa 2007-2017: de {P[P.ano >= 2007].queda_set_dez_pct.min()} a {P[P.ano >= 2007].queda_set_dez_pct.max()}%")
# (2) reconstruido do registro
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"), columns=["d_sol1", "d_enc1", "d_age47", "d_des1"])
R = []
for y in range(2010, 2019):
    r = dict(ano=y)
    for lab, t in (("set", pd.Timestamp(y, 9, 30, 23, 59, 59)), ("dez", pd.Timestamp(y, 12, 31, 23, 59, 59))):
        q = (sp.d_sol1 <= t) & ~(sp.d_enc1 <= t) & (sp.d_age47 > t) & ~(sp.d_des1 <= t)
        r[lab] = int(q.sum())
    r["queda_set_dez_pct"] = round(100 * (r["set"] - r["dez"]) / r["set"], 1); R.append(r)
R = pd.DataFrame(R); print(R.to_string(index=False)); save(R, "saidaC_reconstruido.csv")
rr = R.set_index("ano")
for a, b in ((2013, 2017), (2013, 2018)):
    print(f"reconstruido {a}->{b}: set {100 * (rr.set[b] - rr.set[a]) / rr.set[a]:+.0f}% | dez {100 * (rr.dez[b] - rr.dez[a]) / rr.dez[a]:+.0f}%")
