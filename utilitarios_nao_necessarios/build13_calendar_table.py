# -*- coding: utf-8 -*-
# 30/10/2026 (rodada fecha-trava-2026-10-30): os titulos e as notas das exibicoes (\caption e \tabnote) sao
# TEXTO DO AUTOR, de 30/10/2026, gravado nos .tex. Nao regravar os .tex gerados por este script sem autorizacao do autor.
# A_calendar.tex do paper (Tabela A3, 2013-2017) e gerada pelo build15_appx.py; este script gera a versao de 2011-2017,
# substituida em 25/10/2026 (build12_appendix.py, L120-122), com o titulo e a nota antigos.
# Trava (trava_legenda.py, 30/10/2026): \caption e \tabnote que difiram do arquivo nao sao regravados, e o arquivo nao e
# regravado se o texto fora dos numeros diferir; NE_SOBRESCREVER_LEGENDA=1 grava tudo.
# OQ-25 (aprovado 25/10): tabela de apendice com a distribuicao mensal de primeiras solicitacoes, primeiros
# encaminhamentos e primeiras matriculas, 2011-2017. Entrada: 03_build/build13_coverage/calendario_enc_mat.csv
# (gerado por 02_audit/build13_refcalendar.py). Saida: 04_paper/assets/tables/appx/A_calendar.tex
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
from trava_legenda import grava_tex  # trava das legendas (30/10/2026)
ROOT = (NE_ROOT + "/")
c = pd.read_csv(ROOT + "03_build/build13_coverage/calendario_enc_mat.csv")
p = c.pivot(index="mes", columns="evento", values="share")
n = c.groupby("evento").n.sum()
MES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
L = ["% Apendice A (revisao pos-EE). Gerado por 02_audit/build13_calendar_table.py.",
     "\\begin{table}[htbp]\\centering",
     "\\caption{Calendar month of first applications, first referrals and first enrollments, 2011--2017}",
     "\\label{tab:calendar}", "\\footnotesize",
     "\\begin{tabular}{lrrr}", "\\toprule",
     "Month & First applications & First referrals & First enrollments \\\\", "\\midrule"]
for m in range(1, 13):
    L.append(f"{MES[m-1]} & {100*p.loc[m,'d_sol1']:.1f} & {100*p.loc[m,'d_enc1']:.1f} & {100*p.loc[m,'d_mat1']:.1f} \\\\")
L += ["\\midrule", f"N (events) & {n['d_sol1']:,} & {n['d_enc1']:,} & {n['d_mat1']:,} \\\\", "\\bottomrule", "\\end{tabular}",
      "\\tabnote{\\emph{Source:} SME childcare request record, 2010--2018 applications, with referral and enrollment dates through November 2019. "
      "\\emph{Sample:} one first application, first referral and first enrollment per child, counted when the event falls in calendar years 2011--2017. "
      "\\emph{Variables:} percent of each event type falling in each calendar month; columns sum to 100. "
      "\\emph{Exercise:} shares; descriptive.}",
      "\\end{table}"]
grava_tex(ROOT + "04_paper/assets/tables/appx/A_calendar.tex", "\n".join(L) + "\n", "A_calendar.tex")
print("\n".join(L[9:23]))
