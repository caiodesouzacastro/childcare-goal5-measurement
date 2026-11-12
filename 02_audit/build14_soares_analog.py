# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import os, sys, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
R = NE_ROOT
cm = pd.read_feather(os.path.join(R, r"03_build\build01\_staging\child_master.feather"), columns=["ano_sol", "idade_sol", "ever_mat"])
for lab, d in (("todos os solicitantes", cm), ("matriculados (definicao do build01 T3)", cm[cm.ever_mat == 1])):
    m = d.groupby("ano_sol").idade_sol.mean().round(2)
    print(lab + ":", {k: m[k] for k in (2010, 2013, 2018)})
print("validacao build01 T3 (matriculados): 32.62 (2010) -> 17.30 (2018)")
