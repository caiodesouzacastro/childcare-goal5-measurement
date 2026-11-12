# -*- coding: utf-8 -*-
# Monta os 10 floats do corpo (revisao pos-EE) a partir dos tabulars EXISTENTES, copiados verbatim
# de 04_paper\assets\tables\*.tex. Nenhum numero e redigitado: o script extrai os blocos tabular.
# Saida: 04_paper\assets\tables\body\B01..B10.tex
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, re; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from build12_tabclean import clean
T=(NE_ROOT + r"\04_paper\assets\tables")
OUT=os.path.join(T,"body"); os.makedirs(OUT,exist_ok=True)
def tab(name, k=0):
    s=open(os.path.join(T,name+".tex"),encoding="utf-8").read()
    blocks=re.findall(r"\\begin\{tabular\}.*?\\end\{tabular\}",s,flags=re.S)
    return clean(blocks[k])
def fit(b): return "\\fitbox{%\n"+b+"}"
def panel(t): return f"\\par\\medskip\\textbf{{{t}}}\\par\\smallskip"
def emit(fn,cap,labels,parts,note):
    L=["% Float do corpo (revisao pos-EE). Tabulars copiados verbatim por 02_audit/build12_bodyfloats.py.",
       "\\begin{table}[htbp]\\centering",f"\\caption{{{cap}}}"]+[f"\\label{{tab:{l}}}" for l in labels]+["\\footnotesize"]
    L+=parts+[f"\\tabnote{{{note}}}","\\end{table}"]
    open(os.path.join(OUT,fn),"w",encoding="utf-8").write("\n".join(L)+"\n"); print("ok",fn)
SRC="\\emph{Source:} SME childcare request record, 2010--2018 applications, with referral and enrolment dates through November 2019."

emit("B01_referral.tex","One-year referral and enrolment by birth cohort, with aging out as a competing risk",
 ["E1cohort","P2end"],
 [panel("Panel A. Referral as the terminal event"),tab("E1_cohort"),
  panel("Panel B. Referral versus enrolment as the terminal event"),tab("P2_endpoint")],
 SRC+" \\emph{Sample:} applicants of birth cohorts 2010--2016 with eligible time, that is, first application at or before 47 months of age (the duration sample; Table~\\ref{tab:P2rec} reconciles it with all applicants). \\emph{Variables:} time is measured in days from first application. ref$_{t}$ and CIF ref: cumulative incidence of referral by day $t$; age$_{365}$: cumulative incidence of aging out (reaching 47 months unreferred) by day 365; CIF enr, RMST enr: the same with enrollment as the terminal event; RMST: restricted mean days in the eligible queue within 365 days; Median: day on which referral incidence reaches 0.5. \\emph{Exercise:} Aalen--Johansen estimator with aging out as the competing event; descriptive. Panel B repeats the referral columns of Panel A for comparison.")

emit("B02_standardization.tex","One-year referral incidence holding the composition of applicants fixed",
 ["P3series","P3boot","P3decomp"],
 [panel("Panel A. Raw and standardized series"),fit(tab("P3_series")),
  panel("Panel B. Sampling uncertainty of the 2010--2016 change"),tab("P3_boot"),
  panel("Panel C. Exact decomposition of the raw change and sensitivity to the cell definition"),fit(tab("P3_decomp"))],
 SRC+" \\emph{Sample:} duration sample of Table~\\ref{tab:E1cohort}, birth cohorts 2010--2016. \\emph{Variables:} cumulative incidence of referral within 365 days (aging out competing). Applicant attributes: age at application, priority stratum, postcode-income quartile, district and semester of application (main cells); coarse cells use age, priority and income only; fine cells use eight age bins and month of application. Service environment: number of centres open within 2\\,km at the application date. \\emph{Exercise:} each cohort is reweighted to the 2013 cohort's joint distribution of the attributes in a cell, with weights trimmed at the 1st and 99th percentiles; $\\Delta$ is 2016 minus 2010. In Panel C, Appl.\\ comp.\\ $=$ Raw $-$ Appl., Service env.\\ $=$ Appl.\\ $-$ Both, and the three contributions add to the raw change. The final column is the standardized difference that remains after balancing observed attributes; unobserved determinants of referral, including any change in referral recording, are not held fixed. Panel B: 1,000 bootstrap replications resampling children within the 2010, 2013 and 2016 cohorts, weights recomputed in each; percentile interval. It reflects sampling variability only; the cell definition moves the standardized change between $+0.365$ and $+0.421$. Descriptive.")

