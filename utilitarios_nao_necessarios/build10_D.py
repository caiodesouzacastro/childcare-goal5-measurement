# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD10-D - a correcao de censura do C1 e a decomposicao 9.37/93/7 da §5.
# Verifica se a censura por idade afeta a decomposicao (nao afeta: e sobre
# matriculadas, espera observada), reproduz, e da a versao por encaminhamento
# e o diagnostico de selecao (o unico canal por que C1 e relevante).
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
ROOT=NE_ROOT
B1=os.path.join(ROOT,r"03_build\build01\_staging")
OUT=os.path.join(ROOT,r"03_build\build10"); TAB=os.path.join(OUT,"tables")
STG=os.path.join(OUT,"_staging"); EP=pd.Timestamp("1960-01-01"); PANEL=pd.Timestamp("2019-11-28")
LOG=[]; FACTS=[]
def S(x): LOG.append(str(x)); print(x)
def emit(name,cap,note,cols,header,body,label=None):
    label=label or name
    L=["% BUILD10-D. Descritivo.","\\begin{table}[htbp]\\centering",f"\\caption{{{cap}}}",
       f"\\label{{tab:{label}}}","\\footnotesize","\\setlength{\\tabcolsep}{4pt}",
       f"\\begin{{tabular}}{{{cols}}}","\\toprule"," & ".join(header)+" \\\\","\\midrule"]
    for r in body: L.append("\\midrule" if r=="MID" else " & ".join(r)+" \\\\")
    L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
    open(os.path.join(TAB,name+".tex"),"w",encoding="utf-8").write("\n".join(L)+"\n"); print("tex:",name)

cm=pd.read_feather(os.path.join(B1,"child_master.feather"),
    columns=["cd_aluno_sme","ano_sol","ano_nasc","mes_nasc","idade_sol","idade_ent",
             "espera_m","ever_mat","dt_sol"])
sp=pd.read_parquet(os.path.join(STG,"spine.parquet"),columns=["cd_aluno_sme","d_enc1"])
d=cm.merge(sp,on="cd_aluno_sme",how="left")
d["d_sol"]=EP+pd.to_timedelta(d.dt_sol,unit="D")
d["d_birth"]=pd.to_datetime(dict(year=d.ano_nasc,month=d.mes_nasc,day=1),errors="coerce")
d["d_age47"]=d["d_birth"]+pd.DateOffset(months=47)
# idade e espera ate o ENCAMINHAMENTO (observada p/ encaminhados)
d["age_ref"]=(d.d_enc1.dt.year-d.ano_nasc)*12+(d.d_enc1.dt.month-d.mes_nasc)
d["wait_ref"]=(d.d_enc1-d.d_sol).dt.days/30.44
d["referred"]=d.d_enc1.notna()&(d.d_enc1>=d.d_sol)

def decomp(df,grp,val_ent,val_sol,val_wait,cohorts):
    rows=[]
    for c in cohorts:
        s=df[df[grp]==c]
        rows.append({"c":c,"N":len(s),"ent":s[val_ent].mean(),
                     "sol":s[val_sol].mean(),"wait":s[val_wait].mean()})
    R=pd.DataFrame(rows)
    a,b=R.iloc[0],R.iloc[-1]
    d_ent=b.ent-a.ent; d_sol=b.sol-a.sol; d_wait=b.wait-a.wait
    resid=d_ent-(d_sol+d_wait)
    return R,d_ent,d_sol,d_wait,resid

# ============ D1/D2: decomposicao por coorte de nascimento 2010-2014 ============
COH=list(range(2010,2015))
S("## Enrolled-only (paper): entry = matricula age, wait = mat-sol (OBSERVADA)")
mEn=d[(d.ever_mat==1)&(d.idade_ent<=48)]
Ren,de,ds,dw,rr=decomp(mEn,"ano_nasc","idade_ent","idade_sol","espera_m",COH)
S(f"  d_ent={de:.2f} sol={ds:.2f}({ds/de:.1%}) wait={dw:.2f}({dw/de:.1%}) resid={rr:.3f}")
for _,r in Ren.iterrows(): S(f"    {int(r.c)}: N={int(r.N):,} ent={r.ent:.2f} sol={r.sol:.2f} wait={r.wait:.2f}")

