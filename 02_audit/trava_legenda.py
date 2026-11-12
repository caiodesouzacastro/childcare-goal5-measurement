# -*- coding: utf-8 -*-
# Trava das legendas e do texto das tabelas (30/10/2026; rodadas legendas-trava-2026-10-30 e trava2-2026-10-30, pedidos
# do autor). Os geradores gravam os .tex por grava_tex(path, texto, exibicao):
#  1. \caption e \tabnote: se o arquivo ja existe e o campo que o script produziria difere do que esta no arquivo, vale o
#     do arquivo (texto do autor), com aviso.
#  2. Resto do arquivo (rotulos de linha e de coluna, titulos de painel, comentarios, estrutura): depois do passo 1, a
#     saida do script e comparada com o arquivo linha a linha, com os numeros mascarados. Havendo diferenca fora dos
#     numeros, o arquivo NAO e regravado, e o aviso nomeia a tabela e as linhas. Se so os numeros mudam, o arquivo e
#     regravado (numeros do script, legendas do arquivo).
#  3. Se o numero de \caption ou de \tabnote nao bate entre o arquivo e a saida do script, o arquivo nao e regravado.
#  Com a variavel de ambiente NE_SOBRESCREVER_LEGENDA=1 o script grava tudo, como antes da trava.
# Mascara: inteiros e decimais, com separador de milhar e com sinal "+" ou "$-$", viram "#". Os anos (1900-2099, sem
# separador) nao sao mascarados, porque nas tabelas sao rotulos. Limites: uma mudanca de valor num numero que e rotulo
# (por exemplo "7" num titulo de painel) passa como numero; linhas acrescentadas ou retiradas pelos dados contam como
# diferenca de estrutura e so entram com NE_SOBRESCREVER_LEGENDA=1, que tambem regrava as legendas.
import difflib, os, re

VAR = "NE_SOBRESCREVER_LEGENDA"
_NUM = re.compile(r"(?:\$-\$|\+)?\d+(?:[.,]\d+)*")
_ANO = re.compile(r"(?:19|20)\d\d")


def _campos(s, cmd):
    # (inicio, fim) do conteudo de cada \cmd{...} fora de comentario, com chaves balanceadas
    r = []
    for m in re.finditer(r"\\" + cmd + r"\{", s):
        ini_linha = s.rfind("\n", 0, m.start()) + 1
        if re.search(r"(?<!\\)%", s[ini_linha:m.start()]):
            continue
        d = 0
        for j in range(m.end() - 1, len(s)):
            if s[j] == "{" and s[j - 1] != "\\":
                d += 1
            elif s[j] == "}" and s[j - 1] != "\\":
                d -= 1
                if d == 0:
                    r.append((m.end(), j))
                    break
    return r


def _linhas(s):
    return s.replace("\r\n", "\n").split("\n")


def _mascara(s):
    return [_NUM.sub(lambda m: m.group(0) if _ANO.fullmatch(m.group(0)) else "#", l.rstrip()) for l in _linhas(s)]


def grava_tex(path, novo, exibicao=None):
    # Grava novo em path pela regra do cabecalho; devolve o texto que ficou no arquivo.
    nome = exibicao or os.path.basename(path)
    if os.path.exists(path) and os.environ.get(VAR) != "1":
        velho = open(path, encoding="utf-8").read()
        trocas = []
        for cmd in ("caption", "tabnote"):
            cv, cn = _campos(velho, cmd), _campos(novo, cmd)
            if len(cv) != len(cn):
                print(f"[trava] {nome}: \\{cmd} aparece {len(cv)} vez(es) no arquivo e {len(cn)} na saida do script; "
                      f"arquivo NAO regravado. Para gravar assim mesmo: {VAR}=1.")
                return velho
            for (a, b), (c, d) in zip(cv, cn):
                if velho[a:b] != novo[c:d]:
                    trocas.append((c, d, velho[a:b], cmd))
        for c, d, txt, cmd in sorted(trocas, reverse=True):
            novo = novo[:c] + txt + novo[d:]
        for cmd in ("caption", "tabnote"):
            if any(t[3] == cmd for t in trocas):
                print(f"[trava] {nome}: \\{cmd} do script difere do arquivo; mantido o que esta no arquivo.")
        mv, mn = _mascara(velho), _mascara(novo)
        if mv != mn:
            difs = [(i1, i2, j1, j2) for op, i1, i2, j1, j2 in
                    difflib.SequenceMatcher(None, mv, mn, autojunk=False).get_opcodes() if op != "equal"]
            onde = ", ".join((f"L{i1 + 1}" + (f"-{i2}" if i2 > i1 + 1 else "")) if i2 > i1 else f"linha nova depois da L{i1}"
                             for i1, i2, j1, j2 in difs)
            print(f"[trava] {nome}: texto fora dos numeros difere do arquivo em {len(difs)} trecho(s) ({onde}); "
                  f"arquivo NAO regravado. Para gravar tudo: {VAR}=1.")
            va, vn = _linhas(velho), _linhas(novo)
            i1, i2, j1, j2 = difs[0]
            if i2 > i1:
                print(f"        arquivo L{i1 + 1}: {va[i1].strip()[:120]}")
            if j2 > j1:
                print(f"        script        : {vn[j1].strip()[:120]}")
            return velho
    open(path, "w", encoding="utf-8").write(novo)
    return novo
