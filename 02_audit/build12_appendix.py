# -*- coding: utf-8 -*-
# 30/10/2026 (rodada legendas-instala-2026-10-30): os titulos e as notas das exibicoes (\caption e \tabnote) sao
# TEXTO DO AUTOR, de 30/10/2026, gravado nos .tex. Nao regravar os .tex gerados por este script sem autorizacao do autor.
# Neste script so os titulos foram atualizados; as notas, montadas por concatenacao de constantes e trechos, continuam
# com o texto anterior. A trava (trava_legenda.py, 30/10/2026) impede que uma nova execucao grave essas notas antigas
# por cima das do autor: \caption e \tabnote que difiram do arquivo nao sao regravados, salvo com NE_SOBRESCREVER_LEGENDA=1.
# Monta os floats do Apendice A (revisao pos-EE): tabulars copiados verbatim (com limpeza tipografica
# que nao altera valores) e notas padronizadas Source/Sample/Variables/Exercise. Fusoes aprovadas (S, agente 7):
# T2a+T2b+T2c; S6a+S6b; S6c+S6d; S8a+S8c; E2+P2grad; E1d+R2b_km; T11+T12; C2 absorve N2 (rotulo).
# Saida: 04_paper\assets\tables\appx\*.tex e um indice appx_index.csv (label -> arquivo).
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, re, csv; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from build12_tabclean import clean
from trava_legenda import grava_tex  # trava das legendas (30/10/2026)
# PAPER_ROOT (opcional, 26/10/2026): redireciona leitura e escrita para uma copia de 04_paper (teste de sincronia).
T=os.path.join(os.environ.get("PAPER_ROOT",(NE_ROOT + r"\04_paper")),"assets","tables")
OUT=os.path.join(T,"appx"); os.makedirs(OUT,exist_ok=True)
def tab(name,k=0):
    s=open(os.path.join(T,name+".tex"),encoding="utf-8").read()
    return clean(re.findall(r"\\begin\{tabular\}.*?\\end\{tabular\}",s,flags=re.S)[k])
def fit(b): return "\\fitbox{%\n"+b+"}"
def panel(t): return f"\\par\\medskip\\textbf{{{t}}}\\par\\smallskip"
INDEX=[]
def emit(fn,cap,labels,parts,note):
    L=["% Apendice A (revisao pos-EE). Gerado por 02_audit/build12_appendix.py; tabulars verbatim.",
       "\\begin{table}[htbp]\\centering",f"\\caption{{{cap}}}"]+[f"\\label{{tab:{l}}}" for l in labels]+["\\footnotesize"]
    L+=parts+[f"\\tabnote{{{note}}}","\\end{table}"]
    grava_tex(os.path.join(OUT,fn),"\n".join(L)+"\n",fn); INDEX.append((fn,labels))
REQ="\\emph{Source:} SME childcare request record, 2010--2018 applications, with referral and enrollment dates through November 2019."
PROF="\\emph{Source:} municipal class profile (offered places, classes and enrollment by centre, band and semester), 2013--2019."
SIN="live births by district of residence from the municipal health secretariat's vital statistics (SINASC)"
MODE="Direct: municipally operated centres; Partner: the contracted network, partner-run and indirect centres together."

emit("A_T2.tex","Authorized childcare places, centers, and classes in municipal and contracted centers by age band and contractual mode, first semester of each year",
 ["T2a_capacidade","T2b_nescolas","T2c_nturmas"],
 [panel("Panel A. Authorized places"),tab("T2a_capacidade"),panel("Panel B. Centres with at least one childcare class"),tab("T2b_nescolas"),
  panel("Panel C. Childcare classes"),tab("T2c_nturmas")],
 PROF+" \\emph{Sample:} all municipal and contracted childcare centres, first semester of each year; 2018S1 is a June snapshot; second-semester columns are omitted. \\emph{Variables:} "+MODE+" Authorized places are offered places; enrollment is never used. \\emph{Exercise:} totals; descriptive.")
