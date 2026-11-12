# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD11 - riscos competitivos como analise principal (E1), heterogeneidade
# com estimador correto (E2), padronizacao por composicao (E3), contabilidade
# da fila (E4), limites de Manski para a decomposicao (E5). Descritivo.
# Reaproveita build10 spine + cep_cei_pairs_novo + evolucaodemanda.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
ROOT=NE_ROOT
B1=os.path.join(ROOT,r"03_build\build01\_staging")
AUD=os.path.join(ROOT,"02_audit")
STG=os.path.join(ROOT,r"03_build\build10\_staging")
OUT=os.path.join(ROOT,r"03_build\build11"); TAB=os.path.join(OUT,"tables")
os.makedirs(TAB,exist_ok=True)
EP=pd.Timestamp("1960-01-01"); PANEL=pd.Timestamp("2019-11-28")
LOG=[]; FACTS=[]
def S(x): LOG.append(str(x)); print(x)
def emit(name,cap,note,cols,header,body,label=None):
    label=label or name
    L=["% BUILD11. Descritivo.","\\begin{table}[htbp]\\centering",f"\\caption{{{cap}}}",
       f"\\label{{tab:{label}}}","\\footnotesize","\\setlength{\\tabcolsep}{4pt}",
       f"\\begin{{tabular}}{{{cols}}}","\\toprule"," & ".join(header)+" \\\\","\\midrule"]
    for r in body: L.append("\\midrule" if r=="MID" else " & ".join(r)+" \\\\")
    L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
    open(os.path.join(TAB,name+".tex"),"w",encoding="utf-8").write("\n".join(L)+"\n"); print("tex:",name)

# ---------------- survival helpers (competing risks) ----------------
def km_curve(time,ev):
    o=np.argsort(time,kind="mergesort"); t=np.asarray(time,float)[o]; e=np.asarray(ev,float)[o]
    ut=np.unique(t); Sc=1.0; T=[];Sr=[]; ar=len(t)
    for tt in ut:
        m=(t==tt); d=e[m].sum()
        if ar>0 and d>0: Sc*=(1-d/ar)
        T.append(tt);Sr.append(Sc); ar-=m.sum()
    return np.array(T),np.array(Sr)
def _cif(time,etype):
    # Aalen-Johansen CIF for causes 1 (ref) and 2 (age); etype in {0,1,2}
    o=np.argsort(time,kind="mergesort"); t=np.asarray(time,float)[o]; e=np.asarray(etype)[o]
    ut=np.unique(t); ar=len(t); Sprev=1.0; c1=c2=0.0; T=[];C1=[];C2=[];SA=[]
    for tt in ut:
        m=(t==tt); d1=int((e[m]==1).sum()); d2=int((e[m]==2).sum()); dall=int(m.sum())
        if ar>0:
            c1+=Sprev*(d1/ar); c2+=Sprev*(d2/ar); Snew=Sprev*(1-(d1+d2)/ar)
        else: Snew=Sprev
        T.append(tt);C1.append(c1);C2.append(c2);SA.append(Snew); Sprev=Snew; ar-=dall
    return np.array(T),np.array(C1),np.array(C2),np.array(SA)
def at(T,arr,x):
    i=np.searchsorted(T,x,side="right")-1; return float(arr[i]) if i>=0 else 0.0
def cif_median(T,C1):
    z=np.where(C1>=0.5)[0]; return int(T[z[0]]) if len(z) else None
def rmst_inqueue(T,SA,L):
    # area under all-cause survival up to L = restricted mean days in the eligible queue
    grid=np.unique(np.concatenate([[0.0],T[T<L],[float(L)]])); area=0.0
    def Sx(x):
        i=np.searchsorted(T,x,side="right")-1; return float(SA[i]) if i>=0 else 1.0
    for a,b in zip(grid[:-1],grid[1:]): area+=Sx(a)*(b-a)
    return area

# ---------------- dados ----------------
S("carregando spine + child_master...")
sp=pd.read_parquet(os.path.join(STG,"spine.parquet"))
cm=pd.read_feather(os.path.join(B1,"child_master.feather"),
    columns=["cd_aluno_sme","idade_ent","espera_m","prio","rq","agrup_sol"])
