# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BLOCO P4 - irmaos: dar conteudo a "prior contact" (estagio do mais velho na data
# de solicitacao do mais novo) + validacao do identificador de guardiao + distribuicao
# das diferencas intra-familia. Reaproveita a spine (build10) e o areg (pyhdfe).
# NAO edita o corpo; salva .tex em build11/tables.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os, pyhdfe
ROOT=NE_ROOT
STG=os.path.join(ROOT,r"03_build\build10\_staging")
OUT=os.path.join(ROOT,r"03_build\build11\tables"); LOG=[]
def S(x): LOG.append(str(x)); print(x)
def emit(name,cap,note,cols,header,body,label=None):
    label=label or name
    L=["% BLOCO P4. Descritivo.","\\begin{table}[htbp]\\centering",f"\\caption{{{cap}}}",
       f"\\label{{tab:{label}}}","\\footnotesize","\\setlength{\\tabcolsep}{4pt}",
       f"\\begin{{tabular}}{{{cols}}}","\\toprule"," & ".join(header)+" \\\\","\\midrule"]
    for r in body: L.append("\\midrule" if r=="MID" else " & ".join(r)+" \\\\")
    L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
    open(os.path.join(OUT,name+".tex"),"w",encoding="utf-8").write("\n".join(L)+"\n"); print("tex:",name)
def areg(df,y,xvars,fe_cols,cluster=None):
    cols=[y]+xvars+fe_cols+([cluster] if cluster else [])
    sub=df.dropna(subset=cols).copy()
    if len(sub)<10: return np.nan,np.nan,len(sub)
    ids=np.column_stack([sub[c].astype("category").cat.codes.values for c in fe_cols])
    alg=pyhdfe.create(ids,drop_singletons=False)
    res=alg.residualize(sub[[y]+xvars].astype(float).values)
    yr=res[:,0]; Xr=res[:,1:]; n,k=Xr.shape
    if np.linalg.matrix_rank(Xr)<k: return np.nan,np.nan,n
    XtXi=np.linalg.inv(Xr.T@Xr); beta=XtXi@(Xr.T@yr); resid=yr-Xr@beta
    scc=Xr*resid[:,None]; g=pd.DataFrame(scc); g["cl"]=sub[cluster].values
    gs=g.groupby("cl").sum().values; meat=gs.T@gs; G=len(gs); V=XtXi@meat@XtXi*(G/(G-1))
    return beta[0],np.sqrt(np.diag(V))[0],n

# ---------- dados ----------
sp=pd.read_parquet(os.path.join(STG,"spine.parquet"),
    columns=["cd_aluno_sme","cpf","d_sol1","d_enc1","d_mat1","idade_sol","ano_nasc","mes_nasc","cep_aluno","prio","rq"])
sp["cpf"]=sp["cpf"].astype(str).str.strip()
sp["cpf_ok"]=sp.cpf.notna() & ~sp.cpf.isin(["","nan","0","None"])
sp["d_birth"]=pd.to_datetime(dict(year=sp.ano_nasc,month=sp.mes_nasc,day=1),errors="coerce")
N_ALL=len(sp)

# ---------- grupos de guardiao (validacao) ----------
fam_all=sp[sp.cpf_ok].copy()
per_cpf=fam_all.groupby("cpf").size()
S(f"# guardioes com cpf valido: {per_cpf.size:,} cobrindo {len(fam_all):,} criancas ({100*sp.cpf_ok.mean():.1f}% do universo)")
S("  distribuicao de filhos por guardiao: "+", ".join(f"{k}={v:,}" for k,v in per_cpf.value_counts().sort_index().head(6).items())+
  f", 6+={int((per_cpf>=6).sum()):,}")
# pares: exatamente 2, ambos 2010-2016, espac>0
two=per_cpf[per_cpf==2].index
t=fam_all[fam_all.cpf.isin(two)].copy()
t["nasc_idx"]=t.ano_nasc*12+t.mes_nasc
t=t.sort_values(["cpf","nasc_idx","d_sol1"]); t["ord"]=t.groupby("cpf").cumcount()+1
p1=t[t.ord==1].set_index("cpf"); p2=t[t.ord==2].set_index("cpf")
com=p1.index.intersection(p2.index)
P=pd.DataFrame(index=com)
for c in ["ano_nasc","mes_nasc","nasc_idx","idade_sol","d_sol1","d_enc1","d_mat1","d_birth","cep_aluno","prio","rq"]:
    P[c+"_1"]=p1.loc[com,c]; P[c+"_2"]=p2.loc[com,c]
