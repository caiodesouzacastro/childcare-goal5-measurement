# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD12 (revisao pos-EE, aprovada pelo autor em 25/10/2026). Descritivo, nenhuma estimacao causal.
#   N1: decomposicao do aging out da P55 (inscritos ja fora da faixa vs elegiveis).
#   N2: irmaos -- inscricao conjunta, mudanca de CEP, espacamento (replica P4/S5a como base).
#   N3: timing (<12m | <24m) reponderado a pesos distritais fixos.
#   N4: fracao da coorte de nascimento MATRICULADA ate 12/24/36 meses (denominador SINASC).
# Le apenas staging de 03_build (build01, build05, build10) e o SINASC de 01_dados_publicos.
# Escreve SOMENTE em 03_build\build12\ (pasta nova). Nao altera nenhum numero existente.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os, csv, unicodedata
ROOT=NE_ROOT
B1=os.path.join(ROOT,r"03_build\build01\_staging"); B5=os.path.join(ROOT,r"03_build\build05")
B10=os.path.join(ROOT,r"03_build\build10\_staging")
OUT=os.path.join(ROOT,r"03_build\build12"); STG=os.path.join(OUT,"_staging"); os.makedirs(STG,exist_ok=True)
SIN=os.path.join(ROOT,r"01_dados_publicos\ceinfo\sinasc_nv_distrito_2006_2026.csv")
LOG=[]
def S(x=""): LOG.append(str(x)); print(x)
def w(df,n): df.to_csv(os.path.join(STG,n),index=False)

def _demean(M,codes,tol=1e-10,maxit=1000):
    # projecoes alternadas (Gauss-Seidel) sobre os grupos de FE; equivale a pyhdfe sem singletons removidos
    M=M.copy()
    for it in range(maxit):
        prev=M.copy()
        for g in codes:
            cnt=np.bincount(g); 
            for j in range(M.shape[1]):
                M[:,j]-=(np.bincount(g,weights=M[:,j])/cnt)[g]
        if np.max(np.abs(M-prev))<tol: break
    return M
def areg(df,y,xvars,fe_cols,cluster=None):   # mesma estimativa de build_p4.py / build05_S5.py
    cols=[y]+xvars+fe_cols+([cluster] if cluster else [])
    sub=df.dropna(subset=cols).copy()
    codes=[sub[c].astype("category").cat.codes.values for c in fe_cols]
    res=_demean(sub[[y]+xvars].astype(float).values,codes)
    yr=res[:,0]; Xr=res[:,1:]; n,k=Xr.shape
    XtXi=np.linalg.inv(Xr.T@Xr); beta=XtXi@(Xr.T@yr); resid=yr-Xr@beta
    sc=Xr*resid[:,None]; g=pd.DataFrame(sc); g["cl"]=sub[cluster].values
    gs=g.groupby("cl").sum().values; meat=gs.T@gs; G=len(gs); V=XtXi@meat@XtXi*(G/(G-1))
    return beta[0],np.sqrt(np.diag(V))[0],n

sp=pd.read_parquet(os.path.join(B10,"spine.parquet"))
S(f"spine: {len(sp):,} criancas")

# ======================= N1 =======================
S("\n## N1: aging out (P55 base) decomposto, coortes 2010-2014")
COH=list(range(2010,2015))
q=sp[sp.d_sol1.notna()&sp.d_birth.notna()].copy(); q["d_sol"]=q.d_sol1
big=pd.Timestamp("2100-01-01")
c={"ref":q.d_enc1.where(q.d_enc1>=q.d_sol),"mat":q.d_mat1.where(q.d_mat1>=q.d_sol),
   "age":q.d_age47.where(q.d_age47>=q.d_sol,q.d_sol),"des":q.d_des1.where(q.d_des1>=q.d_sol)}
D=pd.DataFrame({k:v.fillna(big) for k,v in c.items()})
rt=D.idxmin(axis=1); rd=D.min(axis=1); ok=rd<big
q=q[ok].copy(); q["rtype"]=rt[ok]
q["late"]=q.d_sol>q.d_age47          # inscrito ja apos 47 meses: sem tempo elegivel
rows=[]
for co in COH:
    d=q[q.ano_nasc==co]; n=len(d); L=d.late; A=d.rtype=="age"
    e=d[~L]; ne=len(e)
    r=dict(cohort=co,N_all=n,pct_aged_all=100*A.mean(),pct_late=100*L.mean(),
           pct_late_and_aged=100*(L&A).mean(),pct_elig_aged_of_all=100*((~L)&A).mean(),
           N_elig=ne,pct_aged_among_elig=100*(e.rtype=="age").mean(),
           pct_ref_among_elig=100*(e.rtype=="ref").mean(),pct_des_among_elig=100*(e.rtype=="des").mean())
    rows.append(r)
    S(f"  {co}: N={n:,} aged(all)={r['pct_aged_all']:.1f}% = late&aged {r['pct_late_and_aged']:.1f} + elig&aged {r['pct_elig_aged_of_all']:.1f} | "
      f"late={r['pct_late']:.1f}% | eligible N={ne:,}: aged={r['pct_aged_among_elig']:.1f}% ref={r['pct_ref_among_elig']:.1f}% des={r['pct_des_among_elig']:.1f}%")