emit("A_T7a.tex","Centers with at least one childcare class in the first-semester profile, by contractual mode",["T7a_ceis"],[tab("T7a_ceis")],
 PROF+" \\emph{Sample:} centres with at least one childcare class in the first-semester profile. \\emph{Variables:} "+MODE+" \\emph{Exercise:} counts; descriptive.")
emit("A_T5c.tex","Enrolled children by the center's contractual mode and year of enrollment (row \\%)",["T5c_modal"],[tab("T5c_modal")],
 REQ+" \\emph{Sample:} enrolled children by year of enrollment. \\emph{Variables:} contractual mode of the centre of enrollment: direct, indirect, partner; rows sum to 100. \\emph{Exercise:} shares; descriptive.")
emit("A_T7b.tex","Openings and closures of partner childcare contracts",["T7b_aber_fech"],[tab("T7b_aber_fech")],
 "\\emph{Source:} municipal file of partner agreements (contracted places, start and end dates). \\emph{Sample:} partner centres, 2013--2019. \\emph{Variables:} an opening is a centre's first contract; a closure is a termination with places attached; net places $=$ places opened $-$ places closed. \\emph{Exercise:} counts; descriptive.")
emit("A_T6c.tex","Childcare classes per centre by age band and contractual mode, first semester",["T6c_turmas_por_escola"],[fit(tab("T6c_turmas_por_escola"))],
 PROF+" \\emph{Sample:} centres with at least one class in the band. \\emph{Variables:} mean number of classes per centre. "+MODE+" \\emph{Exercise:} means; descriptive.")
emit("A_S6ab.tex","Live births in S\\~ao Paulo, total and by district income quartile, 2006--2018",["S6a_nascidos_municipio","S6b_nascidos_renda"],
 [panel("Panel A. Municipality"),tab("S6a_nascidos_municipio"),panel("Panel B. By district income quartile"),fit(tab("S6b_nascidos_renda"))],
 "\\emph{Source:} "+SIN+", 2006--2018. \\emph{Sample:} 96 districts; the ``unknown district'' row and the partial final year of the source are excluded. \\emph{Variables:} live births by year; district income quartiles by mean household income in the 2010 Census (Q1 lowest). \\emph{Exercise:} totals; descriptive.")
emit("A_S6cd.tex","Authorized places per eligible child and the decomposition of its change, 2013--2019",["S6c_cobertura","S6d_decomp"],
 [panel("Panel A. Places per eligible child"),tab("S6c_cobertura"),panel("Panel B. Decomposition of the 2013--2019 change"),tab("S6d_decomp")],
 PROF+" Births: "+SIN+". \\emph{Sample:} first semesters of 2013--2019, municipality and district income quartiles. \\emph{Variables:} eligible pool in year $Y$ $=$ live births in $Y$, $Y-1$, $Y-2$ and $Y-3$; coverage $=$ authorized places $/$ pool, first semester. \\emph{Exercise:} Panel B holds the pool at its 2013 level for the capacity component and capacity at its 2019 level for the pool component; the split depends on this order. Descriptive.")
emit("A_T7c.tex","Authorized infant-band places per application, by sector income quartile",["T7c_percap"],[tab("T7c_percap")],
 PROF+" Applications: SME childcare request record. \\emph{Sample:} educational sectors, 2013--2018. \\emph{Variables:} authorized places in the two infant bands, first semester, divided by childcare applications recorded in the sector and year; median across sectors within each sector income quartile. \\emph{Exercise:} ratios; descriptive.")
emit("A_T6b.tex","Enrollment relative to authorized places, by age band and semester",["T6b_ratio"],[fit(tab("T6b_ratio"))],
 PROF+" \\emph{Sample:} all childcare classes; 2018S1 is a mid-year snapshot; second-semester columns are omitted. \\emph{Variables:} total enrollment divided by total offered places. \\emph{Exercise:} ratio; descriptive. Enrollment enters only the numerator, never the definition of capacity.")
