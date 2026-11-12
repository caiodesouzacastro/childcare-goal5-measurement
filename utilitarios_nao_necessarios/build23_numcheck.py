# V3 FINAL (26/10/2026): COPIA de build15_numcheck.py (que chegou a 3 execucoes na FUSAO). Mesmo codigo; criada para conferir a etapa V3 FINAL. Registrado como falha da M3 em V3_FINAL.md.
# -*- coding: utf-8 -*-
# FUSAO (26/10/2026): aponta para paper_v3.tex (secV*, floats em assets/tables/v3w); le NUMEROS_V3 + V4 + V5 + congelados_v3.
# FASE 2, etapa 5.1 (25/10/2026): todo numero do texto (resumo + corpo) tem de estar na tabela congelada
# (referee_EE_2026-10/NUMEROS_V2.md + 03_build/build15/congelados_tabelas.csv). Lista os que nao estao.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import re, os, sys, csv; sys.stdout.reconfigure(encoding="utf-8")
P = (NE_ROOT + r"\04_paper"); BS = chr(92)
def norm_pt(s):   # NUMEROS_V2 (pt-BR): 1.524.560 -> 1524560 ; 0,753 -> 0.753
    s = re.sub(r"(?<=\d)\.(?=\d{3}\b)", "", s); return s.replace(",", ".")
W = set()
txt = "".join(open(os.path.join(P, "referee_EE_2026-10", f), encoding="utf-8").read() for f in ("NUMEROS_V3.md", "NUMEROS_V4.md", "NUMEROS_V5.md") if os.path.exists(os.path.join(P, "referee_EE_2026-10", f)))
for n in re.findall(r"[-+−]?\d[\d.,]*\d|\d", norm_pt(txt.replace("−", "-"))): W.add(n.lstrip("+-").rstrip("."))
for r in csv.DictReader(open((NE_ROOT + r"\03_build\build18\congelados_v3.csv"), encoding="utf-8")):
    for n in re.findall(r"\d[\d.,]*\d|\d", r["valor"].replace(",", "")): W.add(n.rstrip("."))
def _addround(S):
    out = set(S)
    for x in S:
        try:
            v = float(x)
            for d in (0, 1, 2): out.add(f"{v:.{d}f}")
            out.add(str(int(round(v / 1000.0)) * 1000))
        except ValueError: pass
    return out
W = _addround(W)
def variants(n):
    v = {n}
    if "." in n:
        a, b = n.split(".", 1); v.add(a + "." + b.rstrip("0") if b.rstrip("0") else a)
        if b.endswith("0"): v.add(a + "." + b[:-1])
    return v
files = ["secV1_intro", "secV2_setting", "secV3_data", "secV4_coverage", "secV5_change", "secV6_series", "secV7_goal", "secV8_indicators", "secV9_scope", "secV10_conclusion"] + ["assets/tables/v3w/" + f[:-4] for f in sorted(os.listdir(os.path.join(P, "assets", "tables", "v3w"))) if f.endswith(".tex")]
main = open(os.path.join(P, "paper_v3.tex"), encoding="utf-8").read()
ab = main[main.index(BS + "begin{abstract}"):main.index(BS + "end{abstract}")]
srcs = [("abstract", ab)] + [(f, open(os.path.join(P, f + ".tex"), encoding="utf-8").read()) for f in files]
YEARS = re.compile(r"^(19|20)\d\d$")
miss = []
for name, s in srcs:
    for i, l in enumerate(s.splitlines(), 1):
        l2 = re.sub(r"(?<!" + re.escape(BS) + r")%.*$", "", l)
        l2 = re.sub(re.escape(BS) + r"(ref|label|cite[tp]?|citealp|citet|input|pending|section|subsection|paragraph)\*?(\[[^\]]*\])*\{[^}]*\}", " ", l2)
        l2 = l2.replace("{,}", "").replace("--", " ")
        for n in re.findall(r"(?<![A-Za-z_])\d[\d.]*\d|(?<![A-Za-z_])\d", l2):
            n = n.rstrip(".")
            if YEARS.match(n) or n in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}: continue
            if not (variants(n) & W): miss.append(f"{name}:{i}\t{n}\t{l.strip()[:110]}")
print(f"numeros fora da tabela congelada: {len(miss)}")
for m in miss: print(m)
