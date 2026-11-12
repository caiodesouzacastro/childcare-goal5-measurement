# -*- coding: utf-8 -*-
# MANHA (26/10/2026): renumeracao das exibicoes entre a versao anterior a MANHA (03_build/build18/aux_antes_manha.aux)
# e a atual (04_paper/paper_queue_v1.aux). Regra permanente (memoria appendix-renumbering-rule). Acrescenta uma secao
# ao fim de referee_EE_2026-10/renumeracao.md (com .bak) e imprime as contagens.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import re, os, sys, shutil; sys.stdout.reconfigure(encoding="utf-8")
R = NE_ROOT
def labels(p):
    out = {}
    for m in re.finditer(r"\\newlabel\{((?:tab|fig):[^}]+)\}\{\{([^}]*)\}", open(p, encoding="latin-1").read()): out[m.group(1)] = m.group(2)
    return out
a = labels(os.path.join(R, r"03_build\build18\aux_antes_manha.aux")); b = labels(os.path.join(R, r"04_paper\paper_queue_v1.aux"))
rows = []
for k in sorted(set(a) | set(b), key=lambda k: (k.split(":")[0], b.get(k, a.get(k)))):
    o, n = a.get(k, "(novo)"), b.get(k, "(fora do paper)")
    if o != n: rows.append(f"| `{k}` | {o} | {n} |")
same = sum(1 for k in set(a) & set(b) if a[k] == b[k])
txt = (f"\n\n## MANHA (26/10/2026): versão pré-MANHA → versão com janela a partir de jul./2012\n\nGerado por `02_audit/build18_renum.py` "
       f"a partir de `03_build/build18/aux_antes_manha.aux` e `04_paper/paper_queue_v1.aux`. Rótulos com o mesmo número: {same}; mudaram, entraram ou saíram: {len(rows)}.\n\n"
       "| Rótulo | Número antes | Número agora |\n|---|---|---|\n" + "\n".join(rows) + "\n")
md = os.path.join(R, r"04_paper\referee_EE_2026-10\renumeracao.md"); shutil.copy(md, md + ".bak-2026-10-26-manha")
s = open(md, encoding="utf-8").read(); s = s.split("\n\n## MANHA (26/10/2026)")[0] + txt; open(md, "w", encoding="utf-8").write(s)
assert open(md, encoding="utf-8").read() == s
print(f"iguais {same}; mudaram/entraram/sairam {len(rows)}"); print("\n".join(rows))