emit("A_T6a.tex","Childcare classes at and above the module (authorized class size) by age band, 2016 and 2017",["T6a_modulo"],[fit(tab("T6a_modulo"))],
 PROF+" \\emph{Sample:} childcare classes, 2016 and 2017. \\emph{Variables:} module: authorized class size (modal values 7, 9, 12 and 25 by band); at capacity: enrollment equals the module; above: enrollment exceeds it. \\emph{Exercise:} shares of classes; descriptive.")
emit("A_C2.tex","Number of childcare centers within 2\\,km of the child's postcode at first request, counting all centers and only those open on the request date, 2006--2018",["C2","N2"],[fit(tab("C2_grid_dyn"))],
 REQ+" Centres: municipal register with opening dates. \\emph{Sample:} first applications, one per child (1,524,560), 2006--2018. \\emph{Variables:} st: all centres within 2\\,km of the postcode, whether or not open at the application date; dy: centres within 2\\,km already open at the application date; p10--p90: percentiles; p50: median. \\emph{Exercise:} distributions; descriptive. The static columns reproduce the previous static-count table.")
emit("A_T5a.tex","Rank of the enrollment center among centers ordered by distance from the child's postcode, enrolled children by year (\\%)",["T5a_rank"],[fit(tab("T5a_rank"))],
 REQ+" Coordinates: register of 2,313 geolocated centres. \\emph{Sample:} enrolled children, by year. \\emph{Variables:} rank of the centre of enrollment among centres near the postcode ordered by distance (1 $=$ nearest); Outside: beyond about 2\\,km or without coordinates. \\emph{Exercise:} shares; descriptive.")
emit("A_T11T12.tex","Published childcare enrollment and registered demand, 2006--2017",["T11","T12"],
 [panel("Panel A. December snapshot"),fit(tab("T11_estoque_demanda")),panel("Panel B. Registered demand by quarterly snapshot"),tab("T12_sazonalidade")],
 "\\emph{Source:} S\\~ao Paulo open data, historical series of registered demand and enrollment, 2006--2017, summed over 96 districts. \\emph{Sample:} municipal childcare, all districts; Panel A at the December snapshot of each year. \\emph{Variables:} enrollment: childcare enrollment; registered demand: stock of children on the childcare waiting list; Panel A also adds preferential demand. Panel B: the stock at the March, June, September and December snapshots (no March figure for 2006). \\emph{Exercise:} levels as published. December 2013 enrollment (214,460) matches the authorized places of 2013S1 (214,561).")
emit("A_N1lotes.tex","First applications sharing the same timestamp to the second, by year of application",["N1"],[fit(tab("N1_lotes"))],
 REQ+" \\emph{Sample:} first application per child (1,524,560). \\emph{Variables:} share of first applications whose timestamp, recorded to the second, is shared by at least $k$ first applications anywhere in the city in that second, $k = 2, 10, 50, 100$. \\emph{Exercise:} shares; descriptive.")
emit("A_Rcap.tex","Authorized capacity measured by offered places and by classes times the statutory module",["R_capcheck"],[fit(tab("R_capcheck"))],
 PROF+" \\emph{Sample:} first semesters of 2013 and 2019. \\emph{Variables:} (i) offered places; (ii) classes multiplied by the statutory module of the band (7, 9, 12, 25), independent of enrollment by construction. \\emph{Exercise:} growth of each measure; the ratio of the two lies between 0.837 and 0.994 across band-semester cells. Descriptive.")
emit("A_P5queue.tex","Reconstruction of the queue stock from first-application flows, and its gap to the published series",["P5queue"],[fit(tab("P5_queue"))],
 REQ+" Published series as in Table~\\ref{tab:T11}. \\emph{Sample:} first applications, one per child. \\emph{Variables:} Q$_0$: stock at 1 January; new: first applications in the year; ref, aged, des: first exits by referral, aging out at 47 months and recorded withdrawal; Q$_t$: year-end stock; int.: internal residual of the identity; off: published December stock. \\emph{Exercise:} Q$_t$ $=$ Q$_{t-1}$ $+$ new $-$ ref $-$ aged $-$ des, closed from the flows themselves (the residual is not a plug). Descriptive.")