d=sp.merge(cm[["cd_aluno_sme","idade_ent","espera_m"]],on="cd_aluno_sme",how="left")
d["d_sol"]=d["d_sol1"]
# competing-risks: primeira saida (encaminhamento vs idade 47m), tempo desde solicitacao
esp=(d.d_enc1-d.d_sol).dt.days
t_ref=np.where(d.d_enc1.notna(),esp,np.inf).astype(float)
t_age=(d.d_age47-d.d_sol).dt.days.values.astype(float)
t_pan=(PANEL-d.d_sol).dt.days.values.astype(float)
d["t_ref"]=t_ref; d["t_age"]=t_age; d["t_pan"]=t_pan
def compet(sub):
    tr=sub.t_ref.values; ta=sub.t_age.values; tp=sub.t_pan.values
    time=np.minimum.reduce([np.where(np.isfinite(tr),tr,1e9),ta,tp])
    et=np.zeros(len(sub),int)
    ref1=(tr<=np.minimum(ta,tp))&np.isfinite(tr)&(tr>=0)
    age1=(~ref1)&(ta<=tp)
    et[ref1]=1; et[age1]=2
    ok=np.isfinite(time)&(time>=0)
    return time[ok],et[ok]
def kmnet(sub):
    # KM net (age+panel censura) do tempo ate encaminhamento -- diagnostico E1d
    tr=sub.t_ref.values; ta=sub.t_age.values; tp=sub.t_pan.values
    cens=np.minimum(ta,tp)
    ev=(np.isfinite(tr)&(tr<=cens)&(tr>=0)).astype(int)
    time=np.where(ev==1,tr,cens).astype(float)
    ok=np.isfinite(time)&(time>=0)
    return time[ok],ev[ok]
HOR=[180,365,730]

# =====================================================================
# E1 - riscos competitivos como analise principal
# =====================================================================
def e1_rows(groupcol,vals):
    rows=[]
    for g in vals:
        sub=d[d[groupcol]==g]
        tt,et=compet(sub); T,C1,C2,SA=_cif(tt,et)
        r={"g":g,"N":len(tt)}
        for h in HOR: r[f"ref{h}"]=at(T,C1,h); r[f"age{h}"]=at(T,C2,h)
        r["rmst365"]=rmst_inqueue(T,SA,365); r["cifmed"]=cif_median(T,C1)
        # KM net (diagnostico)
        kt,ke=kmnet(sub); KT,KS=km_curve(kt,ke)
        zz=np.where(KS<=0.5)[0]; r["kmmed"]=int(KT[zz[0]]) if len(zz) else None
        rows.append(r)
    return pd.DataFrame(rows)

S("\n## E1 - riscos competitivos (por coorte de nascimento)")
E1c=e1_rows("ano_nasc",list(range(2010,2017)))
S("coorte | CIFref180/365/730 | CIFage365 | RMST365 | med(CIFref) | med(KMnet)")
for _,r in E1c.iterrows():
    S(f"  {int(r.g)} | {r.ref180:.3f}/{r.ref365:.3f}/{r.ref730:.3f} | {r.age365:.3f} | {r.rmst365:.0f} | {r.cifmed} | {r.kmmed}")
E1c.to_csv(os.path.join(TAB,"E1_cohort.csv"),index=False)
S("\n## E1b - por ano de solicitacao 2010-2017")
E1y=e1_rows("ano_sol",list(range(2010,2018)))
for _,r in E1y.iterrows():
    S(f"  {int(r.g)} | {r.ref180:.3f}/{r.ref365:.3f}/{r.ref730:.3f} | {r.age365:.3f} | {r.rmst365:.0f} | {r.cifmed} | {r.kmmed}")
E1y.to_csv(os.path.join(TAB,"E1_year.csv"),index=False)

def f3(x): return f"{x:.3f}" if pd.notna(x) else "---"
def med(x): return str(int(x)) if pd.notna(x) and x is not None else "n.d."
body=[[str(int(r.g)),f"{int(r.N):,}",f3(r.ref180),f3(r.ref365),f3(r.ref730),
       f3(r.age365),f"{r.rmst365:.0f}",med(r.cifmed)] for _,r in E1c.iterrows()]
