# -*- coding: utf-8 -*-
# BUILD12 tabelas: le 03_build\build12\_staging\*.csv e 04_paper\referee_EE_2026-10\_revision\adjpairs\*.csv
# e escreve .tex em 03_build\build12\tables\. Nenhum numero novo alem dos CSVs.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
ROOT=NE_ROOT
STG=os.path.join(ROOT,r"03_build\build12\_staging"); TAB=os.path.join(ROOT,r"03_build\build12\tables")
ADJ=os.path.join(ROOT,r"04_paper\referee_EE_2026-10\_revision\adjpairs")
os.makedirs(TAB,exist_ok=True)
def m(x,d=2):
    if pd.isna(x): return "n.d."
    s=f"{x:,.{d}f}"; return f"${s}$".replace("$-","$-") if x<0 else (f"$+{s}$" if d>=2 else s)
def num(x,d=2):
    if pd.isna(x): return "n.d."
    return f"${x:.{d}f}$".replace("-","-") if x<0 else f"{x:.{d}f}"
def sgn(x,d=2):
    if pd.isna(x): return "n.d."
    return f"${x:+.{d}f}$"
def pct(x):
    if pd.isna(x): return "n.d."
    return f"{x:.0f}\\%"
def emit(name,label,cap,cols,lines,note):
    L=["% BUILD12. Descritivo. Gerado por 02_audit/build12_tables.py.","\\begin{table}[htbp]\\centering",
       f"\\caption{{{cap}}}",f"\\label{{tab:{label}}}"]
    if label=="adjpairs": L.append("\\label{tab:S3b_split}")   # S3b_split (2010-14) e a linha 1 do Painel B
    L+=["\\footnotesize","\\setlength{\\tabcolsep}{4pt}"]
    if label in ("adjpairs","enrolledbyage"):
        lines=["\\fitbox{%"]+lines+["}"]
    L+=lines
    L+=[f"\\tabnote{{{note}}}","\\end{table}"]
    open(os.path.join(TAB,name+".tex"),"w",encoding="utf-8").write("\n".join(L)+"\n"); print("tex:",name)

# ---------- T7: pares adjacentes ----------
A=pd.read_csv(os.path.join(ADJ,"adjpairs.csv"))
en=A[A["sample"].str.startswith("entrants")].set_index("pair"); al=A[A["sample"].str.startswith("all")].set_index("pair")
order=[("2010-2011","2010--2011"),("2011-2012","2011--2012"),("2012-2013","2012--2013$^{a}$"),("2013-2014","2013--2014$^{b}$")]
fixed=[("2010-2014","2010--2014"),("2011-2014","2011--2014"),("2012-2014","2012--2014"),("2010-2012","2010--2012"),("2010-2013","2010--2013")]
def row(p,lab):
    e=en.loc[p]; a=al.loc[p]
    sh=e.share_app if e.d_total<0 else np.nan
    return f"{lab} & {sgn(e.d_total)} & {sgn(e.d_app)} & {sgn(e.d_wait)} & {pct(sh)} & {sgn(a.d_total)} & {sgn(a.d_app)} & {sgn(a.d_ival)} & {pct(a.share_app)} \\\\"
hdr=["\\begin{tabular}{lrrrrrrrr}","\\toprule",
     " & \\multicolumn{4}{c}{Entrants (enrolled at or before 48 months)} & \\multicolumn{4}{c}{All applicants (first terminal event)} \\\\",
     "\\cmidrule(lr){2-5}\\cmidrule(lr){6-9}",
     "Birth cohorts & $\\Delta$ entry age & $\\Delta$ appl.\\ age & $\\Delta$ wait & Appl.\\ share & $\\Delta$ resol.\\ age & $\\Delta$ appl.\\ age & $\\Delta$ interval & Appl.\\ share \\\\",
     "\\midrule","\\multicolumn{9}{l}{\\emph{Panel A. Adjacent cohort pairs}}\\\\"]