emit("A_E1d.tex","Kaplan--Meier diagnostics that censor aging out",["E1d","R2b_km"],
 [panel("Panel A. Net Kaplan--Meier and competing-risks medians, by birth cohort"),tab("E1_kmnet"),
  panel("Panel B. Kaplan--Meier survivor function, by year of application"),tab("R2b_km")],
 REQ+" \\emph{Sample:} Panel A, duration sample of Table~\\ref{tab:E1cohort}; Panel B, applications by year. \\emph{Variables:} days from application to referral; S($t$): share not yet referred at day $t$. \\emph{Exercise:} Kaplan--Meier with aging out treated as censoring, which estimates a hypothetical distribution in which no child ages out; children never referred are censored at the end of the panel; blank cells lack full follow-up. Reported as a diagnostic only.")
emit("A_E1year.tex","Referral and aging out by year of application, aging out as a competing risk",["E1year"],[fit(tab("E1_year"))],
 REQ+" \\emph{Sample:} applications 2010--2017 with eligible time (2018 excluded for truncation). \\emph{Variables:} as in Table~\\ref{tab:E1cohort}. \\emph{Exercise:} Aalen--Johansen estimator; descriptive.")
emit("A_E2.tex","Income gradient in one-year referral by birth cohort and postcode income quartile",["E2","P2grad"],
 [panel("Panel A. Referral incidence and restricted mean time"),fit(tab("E2_renda")),panel("Panel B. Full series and the gap between quartiles"),fit(tab("P2_gradient"))],
 REQ+" Income: mean household income of the postcode's census tract (2010 Census), not household income. \\emph{Sample:} duration sample of Table~\\ref{tab:E1cohort}. \\emph{Variables:} cumulative incidence of referral within 365 days by postcode income quartile (Q1 lowest); RMST in days; Q4$-$Q1 gap in percentage points. \\emph{Exercise:} Aalen--Johansen estimator with aging out competing; descriptive.")
emit("A_T1.tex","Characteristics of first requests by request year, including postcode income, enrollment within 365 days, and children never enrolled",["T1_fila"],[fit(tab("T1_fila"))],
 REQ+" \\emph{Sample:} first application per child (1,524,560); the Total column includes 51,106 applications from 2006--2009; odd years are omitted for space. \\emph{Variables:} postcode income: mean household income of the census tract; enrolled within 365 days and never enrolled: enrollment in any municipal centre before the end of the panel. \\emph{Exercise:} shares, medians; descriptive.")
emit("A_T4d.tex","Children never enrolled compared with enrolled children",["T4d_never"],[tab("T4d_never")],
 REQ+" \\emph{Sample:} 203,715 children never enrolled and 1,320,845 enrolled. \\emph{Variables:} IPVS: S\\~ao Paulo state social-vulnerability index group of the postcode (1 to 6); centres within 2\\,km: static count. \\emph{Exercise:} difference in means (never enrolled minus enrolled) with standard errors from group variances. The groups differ in year of application and by construction in age at application and priority, so the differences are not interpreted. Descriptive.")
emit("A_P2rec.tex","Birth-cohort applicants and the duration sample",["P2rec"],[tab("P2_reconcile")],
 REQ+" \\emph{Sample:} birth cohorts 2010--2016. \\emph{Variables:} Total: children with a valid first application; Duration: those with non-negative eligible time; Excl.$>$47m: children whose age at first application exceeds 47 whole months. \\emph{Exercise:} counts. Adding the excluded children as immediate aging out widens the referral gain (Table~\\ref{tab:P2rob}). Total minus Duration (22,052 in 2010) exceeds Excl.$>$47m (20,322) because Table~\\ref{tab:agingout} dates the limit by day (application after the day the child turns 47 months), whereas this column uses age at application in whole months; the day-based count is the one used in Table~\\ref{tab:agingout}.")