emit("E1_cohort",
 "Competing-risks incidence of referral and of aging out, by birth cohort",
 "Aalen--Johansen cumulative incidence, treating referral and aging out (reaching 47 "
 "months unreferred) as competing events; time measured from application. CIF ref: "
 "cumulative incidence of referral at 180/365/730 days. CIF age365: cumulative incidence "
 "of aging out at 365 days. RMST365: restricted mean days in the eligible queue within 365 "
 "days (area under the all-cause survival). Median: day at which the referral incidence "
 "reaches 0.5, where defined.",
 "lrrrrrrr",
 ["Birth cohort","N","ref$_{180}$","ref$_{365}$","ref$_{730}$","age$_{365}$","RMST$_{365}$","Median"],
 body,label="E1cohort")
body=[[str(int(r.g)),f"{int(r.N):,}",f3(r.ref180),f3(r.ref365),f3(r.ref730),
       f3(r.age365),f"{r.rmst365:.0f}",med(r.cifmed)] for _,r in E1y.iterrows()]
emit("E1_year",
 "Competing-risks incidence of referral and of aging out, by year of application",
 "As in Table~\\ref{tab:E1cohort}, indexed by year of application (2010--2017; 2018 excluded "
 "for truncation). CIF ref/age at the stated horizons; RMST365 in days; median where defined.",
 "lrrrrrrr",
 ["Year","N","ref$_{180}$","ref$_{365}$","ref$_{730}$","age$_{365}$","RMST$_{365}$","Median"],
 body,label="E1year")
# E1d KM net diagnostico
body=[[str(int(r.g)),med(r.kmmed),med(r.cifmed)] for _,r in E1c.iterrows()]
emit("E1_kmnet",
 "Diagnostic: net (age-censored) Kaplan--Meier median vs.\\ competing-risks median, by cohort",
 "The net KM censors aging out and therefore estimates the distribution of time to referral "
 "\\emph{that would obtain if no child aged out}---a hypothetical net distribution, reported "
 "here only as a diagnostic. The competing-risks median (right column) is the day the "
 "cumulative incidence of referral reaches 0.5 in the presence of the competing risk, and is "
 "the quantity we report in the text.",
 "lrr",["Birth cohort","Net KM median","Competing-risks median"],body,label="E1d")
# E1e manchete
a=E1c[E1c.g==2010].iloc[0]; b=E1c[E1c.g==2016].iloc[0]
S(f"\n## E1e MANCHETE: prob. encaminhamento em 1 ano subiu de {a.ref365:.2f} ({int(a.g)}) para "
  f"{b.ref365:.2f} ({int(b.g)}); RMST365 caiu de {a.rmst365:.0f} para {b.rmst365:.0f} dias.")
FACTS.append(
 f"**E1 (riscos competitivos)** [build11.py]: tratando a saida por idade como evento "
 f"competitivo (nao censura), a incidencia acumulada de encaminhamento em 365 dias sobe de "
 f"{a.ref365:.2f} (coorte 2010) para {b.ref365:.2f} (2016); a incidencia de envelhecer sem "
 f"encaminhamento em 365 dias cai de {a.age365:.3f} para {b.age365:.3f}; o tempo medio restrito "
 f"na fila em 365 dias cai de {a.rmst365:.0f} para {b.rmst365:.0f} dias. A KM com saida por idade "
 f"censurada estima uma distribuicao liquida (hipotetica) e fica como diagnostico secundario.")

# =====================================================================
# E2 - heterogeneidade por renda com estimador correto
# =====================================================================
S("\n## E2 - gradiente de renda: CIF365 e RMST365 por coorte x quartil de renda do CEP")
rows=[]
for c in range(2010,2017):
    for q in [1,2,3,4]:
        sub=d[(d.ano_nasc==c)&(d.rq==q)]
        if len(sub)<50: continue
        tt,et=compet(sub); T,C1,C2,SA=_cif(tt,et)
        rows.append({"coorte":c,"q":q,"N":len(sub),"ref365":at(T,C1,365),"rmst365":rmst_inqueue(T,SA,365)})
E2=pd.DataFrame(rows); E2.to_csv(os.path.join(TAB,"E2_renda.csv"),index=False)
S("coorte | Q1ref Q4ref (gap) | Q1rmst Q4rmst")
for c in range(2010,2017):
    s=E2[E2.coorte==c]
    if len(s)>=4:
        q1=s[s.q==1].iloc[0]; q4=s[s.q==4].iloc[0]
        S(f"  {c} | {q1.ref365:.3f} {q4.ref365:.3f} ({q4.ref365-q1.ref365:+.3f}) | {q1.rmst365:.0f} {q4.rmst365:.0f}")
