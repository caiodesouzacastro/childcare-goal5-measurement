# -*- coding: utf-8 -*-
# RETOMADA (27/10/2026, PC <usuario>): registro automatico de execucoes para a regra M3 (no maximo 3 por script).
# Causa 1 do esgotamento (HANDOFF, secao d): o contador era reconstruido a mao a partir de logs soltos, e scripts de
# infraestrutura (ordenacao, verificador) eram contados junto com a analise, sem separar rodadas. Cada script chama
# registra(__file__, tipo) ao comecar; a linha vai para 03_build/m3_execucoes.tsv com data, maquina, rodada (variavel
# NE_RODADA), tipo ("analise" ou "infra"), script, sha256 do script e numero da execucao naquela rodada. Ao passar de 3
# na rodada, o script para antes de fazer qualquer coisa (esgotado vai para o registro, sem copia).
import datetime, hashlib, os, platform, sys

_H = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.environ.get("NE_ROOT", os.path.dirname(_H))
ARQ = os.path.join(_ROOT, "03_build", "m3_execucoes.tsv")
LIMITE = 3


def contagem(script, rodada=None):
    rodada = rodada or os.environ.get("NE_RODADA", "retomada-2026-10-27")
    if not os.path.exists(ARQ):
        return 0
    n = 0
    for l in open(ARQ, encoding="utf-8").read().splitlines()[1:]:
        c = l.split("\t")
        if len(c) >= 5 and c[2] == rodada and c[4] == script:
            n += 1
    return n


def registra(arquivo, tipo):
    assert tipo in ("analise", "infra"), tipo
    script = os.path.basename(arquivo)
    rodada = os.environ.get("NE_RODADA", "retomada-2026-10-27")
    n = contagem(script, rodada) + 1
    if n > LIMITE:
        sys.exit(f"[M3] {script}: {n - 1} execucoes na rodada {rodada}; limite {LIMITE}. Esgotado: registrar, nao copiar.")
    sha = hashlib.sha256(open(arquivo, "rb").read()).hexdigest()[:16]
    novo = not os.path.exists(ARQ)
    with open(ARQ, "a", encoding="utf-8") as o:
        if novo:
            o.write("data\tmaquina\trodada\ttipo\tscript\tsha256_16\texecucao_na_rodada\targs\n")
        o.write("\t".join([datetime.datetime.now().isoformat(timespec="seconds"), platform.node(), rodada, tipo, script, sha,
                           str(n), " ".join(sys.argv[1:])]) + "\n")
    print(f"[M3] {script} ({tipo}): execucao {n} de {LIMITE} na rodada {rodada}")
    return n