emit("B03_robustness.tex","Robustness of the one-year referral incidence",
 ["P2rob","P2fu"],
 [panel("Panel A. Alternative competing events, windows and samples"),tab("P2_robust"),
  panel("Panel B. Current follow-up versus a common 365-day administrative window"),tab("P2_followup")],
 SRC+" \\emph{Sample:} duration sample of Table~\\ref{tab:E1cohort}, except where a column says otherwise. \\emph{Variables:} cumulative incidence of referral within 365 days; RMST in days. Panel A: Base, referral against aging out; +Withdr., recorded withdrawals added as a competing event; Excl.\\ break, applications dated July 2012 to December 2013 excluded; H1 only, applications in the first calendar semester; +Late appl., children who first applied after 47 months added as immediate aging out. Panel B: right block keeps only applications with a full 365-day window before the panel closes. \\emph{Exercise:} Aalen--Johansen estimator; descriptive.")

emit("B05_timing.tex","Registration before 12 months among children registered before 24 months, by birth cohort",
 ["P5timing","districtmix"],
 [panel("Panel A. All children registered before 24 months"),tab("P5_timing"),
  panel("Panel B. Holding the district composition fixed"),tab("N3_district")],
 "\\emph{Source:} SME childcare request record; district from the residential postcode. \\emph{Sample:} children of birth cohorts 2010--2016 first registered before 24 months; every cohort is observed over this whole window. \\emph{Variables:} share first registered before 12 months. \\emph{Exercise:} Panel A, unweighted shares; Panel B, district-specific shares averaged with the district weights of the 2010 or 2016 cohort, so that a change in where registrants live cannot move the series. The share rises between the 2010 and 2016 cohorts in all 96 districts (median within-district rise 0.407, smallest 0.244). The common window fixes exposure, not the composition of families who register within it. Descriptive.")

emit("B06_siblings.tex","Within-family differences in age at first application",
 ["S5_robustez","P4stage","siblingsN2"],
 [panel("Panel A. Birth-order coefficient under alternative cohort controls"),fit(tab("S5_robustez")),
  panel("Panel B. By the older sibling's position"),tab("P4_stage"),
  panel("Panel C. Joint registration, residential moves and spacing"),fit(tab("N2_siblings"))],
 "\\emph{Source:} SME childcare request record; guardian taxpayer identifier. \\emph{Sample:} guardians with exactly two children, both born 2010--2016 (79,893 pairs; 159,786 children); the identifier groups children by registered guardian, not by biological siblinghood. \\emph{Variables:} age at first application in months, except the two placebo rows of Panel A (female, Black). \\emph{Exercise:} regression of the outcome on birth order with family fixed effects and the stated cohort controls (birth-year dummies unless stated), standard errors clustered by family. Because the cohort controls absorb the common trend, Coef.\\ is the younger-minus-older gap beyond the cohort profile. Panel B rows (a)--(c) classify the older child's furthest stage on the day the younger applied, which selects on the younger's own timing; the last row, older applied before the younger was born, does not. Panel C: same-day and 30-day refer to the absolute difference between the two children's first application dates; median raw difference and share with the younger earlier are unadjusted and include the cohort trend. Descriptive.")

emit("B08_nonentrants.tex","Decomposition of the change in age at entry when children who never enter are included",
 ["E5"],
 [tab("E5_manski")],
 "\\emph{Source:} SME childcare request record. \\emph{Sample:} birth cohorts 2010 and 2014. Row 1: children who enrolled at or before 48 months (as in Table~\\ref{tab:adjpairs}). Rows 2--3 add applicants of the cohort who reached 47 months without a referral (27.4 percent of 2010-cohort applicants and 5.2 percent in 2014; Table~\\ref{tab:D4}). \\emph{Variables:} changes in mean age at application and at entry, months. Entry age is undefined for a child who never enters, so it is imputed at two extremes: the 48-month ceiling on age at entry, or the child's age at application (no wait). \\emph{Exercise:} accounting identity in means; the two rows are extreme imputations, not bounds on an estimand. Both imputations give an application share above 100 percent, that is, a waiting component of the opposite sign: the sign depends on whether non-entrants are counted, not on how they are imputed. Descriptive.")

emit("B10_sme.tex","What the municipal education secretariat publishes about childcare demand",
 ["SMEpub","SMEshort"],
 [fit(tab("P7_sme_indicators"))],
 "\\emph{Source:} recurring public products of the S\\~ao Paulo municipal education secretariat: Demanda Escolar reporting \\citep{sme_demanda_escolar}, the S\\~ao Paulo Open Data Portal series on registered demand and enrolments (EOL) \\citep{sme_dados_abertos}, a representative bimonthly district release \\citep{sme_demanda_junho2026}, and the ``Vaga na Creche'' platform \\citep{sme_vaga_creche}; all accessed 24 July 2026. \\emph{Sample:} products current in July 2026 and the historical series. \\emph{Variables:} \\checkmark\\ reported, --- not reported. Duration: the childcare stock is split only into waits up to and over 30 days. None of the products reports the distribution of age at application, an exact or mean waiting time, or the entry, referral and exit flows that generate the stock. The historical series in Figure~\\ref{fig:F10} is quarterly; the current release is bimonthly. \\emph{Exercise:} inventory of published indicators.")
