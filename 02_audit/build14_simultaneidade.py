# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import os, sys, numpy as np, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
R = NE_ROOT; O = os.path.join(R, r"03_build\build14_cobertura")
e = pd.read_parquet(os.path.join(O, "eol_creche.parquet"), columns=["CD_ALUNO_SME", "AN_LETIVO", "DT_IN_MAT", "CD_UNIDADE_EDUCACAO", "TIPO_ESCOLA"])
e["id"] = pd.to_numeric(e.CD_ALUNO_SME, errors="coerce").astype("Int64"); e["an"] = pd.to_numeric(e.AN_LETIVO); e["dt"] = pd.to_datetime(e.DT_IN_MAT.str[:10], errors="coerce")
f = e.sort_values(["id", "an", "dt"]).groupby("id").first()
sp = pd.read_parquet(os.path.join(R, r"03_build\build10\_staging\spine.parquet"), columns=["cd_aluno_sme"])
ids = set(pd.to_numeric(sp.cd_aluno_sme, errors="coerce").astype("Int64"))
f["cob"] = f.index.isin(ids); f["fev"] = f.dt.dt.month == 2; f["ano"] = f.an.astype(int)
g = f[f.fev & f.ano.between(2011, 2014)]
t = g.groupby(["TIPO_ESCOLA", "ano"]).cob.agg(["size", "mean"]).unstack("ano")
t = t[t[("size", 2012)] >= 200]; print("Cobertura das entradas de FEVEREIRO por tipo de escola (%; tipos com >=200 entradas em fev/2012):")
print((100 * t["mean"]).round(1).join(t["size"].add_prefix("N_")).to_string())
u = g.groupby(["CD_UNIDADE_EDUCACAO", "ano"]).cob.agg(["size", "mean"]).unstack("ano")
for y in (2011, 2012, 2013):
    s = u[u[("size", y)] >= 20][("mean", y)]
    print(f"{y}: unidades com >=20 entradas em fev: {len(s)} | cobertura >=90%: {100 * (s >= .9).mean():.1f}% das unidades | <=10%: {100 * (s <= .1).mean():.1f}% | p10/p50/p90 = {s.quantile(.1):.2f}/{s.median():.2f}/{s.quantile(.9):.2f}")
both = u[(u[("size", 2012)] >= 20) & (u[("size", 2013)] >= 20)]
print("unidades com >=20 em fev/2012 e fev/2013:", len(both), "| cobertura subiu >=30 pontos de 2012 para 2013:", f"{100 * ((both[('mean', 2013)] - both[('mean', 2012)]) >= .3).mean():.1f}%")
pd.DataFrame(t).to_csv(os.path.join(O, "cob_fev_tipo.csv"))
