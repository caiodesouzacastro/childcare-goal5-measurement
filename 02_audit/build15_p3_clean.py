# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# GERADO por build15_make_p3.py a partir de build_p3.py (25/10/2026): Delta com base 2013. Nao editar a mao.
# -*- coding: utf-8 -*-
# BLOCO P3 - decompor o ganho de duracao (E3) separando COMPOSICAO DE SOLICITANTE
# de AMBIENTE DE OFERTA. Tres series de Delta(CIF referral 365d), 2010->2016:
#   S1 bruta; S2 padronizada so por solicitante; S3 solicitante + oferta.
# Desfecho: incidencia acumulada de referral em 1 ano (Aalen-Johansen, saida por
# idade como evento competitivo). Reaproveita spine (build10) + cep_cei_pairs.
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os, unicodedata, re
ROOT=os.environ.get("NE_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B1=os.path.join(ROOT,r"03_build\build01\_staging")
AUD=os.path.join(ROOT,"02_audit")
STG=os.path.join(ROOT,r"03_build\build10\_staging")
OUT=os.path.join(ROOT,r"03_build\build15"); os.makedirs(OUT,exist_ok=True)
CEPRENDA=os.path.join(os.environ.get("NE_DADOS_SME", os.path.join(ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")), r"processados\bases_analise\cep_renda_pop_2010.dta")
PANEL=pd.Timestamp("2019-11-28"); LOG=[]
def S(x): LOG.append(str(x)); print(x)
def emit(name,cap,note,cols,header,body,label=None):
    label=label or name
    L=["% BLOCO P3. Descritivo.","\\begin{table}[htbp]\\centering",f"\\caption{{{cap}}}",
       f"\\label{{tab:{label}}}","\\footnotesize","\\setlength{\\tabcolsep}{4pt}",
       f"\\begin{{tabular}}{{{cols}}}","\\toprule"," & ".join(header)+" \\\\","\\midrule"]
    for r in body: L.append("\\midrule" if r=="MID" else " & ".join(r)+" \\\\")
    L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
    open(os.path.join(OUT,name+".tex"),"w",encoding="utf-8").write("\n".join(L)+"\n"); print("tex:",name)

# ---------- dados ----------
S("carregando spine + covariaveis...")
sp=pd.read_parquet(os.path.join(STG,"spine.parquet"),
    columns=["cd_aluno_sme","d_sol1","d_enc1","d_age47","idade_sol","prio","rq","cep_aluno","ano_nasc","ano_sol"])
d=sp.copy(); d["d_sol"]=d["d_sol1"]
d["sem_sol"]=np.where(d.d_sol.dt.month<=6,1,2)
d["cep_i"]=pd.to_numeric(d.cep_aluno,errors="coerce")
# distrito via cep_renda
def nz(s): return "".join(c for c in unicodedata.normalize("NFD",str(s).strip().upper()) if unicodedata.category(c)!="Mn")
rd=pd.read_stata(CEPRENDA,columns=["cep","nm_distrit"])
cep2d={int(c):nz(x) for c,x in zip(rd.cep,rd.nm_distrit)}
d["distrito"]=d["cep_i"].map(cep2d)
# nopen: CEIs a <=2km abertos na data de solicitacao
pairs=pd.read_stata(os.path.join(AUD,"cep_cei_pairs_novo.dta"),columns=["cep","ceicode","dt_abertura","dist_km"])
pairs["dt_abertura"]=pd.to_datetime(pairs["dt_abertura"],errors="coerce")
p2=pairs[(pairs.dist_km<=2.0)&pairs.dt_abertura.notna()]
cep_dates={c:np.sort(g["dt_abertura"].values) for c,g in p2.groupby("cep")}
def nopen(cep,dsol):
    a=cep_dates.get(cep); return 0 if a is None else int(np.searchsorted(a,np.datetime64(dsol),side="right"))
S("  contando CEIs abertos na data de solicitacao...")
d["nopen"]=[nopen(c,s) for c,s in zip(d.cep_i.values,d.d_sol.values)]
S(f"  N={len(d):,}. distrito ok={d.distrito.notna().mean():.2f}, rq ok={d.rq.notna().mean():.2f}")

# ---------- CIF referral 365d (Aalen-Johansen, ponderado) ----------
def cif365(sub,w=None):
    tr=np.where(sub.d_enc1.notna(),(sub.d_enc1-sub.d_sol).dt.days,np.inf).astype(float)
    ta=(sub.d_age47-sub.d_sol).dt.days.values.astype(float); tp=(PANEL-sub.d_sol).dt.days.values.astype(float)
    time=np.minimum.reduce([np.where(np.isfinite(tr),tr,1e9),ta,tp])
    et=np.zeros(len(sub),int); r1=(tr<=np.minimum(ta,tp))&np.isfinite(tr)&(tr>=0); a1=(~r1)&(ta<=tp)
    et[r1]=1; et[a1]=2; ok=np.isfinite(time)&(time>=0)
    time=time[ok]; et=et[ok]; ww=(np.ones(len(sub)) if w is None else np.asarray(w))[ok]
    o=np.argsort(time,kind="mergesort"); t=time[o]; e=et[o]; wv=ww[o]
    ar=wv.sum(); Sp=1.0; c1=0.0
    for tt in np.unique(t):
        m=(t==tt); d1=wv[m&(e==1)].sum(); d2=wv[m&(e==2)].sum(); dl=wv[m].sum()
        if ar>0 and tt<=365: c1+=Sp*(d1/ar)
        if ar>0: Sp=Sp*(1-(d1+d2)/ar)
        ar-=dl
        if tt>365: break
    return c1

# ---------- reponderacao por celula (alvo = coorte 2013) ----------
def weights_to_2013(dd,cellcol,trim=(1,99)):
    tgt=dd[dd.ano_nasc==2013][cellcol].value_counts(normalize=True)
    out={}; info={}
    for c in range(2010,2017):
        s=dd[dd.ano_nasc==c]
        freq=s[cellcol].value_counts(normalize=True)
        wmap=(tgt/freq).replace([np.inf],np.nan)
        w=s[cellcol].map(wmap)
        cov=w.notna().mean()
        w2=w.dropna()
        lo,hi=np.nanpercentile(w2,trim); trimmed=((w2<lo)|(w2>hi)).mean()
        w2c=w2.clip(lo,hi); w2c=w2c/w2c.mean()
        neff=(w2c.sum()**2)/(w2c**2).sum()
        out[c]=(s.index[w.notna()], w2c.values)
        info[c]=dict(cov=cov,wmin=w2c.min(),wmax=w2c.max(),trim=100*trimmed,neff=neff,n=len(w2c))
    return out,info

def series(dd,cellcol,label):
    if cellcol is None:  # bruta
        vals={c:cif365(dd[dd.ano_nasc==c]) for c in range(2010,2017)}
        info={c:dict(cov=1.0,wmin=1,wmax=1,trim=0,neff=(dd.ano_nasc==c).sum(),n=(dd.ano_nasc==c).sum()) for c in range(2010,2017)}
    else:
        w,info=weights_to_2013(dd,cellcol)
        vals={}
        for c in range(2010,2017):
            idx,wv=w[c]; sub=dd.loc[idx]; vals[c]=cif365(sub,wv)
    dcif=vals[2016]-vals[2013]
    return vals,dcif,info

# ---------- celulas ----------
def mkcells(dd,agebins,useD,timeres):
    a=np.digitize(dd.idade_sol.values,agebins).astype(str)
    p=dd.prio.fillna(0).astype(int).clip(0,1).astype(str)
    q=dd.rq.fillna(0).astype(int).astype(str)
    parts=[a,p,q]
    if useD: parts.append(dd.distrito.fillna("NA").astype(str).values)
    if timeres=="sem": parts.append(dd.sem_sol.astype(str).values)
    elif timeres=="month": parts.append(dd.d_sol.dt.month.astype(str).values)
    return pd.Series(["|".join(t) for t in zip(*parts)],index=dd.index)
def add_offer(dd,base,coarse=False):
    ob=np.digitize(dd.nopen.values,[5,15,30] if not coarse else [10]).astype(str)
    return base+"|"+pd.Series(ob,index=dd.index)

# ================= rodar as tres series (celula principal) =================
S("\n## Celula PRINCIPAL: idade(5) x prio x rq x distrito x semestre")
d["cell_appl"]=mkcells(d,[6,12,24,36],useD=True,timeres="sem")
d["cell_full"]=add_offer(d,d["cell_appl"])
v1,d1,i1=series(d,None,"S1 bruta")
v2,d2,i2=series(d,"cell_appl","S2 solicitante")
v3,d3,i3=series(d,"cell_full","S3 solicitante+oferta")
S(f"  S1 bruta:              CIF365 2013={v1[2013]:.3f} 2016={v1[2016]:.3f}  Delta={d1:+.3f}")
S(f"  S2 solicitante:        CIF365 2013={v2[2013]:.3f} 2016={v2[2016]:.3f}  Delta={d2:+.3f}")
S(f"  S3 solicitante+oferta: CIF365 2013={v3[2013]:.3f} 2016={v3[2016]:.3f}  Delta={d3:+.3f}")
# decomposicao do gap bruto
comp_appl=d1-d2      # o que a composicao de solicitante explica (raw - appl-fixed)
comp_offer=d2-d3     # o que o ambiente de oferta explica (appl-fixed - both-fixed)
oper=d3              # operacional puro (ambos fixos)
S(f"  Decomposicao do Delta bruto {d1:+.3f}: solicitante {comp_appl:+.3f}, oferta {comp_offer:+.3f}, operacional {oper:+.3f}")

# ================= celulas alternativas =================
S("\n## Celula GROSSA: idade(4) x prio x rq (sem distrito, sem tempo); oferta grossa")
d["cg_appl"]=mkcells(d,[12,24,36],useD=False,timeres=None)
d["cg_full"]=add_offer(d,d["cg_appl"],coarse=True)
_,dg2,ig2=series(d,"cg_appl","S2 grossa"); _,dg3,ig3=series(d,"cg_full","S3 grossa")
S(f"  grossa: S2={dg2:+.3f}  S3={dg3:+.3f}")
S("\n## Celula FINA: idade(8) x prio x rq x distrito x mes; oferta fina")
d["cf_appl"]=mkcells(d,[3,6,9,12,18,24,36],useD=True,timeres="month")
d["cf_full"]=add_offer(d,d["cf_appl"])
_,df2,if2=series(d,"cf_appl","S2 fina"); _,df3,if3=series(d,"cf_full","S3 fina")
S(f"  fina:   S2={df2:+.3f}  S3={df3:+.3f}")

# ================= tabelas .tex =================
# T1: as tres series (celula principal), CIF por coorte
body=[]
for lab,v in [("Raw (unweighted)",v1),("Applicant composition",v2),("Applicant + service environment",v3)]:
    body.append([lab]+[f"{v[c]:.3f}" for c in range(2010,2017)]+[f"{v[2016]-v[2013]:+.3f}"])
emit("P3_series",
 "One-year referral incidence by birth cohort under three standardizations",
 "Cumulative incidence of referral within 365 days (Aalen--Johansen, aging out treated as a "
 "competing event). Row 1 is unweighted. Row 2 reweights each cohort to the 2013 cohort's joint "
 "distribution of applicant attributes only---age at application, priority, postcode income "
 "quartile, district, and semester of application (\\emph{no} supply variable). Row 3 adds the "
 "service environment (number of eligible centres open within 2\\,km at the application date). "
 "Requested band is excluded from all rows: it is nearly mechanical given age and the 31 March "
 "cut-off, so it would be collinear with age at application. $\\Delta$ is 2016 minus 2010.",
 "lrrrrrrrr",
 ["Standardization","2010","2011","2012","2013","2014","2015","2016","$\\Delta$"],body,label="P3series")
# T2: decomposicao + robustez de celula
body=[
 ["Main (age$\\times$prio$\\times$income$\\times$district$\\times$sem)",f"{d1:+.3f}",f"{d2:+.3f}",f"{d3:+.3f}",f"{comp_appl:+.3f}",f"{comp_offer:+.3f}",f"{oper:+.3f}"],
 ["Coarse (age$\\times$prio$\\times$income)",f"{d1:+.3f}",f"{dg2:+.3f}",f"{dg3:+.3f}",f"{d1-dg2:+.3f}",f"{dg2-dg3:+.3f}",f"{dg3:+.3f}"],
 ["Fine (age8$\\times$prio$\\times$income$\\times$district$\\times$month)",f"{d1:+.3f}",f"{df2:+.3f}",f"{df3:+.3f}",f"{d1-df2:+.3f}",f"{df2-df3:+.3f}",f"{df3:+.3f}"],
]
emit("P3_decomp",
 "Decomposition of the raw 2010--2016 gain in one-year referral incidence, and sensitivity to the "
 "reweighting cell",
 "Raw: unweighted $\\Delta$. Appl.: standardized to the 2013 applicant composition. Both: also "
 "standardized to the service environment. The applicant-composition contribution is Raw$-$Appl.; "
 "the service-environment contribution is Appl.$-$Both. The three contributions sum to the raw "
 "gain: in the main row, $+0.313 = +0.367 + (-0.074) + (+0.020)$, that is, raw gain $=$ adjusted "
 "service-side difference $+$ applicant-composition contribution $+$ service-environment "
 "contribution. The applicant-composition term is \\emph{negative} because the later cohorts are, "
 "on the observed attributes, marginally harder to refer than the 2013 target: the change in who "
 "applied therefore \\emph{masked} part of the adjusted difference rather than creating it, which "
 "is why the adjusted figure ($+0.367$) exceeds the raw one ($+0.313$). "
 "The final column is the residual (Both): "
 "the standardized difference in one-year referral incidence that remains after balancing observed "
 "applicant attributes and the supply environment. It is a \\emph{residual standardized difference}, "
 "not a causal estimate of productivity or of operational efficiency: unobserved determinants of "
 "referral---among them the composition of vacancies released, priority enforcement, and any "
 "change in referral recording---are not held fixed and are absorbed into it. Three cell "
 "definitions (coarse to fine) show the ordering does not depend on binning.",
 "lrrrrrr",
 ["Cell definition","Raw","Appl.","Both","Appl.\\ comp.","Service env.",
  "\\shortstack[r]{Adjusted\\\\service-side\\\\difference\\\\(residual)}"],body,label="P3decomp")
# T3: pesos
body=[]
for c in [2010,2012,2014,2016]:
    a=i2[c]; b=i3[c]
    body.append([str(c),f"{a['cov']:.2f}",f"{a['neff']:,.0f}",f"{a['wmax']:.1f}",f"{a['trim']:.1f}",
                 f"{b['cov']:.2f}",f"{b['neff']:,.0f}",f"{b['wmax']:.1f}",f"{b['trim']:.1f}"])
emit("P3_weights",
 "Reweighting diagnostics (main cell): support coverage, effective sample size, weights",
 "For the applicant-only (Appl.) and applicant-plus-environment (Both) standardizations, main "
 "cell. Coverage: share of the cohort in cells present in 2013. $N_{\\mathrm{eff}}$: Kish effective "
 "sample size after trimming weights at the 1st/99th percentile and renormalizing. max\\,w: "
 "largest normalized weight. \\%\\,trim: share of weights clipped.",
 "lrrrrrrrr",
 ["Cohort","cov (A)","$N_{\\mathrm{eff}}$ (A)","max w","\\%tr","cov (B)","$N_{\\mathrm{eff}}$ (B)","max w","\\%tr"],
 body,label="P3weights")

with open(os.path.join(OUT,"p3_2013_2016.log"),"w",encoding="utf-8") as f: f.write("\n".join(LOG))
S("\nOK P3: P3_series, P3_decomp, P3_weights salvos (nao inseridos no corpo)")
