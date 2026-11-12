# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BLOCO P2 - robustezes da analise de duracao (E1). CIF Aalen-Johansen de referral,
# RMST(365), aging-out como evento competitivo. Cinco robustezes + gradiente de renda.
# Reaproveita spine (build10). NAO edita o corpo; salva .tex em build11/tables.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
ROOT=NE_ROOT
STG=os.path.join(ROOT,r"03_build\build10\_staging")
OUT=os.path.join(ROOT,r"03_build\build11\tables")
PANEL=pd.Timestamp("2019-11-28"); LOG=[]
def S(x): LOG.append(str(x)); print(x)
def emit(name,cap,note,cols,header,body,label=None):
    label=label or name
    L=["% BLOCO P2. Descritivo.","\\begin{table}[htbp]\\centering",f"\\caption{{{cap}}}",
       f"\\label{{tab:{label}}}","\\footnotesize","\\setlength{\\tabcolsep}{4pt}",
       f"\\begin{{tabular}}{{{cols}}}","\\toprule"," & ".join(header)+" \\\\","\\midrule"]
    for r in body: L.append("\\midrule" if r=="MID" else " & ".join(r)+" \\\\")
    L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
    open(os.path.join(OUT,name+".tex"),"w",encoding="utf-8").write("\n".join(L)+"\n"); print("tex:",name)

sp=pd.read_parquet(os.path.join(STG,"spine.parquet"),
    columns=["cd_aluno_sme","d_sol1","d_enc1","d_mat1","d_des1","d_age47","idade_sol","rq","ano_nasc","ano_sol"])
d=sp.copy(); d["d_sol"]=d["d_sol1"]

# ---------- CIF Aalen-Johansen com K causas (cause 1 = evento de interesse) ----------
def aj(time,etype,horizon=365):
    ok=np.isfinite(time)&(time>=0); time=np.asarray(time,float)[ok]; e=np.asarray(etype)[ok]
    o=np.argsort(time,kind="mergesort"); t=time[o]; e=e[o]; ar=len(t); Sp=1.0; c1=0.0; SA=[]; TT=[]; C1=[]
    for tt in np.unique(t):
        m=(t==tt); d1=int((e[m]==1).sum()); dall=int(m.sum()); dother=dall-int((e[m]==0).sum())-d1
        # eventos: e==0 censura; e>=1 eventos competitivos; cause1 = interesse
        dcomp=int((e[m]>=1).sum())
        if ar>0:
            c1+=Sp*(d1/ar); Snew=Sp*(1-dcomp/ar)
        else: Snew=Sp
        TT.append(tt); C1.append(c1); SA.append(Snew); Sp=Snew; ar-=dall
    TT=np.array(TT); C1=np.array(C1); SA=np.array(SA)
    def at(a,x):
        i=np.searchsorted(TT,x,side="right")-1; return float(a[i]) if i>=0 else (0.0 if a is C1 else 1.0)
    cif=at(C1,horizon)
    # RMST = area sob sobrevivencia de todas as causas ate horizon
    grid=np.unique(np.concatenate([[0.0],TT[TT<horizon],[float(horizon)]])); area=0.0
    for x0,x1 in zip(grid[:-1],grid[1:]):
        i=np.searchsorted(TT,x0,side="right")-1; area+=(float(SA[i]) if i>=0 else 1.0)*(x1-x0)
    z=np.where(C1>=0.5)[0]; med=int(TT[z[0]]) if len(z) else None
    return cif,area,med,len(time)

# ---------- construtor de tempos/eventos ----------
def build(sub,event="ref",withdrawals=False,cens=None):
    # event: 'ref' (encaminhamento) ou 'mat' (matricula). cause1 = event.
    ev_date = sub.d_enc1 if event=="ref" else sub.d_mat1
    t_ev=np.where(ev_date.notna(),(ev_date-sub.d_sol).dt.days,np.inf).astype(float)
    t_age=(sub.d_age47-sub.d_sol).dt.days.values.astype(float)
    panel=PANEL if cens is None else cens
    t_pan=(panel-sub.d_sol).dt.days.values.astype(float)
    cand=[np.where(np.isfinite(t_ev),t_ev,1e9),t_age,t_pan]; names=["ev","age","pan"]
    if withdrawals:
        t_wd=np.where(sub.d_des1.notna(),(sub.d_des1-sub.d_sol).dt.days,np.inf).astype(float)
        cand.append(np.where(np.isfinite(t_wd),t_wd,1e9)); names.append("wd")
    A=np.vstack(cand); time=A.min(axis=0); who=A.argmin(axis=0)
    et=np.zeros(len(sub),int)
    et[(who==0)&np.isfinite(t_ev)]=1                    # cause1 = evento
    et[who==1]=2                                        # aging-out
    if withdrawals: et[who==(len(names)-1)]=3           # desistencia
    # pan (censura) -> et=0 (ja e 0 por padrao onde who==2index? who==2 is pan)
    et[who==2]=0
    return time,et

