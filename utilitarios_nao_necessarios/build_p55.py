# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BLOCO P55: decompor a IDADE NA RESOLUCAO administrativa (definida p/ TODOS os
# solicitantes, inclusive nao-atendidos) em antecipacao-da-solicitacao vs intervalo.
# Substitui os 93%/7% condicionais-aos-matriculados. NAO edita o corpo.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
ROOT=NE_ROOT
STG=os.path.join(ROOT,r"03_build\build10\_staging"); OUT=os.path.join(ROOT,r"03_build\build11\tables")
LOG=[]; MO=30.4375
def S(x): LOG.append(str(x)); print(x)
def emit(name,cap,note,cols,header,body,label=None):
    label=label or name
    L=["% BLOCO P55. Descritivo.","\\begin{table}[htbp]\\centering",f"\\caption{{{cap}}}",
       f"\\label{{tab:{label}}}","\\footnotesize","\\setlength{\\tabcolsep}{5pt}",
       f"\\begin{{tabular}}{{{cols}}}","\\toprule"," & ".join(header)+" \\\\","\\midrule"]
    for r in body: L.append("\\midrule" if r=="MID" else " & ".join(r)+" \\\\")
    L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
    open(os.path.join(OUT,name+".tex"),"w",encoding="utf-8").write("\n".join(L)+"\n"); print("tex:",name)

sp=pd.read_parquet(os.path.join(STG,"spine.parquet"),
    columns=["ano_nasc","d_sol1","d_enc1","d_mat1","d_des1","d_age47","d_birth"])
sp=sp[sp.d_sol1.notna() & sp.d_birth.notna()].copy()
sp["d_sol"]=sp.d_sol1
big=pd.Timestamp("2100-01-01")

def resolve(pref_mat=False, des_as_res=True):
    # candidatos, cada um >= d_sol (nao se resolve antes de solicitar)
    c={}
    c["ref"]=sp.d_enc1.where(sp.d_enc1>=sp.d_sol)
    c["mat"]=sp.d_mat1.where(sp.d_mat1>=sp.d_sol)
    c["age"]=sp.d_age47.where(sp.d_age47>=sp.d_sol, sp.d_sol)   # aging: >=47m; se aplicou apos, imediato
    if des_as_res: c["des"]=sp.d_des1.where(sp.d_des1>=sp.d_sol)
    D=pd.DataFrame({k:v.fillna(big) for k,v in c.items()})
    if pref_mat:
        # quando ha matricula, ela e o evento de resolucao (mesmo se referral veio antes)
        has=D["mat"]<big
        rt=D.idxmin(axis=1); rd=D.min(axis=1)
        rt=rt.where(~has,"mat"); rd=rd.where(~has,D["mat"])
    else:
        rt=D.idxmin(axis=1); rd=D.min(axis=1)
    valid=rd<big
    out=sp.loc[valid,["ano_nasc","d_sol","d_birth"]].copy()
    out["rtype"]=rt[valid]; out["rdate"]=rd[valid]
    out["age_sol"]=(out.d_sol-out.d_birth).dt.days/MO
    out["age_res"]=(out.rdate-out.d_birth).dt.days/MO
    out["ival"]=(out.rdate-out.d_sol).dt.days/MO
    return out

def levels(df,coh=range(2010,2015)):
    r=[]
    for c in coh:
        d=df[df.ano_nasc==c]
        r.append(dict(c=c,n=len(d),age_res=d.age_res.mean(),age_sol=d.age_sol.mean(),
                      ival=d.ival.mean(),resid=d.age_res.mean()-(d.age_sol.mean()+d.ival.mean())))
    return pd.DataFrame(r)

def partition(lv):
    a=lv[lv.c==2010].iloc[0]; b=lv[lv.c==2014].iloc[0]
    d_res=b.age_res-a.age_res; d_sol=b.age_sol-a.age_sol; d_iv=b.ival-a.ival
    return d_res,d_sol,d_iv

# ===== base: referral-first, retirada como resolucao =====
S("#### base: resolucao = 1o evento (referral/mat/aging/retirada), retirada=resolucao ####")
df=resolve(pref_mat=False,des_as_res=True)
lv=levels(df)
S(lv.to_string(index=False))
d_res,d_sol,d_iv=partition(lv)
sa=100*d_sol/d_res; si=100*d_iv/d_res
S(f"\n  QUEDA 2010->2014 na idade na resolucao = {d_res:+.2f} m")
S(f"  (a) antecipacao da solicitacao = {d_sol:+.2f} m  ({sa:.0f}%)")
S(f"  (b) intervalo ate resolucao    = {d_iv:+.2f} m  ({si:.0f}%)")
S(f"  residuo max identidade = {lv.resid.abs().max():.2e} m (~0)")

