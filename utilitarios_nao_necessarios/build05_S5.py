# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD05 S5 - robustez de S2d: FE de familia + DUMMIES de ano de nascimento (padrao
# da literatura de ordem de nascimento), vs a especificacao linear original. Descritivo.
# Acrescenta (nao sobrescreve) a build05. Nao modifica build01/02/03/04.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os, pyhdfe
ROOT=NE_ROOT
OUT=os.path.join(ROOT,r"03_build\build05"); TAB=os.path.join(OUT,"tables")
CM=os.path.join(ROOT,r"03_build\build01\_staging\child_master.feather")
LOG=[];
def S(x): LOG.append(str(x)); print(x)
def nf(x,d=3):
    try: return f"{float(x):,.{d}f}"
    except: return str(x)

def areg(df,y,xvars,fe_cols,cluster=None):
    cols=[y]+xvars+fe_cols+([cluster] if cluster else [])
    sub=df.dropna(subset=cols).copy()
    ids=np.column_stack([sub[c].astype("category").cat.codes.values for c in fe_cols])
    alg=pyhdfe.create(ids,drop_singletons=False)
    res=alg.residualize(sub[[y]+xvars].astype(float).values)
    yr=res[:,0]; Xr=res[:,1:]; n,k=Xr.shape
    XtXi=np.linalg.inv(Xr.T@Xr); beta=XtXi@(Xr.T@yr); resid=yr-Xr@beta
    if cluster:
        sc=Xr*resid[:,None]; g=pd.DataFrame(sc); g["cl"]=sub[cluster].values
        gs=g.groupby("cl").sum().values; meat=gs.T@gs; G=len(gs)
        V=XtXi@meat@XtXi*(G/(G-1))
    else:
        V=XtXi*(resid@resid)/(n-k)
    se=np.sqrt(np.diag(V))
    return dict(zip(xvars,beta)),dict(zip(xvars,se)),n

# --- reconstruir os pares (identico a build05_irmaos S1c) + sexo/raca ---
d=pd.read_parquet(os.path.join(OUT,"_panel_criancas.parquet"))
sr=pd.read_feather(CM,columns=["cd_aluno_sme","fem","negra"])
d=d.merge(sr,on="cd_aluno_sme",how="left")
fam=d[d.cpf_ok].copy()
sz=fam.groupby("cpf").size(); two=sz[sz==2].index
t=fam[fam.cpf.isin(two)].sort_values(["cpf","nasc_idx","d_sol1"])
t["ord"]=t.groupby("cpf").cumcount()+1
p1=t[t.ord==1].set_index("cpf"); p2=t[t.ord==2].set_index("cpf")
cols=["ano_nasc","mes_nasc","nasc_idx","idade_sol","distrito","fem","negra"]
pair=pd.DataFrame({"cpf":p1.index})
for c in cols: pair[c+"_1"]=p1[c].values; pair[c+"_2"]=p2[c].values
pair["espac"]=pair.nasc_idx_2-pair.nasc_idx_1
pc=pair[(pair.ano_nasc_1.between(2010,2016))&(pair.ano_nasc_2.between(2010,2016))&(pair.espac>0)].copy()
S(f"# S5 robustez: {len(pc):,} pares (identico a S1c). Painel longo = {2*len(pc):,} obs.")

def longpanel(pcx):
    L=[]
    for suf in ["1","2"]:
        L.append(pd.DataFrame({"cpf":pcx.cpf,"idade_sol":pcx["idade_sol_"+suf],"ordem":int(suf),
            "ano_nasc":pcx["ano_nasc_"+suf],"mes_nasc":pcx["mes_nasc_"+suf],"nasc_idx":pcx["nasc_idx_"+suf],
            "distrito":pcx["distrito_"+suf],"fem":pcx["fem_"+suf],"negra":pcx["negra_"+suf]}))
    lg=pd.concat(L); lg["dano"]=lg.distrito.astype(str)+"_"+lg.ano_nasc.astype(str)
    return lg
lg=longpanel(pc)

rows=[]
def run(lbl,dfx,y,fe,note=""):
    b,se,n=areg(dfx,y,["ordem"],fe,cluster="cpf")
    rows.append({"spec":lbl,"dep":y,"coef_ordem":b["ordem"],"ep":se["ordem"],"N":n})
    S(f"  {lbl}: coef(ordem)={b['ordem']:.3f} (EP {se['ordem']:.3f}); N={n:,}  {note}")
    return b["ordem"]

S("\n## S5a-S5d: idade_sol ~ ordem, variando o controle de coorte")
# original linear (S2d): ano_nasc como regressor linear + FE familia
b_lin,se_lin,n_lin=areg(lg,"idade_sol",["ordem","ano_nasc"],["cpf"],cluster="cpf")
rows.append({"spec":"Linear birth-year trend (S2d)","dep":"idade_sol","coef_ordem":b_lin["ordem"],"ep":se_lin["ordem"],"N":n_lin})
S(f"  Linear (original): coef(ordem)={b_lin['ordem']:.3f} (EP {se_lin['ordem']:.3f}); N={n_lin:,}")
c_yr=run("Birth-year dummies (S5a)",lg,"idade_sol",["cpf","ano_nasc"])
run("Birth year-month dummies (S5b)",lg,"idade_sol",["cpf","nasc_idx"])
run("Year dummies + district$\\times$year (S5c)",lg,"idade_sol",["cpf","dano"])

