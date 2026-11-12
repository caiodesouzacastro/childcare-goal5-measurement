# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import os, re, difflib, sys, csv
sys.stdout.reconfigure(encoding="utf-8")
S = os.path.dirname(os.path.abspath(__file__))
A = (NE_ROOT + r"\04_paper\assets\tables\appx")
G = os.path.join(S, "appx_gen")
NUM = re.compile(r"(?<![A-Za-z])[-+]?\d[\d,]*(?:\.\d+)?")
def nums(s):
    s = s.replace("$-$", "-").replace("\\%", "")
    s = re.sub(r"\\(ref|label|cite[tp]?|citealp)\{[^}]*\}", "", s)   # numeros dentro de rotulos/chaves nao sao valores
    s = re.sub(r"\b(Table|Figure|Section|Panel)~?\S*", "", s)
    return [n.replace(",", "") for n in NUM.findall(s)]
def kind(line):
    l = line.strip()
    if "&" in l and l.endswith("\\\\"): return "celula"
    if l.startswith("\\tabnote") or l.startswith("\\caption") or "textbf{Panel" in l: return "nota/legenda"
    return "outro"
rows = []
for fn in sorted(os.listdir(A)):
    if not fn.endswith(".tex"): continue
    pg = os.path.join(G, fn)
    if not os.path.exists(pg): rows.append(dict(arquivo=fn, tipo="sem versao gerada", detalhe="")); continue
    a = open(os.path.join(A, fn), encoding="utf-8").read().splitlines()
    g = open(pg, encoding="utf-8").read().splitlines()
    if a == g: continue
    sm = difflib.SequenceMatcher(None, g, a, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal": continue
        gl, al = g[i1:i2], a[j1:j2]
        ng, na = nums(" ".join(gl)), nums(" ".join(al))
        ks = {kind(x) for x in gl + al}
        if ng != na:
            t = "(iii) VALOR NUMERICO"
        elif [re.sub(r"\s+", "", x) for x in gl] == [re.sub(r"\s+", "", x) for x in al]:
            t = "(ii) formatacao (espacos)"
        elif ks <= {"nota/legenda", "outro"} and all(not ("&" in x) for x in gl + al):
            t = "(i) rotulo/cabecalho/nota"
        else:
            # celulas: so texto mudou (mesmos numeros) -> rotulo de linha/cabecalho; senao formatacao
            t = "(i) rotulo/cabecalho/nota" if any(re.sub(r"[\d.,\s$\\-]", "", x) for x in gl + al) else "(ii) formatacao"
        rows.append(dict(arquivo=fn, tipo=t, onde="/".join(sorted(ks)), gerado=" || ".join(gl)[:600], em_uso=" || ".join(al)[:600],
                         nums_gerado=" ".join(ng)[:200], nums_em_uso=" ".join(na)[:200]))
with open(os.path.join(S, "diff_appx.csv"), "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["arquivo", "tipo", "onde", "gerado", "em_uso", "nums_gerado", "nums_em_uso", "detalhe"]); w.writeheader(); w.writerows(rows)
from collections import Counter
c = Counter((r["arquivo"], r["tipo"]) for r in rows)
for (fn, t), n in sorted(c.items()): print(f"{fn:20s} {t:30s} {n}")
print("arquivos com diferenca:", len({r['arquivo'] for r in rows}), "| hunks:", len(rows), "| hunks (iii):", sum(r["tipo"].startswith("(iii)") for r in rows))
