# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import pandas as pd, numpy as np, sys, os
sys.stdout.reconfigure(encoding="utf-8")
R = NE_ROOT
pan = pd.read_parquet(os.path.join(R, r"03_build\build05\_panel_criancas.parquet"), columns=["cd_aluno_sme", "distrito"])
sp = pd.read_parquet(os.path.join(R, r"03_build\build10\_staging\spine.parquet"), columns=["cd_aluno_sme", "ano_nasc", "idade_sol"])
pan["cd_aluno_sme"] = pan.cd_aluno_sme.astype(str); sp["cd_aluno_sme"] = sp.cd_aluno_sme.astype(str)
z = sp.merge(pan, on="cd_aluno_sme", how="left")
z = z[(z.idade_sol < 24) & z.distrito.notna()]; z["lt12"] = (z.idade_sol < 12).astype(int)
out = {}
for a, b in ((2010, 2016), (2013, 2016)):
    g = z[z.ano_nasc.isin([a, b])].groupby(["distrito", "ano_nasc"]).lt12.mean().unstack()
    d = (g[b] - g[a]).dropna()
    out[f"{a}-{b}"] = dict(distritos=len(d), sobe=int((d > 0).sum()), mediana=round(d.median(), 3), minimo=round(d.min(), 3), maximo=round(d.max(), 3))
print(pd.DataFrame(out).T.to_string()); pd.DataFrame(out).T.to_csv(os.path.join(R, r"03_build\build14_cobertura\janela_distritos.csv"))
