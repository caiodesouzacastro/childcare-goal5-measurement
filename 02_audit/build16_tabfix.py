# -*- coding: utf-8 -*-
# Etapas 3.2 e 6 (26/10/2026): correcoes de rotulo, nota e tipografia nas tabelas geradas, apontadas na revisao
# REVIEW_V2.md (agentes 1, 2, 4 e 5). Pos-processamento idempotente, como o build12_spelling.py: NAO altera numeros
# (exceto o arredondamento de dois intervalos de 4 para 3 casas, igual ao texto). Roda por ultimo:
#   build12_appendix.py --full (que ja chama este script) e, depois de build15_tables.py, de novo este script.
# Cada par: o antigo tem de ocorrer exatamente uma vez, ou o novo ja estar presente (rodada anterior); senao, falha.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import os, sys, io
P = os.path.join(os.environ.get("PAPER_ROOT", (NE_ROOT + r"\04_paper")), "assets", "tables")
FX = {
 "appx/A_C2.tex": [(" The static columns reproduce the previous static-count table.", "")],
 "appx/A_P5queue.tex": [("& int. & official & gap \\\\", "& int. & published & gap \\\\"),
                        ("& aged & des & Q$_t$", "& aged & wd & Q$_t$"),
                        ("ref, aged, des: first exits", "ref, aged, wd: first exits"),
                        ("off: published December stock.", "published: December stock in the published series; gap: published minus Q$_t$."),
                        ("$-$ aged $-$ des, closed", "$-$ aged $-$ wd, closed")],
 "appx/A_N1lotes.tex": [("\\emph{Sample:} first application per child (1,524,560).",
                         "\\emph{Sample:} first application per child (1,524,560, including 51,106 first applications dated 2006--2009, which are not shown by year).")],
 "appx/A_T4dv2.tex": [("so the differences are not interpreted", "so the differences are partly mechanical")],
 "appx/A_P55type.tex": [("& Aging-out &", "& Aging out &")],
 "appx/A_T1.tex": [("$\\leq$2km", "$\\leq$2\\,km")],
 "appx/A_E1year.tex": [("competing risk", "competing event")],
 "appx/A_full_B01.tex": [("competing risk", "competing event"),
                         ("RMST: restricted mean days in the eligible queue within 365 days;", "RMST: restricted mean days without the event within 365 days;"),
                         ("\\caption{Full extract: One-year", "\\caption{Full extract: one-year")],
 "appx/A_full_B02.tex": [("\\caption{Full extract: One-year", "\\caption{Full extract: one-year")],
 "appx/A_full_B03.tex": [("\\caption{Full extract: Robustness", "\\caption{Full extract: robustness")],
 "appx/A_full_B05.tex": [("\\caption{Full extract: Registration", "\\caption{Full extract: registration")],
 "appx/A_full_N4.tex": [("\\caption{Full extract: Share", "\\caption{Full extract: share")],
 "appx/A_full_N1ag.tex": [("\\caption{Full extract: Aging out of eligibility: applicants who applied after the limit versus",
                           "\\caption{Full extract: aging out of eligibility among applicants who applied after the limit and")],
 "appx/A_Rcap.tex": [("Age band & 2013s1 & 2019s1 & Change \\% & 2013s1 & 2019s1 & Change \\%", "Age band & 2013S1 & 2019S1 & Change \\% & 2013S1 & 2019S1 & Change \\%")],
 "appx/A_T6b.tex": [("Age band & 2013s1 & 2014s1 & 2015s1 & 2016s1 & 2017s1 & 2018s1 & 2019s1", "Age band & 2013S1 & 2014S1 & 2015S1 & 2016S1 & 2017S1 & 2018S1 & 2019S1")],
 "body/B10_sme.tex": [("Enrolments by stage", "Enrollments by stage")],
 "v2/V2_specs.tex": [("[+0.1282, +0.1335]", "[+0.128, +0.134]"), ("[+0.1201, +0.1260]", "[+0.120, +0.126]"),
                     ("composition contributes -0.009", "composition contributes $-$0.009")],
 "v2/V2_coverage.tex": [("& Centers & Median center & Centers", "& Centers & Median center (share) & Centers")],
}
# A_T2: o mesmo cabecalho aparece 3 vezes (paineis); troca todas.
ALL = {"appx/A_T2.tex": [("& 2013s1 & 2014s1 & 2015s1 & 2016s1 & 2017s1 & 2018s1 & 2019s1", "& 2013S1 & 2014S1 & 2015S1 & 2016S1 & 2017S1 & 2018S1 & 2019S1", 3),
                         ("Partner: the contracted network, partner-run and indirect centers together",
                          "Partner (in this table): the contracted network, partner-run and indirect centers together, which Section~\\ref{sec:institutions} and Table~\\ref{tab:T5c_modal} separate", None)],
       "body/B10_sme.tex": [("Bimonthly", "Every two months", None)],
       # "Partner" nestas tres tabelas inclui as indiretas; a Secao 2 e a T5c as separam (REVIEW_V2, agentes 1, 2, 5).
       "appx/A_T7a.tex": [("Partner: the contracted network, partner-run and indirect centers together",
                           "Partner (in this table): the contracted network, partner-run and indirect centers together, which Section~\\ref{sec:institutions} and Table~\\ref{tab:T5c_modal} separate", None)],
       "appx/A_T6c.tex": [("Partner: the contracted network, partner-run and indirect centers together",
                           "Partner (in this table): the contracted network, partner-run and indirect centers together, which Section~\\ref{sec:institutions} and Table~\\ref{tab:T5c_modal} separate", None)],
       # "Coverage" no paper e a cobertura do registro; aqui sao vagas por crianca elegivel.
       "appx/A_S6cd.tex": [("& Coverage (mun.) & Coverage Q1 & Coverage Q4", "& Per child (mun.) & Per child Q1 & Per child Q4", None),
                           ("Value (coverage)", "Value (places per child)", None),
                           ("; coverage $=$ authorized places $/$ pool, first semester.", "; per child (places per eligible child) $=$ authorized places $/$ pool, first semester.", None)]}
bad = 0; done = 0
def rw(fn, fun):
    global bad, done
    p = os.path.join(P, fn); s = io.open(p, encoding="utf-8", newline="").read(); r = fun(s)
    if r is None: bad += 1; return
    if r != s:
        io.open(p, "w", encoding="utf-8", newline="").write(r)
        if io.open(p, encoding="utf-8", newline="").read() != r: print("FALHA releitura", fn); bad += 1; return
        done += 1
for fn, pairs in FX.items():
    def f(s, pairs=pairs, fn=fn):
        for a, b in pairs:
            c = s.count(a)
            if c == 1: s = s.replace(a, b)
            elif not (b and b in s) and not (b == "" and c == 0): print("FALHA", fn, c, a[:60]); return None
        return s
    rw(fn, f)
for fn, pairs in ALL.items():
    def g(s, pairs=pairs, fn=fn):
        for a, b, n in pairs:
            c = s.count(a)
            if n is not None and c not in (0, n): print("FALHA", fn, c, a[:60]); return None
            if c == 0 and b not in s: print("FALHA", fn, "nem antigo nem novo", a[:60]); return None
            s = s.replace(a, b)
        return s
    rw(fn, g)
print(f"build16_tabfix: {done} arquivos alterados, {bad} falhas")
sys.exit(1 if bad else 0)
