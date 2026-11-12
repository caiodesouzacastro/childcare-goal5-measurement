# -*- coding: utf-8 -*-
# RETOMADA (27/10/2026, PC <usuario>): verificador de numeros escrito do zero (decisao D3 do autor). Nao e copia nem
# derivado de build15/20/23/25_numcheck.py, que nao foram lidos para escreve-lo.
# Infraestrutura (causa 1 do HANDOFF, secao d): parametrizado pelo manuscrito, pelo indice de floats e pelas fontes,
# para servir a qualquer versao do texto sem mudar o script; cada execucao entra em 03_build/m3_execucoes.tsv como
# "infra", contada por rodada.
#
# Pergunta: cada numero escrito no resumo, no corpo e nas notas e legendas dos floats tem lastro numa fonte registrada?
# Fontes: os arquivos passados em --fontes (tabela congelada, registros NUMEROS_*.md) e os corpos dos floats do paper
# (o .tex de cada float e os .tex que ele inclui, SEM legenda e SEM nota, que sao texto verificado e nao fonte).
# Classes de cada ocorrencia:
#   ano            inteiro de 1900 a 2100 sem separador de milhar (nao verificado)
#   identificador  numero de lei, portaria, processo, artigo, capitulo, pagina (pelo contexto); nao verificado
#   forte          achado nas fontes, com casa decimal e 2+ algarismos significativos, ou inteiro >= 100
#   fraco          achado, mas inteiro abaixo de 100 ou decimal de 1 algarismo: coincidencia provavel, nao e prova
#   FORA           nao achado em fonte nenhuma
# Leitura das fontes: notacao inglesa (17.8; 75,267; 75{,}267) e brasileira (29.213; 0,240) entram as duas; e
# deliberadamente liberal, e por isso inteiros pequenos so contam como "fraco".
# Controle positivo antes de tudo: numeros plantados que nao existem em fonte nenhuma tem de sair FORA, e numeros
# sabidamente registrados tem de sair "forte"; se nao, o script para sem relatorio (defeito de leitura produz
# concordancia).
#
# Uso: python 02_audit/infra_numcheck.py --paper 04_paper/paper_v3.tex --indice 04_paper/assets/tables/v3w/float_index_v3.csv
#        --fontes <arquivos> --saida <pasta> [--controle 75267 17.8]
import argparse, csv, glob, os, re, sys
from decimal import Decimal

sys.stdout.reconfigure(encoding="utf-8")
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
ROOT = os.environ.get("NE_ROOT", os.path.dirname(H))
BS = chr(92)

# 28/10/2026 (<maquina>), causa do esgotamento (3/3 na retomada-2026-10-27, uma execucao por versao do texto): --paper
# aceita varios manuscritos na mesma execucao (saida em <saida>/<nome> quando ha mais de um); entradas conferidas antes
# do registro (arquivo ausente ou glob vazio nao gasta execucao); resumo ou marcador ausente e relatado e a varredura
# segue; resumo de classes por arquivo de secao, para uma execucao no paper inteiro servir a secao entregue.
ap = argparse.ArgumentParser()
ap.add_argument("--paper", nargs="+", required=True)
ap.add_argument("--indice", required=True)
ap.add_argument("--fontes", nargs="+", required=True)
ap.add_argument("--saida", required=True)
ap.add_argument("--controle", nargs="+", default=["75267", "17.8"], help="numeros sabidamente registrados")
a = ap.parse_args()