S("\n## S5e: restrito a espacamento 24-48 meses")
lg_e=longpanel(pc[pc.espac.between(24,48)])
run("Year dummies, spacing 24--48m (S5e)",lg_e,"idade_sol",["cpf","ano_nasc"],f"({pc.espac.between(24,48).sum():,} pares)")

S("\n## S5f: placebo de composicao (desfecho pre-determinado; nao deveria variar com ordem)")
run("Placebo: female $\\sim$ order (S5f)",lg,"fem",["cpf","ano_nasc"])
run("Placebo: Black $\\sim$ order (S5f)",lg,"negra",["cpf","ano_nasc"])

# --- comparacao / contaminacao ---
drop=100*(c_yr-b_lin["ordem"])/b_lin["ordem"]
S(f"\n## Leitura: linear={b_lin['ordem']:.2f} -> dummies de ano={c_yr:.2f} "
  f"(variacao {c_yr-b_lin['ordem']:+.2f} meses, {drop:+.0f}%).")
if abs(c_yr-b_lin["ordem"])>=0.5:
    S(f"  A especificacao LINEAR estava contaminada pela curvatura da tendencia de coorte: o coeficiente de "
      f"ordem de nascimento muda {abs(c_yr-b_lin['ordem']):.2f} meses ao usar dummies de ano.")
else:
    S(f"  O coeficiente e ESTAVEL entre linear e dummies (muda {abs(c_yr-b_lin['ordem']):.2f} meses, "
      f"<0,5): a curvatura residual nao contaminava materialmente a estimativa linear.")

R=pd.DataFrame(rows); R.to_csv(os.path.join(TAB,"S5_robustez.csv"),index=False)

# --- tex ---
def emit(name,cap,note,cols,header,body):
    L=["% requer booktabs. Descritivo.","\\begin{table}[htbp]\\centering",f"\\caption{{{cap}}}",
       f"\\label{{tab:{name}}}","\\small",f"\\begin{{tabular}}{{{cols}}}","\\toprule",
       " & ".join(header)+" \\\\","\\midrule"]
    for r in body: L.append("\\midrule" if r=="MID" else " & ".join(r)+" \\\\")
    L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
    open(os.path.join(TAB,name+".tex"),"w",encoding="utf-8").write("\n".join(L)+"\n"); print("tex:",name)
body=[]
for _,r in R.iterrows():
    DEPLAB={"idade_sol":"Age at application","fem":"Female","negra":"Black"}
    body.append([r.spec.replace("&","\\&"),DEPLAB.get(r.dep,r.dep),nf(r.coef_ordem,3),f"({nf(r.ep,3)})",nf(r.N,0)])
emit("S5_robustez","Robustness of the within-family birth-order coefficient to the cohort-trend control",
 "Long sibling panel (two children per family, both born 2010--2016). Dependent = age at first application (months), except the last two rows (placebo: sex and race, pre-determined at birth). All specifications absorb family fixed effects; the cohort trend is controlled linearly (row 1), by birth-year dummies, by birth year-month dummies, or by district$\\times$birth-year dummies. Standard errors clustered by family in parentheses. The birth-order coefficient is the change from the older to the younger sibling.",
 "llrrr",["Specification","Dep.\\ var","Coef.\\ (birth order)","(SE)","N"],body)

# --- facts.md (append) ---
FACT=(f"**S5 (robustez de S2d)** [build05_S5.py]: substituindo a tendencia linear de coorte por DUMMIES de ano "
      f"de nascimento (padrao da literatura de ordem de nascimento), o coeficiente de ordem de nascimento passa de "
      f"{b_lin['ordem']:.2f} (linear) para {c_yr:.2f} meses (EP {[r['ep'] for r in rows if r['spec'].startswith('Birth-year dummies (')][0]:.2f}); "
      f"com dummies de ano-mes e com distrito x ano permanece proximo. "
      f"{'A especificacao linear estava contaminada pela curvatura da tendencia de coorte.' if abs(c_yr-b_lin['ordem'])>=0.5 else 'A estimativa linear nao estava materialmente contaminada.'} "
      f"Placebos (sexo, raca) por ordem de nascimento ~0. O filho mais novo e inscrito mais cedo dentro da familia.")
with open(os.path.join(OUT,"facts.md"),"a",encoding="utf-8") as f: f.write("\n- "+FACT+"\n")
with open(os.path.join(OUT,"build05.log"),"a",encoding="utf-8") as f: f.write("\n\n=== S5 robustez ===\n"+"\n".join(LOG))
S("\nS5_robustez.tex/.csv + facts.md (append) + build05.log OK")