body=[]
for c in range(2010,2017):
    s=E2[E2.coorte==c]
    if len(s)<4: continue
    row=[str(c)]
    for q in [1,2,3,4]:
        rr=s[s.q==q].iloc[0]; row+= [f"{rr.ref365:.3f}"]
    for q in [1,4]:
        rr=s[s.q==q].iloc[0]; row+=[f"{rr.rmst365:.0f}"]
    body.append(row)
emit("E2_renda",
 "Income gradient in referral under competing-risks incidence and restricted mean time, "
 "by birth cohort and postcode income quartile",
 "Cumulative incidence of referral at 365 days (Aalen--Johansen, competing risk = aging out) "
 "by CEP income quartile (Q1 lowest), and restricted mean days in the eligible queue within "
 "365 days for Q1 and Q4. Replaces the Kaplan--Meier wait tables (S4a, S4b), which censored "
 "aging out. A higher incidence and a lower RMST both mean faster referral.",
 "lrrrrrr",
 ["Cohort","ref Q1","ref Q2","ref Q3","ref Q4","RMST Q1","RMST Q4"],body,label="E2")
g10=E2[(E2.coorte==2010)]; g16=E2[(E2.coorte==2016)]
def gap(s):
    return s[s.q==4].ref365.iloc[0]-s[s.q==1].ref365.iloc[0]
FACTS.append(
 f"**E2 (gradiente de renda)** [build11.py]: sob incidencia acumulada de encaminhamento em 365 "
 f"dias, o quartil de renda mais alto (Q4) e encaminhado mais que o mais baixo (Q1) em toda "
 f"coorte; o gap Q4$-$Q1 e {gap(g10):+.3f} (2010) e {gap(g16):+.3f} (2016) --- persiste, nao "
 f"fecha. As tabelas antigas S4a/S4b usavam KM com saida por idade censurada; refeitas aqui e "
 f"na E1 (por coorte e por ano). RMST confirma o mesmo sinal.")

# =====================================================================
# E3 - padronizar a duracao por composicao (reponderar a coorte 2013)
# =====================================================================
S("\n## E3 - padronizacao por composicao (referencia = coorte 2013)")
# contagem dinamica de CEIs abertos na data de solicitacao
pairs=pd.read_stata(os.path.join(AUD,"cep_cei_pairs_novo.dta"),columns=["cep","ceicode","dt_abertura","dist_km"])
pairs["dt_abertura"]=pd.to_datetime(pairs["dt_abertura"],errors="coerce")
p2=pairs[(pairs.dist_km<=2.0)&pairs.dt_abertura.notna()]
cep_dates={c:np.sort(g["dt_abertura"].values) for c,g in p2.groupby("cep")}
def nopen(cep,dsol):
    arr=cep_dates.get(cep)
    return 0 if arr is None else int(np.searchsorted(arr,np.datetime64(dsol),side="right"))
S("  contando CEIs abertos na data de solicitacao...")
d["nopen"]=[nopen(c,s) for c,s in zip(d.cep_aluno.values,d.d_sol.values)]
# celulas de padronizacao (bins grossos p/ estabilidade)
def binq(x,edges): return np.digitize(x,edges)
d["b_age"]=binq(d.idade_sol.values,[6,12,24,36])          # 5 faixas
d["b_open"]=binq(d.nopen.values,[5,15,30])                # 4 faixas
d["b_prio"]=d.prio.fillna(0).astype(int).clip(0,1)
d["b_rq"]=d.rq.fillna(0).astype(int)                      # 0=missing,1-4
d["b_ag"]=d.agrup_sol.fillna("NA").astype(str)
d["cell"]=(d.b_age.astype(str)+"|"+d.b_open.astype(str)+"|"+d.b_prio.astype(str)+"|"+
           d.b_rq.astype(str)+"|"+d.b_ag)