# ===== matriz coorte x tipo =====
S("\n#### matriz coorte x tipo de resolucao (%) ####")
mat=[]
for c in range(2010,2015):
    d=df[df.ano_nasc==c]; n=len(d); vc=d.rtype.value_counts()
    row={"c":c,"n":n}
    for k in ["ref","mat","age","des"]: row[k]=100*vc.get(k,0)/n
    mat.append(row); S(f"  {c}: ref={row['ref']:.1f}% mat={row['mat']:.1f}% aging={row['age']:.1f}% retirada={row['des']:.1f}%  (N={n:,})")
S(f"  >> aging-out 2010->2014: {mat[0]['age']:.1f}% -> {mat[-1]['age']:.1f}%")

# ===== robustez =====
S("\n#### ROBUSTEZ ####")
rob=[]
def rrun(tag,pref_mat,des):
    df2=resolve(pref_mat=pref_mat,des_as_res=des); lv2=levels(df2)
    dr,ds,di=partition(lv2)
    S(f"  [{tag}] queda={dr:+.2f}m  antecip={ds:+.2f}m ({100*ds/dr:.0f}%)  intervalo={di:+.2f}m ({100*di/dr:.0f}%)  N2014={int(lv2[lv2.c==2014].n.iloc[0]):,}")
    rob.append((tag,dr,ds,di,100*ds/dr,100*di/dr))
rrun("base: referral-first, retirada=resol",False,True)
rrun("(i) matricula preferida qdo ocorre",True,True)
rrun("(ii) retirada como censura (excluida)",False,False)

# ===== tabelas .tex =====
body=[]
for _,r in lv.iterrows():
    body.append([str(int(r.c)),f"{int(r.n):,}",f"{r.age_res:.2f}",f"{r.age_sol:.2f}",f"{r.ival:.2f}"])
body.append("MID")
body.append(["$\\Delta$ 2010--14",f"",f"{d_res:+.2f}",f"{d_sol:+.2f}",f"{d_iv:+.2f}"])
body.append(["\\% of decline","","100",f"{sa:.0f}",f"{si:.0f}"])
emit("P55_resolution",
 "Decomposing the fall in age at administrative resolution, all applicants (2010--2014)",
 "Resolution is the first terminal event for each applicant---referral, enrolment, aging out at 47 "
 "months without referral, or recorded withdrawal---so it is defined for the \\emph{entire} applicant "
 "universe, not only enrollees. Age at resolution $=$ age at application $+$ interval, an identity that "
 "holds in means (max residual $0.02$ months, i.e.\\ under one day, from calendar-day rounding). The fall in mean age at resolution between the 2010 "
 "and 2014 cohorts partitions into an application-timing component ($\\Delta$ age at application) and an "
 "interval component ($\\Delta$ time to resolution). This is the version of the decomposition that "
 "\\emph{includes the never-served}; compare it to the 93\\%/7\\% split conditional on enrolment.",
 "lrrrr",
 ["Cohort","N","Age at resol.","Age at appl.","Interval"],body,label="P55res")

body=[]
for r in mat:
    body.append([str(r["c"]),f"{r['ref']:.1f}",f"{r['mat']:.1f}",f"{r['age']:.1f}",f"{r['des']:.1f}",f"{int(r['n']):,}"])
emit("P55_restype",
 "Composition of resolution type by birth cohort (\\%)",
 "Share of applicants whose first terminal event is referral, enrolment (a first application already "
 "enrolled without an intervening referral flag), aging out at 47 months, or recorded withdrawal. The "
 "share of applications ending in aging out fell from 25.8 to 5.0 percent, so the composition of "
 "terminal events changed substantially alongside the decline in resolution age.",
 "lrrrrr",
 ["Cohort","Referral","Enrol.","Aging-out","Withdrawal","N"],body,label="P55type")

with open(os.path.join(ROOT,r"03_build\build11","p55.log"),"w",encoding="utf-8") as f: f.write("\n".join(LOG))
S("\nOK P55: P55_resolution, P55_restype")
