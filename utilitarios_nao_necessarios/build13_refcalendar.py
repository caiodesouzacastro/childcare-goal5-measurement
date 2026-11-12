# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# Verificacao (nao inserida no texto): calendario mensal das primeiras referencias (d_enc1) e primeiras
# matriculas (d_mat1), 2011-2017, para checar se a queda setembro->dezembro do estoque publicado
# coincide com uma onda de encaminhamentos. Descritivo. Saida: 03_build/build13_coverage/calendario_enc_mat.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import os, sys, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"), columns=["d_enc1", "d_mat1", "d_sol1"])
rows = []
for v in ("d_enc1", "d_mat1", "d_sol1"):
    d = pd.to_datetime(sp[v]).dropna()
    d = d[(d.dt.year >= 2011) & (d.dt.year <= 2017)]
    m = d.dt.month.value_counts().sort_index()
    for k, n in m.items(): rows.append(dict(evento=v, mes=k, n=int(n), share=round(n / m.sum(), 4)))
out = pd.DataFrame(rows)
out.to_csv(os.path.join(ROOT, r"03_build\build13_coverage\calendario_enc_mat.csv"), index=False)
print(out.pivot(index="mes", columns="evento", values="share").to_string())
for v in ("d_enc1", "d_mat1", "d_sol1"):
    s = out[out.evento == v].set_index("mes").share
    print(v, "out-dez:", round(s.loc[[10, 11, 12]].sum(), 3), "| jan-fev:", round(s.loc[[1, 2]].sum(), 3), "| nov-fev:", round(s.loc[[11, 12, 1, 2]].sum(), 3))