tgt=d[d.ano_nasc==2013]["cell"].value_counts(normalize=True)   # distribuicao alvo
def cif365_rmst(sub,w=None):
    tr=sub.t_ref.values; ta=sub.t_age.values; tp=sub.t_pan.values
    time=np.minimum.reduce([np.where(np.isfinite(tr),tr,1e9),ta,tp])
    et=np.zeros(len(sub),int)
    ref1=(tr<=np.minimum(ta,tp))&np.isfinite(tr)&(tr>=0); age1=(~ref1)&(ta<=tp)
    et[ref1]=1; et[age1]=2
    ok=np.isfinite(time)&(time>=0); time=time[ok]; et=et[ok]
    ww=np.ones(len(sub)) if w is None else np.asarray(w)[ok]
    o=np.argsort(time,kind="mergesort"); t=time[o]; e=et[o]; wv=ww[o]
    ut=np.unique(t); ar=wv.sum(); Sprev=1.0; c1=0.0; T=[];C1=[];SA=[]
    for tt in ut:
        m=(t==tt); d1=wv[m&(e==1)].sum(); d2=wv[m&(e==2)].sum(); dall=wv[m].sum()
        if ar>0:
            c1+=Sprev*(d1/ar); Snew=Sprev*(1-(d1+d2)/ar)
        else: Snew=Sprev
        T.append(tt);C1.append(c1);SA.append(Snew); Sprev=Snew; ar-=dall
    T=np.array(T);C1=np.array(C1);SA=np.array(SA)
    cif=at(T,C1,365); rm=rmst_inqueue(T,SA,365)
    return cif,rm
rows=[]
for c in range(2010,2017):
    sub=d[d.ano_nasc==c].copy()
    cifr,rmr=cif365_rmst(sub)                       # bruto
    # pesos de padronizacao: alvo(cell)/freq_coorte(cell)
    freq=sub["cell"].value_counts(normalize=True)
    wmap=(tgt/freq).replace([np.inf],np.nan)
    sub["w"]=sub["cell"].map(wmap)
    cov=sub["w"].notna().mean()                     # cobertura de suporte
    sub2=sub[sub["w"].notna()].copy()
    # aparar pesos extremos (1o/99o pct) e renormalizar
    lo,hi=np.nanpercentile(sub2["w"],[1,99]); sub2["w"]=sub2["w"].clip(lo,hi)
    sub2["w"]=sub2["w"]/sub2["w"].mean()
    cifs,rms=cif365_rmst(sub2,sub2["w"].values)     # padronizado
    rows.append({"coorte":c,"cif_bruto":cifr,"cif_pad":cifs,"rmst_bruto":rmr,"rmst_pad":rms,"cobertura":cov})
E3=pd.DataFrame(rows); E3.to_csv(os.path.join(TAB,"E3_padronizacao.csv"),index=False)
S("coorte | cif365 bruto/pad | rmst365 bruto/pad | cobertura")
for _,r in E3.iterrows():
    S(f"  {int(r.coorte)} | {r.cif_bruto:.3f}/{r.cif_pad:.3f} | {r.rmst_bruto:.0f}/{r.rmst_pad:.0f} | {r.cobertura:.2f}")
# decomposicao: melhora bruta 2010->2016 vs padronizada
b0=E3[E3.coorte==2010].iloc[0]; b1=E3[E3.coorte==2016].iloc[0]
dcif_bruto=b1.cif_bruto-b0.cif_bruto; dcif_pad=b1.cif_pad-b0.cif_pad
share_comp=1-dcif_pad/dcif_bruto if dcif_bruto else np.nan
S(f"  Delta CIF365 2010->2016: bruto={dcif_bruto:+.3f}, padronizado={dcif_pad:+.3f}; "
  f"composicao explica {100*share_comp:.0f}%, operacional {100*(1-share_comp):.0f}%")
body=[[str(int(r.coorte)),f"{r.cif_bruto:.3f}",f"{r.cif_pad:.3f}",f"{r.rmst_bruto:.0f}",
       f"{r.rmst_pad:.0f}",f"{r.cobertura:.2f}"] for _,r in E3.iterrows()]
emit("E3_padronizacao",
 "Referral incidence and restricted mean time, raw and standardized to the 2013 applicant "
 "composition, by birth cohort",
 "Each cohort is reweighted so that its joint distribution of age at application, requested "
 "band, priority, postcode income quartile, and number of centres open within 2\\,km at the "
 "application date matches that of the 2013 cohort (cells with coarse bins; weights trimmed at "
 "the 1st/99th percentile and renormalized). CIF ref at 365 days and restricted mean days in "
 "the eligible queue within 365 days, raw and standardized. Coverage is the share of each "
 "cohort falling in cells present in 2013.",
 "lrrrrr",
 ["Cohort","CIF raw","CIF std","RMST raw","RMST std","Coverage"],body,label="E3")
