# -*- coding: utf-8 -*-
# RETOMADA (27/10/2026, PC <usuario>), decisao D2 do autor: a Tabela 1 em dois niveis.
#   corpo (tab:indet): so as leituras que o texto sustenta -- braco A em todas as redes, so o braco maior exigido,
#         populacao principal ou linear (a SEADE fica fora: a lei remete aos "censos mais atualizados" e a projecao
#         excede o Censo 2022 em 14,4%) -- 2 filas x 2 populacoes x 2 fontes x 3 datas = 24 combinacoes;
#   apendice (tab:indetfull): a enumeracao das 144.
# So formatacao: recebe o DataFrame das combinacoes (o R do build25_indeterminacia.py, ou o combinacoes.csv relido)
# e o indicador da revisao, e devolve as linhas .tex. Sem efeito colateral. Testado por test_build25_tabelas.py
# sobre o combinacoes.csv existente antes da execucao do build25 (causa 4 do HANDOFF). O rotulo "of which" do resumo,
# antes editado a mao no gerado (OQ-107), sai daqui (causa 3).
# RETOMADA, ajuste OQ-109 (27/10/2026, decisao do autor): a data da contagem deixa de ser escolha aberta no corpo. A lei
# nao fixa data; a Portaria SME 7.972 (dez./2016), posterior a lei, fixa o valor em 31/12. O nucleo do corpo passa a
# ser so a contagem de dezembro: 2 filas x 2 populacoes x 2 fontes = 8 combinacoes. O apendice continua com as 144
# (a data segue como dimensao, porque a lei nao a fixa). O corpo se confere sozinho: cada celula impressa e refeita por
# celula() e cada contagem por resumo() antes de devolver as linhas.
# RODADA autor-01 (27/10/2026, decisao do autor): a SEADE entra no corpo. A justificativa da linha 4 caiu: a Lei 16.271
# nao trata da fonte de populacao (o art. 4o fala dos censos educacionais; notas/populacao.md), e a SME usa a SEADE.
# Nucleo: 2 filas x 3 populacoes (principal, linear, SEADE) x 2 fontes = 12 combinacoes. A SEADE reescalada ao Censo
# 2022 (build27) nao entra: fica 11,7% abaixo do Censo 2010 (498.176 contra 564.210). O apendice nao muda.
import pandas as pd

BS = chr(92)
K = ["fila", "data", "pop", "fonte_B", "rede_A", "clausula"]
DATAS = ("12", "9", "media")
PL = {"principal": "Births scaled to Censuses", "linear": "Straight line between Censuses", "SEADE": "SEADE projection"}
FL = {"total": "Published list (all requests)", "sem_unid_especifica": "Narrower list (no specific-centre requests)"}
FO = {"SME": "Secretariat", "Censo": "School census"}
RL = {"todas": "Arm A on all networks", "municipal": "Arm A on municipal and partner centres"}
CL = {"so_maior": "only the greater arm must be met", "fila_sempre": "an empty list is required whichever arm is greater"}
NUCLEO = dict(rede_A="todas", clausula="so_maior", pops=("principal", "linear", "SEADE"), data="12")


def padroes(R):
    """Um registro por combinacao: anos cumpridos (dentro dos avaliaveis), janela avaliavel, monotonia.
    Mesma definicao do pattern() do build25_indeterminacia.py."""
    R = R.copy()
    R["data"] = R["data"].astype(str)
    out = []
    for key, g in R.groupby(K, sort=True):
        ev = g[g.avaliavel == True]  # noqa: E712 (le tanto o bool do build25 quanto o object do CSV)
        yrs = sorted(int(a) for a in ev[ev.cumpre == True].ano)  # noqa: E712
        ult = int(ev.ano.max()) if len(ev) else None
        out.append(dict(zip(K, key), anos=yrs, n_aval=len(ev), primeiro_avaliavel=int(ev.ano.min()) if len(ev) else None,
                        ultimo_avaliavel=ult, monotona=(not yrs) or yrs == list(range(yrs[0], ult + 1))))
    P = pd.DataFrame(out)
    P["anos_s"] = P.anos.apply(lambda v: ",".join(map(str, v)) if v else "nunca")
    assert len(P) == 144, len(P)
    return P