body=[row(p,l) for p,l in order]+["\\midrule","\\multicolumn{9}{l}{\\emph{Panel B. Fixed base years}}\\\\"]+[row(p,l) for p,l in fixed]
emit("T7_adjpairs","adjpairs","Decomposition of the change in age at entry and at administrative resolution, every adjacent pair of birth cohorts and fixed base years",
 "",hdr+body+["\\bottomrule","\\end{tabular}"],
 "\\emph{Source:} SME childcare request record, 2010--2018 applications. \\emph{Sample:} left block, children of birth cohorts 2010--2014 who enrolled at or before 48 months (N = 85,602 in 2010 to 133,685 in 2014, as in Table~\\ref{tab:S3decomp}); right block, all applicants of the same cohorts with a first terminal event (N = 128,352 to 151,772, as in Table~\\ref{tab:P55res}). \\emph{Variables:} changes in cohort means, in months. Entry age $=$ application age $+$ wait (application to enrolment); resolution age $=$ application age $+$ interval to the first of referral, enrolment, aging out or withdrawal. The interval to resolution pools successful and unsuccessful exits and is not a waiting time. Appl.\\ share: change in application age as a percentage of the change in entry (resolution) age. \\emph{Exercise:} accounting identity in means, evaluated on each pair; descriptive. $^{a}$ The 2012--2013 pair spans the step in recorded referrals (110,205 in 2012 to 341,031 in 2013; Section~\\ref{sec:institutions}). $^{b}$ Entry age rises between 2013 and 2014 while application age falls, so the share is not defined (n.d.).")

# ---------- N1: aging out ----------
N1=pd.read_csv(os.path.join(STG,"N1_agingout.csv"))
lines=["\\begin{tabular}{lrrrrrr}","\\toprule",
 " & \\multicolumn{4}{c}{All applicants} & \\multicolumn{2}{c}{Eligible applicants} \\\\","\\cmidrule(lr){2-5}\\cmidrule(lr){6-7}",
 "Birth cohort & N & Aged out (\\%) & \\multicolumn{1}{c}{of which: applied} & \\multicolumn{1}{c}{of which: aged out} & N & Aged out (\\%) \\\\",
 " & & & \\multicolumn{1}{c}{after 47 months} & \\multicolumn{1}{c}{while eligible} & & \\\\","\\midrule"]
for _,r in N1.iterrows():
    lines.append(f"{int(r.cohort)} & {int(r.N_all):,} & {r.pct_aged_all:.1f} & {r.pct_late_and_aged:.1f} & {r.pct_elig_aged_of_all:.1f} & {int(r.N_elig):,} & {r.pct_aged_among_elig:.1f} \\\\")
lines+=["\\bottomrule","\\end{tabular}"]
emit("N1_agingout","agingout","Aging out of eligibility: applicants who applied after the limit versus eligible applicants who aged out unreferred","",lines,
 "\\emph{Source:} SME childcare request record. \\emph{Sample:} birth cohorts 2010--2014; all applicants with a first terminal event (as in Table~\\ref{tab:P55type}), and the eligible subset that applied at or before 47 months of age (the duration sample of Table~\\ref{tab:E1cohort}). \\emph{Variables:} aged out: first terminal event is reaching 47 months without referral. Children who first applied after 47 months have no eligible time and are recorded as aging out on the day they apply. The two middle columns partition the aged-out share of all applicants and sum to it up to rounding. \\emph{Exercise:} shares; descriptive. The paper's definition of aging out is the last column.")

# ---------- N2: siblings ----------
N2=pd.read_csv(os.path.join(STG,"N2_siblings.csv"))
lab={"All pairs (baseline, = tab:P4stage row 1)":"All pairs (baseline)",
 "Same-day joint registration":"Both children registered on the same day",
 "Excluding same-day joint registration":"Excluding same-day registration",
 "Registrations within 30 days of each other":"Both registered within 30 days of each other",
 "Excluding registrations within 30 days":"Excluding registrations within 30 days",
 "Older applied before younger's birth (= tab:P4stage last row)":"Older applied before the younger's birth",
 "Older applied on/after younger's birth":"Older applied on or after the younger's birth",
 "Same postcode for both children":"Same postcode for both children",
 "Spacing >= 9 months (log p4: -7.65)":"Birth spacing of 9 months or more",
 "Excl. within-30-day, same postcode, spacing >= 9":"Excl.\\ 30-day registration, same postcode, spacing $\\geq$ 9"}
lines=["\\begin{tabular}{lrrrrr}","\\toprule",
 "Sample of sibling pairs & Coef. & (SE) & Pairs & Median raw & Younger \\\\"," & & & & difference & earlier (\\%) \\\\","\\midrule"]
for _,r in N2.iterrows():
    lines.append(f"{lab[r['sample']]} & {sgn(r.coef)} & ({r.se:.2f}) & {int(r.pairs):,} & {sgn(r.raw_median_diff,0)} & {r.pct_younger_earlier:.1f} \\\\")