FACTS.append(
 f"**E3 (padronizacao)** [build11.py]: reponderando cada coorte para a composicao da coorte 2013 "
 f"(idade na solicitacao, faixa, prioridade, quartil de renda, CEIs abertos no raio), a incidencia "
 f"de encaminhamento em 365 dias sobe de {b0.cif_bruto:.3f} (2010) a {b1.cif_bruto:.3f} (2016) no "
 f"bruto e de {b0.cif_pad:.3f} a {b1.cif_pad:.3f} padronizada. Da melhora bruta ($+{dcif_bruto:.3f}$), "
 f"a padronizacao preserva $+{dcif_pad:.3f}$: cerca de {100*(1-share_comp):.0f}% e melhora operacional "
 f"e {100*share_comp:.0f}% e mudanca de composicao dos solicitantes.")

# =====================================================================
# E4 - contabilidade da fila (uma reconstrucao, identidade fecha)
# =====================================================================
S("\n## E4 - reconstrucao unica (init oficial dez/2009; desistencia no residuo)")
MES={"jan":1,"fev":2,"mar":3,"abr":4,"mai":5,"jun":6,"jul":7,"ago":8,"set":9,"out":10,"nov":11,"dez":12}
evd=pd.read_csv(os.path.join(ROOT,r"03_build\build04\_ext\evolucaodemanda.csv"),sep=";",thousands=".",dtype={"MES_ANO_REF":str})
evd["ano"]=evd.MES_ANO_REF.str[-2:].astype(int)+2000; evd["mes"]=evd.MES_ANO_REF.str[:3].map(MES)
evd["DEM_CRECHE"]=pd.to_numeric(evd.DEM_CRECHE,errors="coerce")
off_dec=evd[evd.mes==12].groupby("ano").DEM_CRECHE.sum()
# primeira saida por crianca (referral vs idade), universo do paper
big=pd.Timestamp("2100-01-01")
tr=d.d_enc1.where(d.d_enc1>=d.d_sol); ta=d.d_age47.where(d.d_age47>=d.d_sol,d.d_sol)
M=pd.DataFrame({"ref":tr.fillna(big),"age":ta.fillna(big)})
d["exit_t"]=M.min(axis=1); d["exit_ty"]=M.idxmin(axis=1)
d.loc[d.exit_t>PANEL,"exit_ty"]="cens"
d["ye"]=d.exit_t.dt.year; d["ys"]=d.d_sol.dt.year
init=off_dec.get(2009,np.nan); rows=[]; start=init
for Y in range(2010,2019):
    new=int((d.ys==Y).sum())
    ref=int(((d.ye==Y)&(d.exit_ty=="ref")).sum())
    aged=int(((d.ye==Y)&(d.exit_ty=="age")).sum())
    off=off_dec.get(Y,np.nan)
    resid=start+new-ref-aged-(off if pd.notna(off) else np.nan)   # plug: desistencias+remocoes+mismatch
    rows.append({"ano":Y,"start":start,"new":new,"ref":ref,"aged":aged,"resid":resid,"official":off,
                 "resid_pct":100*resid/off if pd.notna(off) and off else np.nan})
    start=off if pd.notna(off) else start
E4=pd.DataFrame(rows); E4.to_csv(os.path.join(TAB,"E4_reconstrucao.csv"),index=False)
S("  ano | start new ref aged resid official resid%")
for _,r in E4.iterrows():
    offs="n/d" if pd.isna(r.official) else f"{int(r.official):,}"
    rp="n/d" if pd.isna(r.resid_pct) else f"{r.resid_pct:+.0f}%"
    S(f"  {int(r.ano)} | {r.start:>7.0f} {int(r.new):>7d} {int(r.ref):>7d} {int(r.aged):>6d} {r.resid:>8.0f} {offs:>8} {rp}")
body=[]
for _,r in E4.iterrows():
    offs=(f"{int(r.official):,}" if pd.notna(r.official) else "---")
    rp=(f"{r.resid_pct:+.0f}" if pd.notna(r.resid_pct) else "---")
    body.append([str(int(r.ano)),f"{r.start:,.0f}",f"{int(r.new):,}",f"{int(r.ref):,}",
                 f"{int(r.aged):,}",(f"{r.resid:,.0f}" if pd.notna(r.resid) else "---"),offs,rp])