P["espac"]=P.nasc_idx_2-P.nasc_idx_1
pc=P[(P.ano_nasc_1.between(2010,2016))&(P.ano_nasc_2.between(2010,2016))&(P.espac>0)].copy()
S(f"# pares base (2 filhos, ambos 2010-2016, espac>0): {len(pc):,}")

def longp(pcx):
    L=[pd.DataFrame({"cpf":pcx.index,"idade_sol":pcx["idade_sol_"+s],"ordem":int(s),"ano_nasc":pcx["ano_nasc_"+s]}) for s in ["1","2"]]
    return pd.concat(L)
b0,s0,n0=areg(longp(pc),"idade_sol",["ordem"],["cpf","ano_nasc"],cluster="cpf")
S(f"# baseline replicado: coef={b0:.2f} (EP {s0:.2f}) N={n0:,} pares={len(pc):,}")

# ================= 1. estagio do mais velho na data de solic do mais novo =================
S("\n## 1. estagio do mais velho na d_sol do mais novo")
ty=pc.d_sol1_2   # data de solicitacao do mais novo
enr_by=pc.d_mat1_1.notna() & (pc.d_mat1_1<=ty)
ref_by=pc.d_enc1_1.notna() & (pc.d_enc1_1<=ty)
pc["stage"]=np.where(enr_by,"c_enrolled",np.where(ref_by,"b_referred","a_applied"))
res_stage=[]
for st in ["a_applied","b_referred","c_enrolled"]:
    sub=pc[pc.stage==st]; b,s,n=areg(longp(sub),"idade_sol",["ordem"],["cpf","ano_nasc"],cluster="cpf")
    res_stage.append((st,b,s,len(sub))); S(f"  {st}: coef={b:.2f} (EP {s:.2f}) pares={len(sub):,}")
# pre-nascimento: solic do mais velho precede o NASCIMENTO do mais novo
pre=pc[pc.d_sol1_1 < pc.d_birth_2]
bp,sp_,np_=areg(longp(pre),"idade_sol",["ordem"],["cpf","ano_nasc"],cluster="cpf")
S(f"  pre-birth (solic velho < nasc novo): coef={bp:.2f} (EP {sp_:.2f}) pares={len(pre):,}")

# ================= 2. validacao do guardiao =================
S("\n## 2. validacao do guardiao")
imposs=(pc.espac<9).sum()
S(f"  espac impossivel (<9m): {imposs:,} ({100*imposs/len(pc):.1f}% dos pares)")
cep_change=(pd.to_numeric(pc.cep_aluno_1,errors='coerce')!=pd.to_numeric(pc.cep_aluno_2,errors='coerce')).sum()
S(f"  mudanca de CEP entre filhos: {cep_change:,} ({100*cep_change/len(pc):.1f}%)")
# seletividade vs universo
sib_ids=set(t[t.cpf.isin(pc.index)].cd_aluno_sme)  # criancas em pares
insib=sp.cd_aluno_sme.isin(sib_ids)
def cmp(col,f):
    return sp.loc[insib,col].pipe(f), sp[col].pipe(f)
inc_s,inc_u=cmp("rq",lambda x:x.mean()); pr_s,pr_u=cmp("prio",lambda x:100*x.fillna(0).mean())
S(f"  amostra de pares = {2*len(pc):,} criancas ({100*2*len(pc)/N_ALL:.1f}% do universo)")
S(f"  quartil renda medio: pares={inc_s:.2f} universo={inc_u:.2f} | % prioridade: pares={pr_s:.1f} universo={pr_u:.1f}")
# re-estimativas
pc_np=pc[pc.espac>=9]
bne,sne,nne=areg(longp(pc_np),"idade_sol",["ordem"],["cpf","ano_nasc"],cluster="cpf")
S(f"  (i) excl espac<9m: coef={bne:.2f} (EP {sne:.2f}) pares={len(pc_np):,}")
S(f"  (ii) so grupos de exatamente 2 filhos: JA e a amostra base (coef={b0:.2f})")