def fmt(v):
    if not v:
        return "never"
    runs, st = [], v[0]
    for a, b in zip(v, v[1:] + [None]):
        if b != a + 1:
            runs.append(str(st) if st == a else f"{st}--{a}")
            st = b
    return ", ".join(runs)


def celula(P, **kw):
    q = P
    for k, v in kw.items():
        q = q[q[k] == v]
    assert len(q) == 1, (kw, len(q))
    q = q.iloc[0]
    return "n.a." if q.n_aval == 0 else fmt(q.anos)


def resumo(P):
    com = P[P.anos_s != "nunca"]
    return dict(n=len(P), nunca=int((P.anos_s == "nunca").sum()), algum=len(com),
                primeiro=com.anos.apply(lambda v: v[0]).value_counts().sort_index().to_dict(),
                nao_monotona=int((~P.monotona).sum()),
                antes_2019=int(P.anos.apply(lambda v: any(a < 2019 for a in v)).sum()),
                padroes=int(P.anos_s.nunique()))


def nucleo(P):
    return P[(P.rede_A == NUCLEO["rede_A"]) & (P.clausula == NUCLEO["clausula"]) & P["pop"].isin(NUCLEO["pops"])
             & (P.data == NUCLEO["data"])]


def _cab():
    """Cabecalho comum: rotulos + tres datas."""
    return [BS + "toprule",
            " & Enrolment in & " + BS + "multicolumn{3}{c}{Count date of the list} " + BS + BS,
            BS + "cmidrule(lr){3-5}",
            "Population series & Arm B & December & September & Mean of the year " + BS + BS,
            BS + "midrule"]


def _bloco(P, pops, **fixo):
    L = []
    for fila in ("total", "sem_unid_especifica"):
        L.append(BS + "multicolumn{5}{l}{" + BS + "emph{" + FL[fila] + "}} " + BS + BS)
        for pl in pops:
            for fo in ("SME", "Censo"):
                cells = [celula(P, fila=fila, data=d, pop=pl, fonte_B=fo, **fixo) for d in DATAS]
                L.append(f"{BS}quad {PL[pl] if fo == 'SME' else ''} & {FO[fo]} & " + " & ".join(cells) + " " + BS + BS)
        L.append(BS + "addlinespace")
    return L


def corpo(P, REV, origem):
    """Tabela do corpo: as 12 combinacoes do nucleo (lista contada em 31/12), o indicador da revisao em dezembro e o
    resumo do nucleo. Confere cada celula e cada contagem antes de devolver."""
    N = nucleo(P)
    assert len(N) == 12, len(N)
    s = resumo(N)
    d = NUCLEO["data"]
    L = ["% Gerado por " + origem + " com 02_audit/build25_tabelas.py (RETOMADA, ajuste OQ-109, rodada autor-01, 27/10/2026). Nao editar a mao.",
         BS + "footnotesize", BS + "setlength{" + BS + "tabcolsep}{4pt}", BS + "begin{tabular}{l l l}", BS + "toprule",
         "Population series & Enrolment in Arm B & Years in which the goal is met " + BS + BS, BS + "midrule"]
    impressas = []
    for fila in ("total", "sem_unid_especifica"):
        L.append(BS + "multicolumn{3}{l}{" + BS + "emph{" + FL[fila] + "}} " + BS + BS)
        for pl in NUCLEO["pops"]:
            for fo in ("SME", "Censo"):
                c = celula(P, fila=fila, data=d, pop=pl, fonte_B=fo, rede_A=NUCLEO["rede_A"], clausula=NUCLEO["clausula"])
                impressas.append(((fila, pl, fo), c))
                L.append(f"{BS}quad {PL[pl] if fo == 'SME' else ''} & {FO[fo]} & {c} " + BS + BS)
        L.append(BS + "addlinespace")
    L.append(BS + "multicolumn{2}{l}{" + BS + "emph{Official review's indicator (not an arm of the law)}} & "
             + fmt(REV[d]) + " " + BS + BS)
    L += [BS + "midrule",
          BS + "multicolumn{2}{l}{Combinations in this table} & " + str(s["n"]) + " " + BS + BS,
          BS + "multicolumn{2}{l}{" + BS + "quad goal met in at least one year} & " + str(s["algum"]) + " " + BS + BS,
          BS + "multicolumn{2}{l}{" + BS + "quad goal met in any year before 2019} & " + str(s["antes_2019"]) + " " + BS + BS,
          BS + "multicolumn{2}{l}{" + BS + "quad distinct sets of years in which the goal is met} & " + str(s["padroes"]) + " " + BS + BS,
          BS + "bottomrule", BS + "end{tabular}"]
    # autoconferencia: as 8 celulas impressas sao as 8 do nucleo, e as contagens batem com elas
    assert sorted(k for k, _ in impressas) == sorted(zip(N.fila, N["pop"], N.fonte_B)), "celulas fora do nucleo"
    assert sum(1 for _, c in impressas if c != "never") == s["algum"] and sum(1 for _, c in impressas if c == "never") == s["nunca"]
    assert len({c for _, c in impressas}) == s["padroes"]
    return L