S("\n## Referral-based (aligned w/ identity text 'application to referral'): entry = referral age, wait = sol->enc (OBSERVADA p/ encaminhadas)")
mRef=d[d.referred&(d.age_ref<=48)]
Rref,de2,ds2,dw2,rr2=decomp(mRef,"ano_nasc","age_ref","idade_sol","wait_ref",COH)
S(f"  d_ent={de2:.2f} sol={ds2:.2f}({ds2/de2:.1%}) wait={dw2:.2f}({dw2/de2:.1%}) resid={rr2:.3f}")
for _,r in Rref.iterrows(): S(f"    {int(r.c)}: N={int(r.N):,} refage={r.ent:.2f} sol={r.sol:.2f} wait={r.wait:.2f}")

# ============ D3/D4 diagnostico de selecao (o unico canal de C1) ============
S("\n## Selecao por coorte: aging-out (nunca entra) e taxa de matricula<=48m")
sel=[]
for c in COH:
    s=d[d.ano_nasc==c]
    # envelhece aos 47m antes de encaminhamento (competing, sem censura de painel)
    aged=((s.d_enc1.isna())|(s.d_enc1>s.d_age47))&(s.d_age47<=PANEL)
    entered48=(s.ever_mat==1)&(s.idade_ent<=48)
    ref48=s.referred&(s.age_ref<=48)
    sel.append({"c":c,"N":len(s),"frac_aged":100*aged.mean(),
                "frac_enr48":100*entered48.mean(),"frac_ref48":100*ref48.mean(),
                "wait_enr":s.loc[entered48,"espera_m"].mean(),
                "wait_ref":s.loc[ref48,"wait_ref"].mean()})
Sel=pd.DataFrame(sel)
S("  coorte | %aged-out %enr<=48 %ref<=48 | wait_enr wait_ref")
for _,r in Sel.iterrows():
    S(f"   {int(r.c)}  |  {r.frac_aged:5.1f}   {r.frac_enr48:5.1f}   {r.frac_ref48:5.1f}  | {r.wait_enr:6.2f}  {r.wait_ref:6.2f}")

# tabela D1: lado a lado antiga vs nova
body=[
 ["Enrolled, entry=enrolment (paper's headline)",f"{de:.2f}",f"{ds:.2f}",f"{100*ds/de:.0f}\\%",f"{dw:.2f}",f"{100*dw/de:.0f}\\%",f"{rr:.3f}"],
 ["Referred, entry=referral (application$\\to$referral)",f"{de2:.2f}",f"{ds2:.2f}",f"{100*ds2/de2:.0f}\\%",f"{dw2:.2f}",f"{100*dw2/de2:.0f}\\%",f"{rr2:.3f}"],
]
emit("D1_decomp",
 "Decomposition of the fall in age at entry, birth cohorts 2010--2014: enrolment-based "
 "(paper) vs.\\ referral-based, both with fully observed waits",
 "Means over the stated population. Row 1 (the paper's headline): enrolled children entering "
 "at or before 48 months; wait = enrolment date $-$ application date. Row 2: referred children "
 "referred at or before 48 months of age; wait = referral date $-$ application date. In both "
 "populations the wait is \\emph{observed} (the child was served), so the age-of-eligibility "
 "censoring of Section~C1 does not enter; the identity age at entry $=$ age at application $+$ "
 "wait is exact in means (residual column).",
 "lrrrrrr",
 ["Population / entry definition","$\\Delta$ entry","$\\Delta$ appl.","\\% appl.","$\\Delta$ wait","\\% wait","Resid."],
 body,label="D1")

# tabela D4 selecao
body=[[str(int(r.c)),f"{r.frac_aged:.1f}",f"{r.frac_enr48:.1f}",f"{r.frac_ref48:.1f}",
       f"{r.wait_enr:.2f}",f"{r.wait_ref:.2f}"] for _,r in Sel.iterrows()]
emit("D4_selection",
 "Selection into the enrolled decomposition sample, by birth cohort",
 "\\%\\,aged-out: share of the cohort reaching 47 months unreferred (never enters, excluded "
 "from the decomposition). \\%\\,enr$\\le$48 and \\%\\,ref$\\le$48: share enrolled / referred at "
 "or before 48 months. wait\\_enr / wait\\_ref: mean observed wait (months) among those "
 "populations. Early cohorts lose more members to aging out, so their enrolled sample is more "
 "selected on short waits.",
 "lrrrrr",
 ["Cohort","\\%\\,aged-out","\\%\\,enr$\\le$48","\\%\\,ref$\\le$48","wait\\_enr","wait\\_ref"],
 body,label="D4")