def absp(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


_falta = [p for p in a.paper + [a.indice] if not os.path.exists(absp(p))] + [g for g in a.fontes if not glob.glob(absp(g))]
if _falta:
    sys.exit(f"ENTRADA AUSENTE (nada registrado): {_falta}")
import m3_registro
m3_registro.registra(__file__, "infra")


def ler(p):
    return open(absp(p), encoding="utf-8").read()


def sem_comentario(s):
    return "\n".join(re.split(r"(?<!" + re.escape(BS) + r")%", l)[0] for l in s.splitlines())


def chaves(s, ini):
    """Conteudo entre a chave que abre em s[ini] e a que fecha, com aninhamento."""
    assert s[ini] == "{"
    n = 0
    for k in range(ini, len(s)):
        if s[k] == "{":
            n += 1
        elif s[k] == "}":
            n -= 1
            if n == 0:
                return s[ini + 1:k], k + 1
    raise ValueError("chave sem fechamento")


def tira_comando(s, nome):
    """Separa \\nome{...} do resto: devolve (lista de conteudos, texto sem eles)."""
    achados, out, i = [], [], 0
    pat = re.compile(re.escape(BS + nome) + r"\s*\{")
    while True:
        m = pat.search(s, i)
        if not m:
            out.append(s[i:])
            break
        out.append(s[i:m.start()])
        conteudo, fim = chaves(s, m.end() - 1)
        achados.append(conteudo)
        i = fim
    return achados, "".join(out)


LIMPA = re.compile(re.escape(BS) + r"(?:cite\w*|ref|eqref|pageref|label|input|url|include|includegraphics|graphicspath|"
                   r"setlength|hspace|vspace|addcontentsline|setcounter|bibliographystyle|bibliography)\*?(?:\[[^\]]*\])*\{[^}]*\}")


def limpa_texto(s):
    s = LIMPA.sub(" ", s)
    s = re.sub(re.escape(BS) + r"[A-Za-z]+", " ", s)  # demais comandos: so o nome sai; o argumento e texto
    return s


# ---------------------------------------------------------------- leitura de numeros
NUM_TEX = re.compile(r"(?<![A-Za-z0-9_.])(\d{1,3}(?:(?:\{,\}|,)\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)(?![A-Za-z0-9])")
NUM_BR = re.compile(r"(?<![A-Za-z0-9_])(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+,\d+|\d+)(?![A-Za-z0-9])")
NUM_EN = re.compile(r"(?<![A-Za-z0-9_])(\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+|\d+)(?![A-Za-z0-9])")


def dec_tex(tok):
    return Decimal(tok.replace("{,}", "").replace(",", ""))


def pool_de(s, br_tambem):
    v = set()
    for m in NUM_TEX.finditer(s):
        v.add(dec_tex(m.group(1)).normalize())
    for m in NUM_EN.finditer(s):
        v.add(Decimal(m.group(1).replace(",", "")).normalize())
    if br_tambem:
        for m in NUM_BR.finditer(s):
            v.add(Decimal(m.group(1).replace(".", "").replace(",", ".")).normalize())
    return v


ID_CTX = re.compile(r"(Ordinance|Law|Decree|Resolution|Tema|Theme|RE|ch\.|art\.|Article|No\.|no\.|Lei|vol\.|pp?\.|"
                    r"Portaria|Act|Bill|item|Table|Section|Panel|Goal|Arm|Appendix|strategy|Strategy|indicator)[\s~]*$")


def classe(tok, antes, pool):
    d = dec_tex(tok)
    tem_sep = ("," in tok) or ("{,}" in tok)
    tem_dec = "." in tok
    if not tem_sep and not tem_dec and 1900 <= d <= 2100:
        return "ano"
    if ID_CTX.search(antes):
        return "identificador"
    if d.normalize() not in pool:
        return "FORA"
    sig = len(d.normalize().as_tuple().digits)
    forte = (tem_dec and sig >= 2) or (not tem_dec and d >= 100)
    return "forte" if forte else "fraco"


# ---------------------------------------------------------------- textos verificados e fontes
from collections import Counter
CLASSES = ("ano", "identificador", "forte", "fraco", "FORA")


def trecho(s, ini, fim, nome, avisos):
    """s[ini:fim] pelos marcadores; marcador ausente vira aviso e o trecho vai ate o fim possivel."""
    i = s.find(ini)
    if i < 0:
        avisos.append(f"marcador ausente: {nome} ({ini})")
        return ""
    j = -1
    for f in fim:
        j = s.find(f, i)
        if j >= 0:
            break
    if j < 0:
        avisos.append(f"fim ausente: {nome} ({' / '.join(fim)}); ate o fim do arquivo")
        j = len(s)
    return s[i:j]


def verifica(paper_arg, saida):
    avisos = []
    paper = sem_comentario(ler(paper_arg))
    pdir = os.path.dirname(absp(paper_arg))
    verif = []  # (grupo, arquivo, texto)
    resumo = trecho(paper, BS + "begin{abstract}", [BS + "end{abstract}"], "resumo", avisos).split(BS + "vspace{1em}")[0]
    if not limpa_texto(resumo.replace(BS + "begin{abstract}", "")).strip():
        avisos.append("resumo vazio")
    verif.append(("resumo", os.path.basename(paper_arg), resumo))
    corpo_trecho = trecho(paper, BS + "begin{document}", [BS + "section*{Tables and figures}", BS + "appendix", BS + "end{document}"],
                          "corpo", avisos)
    for f in re.findall(re.escape(BS) + r"input\{([^}]+)\}", corpo_trecho):
        f = f if f.endswith(".tex") else f + ".tex"
        if not os.path.exists(os.path.join(pdir, f)):
            avisos.append(f"input ausente no corpo: {f}")
            continue
        verif.append(("corpo", f, sem_comentario(open(os.path.join(pdir, f), encoding="utf-8").read())))

    fonte_txt = []  # (descricao, texto, br_tambem)
    for pat in a.fontes:
        for f in sorted(glob.glob(absp(pat))):
            fonte_txt.append((os.path.relpath(f, ROOT), open(f, encoding="utf-8").read(), True))

    for row in csv.DictReader(open(absp(a.indice), encoding="utf-8")):
        f = os.path.join(pdir, row["file"] + ".tex")
        if not os.path.exists(f):
            avisos.append(f"float do indice ausente: {row['file']}")
            continue
        s = sem_comentario(open(f, encoding="utf-8").read())
        caps, s = tira_comando(s, "caption")
        notas, s = tira_comando(s, "tabnote")
        for t in caps + notas:
            verif.append(("nota-" + ("corpo" if row["place"] == "body" else "apendice"), row["file"], t))
        corpo_float = s
        for inc in re.findall(re.escape(BS) + r"input\{([^}]+)\}", s):
            g = os.path.join(pdir, inc if inc.endswith(".tex") else inc + ".tex")
            if os.path.exists(g):
                corpo_float += "\n" + sem_comentario(open(g, encoding="utf-8").read())
        fonte_txt.append((row["file"] + " (corpo do float)", corpo_float, False))

    POOL = set()
    for _, t, br in fonte_txt:
        POOL |= pool_de(t, br)

    def varre(grupo, arq, texto):
        t = limpa_texto(texto)
        out = []
        for m in NUM_TEX.finditer(t):
            antes = t[max(0, m.start() - 30):m.start()]
            c = classe(m.group(1), antes, POOL)
            ctx = re.sub(r"\s+", " ", t[max(0, m.start() - 50):m.end() + 30])
            out.append((grupo, arq, m.group(1).replace("{,}", ","), c, ctx))
        return out

    print(f"===== {paper_arg} -> {saida}")
    # ------------------------------------------------------------ controle positivo
    plantado = "planted 987{,}654 and 12.3456 and 31.4159 percent; registered " + " and ".join(
        x if "." in x else f"{int(x):,}".replace(",", "{,}") for x in a.controle) + " here."
    ctl = {r[2].replace(",", ""): r[3] for r in varre("controle", "-", plantado)}
    falha = [k for k in ("987654", "12.3456", "31.4159") if ctl.get(k) != "FORA"]
    falha += [x for x in a.controle if ctl.get(x.replace(",", "")) != "forte"]
    print("controle positivo:", ctl)
    if falha:
        print(f"CONTROLE POSITIVO FALHOU em {falha}: o verificador nao distingue numero registrado de nao registrado; sem relatorio")
        return False

    # ------------------------------------------------------------ varredura
    occ = []
    for g, f, t in verif:
        occ += varre(g, f, t)
    os.makedirs(absp(saida), exist_ok=True)
    with open(os.path.join(absp(saida), "ocorrencias.tsv"), "w", encoding="utf-8") as o:
        o.write("grupo\tarquivo\tnumero\tclasse\tcontexto\n")
        for r in occ:
            o.write("\t".join(r) + "\n")
    for x in avisos:
        print("AVISO:", x)
    print(f"fontes: {len(fonte_txt)} arquivos; {len(POOL)} valores distintos no pool")
    print(f"ocorrencias verificadas: {len(occ)}")
    tab = Counter((r[0], r[3]) for r in occ)
    for g in ("resumo", "corpo", "nota-corpo", "nota-apendice"):
        print(f"  {g:14s} " + " | ".join(f"{c} {tab[(g, c)]}" for c in CLASSES))
    porarq = Counter((r[1], r[3]) for r in occ if r[0] == "corpo")
    for f in [v[1] for v in verif if v[0] == "corpo"]:
        print(f"    {f:28s} " + " | ".join(f"{c} {porarq[(f, c)]}" for c in CLASSES))
    fora = [r for r in occ if r[3] == "FORA"]
    print(f"FORA: {len(fora)}")
    for r in fora:
        print(f"  [{r[0]}] {r[1]}: {r[2]}  ...{r[4]}...")
    with open(os.path.join(absp(saida), "fora.tsv"), "w", encoding="utf-8") as o:
        o.write("grupo\tarquivo\tnumero\tcontexto\n")
        for r in fora:
            o.write("\t".join([r[0], r[1], r[2], r[4]]) + "\n")
    return True


ok = []
for p in a.paper:
    s = a.saida if len(a.paper) == 1 else os.path.join(a.saida, os.path.splitext(os.path.basename(p))[0])
    try:
        ok.append(verifica(p, s))
    except Exception as e:  # falha num manuscrito nao derruba os outros
        print(f"FALHA em {p}: {type(e).__name__}: {e}")
        ok.append(False)
if not all(ok):
    sys.exit(f"{ok.count(False)} de {len(ok)} manuscritos sem relatorio")