N1=pd.DataFrame(rows); w(N1,"N1_agingout.csv")

# ======================= N2 =======================
S("\n## N2: irmaos (replica P4 base, depois variantes)")
s2=sp[["cd_aluno_sme","cpf","d_sol1","d_birth","idade_sol","ano_nasc","mes_nasc","cep_aluno"]].copy()
s2["cpf"]=s2["cpf"].astype(str).str.strip()
s2=s2[s2.cpf.notna()&~s2.cpf.isin(["","nan","0","None"])]
per=s2.groupby("cpf").size(); two=per[per==2].index
t=s2[s2.cpf.isin(two)].copy(); t["nasc_idx"]=t.ano_nasc*12+t.mes_nasc
t=t.sort_values(["cpf","nasc_idx","d_sol1"]); t["ord"]=t.groupby("cpf").cumcount()+1
p1=t[t.ord==1].set_index("cpf"); p2=t[t.ord==2].set_index("cpf"); com=p1.index.intersection(p2.index)
P=pd.DataFrame(index=com)
for col in ["ano_nasc","nasc_idx","idade_sol","d_sol1","d_birth","cep_aluno"]:
    P[col+"_1"]=p1.loc[com,col]; P[col+"_2"]=p2.loc[com,col]
P["espac"]=P.nasc_idx_2-P.nasc_idx_1
pc=P[(P.ano_nasc_1.between(2010,2016))&(P.ano_nasc_2.between(2010,2016))&(P.espac>0)].copy()
pc["gapdays"]=(pc.d_sol1_2-pc.d_sol1_1).dt.days
pc["joint0"]=pc.gapdays.abs()==0
pc["joint30"]=pc.gapdays.abs()<=30
pc["prebirth"]=pc.d_sol1_1<pc.d_birth_2
pc["moved"]=pd.to_numeric(pc.cep_aluno_1,errors="coerce")!=pd.to_numeric(pc.cep_aluno_2,errors="coerce")
def longp(x):
    return pd.concat([pd.DataFrame({"cpf":x.index,"idade_sol":x["idade_sol_"+s],"ordem":int(s),"ano_nasc":x["ano_nasc_"+s]}) for s in ["1","2"]])
def est(lbl,x):
    b,se,n=areg(longp(x),"idade_sol",["ordem"],["cpf","ano_nasc"],cluster="cpf")
    diff=x.idade_sol_2-x.idade_sol_1
    r=dict(sample=lbl,coef=b,se=se,pairs=len(x),pct_pairs=100*len(x)/len(pc),
           raw_median_diff=diff.median(),pct_younger_earlier=100*(diff<0).mean())
    S(f"  {lbl}: coef={b:.2f} (SE {se:.2f}) pares={len(x):,} ({r['pct_pairs']:.1f}%) | diff bruta mediana={r['raw_median_diff']:.0f} m; mais novo antes em {r['pct_younger_earlier']:.1f}%")
    return r
R=[est("All pairs (baseline, = tab:P4stage row 1)",pc),
   est("Same-day joint registration",pc[pc.joint0]),
   est("Excluding same-day joint registration",pc[~pc.joint0]),
   est("Registrations within 30 days of each other",pc[pc.joint30]),
   est("Excluding registrations within 30 days",pc[~pc.joint30]),
   est("Older applied before younger's birth (= tab:P4stage last row)",pc[pc.prebirth]),
   est("Older applied on/after younger's birth",pc[~pc.prebirth]),
   est("Same postcode for both children",pc[~pc.moved]),
   est("Spacing >= 9 months (log p4: -7.65)",pc[pc.espac>=9]),
   est("Excl. within-30-day, same postcode, spacing >= 9",pc[(~pc.joint30)&(~pc.moved)&(pc.espac>=9)])]
S(f"  conjunta no mesmo dia: {100*pc.joint0.mean():.1f}% dos pares; ate 30 dias: {100*pc.joint30.mean():.1f}%")
S(f"  entre os pares 'older on/after younger's birth': {100*pc.loc[~pc.prebirth,'joint0'].mean():.1f}% mesmo dia, {100*pc.loc[~pc.prebirth,'joint30'].mean():.1f}% ate 30 dias")
N2=pd.DataFrame(R); w(N2,"N2_siblings.csv")

