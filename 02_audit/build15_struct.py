# -*- coding: utf-8 -*-
# 30/10/2026 (rodada trava2-2026-10-30): os titulos e as notas das exibicoes (\caption e \tabnote) sao
# TEXTO DO AUTOR, de 30/10/2026, gravado nos .tex. Nao regravar os .tex gerados por este script sem autorizacao do autor.
# Neste script o titulo e a nota vem do arquivo-fonte copiado (N4_enrolled.tex, origem da Tabela A19), que tem o texto antigo.
# Trava (trava_legenda.py, 30/10/2026): \caption e \tabnote que difiram do arquivo nao sao regravados, salvo com NE_SOBRESCREVER_LEGENDA=1.
# FASE 2 (25/10/2026): reestrutura exibicoes sob a tese da cobertura. So move/copia/renomeia; nenhum numero muda.
#  - copia as antigas tabelas do CORPO para o apendice como "Full extract" (A_full_*.tex), com a mesma label;
#  - reescreve appx_index.csv: tira os cortes aprovados (C6, irmaos, decomposicao por pares, quem nunca entra),
#    troca A_C4->A_C4v2 e A_T4d->A_T4dv2, acrescenta as novas (decompyear, covtype) e as copias do corpo;
#  - acrescenta as figuras P6panel e P6res ao dicionario FIG do build12_order.py (apendice), com captions "Full extract".
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import os, re, csv, shutil
from trava_legenda import grava_tex  # trava das legendas (30/10/2026)
P = os.environ.get("PAPER_ROOT", (NE_ROOT + r"\04_paper")); T = os.path.join(P, "assets", "tables"); AP = os.path.join(T, "appx")
COPY = [("body/B01_referral.tex", "A_full_B01.tex", "E1cohort;P2end"), ("body/B02_standardization.tex", "A_full_B02.tex", "P3series;P3boot;P3decomp"),
        ("body/B03_robustness.tex", "A_full_B03.tex", "P2rob;P2fu"), ("N1_agingout.tex", "A_full_N1ag.tex", "agingout"),
        ("body/B05_timing.tex", "A_full_B05.tex", "P5timing;districtmix"), ("N4_enrolled.tex", "A_full_N4.tex", "enrolledbyage")]
for src, dst, _ in COPY:
    s = open(os.path.join(T, src), encoding="utf-8").read()
    s = re.sub(r"\\caption\{", r"\\caption{Full extract: ", s, count=1)
    s = "% Apendice A (Fase 2): copia da antiga tabela do corpo, agora leitura do extrato completo. Origem: " + src + "\n" + s
    grava_tex(os.path.join(AP, dst), s, dst); print("copiada", src, "->", dst)
DROP = {"A_C6.tex", "A_P4dist.tex", "A_P4guard.tex", "A_S3decomp.tex", "A_P55res.tex", "A_D4.tex", "A_C4.tex", "A_T4d.tex"}
idx = [r for r in csv.reader(open(os.path.join(AP, "appx_index.csv"), encoding="utf-8")) if r and r[0] not in DROP]
# A_calendar (build15_appx.py) entrava no indice a mao (OQ-30); desde 26/10 entra aqui. Sem duplicar linhas ja presentes.
add = [("A_calendar.tex", "calendar"), ("A_C4v2.tex", "C4"), ("A_T4dv2.tex", "T4d_never"), ("A_decompyear.tex", "decompyear"), ("A_covtype.tex", "covtype")] + [(d, l) for _, d, l in COPY]
idx += [list(a) for a in add if a[0] not in {r[0] for r in idx}]
with open(os.path.join(AP, "appx_index.csv"), "w", encoding="utf-8", newline="") as f: csv.writer(f).writerows(idx)
print("indice:", len(idx), "tabelas; retiradas:", sorted(DROP))
# build12_order.py: figuras do apendice
o = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build12_order.py"); s = open(o, encoding="utf-8").read()
# Migracao feita uma vez em 25/10. P6panel saiu do apendice em 26/10 (OQ-35): nao readicionar.
# Pulada quando PAPER_ROOT aponta para uma copia de teste.
if '"P6res"' not in s and not os.environ.get("PAPER_ROOT"):
    new = (' "P6panel":("P6_twopanel","Full extract: registration timing and referral by birth cohort, 2010--2016",\n'
           ' "\\\\emph{Source:} SME childcare request record. \\\\emph{Sample:} birth cohorts 2010--2016, full extract (Section~\\\\ref{sec:coverage} shows that the record covers well under three fifths of entrants before 2013). \\\\emph{Variables:} Panel A, median age at first application (months); Panel B, cumulative incidence of referral within one year of application. \\\\emph{Exercise:} Panel A, Kaplan--Meier from birth; Panel B, Aalen--Johansen estimator with aging out as a competing event. Descriptive."),\n'
           ' "P6res":("P6_queueres","Queue stock reconstructed from first-application flows against the published series",\n'
           ' "\\\\emph{Source:} SME childcare request record (flows) and the published registered-demand series (Table~\\\\ref{tab:T11}). \\\\emph{Sample:} one first application per child, 2010--2018. \\\\emph{Variables:} reconstructed stock $=$ initial stock at 1 January 2010 $+$ new first applications $-$ referrals, aging out and recorded withdrawals. \\\\emph{Exercise:} the flow identity closes internally (Table~\\\\ref{tab:P5queue}); the two series are not expected to coincide before 2013, when the record is incomplete (Section~\\\\ref{sec:coverage})."),\n')
    s = s.replace('FIG={"F6":', 'FIG={' + new.lstrip() + ' "F6":', 1)
    s = s.replace('"Share of each birth cohort registered before 6, 12, 18 and 24 months"', '"Full extract: share of each birth cohort registered before 6, 12, 18 and 24 months"')
    s = s.replace('"Median age at first application by month of application, January 2010 to December 2018"', '"Full extract: median age at first application by month of application, January 2010 to December 2018"')
    open(o, "w", encoding="utf-8").write(s); print("build12_order.py: FIG +P6panel +P6res; F6/F8 rotulados Full extract")