# ============ D5: tres janelas ============
# ROWS 1-2 (por ano) usam matriculadas SEM corte idade_ent<=48 (como no build02);
# ROW 3 (coorte de nascimento) aplica idade_ent<=48 (como no build03_cohort).
S("\n## D5: tres janelas")
mEnAll=d[d.ever_mat==1]                 # matriculadas, sem corte (rows 1-2)
mRefAll=d[d.referred]                   # encaminhadas, sem corte
def window(df,grp,cohorts,ent,wait,lab):
    R,de,ds,dw,rr=decomp(df,grp,ent,"idade_sol",wait,cohorts)
    S(f"  {lab}: d_ent={de:.2f} appl={ds/de:.0%} wait={dw/de:.0%} resid={rr:.3f}")
    return de,ds,dw,rr
w1=window(mEnAll,"ano_sol",[2010,2018],"idade_ent","espera_m","Row1 by year full panel (enrolled, uncapped)")
w2=window(mEnAll,"ano_sol",[2010,2016],"idade_ent","espera_m","Row2 by year 2010-2016 (enrolled, uncapped)")
w3=window(mEn,"ano_nasc",COH,"idade_ent","espera_m","Row3 birth cohort 2010-2014 (enrolled, <=48)")
r1=window(mRefAll,"ano_sol",[2010,2018],"age_ref","wait_ref","  ref Row1")
r2=window(mRefAll,"ano_sol",[2010,2016],"age_ref","wait_ref","  ref Row2")
r3=window(mRef,"ano_nasc",COH,"age_ref","wait_ref","  ref Row3")
rows=[]
for lab,(de,ds,dw,rr),(rde,rds,rdw,rrr) in [
    ("By year, full panel (2010--2018)",w1,r1),
    ("By year, 730-day window (2010--2016)",w2,r2),
    ("By birth cohort (2010--2014)",w3,r3)]:
    rows.append([lab,f"{de:.2f}",f"{100*dw/de:.0f}\\%",f"{rde:.2f}",f"{100*rdw/rde:.0f}\\%"])
emit("D5_windows",
 "The three windows under the enrolment-based (paper) and referral-based decompositions",
 "Change in age at entry (months) and the share attributable to waiting, under each window. "
 "Enrolment-based reproduces the paper (S3windows). Referral-based uses age at referral and the "
 "application-to-referral wait, over referred children; both use fully observed waits, so "
 "age censoring does not apply.",
 "lrrrr",
 ["Window","$\\Delta$ enrol.","\\% wait (enrol.)","$\\Delta$ refer.","\\% wait (refer.)"],
 rows,label="D5")

FACTS.append(
 f"**D (decomposicao e a correcao C1)** [build10_D.py]: a decomposicao 9,37/93/7 e sobre "
 f"MATRICULADAS (ever\\_mat=1, idade\\_ent<=48), cuja espera (matricula-solicitacao) e "
 f"OBSERVADA; a identidade idade\\_entrada=idade\\_sol+espera e exata (residuo {rr:.3f}). A "
 f"censura por idade do C1 (tempo ate encaminhamento de NAO encaminhadas) NAO entra: a "
 f"decomposicao usa so quem entrou. Reproduz d\\_ent={de:.2f}, {ds/de:.0%} solicitacao, "
 f"{dw/de:.0%} espera. Versao por encaminhamento (idade no encaminhamento, espera sol->enc): "
 f"d\\_ent={de2:.2f}, {dw2/de2:.0%} espera. O unico canal por que C1 importa e SELECAO: as "
 f"coortes iniciais perdem mais membros por envelhecimento ({Sel.frac_aged.iloc[0]:.1f}\\% em 2010 "
 f"vs {Sel.frac_aged.iloc[-1]:.1f}\\% em 2014), tornando a amostra matriculada inicial mais "
 f"selecionada em esperas curtas --- o que ENVIESA o componente de espera para BAIXO, "
 f"subestimando-o. A decomposicao correta usa so matriculadas (a idade de entrada so existe para "
 f"quem entrou); a censura nao a invalida, mas o 7\\% e um piso.")

fp=os.path.join(OUT,"facts.md")
prev=open(fp,encoding="utf-8").read() if os.path.exists(fp) else ""
# remove bloco D anterior (idempotente)
prev="\n".join(l for l in prev.splitlines() if not l.startswith("- **D (decomposicao"))
with open(fp,"w",encoding="utf-8") as f:
    f.write(prev.rstrip()+"\n")
    for x in FACTS: f.write("\n- "+x+"\n")
with open(os.path.join(OUT,"build10_D.log"),"w",encoding="utf-8") as f: f.write("\n".join(LOG))
S("\nOK build10_D: D1_decomp, D4_selection, D5_windows + facts append")