def cohort_series(mask_extra=None,event="ref",withdrawals=False,cens=None,cohs=range(2010,2017)):
    rows={}
    for c in cohs:
        sub=d[d.ano_nasc==c]
        if mask_extra is not None: sub=sub[mask_extra(sub)]
        t,e=build(sub,event,withdrawals,cens)
        cif,rm,med,n=aj(t,e); rows[c]=(cif,rm,med,n)
    return rows

# ================= (i) amostra atual =================
S("## (i) amostra atual (referral)")
cur=cohort_series()
for c in cur: S(f"  {c}: CIF365={cur[c][0]:.3f} RMST={cur[c][1]:.0f} med={cur[c][2]} N={cur[c][3]:,}")

# ================= 1. follow-up comum 365d =================
S("\n## 1. follow-up comum: d_sol <= panel-365d")
cut=PANEL-pd.Timedelta(days=365)
fu=cohort_series(mask_extra=lambda s: s.d_sol<=cut)
for c in fu: S(f"  {c}: CIF365={fu[c][0]:.3f} RMST={fu[c][1]:.0f} N={fu[c][3]:,}")
S(f"  >> 0.56->0.88 vira {cur[2010][0]:.2f}->{cur[2016][0]:.2f} (atual) / {fu[2010][0]:.2f}->{fu[2016][0]:.2f} (fu comum)")

# ================= 2. endpoint = matricula =================
S("\n## 2. endpoint = matricula")
mat=cohort_series(event="mat")
for c in mat: S(f"  {c}: CIF365(mat)={mat[c][0]:.3f} RMST={mat[c][1]:.0f} N={mat[c][3]:,}")
S(f"  >> matricula: {mat[2010][0]:.2f}->{mat[2016][0]:.2f} (vs referral {cur[2010][0]:.2f}->{cur[2016][0]:.2f})")

# ================= 3. retiradas competitivas =================
S("\n## 3. desistencia como evento competitivo (referral)")
wd=cohort_series(withdrawals=True)
for c in wd: S(f"  {c}: CIF365(ref, wd compet)={wd[c][0]:.3f} (vs {cur[c][0]:.3f} sem wd)")
S(f"  >> com desistencia competitiva: {wd[2010][0]:.2f}->{wd[2016][0]:.2f}")

# ================= 4. descontinuidade 2012->2013 =================
S("\n## 4. quebra 2012->2013")
# (a) excluir aplicacoes na janela da quebra (2012-07 a 2013-12)
brk_lo=pd.Timestamp("2012-07-01"); brk_hi=pd.Timestamp("2013-12-31")
exbrk=cohort_series(mask_extra=lambda s: ~s.d_sol.between(brk_lo,brk_hi))
for c in exbrk: S(f"  (a) excl quebra {c}: CIF365={exbrk[c][0]:.3f} N={exbrk[c][3]:,}")
S(f"  >> excl janela quebra: {exbrk[2010][0]:.2f}->{exbrk[2016][0]:.2f}")
# (b) estrato: so aplicacoes no 1o semestre
h1=cohort_series(mask_extra=lambda s: s.d_sol.dt.month<=6)
h2=cohort_series(mask_extra=lambda s: s.d_sol.dt.month>6)
S(f"  (b) H1 apenas: {h1[2010][0]:.2f}->{h1[2016][0]:.2f} | H2 apenas: {h2[2010][0]:.2f}->{h2[2016][0]:.2f}")

# ================= 5. reconciliacao de amostra =================
S("\n## 5. reconciliacao: coorte total vs amostra de duracao")
rec=[]
for c in range(2010,2017):
    sub=d[d.ano_nasc==c]; ntot=len(sub)
    t,e=build(sub); nvalid=int((np.isfinite(t)&(t>=0)).sum())
    n_late=int((sub.idade_sol>47).sum())           # aplicou apos elegibilidade
    n_neg=ntot-nvalid-n_late if ntot-nvalid>n_late else 0
    # CIF incluindo os >47 como aging-out imediato (t=0, cause2)
    t2=t.copy(); e2=e.copy()
    late=(sub.idade_sol>47).values
    t2=np.where(late,0.0,t2); e2=np.where(late,2,e2)   # entram como aging-out imediato
    cif_inc,_,_,ninc=aj(t2,e2)
    rec.append((c,ntot,nvalid,n_late,cur[c][0],cif_inc))
for c,ntot,nvalid,nlate,cifx,cifi in rec:
    S(f"  {c}: total={ntot:,} duracao={nvalid:,} excl(idade>47)={nlate:,} | CIF excl={cifx:.3f} CIF incl>47={cifi:.3f}")
S(f"  >> incluindo os aplicantes >47m como aging-out: {rec[0][5]:.2f}->{rec[-1][5]:.2f} (vs {cur[2010][0]:.2f}->{cur[2016][0]:.2f})")

# ================= 6. gradiente de renda Q4-Q1 (CIF365) =================
S("\n## 6. gradiente de renda Q4-Q1 (CIF365 referral)")
grad=[]
for c in range(2010,2017):
    row=[c]
    cifs={}
    for q in [1,2,3,4]:
        sub=d[(d.ano_nasc==c)&(d.rq==q)]; t,e=build(sub); cifs[q]=aj(t,e)[0]
    grad.append((c,cifs[1],cifs[4],cifs[4]-cifs[1]))