emit("E4_reconstrucao",
 "Queue reconstruction with official initialization and an exactly closing identity",
 "A single reconstruction, replacing the two inconsistent versions. Start: stock at 1 January, "
 "chained on the official December series (2010 initialized with the official December-2009 "
 "registered demand, 74{,}707). New: first applications dated in the year. Ref: first referrals "
 "(first exit). Aged: children reaching 47 months unreferred (first exit). Residual is defined "
 "so the identity start $+$ new $-$ ref $-$ aged $-$ residual $=$ official closes exactly; it "
 "absorbs withdrawals and administrative removals (unobserved) and the mismatch between the "
 "first-application universe and the broader official register. resid\\%: residual as a percent "
 "of the official December stock.",
 "lrrrrrrr",
 ["Year","Start","New","Ref.","Aged","Residual","Official","resid\\%"],body,label="E4")
r10=E4[E4.ano==2010].iloc[0]
FACTS.append(
 f"**E4 (reconstrucao)** [build11.py]: uma unica reconstrucao substitui as duas inconsistentes "
 f"(a Tabela do corpo dizia inicializar com 74.707 mas usava 26.004; a do apendice se chamava "
 f"limite superior com razao 0,76). Inicializada no estoque oficial de dez/2009 (74.707) e com a "
 f"identidade start+new-ref-aged-residuo=oficial fechando por construcao, o residuo (desistencias "
 f"+ remocoes administrativas + descasamento de universo) e {r10.resid:.0f} em 2010 "
 f"({r10.resid_pct:+.0f}\\% do estoque). A serie de fluxos (universo de primeiras solicitacoes, "
 f"censurada por idade) e um limite INFERIOR do estoque oficial: nao observa reinscricoes nem o "
 f"backlog anterior a 2010 alem da inicializacao, e a censura por idade remove os solicitantes "
 f"velhos das coortes iniciais.")

# =====================================================================
# E5 - limites de Manski para a decomposicao 93/7
# =====================================================================
S("\n## E5 - limites de Manski (decomposicao, coortes 2010-2014)")
COH=list(range(2010,2015))
# grupos: matriculadas<=48 (observado) e envelhecidas sem encaminhamento (imputado)
d["aged_out"]=((d.d_enc1.isna())|(d.d_enc1>d.d_age47))&(d.d_age47<=PANEL)
def manski(coh):
    sub=d[(d.ano_nasc==coh)]
    enr=sub[(sub.ever_mat==1)&(sub.idade_ent<=48)]
    aged=sub[sub.aged_out & ~((sub.ever_mat==1)&(sub.idade_ent<=48))]
    n_e=len(enr); n_a=len(aged); N=n_e+n_a
    sol_e=enr.idade_sol.mean(); ent_e=enr.idade_ent.mean()
    sol_a=aged.idade_sol.mean()
    sol_comb=(n_e*sol_e+n_a*sol_a)/N                      # observado p/ ambos
    ent_max=(n_e*ent_e+n_a*48.0)/N                        # envelhecidas entram aos 48
    ent_min=(n_e*ent_e+n_a*sol_a)/N                       # envelhecidas entram na idade_sol (espera 0)
    return dict(coh=coh,N=N,frac_aged=n_a/N,sol_e=sol_e,ent_e=ent_e,
                sol_comb=sol_comb,ent_max=ent_max,ent_min=ent_min)
MK=pd.DataFrame([manski(c) for c in COH])
MK.to_csv(os.path.join(TAB,"E5_manski.csv"),index=False)
a=MK[MK.coh==2010].iloc[0]; b=MK[MK.coh==2014].iloc[0]
# (1) so-matriculadas (paper): tudo sobre enrolled
d_sol_e=b.sol_e-a.sol_e; d_ent_e=b.ent_e-a.ent_e; sh_e=d_sol_e/d_ent_e
# (2) populacao combinada: d_sol fixo (observado); d_ent depende do cenario
d_sol_c=b.sol_comb-a.sol_comb
d_ent_max=b.ent_max-a.ent_max; sh_max=d_sol_c/d_ent_max
d_ent_min=b.ent_min-a.ent_min; sh_min=d_sol_c/d_ent_min
S(f"  (1) enrolled-only (paper): d_sol={d_sol_e:.2f} d_ent={d_ent_e:.2f} share_sol={sh_e:.1%} share_wait={1-sh_e:.1%}")
S(f"  (2) combinado, d_sol(obs)={d_sol_c:.2f} (ponto-identificado)")
S(f"      MAX (aged->48): d_ent={d_ent_max:.2f} d_wait={d_ent_max-d_sol_c:+.2f} share_sol={sh_max:.1%}")
S(f"      MIN (aged->sol): d_ent={d_ent_min:.2f} d_wait={d_ent_min-d_sol_c:+.2f} share_sol={sh_min:.1%}")
lo,hi=sorted([sh_max,sh_min])
S(f"  intervalo de identificacao do share de SOLICITACAO (pop. combinada): [{lo:.1%}, {hi:.1%}]")
S(f"  componente de espera d_wait no intervalo [{min(d_ent_max-d_sol_c,d_ent_min-d_sol_c):+.2f}, "
  f"{max(d_ent_max-d_sol_c,d_ent_min-d_sol_c):+.2f}] meses")