emit("A_P55type.tex","How applications ended, by birth cohort (percent of applicants)",["P55type"],[tab("P55_restype")],
 REQ+" \\emph{Sample:} all applicants of birth cohorts 2010--2014 with a first terminal event, including those who first applied after 47 months. \\emph{Variables:} first terminal event: referral, enrollment without a recorded referral, aging out at 47 months, recorded withdrawal. Children who first applied after 47 months are counted as aging out on the day they apply (Table~\\ref{tab:agingout}). \\emph{Exercise:} shares; descriptive.")
emit("A_P5cov.tex","Share of each birth cohort registered by 24, 36 and 47 months",["P5cov"],[tab("P5_coverage")],
 REQ+" Births: "+SIN+". \\emph{Sample:} birth cohorts 2010--2014, each fully observed at every horizon. \\emph{Variables:} children with a first application before the stated age, as a share of live births. \\emph{Exercise:} shares; descriptive.")
emit("A_S8ac.tex","Share of each birth cohort ever registered, and the share of registrants who registered before 12 months",["S8a","S8c"],
 [panel("Panel A. Ever registered"),tab("S8a"),panel("Panel B. Registered before 12 months among the ever registered"),tab("S8c")],
 REQ+" Births: "+SIN+". \\emph{Sample:} birth cohorts 2010--2016. \\emph{Variables:} ever registered: at least one application observed in the panel, as a share of live births; Panel B ratio $=$ share registered before 12 months $/$ share ever registered. \\emph{Exercise:} shares. ``Ever'' is right-censored for recent cohorts and the Panel B denominator accumulates over unequal follow-up; Table~\\ref{tab:P5timing} gives the common-age version. Descriptive.")
emit("A_S8b.tex","Share of each birth cohort ever registered, by district income quartile",["S8b"],[tab("S8b")],
 REQ+" Births: "+SIN+". \\emph{Sample:} birth cohorts 2010--2016; children whose postcode maps to a district (98 percent). \\emph{Variables:} numerator, children of the cohort ever registered whose postcode lies in a district of the quartile; denominator, live births in districts of that quartile (Q1 lowest, by 2010 Census mean household income). Because the two sources are not linked at the child level, the share can exceed 100 percent in some districts. \\emph{Exercise:} shares; descriptive.")
emit("A_C6.tex","District enrollment growth and registration before 12 months",["C6"],[tab("C6_local_fix")],
 REQ+" District enrollment: S\\~ao Paulo open data (Table~\\ref{tab:T11}). \\emph{Sample:} district $\\times$ birth cohort cells, 2010--2016 (672 cells, 96 districts). \\emph{Variables:} outcome, share of the cell's applicants who applied before 12 months; regressor, log growth in December childcare enrollment in the district (not authorized capacity), contemporaneous, lagged and led one year. \\emph{Exercise:} regression with district and cohort fixed effects, standard errors clustered by district. Descriptive.")
emit("A_P4dist.tex","Distribution of the within-family difference in age at first application",["P4dist"],[tab("P4_dist")],
 REQ+" Guardian taxpayer identifier. \\emph{Sample:} 79,893 pairs of children of guardians with exactly two children born 2010--2016. \\emph{Variables:} younger-minus-older difference in age at first application, months, in bands. \\emph{Exercise:} shares of pairs; median $-10$, interquartile range $-20$ to $-1$. The raw difference includes the cohort trend. Descriptive.")
emit("A_P4guard.tex","Guardian identifier: validation and selectivity of the sibling sample",["P4guard"],[tab("P4_guardian")],
 REQ+" \\emph{Sample:} as in Table~\\ref{tab:P4dist}. \\emph{Variables:} impossible spacing: two singleton births under nine months apart (twins or registration error); postcode change between the two children; income quartile and priority compared with all applicants. \\emph{Exercise:} counts and shares. Excluding impossible spacing, the birth-order coefficient is $-7.65$ (0.11); further variants are in Table~\\ref{tab:siblingsN2}.")