lines+=["\\bottomrule","\\end{tabular}"]
emit("N2_siblings","siblingsN2","Within-family difference in age at first application: joint registration, residential moves and spacing","",lines,
 "\\emph{Source:} SME childcare request record; guardian taxpayer identifier. \\emph{Sample:} guardians with exactly two children, both born 2010--2016 (79,893 pairs). \\emph{Variables:} age at first application, months. Same-day and 30-day: absolute difference between the two children's first application dates. Postcode: residential postcode recorded for each child. \\emph{Exercise:} Coef.\\ is the younger-minus-older coefficient from a regression of age at application on birth order with family and birth-year fixed effects, standard errors clustered by family (the specification of Table~\\ref{tab:S5_robustez}, row 2); because birth-year dummies absorb the cohort trend, it measures the younger--older gap beyond the common cohort profile. Median raw difference and Younger earlier: unadjusted younger-minus-older difference, which includes the cohort trend. Descriptive.")

# ---------- N3: district reweighting ----------
N3=pd.read_csv(os.path.join(STG,"N3_timing_reweighted.csv"))
lines=["\\begin{tabular}{lrrrr}","\\toprule",
 "Birth cohort & Unweighted & Children with & Reweighted to & Reweighted to \\\\"," & (all) & a district & 2010 district mix & 2016 district mix \\\\","\\midrule"]
for _,r in N3.iterrows():
    lines.append(f"{int(r.cohort)} & {r.raw_all:.3f} & {r.raw_with_district:.3f} & {r.reweighted_2010_district_mix:.3f} & {r.reweighted_2016_district_mix:.3f} \\\\")
lines+=["\\bottomrule","\\end{tabular}"]
W=pd.read_csv(os.path.join(STG,"N3_within_district_change.csv"))
emit("N3_district","districtmix","Share registered before 12 months among children registered before 24 months, holding the district composition fixed","",lines,
 f"\\emph{{Source:}} SME childcare request record; district from the residential postcode. \\emph{{Sample:}} children of birth cohorts 2010--2016 registered before 24 months (715,962; 98.6 percent with a district). \\emph{{Variables:}} share first registered before 12 months. \\emph{{Exercise:}} each cohort's district-specific shares are averaged with the district weights of the 2010 (or 2016) cohort, so that changes in where applicants live cannot move the series. The share rises between the 2010 and 2016 cohorts in all {len(W)} districts; the median within-district rise is {W.d_share_2010_2016.median():.3f} and the smallest {W.d_share_2010_2016.min():.3f}. Descriptive.")

# ---------- N4: enrolled by age ----------
N4=pd.read_csv(os.path.join(STG,"N4_enrolled_by_age.csv"))
def c(x): return "" if pd.isna(x) else f"{x:.1f}"
lines=["\\begin{tabular}{lrrrrrr}","\\toprule",
 " & & \\multicolumn{3}{c}{Enrolled before (\\% of births)} & \\multicolumn{2}{c}{Registered before (\\% of births)} \\\\","\\cmidrule(lr){3-5}\\cmidrule(lr){6-7}",
 "Birth cohort & Live births & 12 months & 24 months & 36 months & 12 months & 24 months \\\\","\\midrule"]
for _,r in N4.iterrows():
    lines.append(f"{int(r.cohort)} & {int(r.births):,} & {c(r.enr_lt12)} & {c(r.enr_lt24)} & {c(r.enr_lt36)} & {c(r.reg_lt12)} & {c(r.reg_lt24)} \\\\")
lines+=["\\bottomrule","\\end{tabular}"]
emit("N4_enrolled","enrolledbyage","Share of each birth cohort enrolled and registered by a given age","",lines,
 "\\emph{Source:} SME childcare request record (enrolment and first application dates); live births by year from the municipal vital statistics (SINASC/CEInfo). \\emph{Sample:} birth cohorts 2010--2017; a cell is reported only if the whole cohort reaches that age within the panel. \\emph{Variables:} numerator, children of the cohort first enrolled (registered) in municipal childcare before the stated age; denominator, live births in the municipality in the birth year. The two sources are not linked at the child level, so levels are approximate. \\emph{Exercise:} cohort shares; descriptive. Unlike the registered stock, these flows are indexed to the child's age and do not depend on when the snapshot is taken.")
print("OK build12_tables")
