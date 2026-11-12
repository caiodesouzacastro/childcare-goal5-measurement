# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import os, sys, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
R = NE_ROOT
sp = pd.read_parquet(os.path.join(R, r"03_build\build10\_staging\spine.parquet"), columns=["d_enc1", "d_mat1", "d_sol1"])
for y0, y1 in ((2011, 2017), (2013, 2017)):
    res = {}
    for v in ("d_sol1", "d_enc1", "d_mat1"):
        d = pd.to_datetime(sp[v]).dropna(); d = d[(d.dt.year >= y0) & (d.dt.year <= y1)]
        s = d.dt.month.value_counts(normalize=True)
        res[v] = dict(dez=round(100 * s.get(12, 0), 1), janfev=round(100 * (s.get(1, 0) + s.get(2, 0)), 1), N=len(d))
    print(y0, y1, res)
