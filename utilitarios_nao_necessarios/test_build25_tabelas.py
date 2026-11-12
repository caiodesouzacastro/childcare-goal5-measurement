# -*- coding: utf-8 -*-
# RETOMADA (27/10/2026): teste de build25_tabelas.py ANTES da execucao do build25 (causa 4 do HANDOFF: erro que so
# aparece na execucao). Nao grava nada no projeto; as tabelas de teste vao para a pasta do 1o argumento.
# Confere contra tres referencias independentes do modulo:
#   (1) o log da ultima execucao do build25 (03_build/build25/indeterminacia.log): padrao de cada uma das 144;
#   (2) a Tabela 1 publicada (04_paper/assets/tables/c/C_indet_body.tex): as 36 celulas do Painel A e as contagens
#       do Painel B;
#   (3) as contagens do texto (13 de 36 com algum ano; nenhuma antes de 2019).
# E compila as duas tabelas num documento minimo (pdflatex) para pegar erro de LaTeX e tabela maior que a pagina.
# Uso: python test_build25_tabelas.py <pasta_de_rascunho>
import ast, os, re, subprocess, sys
import pandas as pd

H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("NE_ROOT", os.path.dirname(H))
sys.path.insert(0, H)
import build25_tabelas as T

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
R = pd.read_csv(os.path.join(ROOT, "03_build", "build25", "combinacoes.csv"))
P = T.padroes(R)
falhas = []

# (1) log
log = open(os.path.join(ROOT, "03_build", "build25", "indeterminacia.log"), encoding="utf-8").read()
linhas = re.findall(r"^(\('.*?'\)) \| (\S+) \| (\S+) - (\S+) \| monotona: (True|False)$", log, re.M)
assert len(linhas) == 144, len(linhas)
for tup, anos_s, a0, a1, mono in linhas:
    key = ast.literal_eval(tup)
    q = P
    for k, v in zip(T.K, key):
        q = q[q[k] == v]
    assert len(q) == 1, key
    q = q.iloc[0]
    if (q.anos_s, str(q.primeiro_avaliavel), str(q.ultimo_avaliavel), str(bool(q.monotona))) != (anos_s, a0, a1, mono):
        falhas.append(f"log difere em {key}: {(q.anos_s, q.primeiro_avaliavel, q.ultimo_avaliavel, q.monotona)} vs {(anos_s, a0, a1, mono)}")
REV = ast.literal_eval(re.search(r"=== indicador da revisao .*?anos: (\{.*\})", log).group(1))
print("(1) 144 padroes do log conferidos; REV:", REV)

# (2) Tabela 1 publicada
pub = open(os.path.join(ROOT, "04_paper", "assets", "tables", "c", "C_indet_body.tex"), encoding="utf-8").read()
painelA = re.findall(r"^\\quad (.*?) & (Secretariat|School census) & (.*?) & (.*?) & (.*?) \\\\$", pub, re.M)
assert len(painelA) == 12, len(painelA)  # 2 filas x 3 pops x 2 fontes; 3 datas por linha = 36 celulas
INV = {v: k for k, v in T.PL.items()}
FOI = {v: k for k, v in T.FO.items()}
pl_atual = None
for i, (pl, fo, *cells) in enumerate(painelA):
    fila = "total" if i < 6 else "sem_unid_especifica"  # 6 linhas por fila: 3 populacoes x 2 fontes
    pl_atual = INV[pl.strip()] if pl.strip() else pl_atual
    for d, c in zip(T.DATAS, cells):
        novo = T.celula(P, fila=fila, data=d, pop=pl_atual, fonte_B=FOI[fo], rede_A="todas", clausula="so_maior")
        if novo != c.strip():
            falhas.append(f"Painel A difere: {fila} {pl_atual} {fo} {d}: publicado {c!r}, modulo {novo!r}")
s = T.resumo(P)
esperado = dict(nunca=123, algum=21, primeiro={2019: 4, 2020: 8, 2021: 9}, nao_monotona=4, antes_2019=0)
for k, v in esperado.items():
    if s[k] != v:
        falhas.append(f"resumo {k}: {s[k]} != {v}")
for rot, n in (("Goal never met in an evaluable year", 123), ("Goal first met in 2019", 4), ("Goal first met in 2020", 8),
               ("Goal first met in 2021", 9), ("of which: met in one year and not in a later evaluable year", 4)):
    m = re.search(re.escape(rot) + r"\} & (\d+)", pub)
    if not m or int(m.group(1)) != n:
        falhas.append(f"Painel B publicado: {rot} -> {m.group(1) if m else None}, esperado {n}")
rev_pub = re.search(r"Official review's indicator.*?\} & (.*?) & (.*?) & (.*?) \\\\", pub).groups()
if tuple(T.fmt(REV[k]) for k in T.DATAS) != tuple(x.strip() for x in rev_pub):
    falhas.append(f"linha da revisao: {rev_pub}")