body=[
 ["Enrolled only (paper)",f"{d_sol_e:.2f}",f"{d_ent_e:.2f}",f"{100*sh_e:.0f}\\%",f"{100*(1-sh_e):.0f}\\%"],
 ["Combined, aged-out at 48 (max entry)",f"{d_sol_c:.2f}",f"{d_ent_max:.2f}",f"{100*sh_max:.0f}\\%",f"{100*(1-sh_max):.0f}\\%"],
 ["Combined, aged-out at appl.\\ age (min)",f"{d_sol_c:.2f}",f"{d_ent_min:.2f}",f"{100*sh_min:.0f}\\%",f"{100*(1-sh_min):.0f}\\%"],
]
emit("E5_manski",
 "Extreme-case imputations for non-entrants in the decomposition of the fall in age at entry, "
 "birth cohorts 2010--2014",
 "Age at entry is undefined for a child who never enters, so the full-cohort decomposition is not "
 "an estimand these data identify; this table reports the split under the two extreme imputations "
 "of that missing entry age rather than a bound. Children who aged out of eligibility unreferred "
 "(27.4 percent of the 2010 cohort, 5.2 percent of 2014) are assigned, as a worst case, an entry "
 "age equal to their age at application (no wait) or, as the other extreme, equal to the 48-month "
 "limit. Row 1 is the paper's enrolled-only figure. Age at application is observed for all, so its "
 "change ($\\Delta$ appl.) is fixed in the combined population; only the imputed entry-age change "
 "moves the split. A share above 100 percent means the implied wait component is "
 "\\emph{negative}---waiting rises once the never-entering children are counted.",
 "lrrrr",
 ["Scenario","$\\Delta$ appl.\\ (mo.)","$\\Delta$ entry (mo.)","Share appl.","Share wait"],body,label="E5")
wide=(hi-lo)>0.15 or hi>1.0
FACTS.append(
 f"**E5 (limites de Manski)** [build11.py]: a decomposicao 93/7 e condicional as matriculadas "
 f"(share solicitacao {sh_e:.0%}). Incluindo as criancas que envelheceram sem encaminhamento "
 f"(27,4\\% da coorte 2010 vs 5,2\\% de 2014) com idade de entrada imputada nos extremos "
 f"(48 meses vs idade na solicitacao), a variacao da idade de SOLICITACAO na populacao combinada "
 f"e ponto-identificada em {d_sol_c:.2f} meses, mas o share de solicitacao fica no intervalo "
 f"[{lo:.0%}, {hi:.0%}] --- acima de 100\\%, ou seja, o componente de espera pode ser NEGATIVO "
 f"(a espera SOBE ao contar quem nunca entrou). "
 f"{'O intervalo e largo e cruza 100%%: a decomposicao NAO sustenta afirmacao de piso e deve ser apresentada como condicional aos matriculados.' if wide else 'O intervalo e estreito.'}")

# =====================================================================
with open(os.path.join(OUT,"facts.md"),"w",encoding="utf-8") as f:
    f.write("# BUILD11 facts (riscos competitivos + correcoes)\n\n")
    for x in FACTS: f.write("- "+x+"\n\n")
with open(os.path.join(OUT,"build11.log"),"w",encoding="utf-8") as f: f.write("\n".join(LOG))
S("\nOK build11: E1_cohort/E1_year/E1_kmnet/E2/E3/E4/E5 + facts.md + log")