def apendice(P, origem):
    """Tabela do apendice: as 144 combinacoes e a distribuicao. As duas redes do braco A ficam lado a lado (6 colunas
    de data) e as duas leituras da clausula sao paineis: 2 paineis x 12 linhas x 6 colunas = 144 celulas, numa pagina."""
    s = resumo(P)
    assert s["n"] == 144
    D3 = ("Dec.", "Sep.", "Mean")
    L = ["% Gerado por " + origem + " com 02_audit/build25_tabelas.py (RETOMADA, 27/10/2026). Nao editar a mao.",
         BS + "footnotesize", BS + "setlength{" + BS + "tabcolsep}{4pt}", BS + "begin{tabular}{l l l l l l l l}",
         BS + "toprule",
         " & Enrolment in & " + BS + "multicolumn{3}{c}{" + RL["todas"] + "} & " + BS + "multicolumn{3}{c}{" + RL["municipal"] + "} " + BS + BS,
         BS + "cmidrule(lr){3-5}" + BS + "cmidrule(lr){6-8}",
         "Population series & Arm B & " + " & ".join(D3 + D3) + " " + BS + BS,
         BS + "midrule"]
    for letra, cl in zip("AB", ("so_maior", "fila_sempre")):
        L.append(BS + "multicolumn{8}{l}{" + BS + "textbf{Panel " + letra + ". " + CL[cl][0].upper() + CL[cl][1:] + "}} " + BS + BS)
        for fila in ("total", "sem_unid_especifica"):
            L.append(BS + "multicolumn{8}{l}{" + BS + "emph{" + FL[fila] + "}} " + BS + BS)
            for pl in ("principal", "linear", "SEADE"):
                for fo in ("SME", "Censo"):
                    cells = [celula(P, fila=fila, data=d, pop=pl, fonte_B=fo, rede_A=rede, clausula=cl)
                             for rede in ("todas", "municipal") for d in DATAS]
                    L.append(f"{BS}quad {PL[pl] if fo == 'SME' else ''} & {FO[fo]} & " + " & ".join(cells) + " " + BS + BS)
            L.append(BS + "addlinespace")
    L += [BS + "midrule",
          BS + "multicolumn{8}{l}{" + BS + "textbf{Panel C. All " + str(s["n"]) + " combinations}} " + BS + BS,
          BS + "multicolumn{7}{l}{" + BS + "quad Goal never met in an evaluable year} & " + str(s["nunca"]) + " " + BS + BS,
          BS + "multicolumn{7}{l}{" + BS + "quad Goal met in at least one year} & " + str(s["algum"]) + " " + BS + BS]
    for y, n in s["primeiro"].items():
        L.append(BS + "multicolumn{7}{l}{" + BS + "qquad first met in " + str(y) + "} & " + str(int(n)) + " " + BS + BS)
    L += [BS + "multicolumn{7}{l}{" + BS + "qquad of which: met in one year and not in a later evaluable year} & " + str(s["nao_monotona"]) + " " + BS + BS,
          BS + "multicolumn{7}{l}{" + BS + "quad Goal met in any year before 2019} & " + str(s["antes_2019"]) + " " + BS + BS,
          BS + "multicolumn{7}{l}{" + BS + "quad Distinct sets of years in which the goal is met} & " + str(s["padroes"]) + " " + BS + BS,
          BS + "bottomrule", BS + "end{tabular}"]
    return L