emit("A_C4.tex","Enrollment and re-referral by age at application and speed of referral",["C4"],[tab("C4_oferta_rapida")],
 REQ+" \\emph{Sample:} referred children. \\emph{Variables:} speed: days from application to first referral; Mat.\\ rate: percent enrolled after referral; Med.\\ age at mat.: median age at enrollment, months; Re-ref.: among children who recorded a formal refusal, percent referred again. \\emph{Exercise:} cell shares; descriptive.")
emit("A_S3decomp.tex","Mean age at application, wait and age at entry, and three observation windows",["S3decomp"],
 [panel("Panel A. Cohort means, entrants, birth cohorts 2010--2014"),tab("S3decomp",0),panel("Panel B. Change in age at entry under three windows and two definitions of the interval"),fit(tab("S3decomp",1))],
 REQ+" \\emph{Sample:} Panel A, children who enrolled at or before 48 months; Panel B, as stated in each row. \\emph{Variables:} months since birth; enrollment interval: application to enrollment; referral interval: application to first referral. \\emph{Exercise:} accounting identity in means (residual at most 0.04 months). Windows indexed by year of application mix timing with the absorption of older children queued before 2010. Descriptive.")
emit("A_P55res.tex","Age at administrative resolution, all applicants, birth cohorts 2010--2014",["P55res"],[tab("P55_resolution")],
 REQ+" \\emph{Sample:} as in Table~\\ref{tab:P55type}. \\emph{Variables:} resolution: first of referral, enrollment, aging out at 47 months or recorded withdrawal; interval: application to resolution, which pools successful and unsuccessful exits and is not a waiting time. \\emph{Exercise:} accounting identity in means (maximum residual 0.02 months). Descriptive.")
emit("A_D4.tex","Selection into the entrant sample, by birth cohort",["D4"],[tab("D4_selection")],
 REQ+" \\emph{Sample:} all children of birth cohorts 2010--2014 with a first application. \\emph{Variables:} aged out: reached 47 months unreferred, including children who first applied after that age; enr$\\le$48, ref$\\le$48: enrolled or referred at or before 48 months; wait\\_enr, wait\\_ref: mean wait to enrollment or referral, months, in those groups. \\emph{Exercise:} shares and means; descriptive. The aged-out share counts every child without a referral by 47 months, so, unlike Table~\\ref{tab:agingout}, it also includes children who withdrew before that age.")

with open(os.path.join(OUT,"appx_index.csv"),"w",encoding="utf-8",newline="") as f:
    w=csv.writer(f); [w.writerow([fn,";".join(l)]) for fn,l in INDEX]
print(len(INDEX),"appendix floats")
# Pipeline completo (OQ-34, 26/10/2026). Este script sozinho gera a versao pre-Fase 2 (grafia britanica, A_C4/A_T4d de
# 2010-2018, sem as copias do corpo). Com --full, roda em seguida as etapas que produzem os arquivos em uso:
# grafia americana (build12_spelling.py, decisao D8), tabelas da janela (build15_appx.py: A_calendar 2013-2017,
# A_C4v2, A_T4dv2, A_decompyear, A_covtype) e reestruturacao (build15_struct.py: copias A_full_* e appx_index.csv).
# build13_calendar_table.py nao entra: sua A_calendar (2011-2017) e substituida pela do build15_appx.py.
if "--full" in sys.argv:
    import subprocess, glob
    H=os.path.dirname(os.path.abspath(__file__))
    for cmd in ([sys.executable,os.path.join(H,"build12_spelling.py")]+sorted(glob.glob(os.path.join(OUT,"*.tex"))),
                [sys.executable,os.path.join(H,"build15_appx.py")],[sys.executable,os.path.join(H,"build15_struct.py")],
                [sys.executable,os.path.join(H,"build16_tabfix.py")]):
        r=subprocess.run(cmd,env=os.environ.copy())
        if r.returncode: sys.exit("falhou: "+os.path.basename(cmd[1]))
