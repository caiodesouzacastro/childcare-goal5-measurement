# -*- coding: utf-8 -*-
# Etapa 4/6 (26/10/2026): verificacoes de congelamento reprodutiveis. (1) varredura de resultados cortados no texto
# do corpo e do PDF; (2) anonimizacao: texto-fonte, texto do PDF, bytes do PDF e metadados (pdfinfo).
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, re, subprocess, glob; sys.stdout.reconfigure(encoding="utf-8")
P = (NE_ROOT + r"\04_paper"); PDF = os.path.join(P, sys.argv[1] if len(sys.argv) > 1 else "paper_queue_v1.pdf")
SRC = [os.path.join(P, f + ".tex") for f in ("paper_queue_v1 sec1_intro sec2_setting sec3_coverage sec4_naive sec5_service sec6_timing "
       "sec7_stock sec8_scope sec9_policy sec10_conclusion tables_main tables_appendix appendix_designs").split()]
SRC += glob.glob(os.path.join(P, "assets", "tables", "v2", "*.tex")) + glob.glob(os.path.join(P, "assets", "tables", "v3", "*.tex")) + [os.path.join(P, "assets", "tables", "body", "B10_sme.tex")]
SRC += [os.path.join(P, "assets", "tables", "appx", l.split(",")[0]) for l in open(os.path.join(P, "assets", "tables", "appx", "appx_index.csv"), encoding="utf-8") if l.strip()]
CUT = [r"sibling", r"rank correlation", r"0\.885", r"tab:C6\b", r"tab:P4dist", r"tab:P4guard", r"tab:D4\b", r"tab:S3decomp", r"tab:P55res",
       r"district enrollment growth", r"fig:P6panel"]
ANON = [r"Castro", r"\bCaio\b", r"Biderman", r"\bFGV\b", r"EESP", r"<usuario>esouza", r"ORCID", r"0000-0002", r"[Aa]cknowledg", r"Getulio"]
def strip_comments(s): return "\n".join(re.sub(r"(?<!\\)%.*", "", l) for l in s.splitlines())
txt = subprocess.run(["pdftotext", "-enc", "UTF-8", PDF, "-"], capture_output=True, text=True, encoding="utf-8").stdout
raw = open(PDF, "rb").read().decode("latin-1")
info = subprocess.run(["pdfinfo", PDF], capture_output=True, text=True).stdout
nb = 0
for kind, pats in (("CORTE", CUT), ("ANON", ANON)):
    for pat in pats:
        hs = [(os.path.basename(f), i + 1) for f in SRC for i, l in enumerate(strip_comments(open(f, encoding="utf-8").read()).splitlines()) if re.search(pat, l)]
        hp = len(re.findall(pat, txt)); hb = len(re.findall(pat, raw)) if kind == "ANON" else 0
        if hs or hp or hb: nb += 1; print(f"{kind} {pat}: fonte {hs[:5]} | pdf texto {hp} | pdf bytes {hb}")
print("pdfinfo:", " | ".join(l for l in info.splitlines() if l.split(":")[0] in ("Title", "Author", "Subject", "Keywords", "Creator", "Producer", "Pages")))
print(f"ocorrencias: {nb}")