print("(2) 36 celulas do Painel A, contagens do Painel B e linha da revisao conferidas contra C_indet_body.tex")

# (3) nucleo
N = T.nucleo(P)
sn = T.resumo(N)
print("(3) nucleo:", sn)
if (len(N), sn["algum"], sn["antes_2019"]) != (24, 13, 0):
    falhas.append(f"nucleo: {len(N)} combinacoes, {sn['algum']} com algum ano, {sn['antes_2019']} antes de 2019")
A36 = P[(P.rede_A == "todas") & (P.clausula == "so_maior")]
if T.resumo(A36)["algum"] != 13 or (A36[A36["pop"] == "SEADE"].anos_s != "nunca").any():
    falhas.append("Painel A: 13 de 36 com algum ano e SEADE sempre nunca nao conferem")

# tabelas e compilacao minima
corpo = T.corpo(P, REV, "test_build25_tabelas.py")
apx = T.apendice(P, "test_build25_tabelas.py")
open(os.path.join(OUT, "t_corpo.tex"), "w", encoding="utf-8").write("\n".join(corpo) + "\n")
open(os.path.join(OUT, "t_apx.tex"), "w", encoding="utf-8").write("\n".join(apx) + "\n")
def n_celulas(L):  # linhas de combinacao: rotulo de populacao & fonte & celulas...; celulas = numero de & menos 1
    return sum(l.count("&") - 1 for l in L if l.startswith(T.BS + "quad ") and ("& Secretariat &" in l or "& School census &" in l))
n_cel_apx, n_cel_corpo = n_celulas(apx), n_celulas(corpo)
# cada celula do apendice confere com celula() na ordem em que a tabela e montada (redes lado a lado)
it = iter([T.celula(P, fila=f, data=d, pop=p, fonte_B=fo, rede_A=r, clausula=c)
           for c in ("so_maior", "fila_sempre") for f in ("total", "sem_unid_especifica") for p in ("principal", "linear", "SEADE")
           for fo in ("SME", "Censo") for r in ("todas", "municipal") for d in T.DATAS])
for l in apx:
    if l.startswith(T.BS + "quad ") and ("& Secretariat &" in l or "& School census &" in l):
        for c in l.rstrip(" " + T.BS).split("&")[2:]:
            if c.strip() != next(it):
                falhas.append(f"celula do apendice fora de ordem: {l[:80]}")
assert next(it, None) is None
print("celulas: corpo", n_cel_corpo, "| apendice", n_cel_apx)
if (n_cel_corpo, n_cel_apx) != (24, 144):
    falhas.append(f"celulas: corpo {n_cel_corpo}, apendice {n_cel_apx}")
doc = (T.BS + "documentclass[12pt,a4paper]{article}" + T.BS + "usepackage[margin=1in]{geometry}" + T.BS + "usepackage{booktabs}"
       + T.BS + "usepackage{graphicx}" + T.BS + "usepackage{setspace}" + T.BS + "usepackage[skip=6pt,position=top]{caption}"
       + T.BS + "onehalfspacing\n"
       + T.BS + "newcommand{" + T.BS + "fitbox}[1]{" + T.BS + "resizebox{" + T.BS + "ifdim" + T.BS + "width>" + T.BS + "linewidth"
       + T.BS + "linewidth" + T.BS + "else" + T.BS + "width" + T.BS + "fi}{!}{#1}}\n"
       + T.BS + "begin{document}\n"
       + T.BS + "begin{table}" + T.BS + "centering" + T.BS + "caption{c}" + T.BS + "fitbox{" + T.BS + "input{t_corpo}}" + T.BS + "end{table}\n"
       + T.BS + "clearpage\n"
       + T.BS + "begin{table}" + T.BS + "centering" + T.BS + "caption{a}" + T.BS + "fitbox{" + T.BS + "input{t_apx}}" + T.BS + "end{table}\n"
       + T.BS + "end{document}\n")
open(os.path.join(OUT, "t_doc.tex"), "w", encoding="utf-8").write(doc)
r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "t_doc.tex"], cwd=OUT, capture_output=True, text=True, encoding="utf-8", errors="replace")
lg = open(os.path.join(OUT, "t_doc.log"), encoding="utf-8", errors="replace").read()
erros = re.findall(r"^! .*", lg, re.M)
grande = re.findall(r"Float too large.*", lg)
over = re.findall(r"^Overfull .*", lg, re.M)
print("compilacao: erros", len(erros), "| float grande demais", len(grande), "| overfull", len(over))
if erros or grande:
    falhas.append(f"LaTeX: {erros[:3]} {grande[:2]}")
print("FALHAS:", len(falhas))
for f in falhas:
    print("  ", f)
sys.exit(1 if falhas else 0)
