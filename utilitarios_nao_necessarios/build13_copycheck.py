# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import os, re, glob, sys
sys.stdout.reconfigure(encoding="utf-8")
A = (NE_ROOT + r"\02_audit")
def norm(l): return re.sub(r"\s+", "", l.split("#")[0])
corpus = {}
for f in glob.glob(os.path.join(A, "build*.py")) + glob.glob(os.path.join(A, "d14*.py")) + [os.path.join(A, "lib.py"), os.path.join(A, "reglib.py")]:
    if not os.path.exists(f) or "build13_" in f: continue
    for l in open(f, encoding="utf-8", errors="replace"):
        n = norm(l)
        if len(n) >= 25: corpus.setdefault(n, set()).add(os.path.basename(f))
src = open(os.path.join(A, "verificacao_final.py"), encoding="utf-8").read().splitlines()
blocks, cur, name = [], [], "carga/B_novo (V1)"
for l in src:
    m = re.match(r"# =+ (.*?) =+", l)
    if m: blocks.append((name, cur)); name, cur = m.group(1), []
    else: cur.append(l)
blocks.append((name, cur))
for name, lines in blocks:
    sig = [norm(l) for l in lines if len(norm(l)) >= 25]
    hit = [s for s in sig if s in corpus]
    srcs = sorted({x for s in hit for x in corpus[s]})
    print(f"{name[:42]:42s} linhas={len(sig):3d} identicas_ao_build={len(hit):3d} ({(100*len(hit)/len(sig) if sig else 0):4.0f}%) fontes={srcs[:6]}")