for c,q1,q4,gap in grad: S(f"  {c}: Q1={q1:.3f} Q4={q4:.3f} gap={gap:+.3f}")
S(f"  >> gap Q4-Q1: {grad[0][3]*100:.1f} -> {grad[-1][3]*100:.1f} p.p.")

# ================= TABELAS .tex =================
def f3(x): return f"{x:.3f}" if x is not None and pd.notna(x) else "---"
# T-A: (i) atual vs (ii) follow-up comum
body=[]
for c in range(2010,2017):
    body.append([str(c),f3(cur[c][0]),f"{cur[c][1]:.0f}",f"{cur[c][3]:,}",f3(fu[c][0]),f"{fu[c][1]:.0f}",f"{fu[c][3]:,}"])
emit("P2_followup",
 "Referral incidence and restricted mean time: current sample vs.\\ common 365-day follow-up",
 "Cumulative incidence of referral within 365 days (Aalen--Johansen, aging out competing) and "
 "restricted mean days in the eligible queue within 365 days, by birth cohort. Right block "
 "restricts to applications with a full 365-day administrative window (application date on or "
 "before the panel close minus 365 days), so late-2018 applications with unobserved one-year "
 "outcomes are removed.",
 "lrrrrrr",
 ["Cohort","CIF (cur)","RMST","N","CIF (fu)","RMST","N"],body,label="P2fu")
# T-B: referral vs matricula
body=[[str(c),f3(cur[c][0]),f"{cur[c][1]:.0f}",f3(mat[c][0]),f"{mat[c][1]:.0f}"] for c in range(2010,2017)]
emit("P2_endpoint",
 "Terminal event: referral vs.\\ enrolment",
 "CIF within 365 days and RMST(365), by birth cohort, using referral (the paper's endpoint) or "
 "enrolment as the terminal event; aging out is the competing risk in both.",
 "lrrrr",["Cohort","CIF ref","RMST ref","CIF mat","RMST mat"],body,label="P2end")
# T-C: withdrawals + break + reconciliation combined robustness
body=[]
for c in range(2010,2017):
    body.append([str(c),f3(cur[c][0]),f3(wd[c][0]),f3(exbrk[c][0]),f3(h1[c][0]),f3(rec[c-2010][5])])
emit("P2_robust",
 "Robustness of one-year referral incidence: withdrawals, the 2012--2013 break, and sample "
 "reconciliation",
 "CIF of referral within 365 days by birth cohort. Base: referral vs.\\ aging out. +Withdr.: adds "
 "recorded queue withdrawals (desist\\^encia) as a competing event. Excl.\\ break: excludes "
 "applications dated July 2012--December 2013, around the step in recorded referrals "
 "(110{,}205 to 341{,}031). H1 only: applications in the first calendar semester, a fixed "
 "application-timing stratum. +Late appl.: adds applicants who applied after the 47-month "
 "eligibility limit as immediate aging-out (they are excluded from the base because they had no "
 "eligible time).",
 "lrrrrr",
 ["Cohort","Base","+Withdr.","Excl.\\ break","H1 only","+Late appl."],body,label="P2rob")
# T-D: reconciliation counts
body=[[str(c),f"{ntot:,}",f"{nvalid:,}",f"{nlate:,}",f"{100*nlate/ntot:.1f}"] for c,ntot,nvalid,nlate,_,_ in rec]
emit("P2_reconcile",
 "Sample reconciliation: birth-cohort total vs.\\ duration-analysis sample",
 "Total: children of the cohort with a valid first application. Duration: those with non-negative "
 "eligible time, the sample of the competing-risks analysis. Excl.$>$47m: applicants who applied "
 "after the 47-month eligibility limit (age at application above 47 months), who have no eligible "
 "time and are dropped; this is the bulk of the gap. The excluded share falls sharply across "
 "cohorts because early applicants were much older, so the exclusion is mechanically tied to the "
 "timing shift; it is conservative for the trend (adding these children as immediate aging-out "
 "lowers early-cohort incidence and widens the gain, see Table~\\ref{tab:P2rob}, +Late appl.).",
 "lrrrr",
 ["Cohort","Total","Duration","Excl.$>$47m","\\% excl."],body,label="P2rec")
# T-E: income gradient full series
body=[[str(c),f3(q1),f3(q4),f"{100*gap:+.1f}"] for c,q1,q4,gap in grad]
emit("P2_gradient",
 "Income gradient in one-year referral incidence, full series by birth cohort",
 "CIF of referral within 365 days by postcode income quartile (Q1 lowest), and the Q4$-$Q1 gap in "
 "percentage points, by birth cohort. Competing-risks estimator (aging out competing). Replaces "
 "the gradient table that used the age-censored Kaplan--Meier.",
 "lrrr",["Cohort","Q1","Q4","gap (p.p.)"],body,label="P2grad")

with open(os.path.join(ROOT,r"03_build\build11","p2.log"),"w",encoding="utf-8") as f: f.write("\n".join(LOG))
S("\nOK P2: P2_followup, P2_endpoint, P2_robust, P2_reconcile, P2_gradient")