# ======================= N3 =======================
S("\n## N3: share <12m | <24m reponderado a pesos distritais fixos")
pan=pd.read_parquet(os.path.join(B5,"_panel_criancas.parquet"),columns=["cd_aluno_sme","distrito"])
z=sp[["cd_aluno_sme","ano_nasc","idade_sol"]].merge(pan,on="cd_aluno_sme",how="left")
OBS=list(range(2010,2017))
z=z[z.ano_nasc.isin(OBS)&(z.idade_sol<24)].copy(); z["lt12"]=(z.idade_sol<12).astype(float)
S(f"  registrados <24m, coortes 2010-16: {len(z):,}; com distrito: {100*z.distrito.notna().mean():.1f}%")
raw_all=z.groupby("ano_nasc").lt12.mean()
zz=z[z.distrito.notna()]
cell=zz.groupby(["ano_nasc","distrito"]).agg(n=("lt12","size"),m=("lt12","mean")).reset_index()
raw_d=zz.groupby("ano_nasc").lt12.mean()
def rew(base):
    wb=cell[cell.ano_nasc==base].set_index("distrito").n; wb=wb/wb.sum()
    out={}
    for co in OBS:
        cc=cell[cell.ano_nasc==co].set_index("distrito").m
        common=wb.index.intersection(cc.index); ww=wb.loc[common]/wb.loc[common].sum()
        out[co]=(cc.loc[common]*ww).sum()
    return pd.Series(out)
r10=rew(2010); r16=rew(2016)
# within-district change: mean over districts of (2016 - 2010) shares
piv=cell.pivot(index="distrito",columns="ano_nasc",values="m")
N3=pd.DataFrame({"cohort":OBS,"raw_all":raw_all.reindex(OBS).values,"raw_with_district":raw_d.reindex(OBS).values,
                 "reweighted_2010_district_mix":r10.reindex(OBS).values,"reweighted_2016_district_mix":r16.reindex(OBS).values})
for _,r in N3.iterrows():
    S(f"  {int(r.cohort)}: bruto={r.raw_all:.3f} (com distrito {r.raw_with_district:.3f}) | pesos 2010={r.reweighted_2010_district_mix:.3f} | pesos 2016={r.reweighted_2016_district_mix:.3f}")
dd=(piv[2016]-piv[2010]).dropna()
S(f"  distritos com aumento 2010->2016: {(dd>0).sum()} de {len(dd)}; mediana do aumento intradistrital = {dd.median():.3f}; min={dd.min():.3f}")
w(N3,"N3_timing_reweighted.csv")
w(pd.DataFrame({"distrito":dd.index,"d_share_2010_2016":dd.values}),"N3_within_district_change.csv")

# ======================= N4 =======================
S("\n## N4: fracao da coorte MATRICULADA ate 12/24/36 meses (denominador SINASC)")
def nz(s): return "".join(ch for ch in unicodedata.normalize("NFD",str(s).strip().upper()) if unicodedata.category(ch)!="Mn")
rows=list(csv.reader(open(SIN,encoding="utf-8"),delimiter=";")); hdr=rows[0]
yidx={int(hdr[i]):i for i in range(1,len(hdr)) if hdr[i].isdigit()}
bd={}
for r in rows[1:]:
    nm=r[0].strip()
    if nm in ("Ignorado","Total"): continue
    for y,i in yidx.items():
        try: bd[(nz(nm),y)]=int(r[i])
        except: pass
dist=sorted(set(k[0] for k in bd))
def births(y): return sum(bd.get((dd_,y),0) for dd_ in dist)
cm=pd.read_feather(os.path.join(B1,"child_master.feather"),columns=["ano_nasc","ever_mat","idade_ent","idade_sol"])
rows=[]
for co in range(2010,2018):
    d=cm[cm.ano_nasc==co]; b=births(co); e=d[d.ever_mat==1]
    r=dict(cohort=co,births=b)
    for X,last in [(12,2017),(24,2016),(36,2015)]:
        r[f"enr_lt{X}"]=100*(e.idade_ent<X).sum()/b if co<=last else np.nan
        r[f"reg_lt{X}"]=100*(d.idade_sol<X).sum()/b if co<=last else np.nan
    rows.append(r)
    S(f"  {co}: nascidos={b:,} | matriculados <12m={r['enr_lt12']:.1f}% <24m={r['enr_lt24']:.1f}% <36m={r['enr_lt36']:.1f}% | inscritos <12m={r['reg_lt12']:.1f}% <24m={r['reg_lt24']:.1f}%")
N4=pd.DataFrame(rows); w(N4,"N4_enrolled_by_age.csv")

open(os.path.join(OUT,"build12.log"),"w",encoding="utf-8").write("\n".join(LOG)+"\n")
S("\nOK build12")