# ================= 3. distribuicao das diferencas intra-familia =================
S("\n## 3. distribuicao das diferencas (idade_sol mais novo - mais velho)")
diff=pc.idade_sol_2-pc.idade_sol_1
qs=diff.quantile([.1,.25,.5,.75,.9])
frac_younger=100*(diff<0).mean()
S(f"  media={diff.mean():.1f} | p10={qs[.1]:.0f} p25={qs[.25]:.0f} med={qs[.5]:.0f} p75={qs[.75]:.0f} p90={qs[.9]:.0f}")
S(f"  fracao com mais novo inscrito mais cedo (diff<0): {frac_younger:.1f}%")
# histograma em bins (texto)
bins=[-60,-36,-24,-12,-6,0,6,12,24,36,60]
hist=pd.cut(diff,bins).value_counts(normalize=True).sort_index()

# ================= TABELAS =================
def f2(x): return f"{x:.2f}" if pd.notna(x) else "---"
# T1: estagio + pre-birth
body=[
 ["All pairs (baseline)",f2(b0),f"({f2(s0)})",f"{len(pc):,}"],
 ["(a) older applied only",f2(res_stage[0][1]),f"({f2(res_stage[0][2])})",f"{res_stage[0][3]:,}"],
 ["(b) older referred, not enrolled",f2(res_stage[1][1]),f"({f2(res_stage[1][2])})",f"{res_stage[1][3]:,}"],
 ["(c) older already enrolled",f2(res_stage[2][1]),f"({f2(res_stage[2][2])})",f"{res_stage[2][3]:,}"],
 ["Older applied before younger's birth",f2(bp),f"({f2(sp_)})",f"{len(pre):,}"],
]
emit("P4_stage",
 "Within-family birth-order coefficient by the older sibling's stage at the younger's application "
 "date",
 "Dependent: age at first application (months); coefficient is the younger-minus-older difference, "
 "absorbing family and birth-year fixed effects, standard errors clustered by family. Rows (a)--(c) "
 "classify the older sibling's furthest stage on the day the younger applied. This classification "
 "is \\emph{endogenous to the younger's own application timing}: for the older to be enrolled by "
 "then, the younger must typically have applied late, so rows (b)--(c) select on late younger "
 "applications and the coefficient loses its meaning as a prior-contact effect. The last row---the "
 "older applied before the younger was born---does not condition on the younger's timing and is the "
 "cleaner test of prior experience.",
 "lrrr",["Sample","Coef.","(SE)","Pairs"],body,label="P4stage")
# T2: validacao guardiao
body=[
 ["Sibling pairs (children)",f"{2*len(pc):,}",f"{100*2*len(pc)/N_ALL:.1f}\\%"],
 ["Impossible spacing $<9$ months",f"{imposs:,}",f"{100*imposs/len(pc):.1f}\\%"],
 ["Postcode change between siblings",f"{cep_change:,}",f"{100*cep_change/len(pc):.1f}\\%"],
 ["Mean income quartile (pairs / universe)",f"{inc_s:.2f}",f"{inc_u:.2f}"],
 ["\\% with priority (pairs / universe)",f"{pr_s:.1f}",f"{pr_u:.1f}"],
]
emit("P4_guardian",
 "Guardian-identifier validation and selectivity of the sibling sample",
 "The guardian identifier groups children by the registered guardian's taxpayer id, not by "
 "biological siblinghood. Impossible spacing (two singleton births under nine months apart) flags "
 "twins or registration error. Postcode change between the two children is reported as a further "
 "check. Selectivity: the sibling sample versus all applicants on mean postcode-income quartile and "
 "share with legal priority. Re-estimates excluding impossible spacing and restricting to exactly-"
 "two-child guardians are in the note below.",
 "lrr",["Item","Pairs / sample","Share / universe"],body,label="P4guard")
# T3: distribuicao das diferencas
body=[[str(i).replace("(","(").replace(", ","--").replace("]",""),f"{100*v:.1f}"] for i,v in hist.items()]
emit("P4_dist",
 "Distribution of the within-family difference in age at application (younger minus older, months)",
 f"Younger-minus-older difference in age at first application, in months, over the {len(pc):,} "
 f"pairs. Median ${qs[.5]:.0f}$, interquartile range ${qs[.25]:.0f}$ to ${qs[.75]:.0f}$; the "
 f"younger sibling applies earlier in {frac_younger:.0f} percent of pairs. Rows give the share of "
 f"pairs in each difference band.",
 "lr",["Difference band (months)","\\% of pairs"],body,label="P4dist")

with open(os.path.join(ROOT,r"03_build\build11","p4.log"),"w",encoding="utf-8") as f: f.write("\n".join(LOG))
S("\nOK P4: P4_stage, P4_guardian, P4_dist"
  f"\nRE-EST: excl espac<9m coef={bne:.2f} (pares {len(pc_np):,})")
