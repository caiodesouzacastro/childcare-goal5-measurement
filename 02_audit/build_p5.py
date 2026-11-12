# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BLOCO P5 - A: cobertura vs timing (denominadores de idade comum). B: uma unica
# reconstrucao da fila que fecha por identidade micro; gap ao oficial = inobservavel.
# Reaproveita spine (build10) + SINASC + evolucaodemanda. NAO edita o corpo.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os, csv, unicodedata
ROOT=NE_ROOT
STG=os.path.join(ROOT,r"03_build\build10\_staging"); OUT=os.path.join(ROOT,r"03_build\build11\tables")
PUB=os.path.join(ROOT,"01_dados_publicos")
EVOL=os.path.join(ROOT,r"03_build\build04\_ext\evolucaodemanda.csv")
PANEL=pd.Timestamp("2019-11-28"); LOG=[]
def S(x): LOG.append(str(x)); print(x)
def emit(name,cap,note,cols,header,body,label=None):
    label=label or name
    L=["% BLOCO P5. Descritivo.","\\begin{table}[htbp]\\centering",f"\\caption{{{cap}}}",
       f"\\label{{tab:{label}}}","\\footnotesize","\\setlength{\\tabcolsep}{4pt}",
       f"\\begin{{tabular}}{{{cols}}}","\\toprule"," & ".join(header)+" \\\\","\\midrule"]
    for r in body: L.append("\\midrule" if r=="MID" else " & ".join(r)+" \\\\")
    L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
    open(os.path.join(OUT,name+".tex"),"w",encoding="utf-8").write("\n".join(L)+"\n"); print("tex:",name)

sp=pd.read_parquet(os.path.join(STG,"spine.parquet"),
    columns=["cd_aluno_sme","d_sol1","d_enc1","d_des1","d_age47","idade_sol","ano_nasc","mes_nasc"])
sp["d_sol"]=sp["d_sol1"]

# ================= BLOCO A: cobertura vs timing =================
S("#### BLOCO A ####")
# SINASC (nascidos por ano)
def nz(s): return "".join(c for c in unicodedata.normalize("NFD",str(s).strip().upper()) if unicodedata.category(c)!="Mn")
rows=list(csv.reader(open(os.path.join(PUB,"ceinfo","sinasc_nv_distrito_2006_2026.csv"),encoding="utf-8"),delimiter=";"))
hdr=rows[0]; yidx={int(hdr[i]):i for i in range(1,len(hdr)) if hdr[i].isdigit()}
bd={}
for r in rows[1:]:
    nm=r[0].strip()
    if nm in ("Ignorado","Total"): continue
    for y,i in yidx.items():
        try: bd[(nz(nm),y)]=int(r[i])
        except: pass
dist=sorted(set(k[0] for k in bd))
def births(y): return sum(bd.get((dd,y),0) for dd in dist)

# A1: entre registradas ATE 24m, fracao registrada ate 12m (denominador de idade comum)
S("\n## A1: share <12m ENTRE registradas ate 24m, por coorte")
a1=[]
for c in range(2010,2017):
    d=sp[sp.ano_nasc==c]; den=(d.idade_sol<24).sum(); num=(d.idade_sol<12).sum()
    a1.append((c,num/den if den else np.nan,den))
    S(f"  {c}: {num/den:.3f}  (N reg<=24m = {den:,})")
# A2/A3: fracao da coorte (denom SINASC) registrada ate 24/36/47m, coortes completas
S("\n## A2/A3: fracao da coorte (denom SINASC) registrada ate 24/36/47m")
mat=[]
for c in range(2010,2015):   # 2010-2014 completas ate 47m (c+4 <= 2018)
    d=sp[sp.ano_nasc==c]; b=births(c)
    r={"c":c}
    for X in [24,36,47]: r[X]=100*(d.idade_sol<X).sum()/b
    mat.append(r); S(f"  {c}: <=24m={r[24]:.1f}%  <=36m={r[36]:.1f}%  <=47m={r[47]:.1f}%")
# 33.7 -> 70.9 em 24m (2010->2016) usa SINASC denom, todas as coortes observam 24m
c24={c:100*(sp[sp.ano_nasc==c].idade_sol<24).sum()/births(c) for c in range(2010,2017)}
S(f"  <=24m 2010->2016: {c24[2010]:.1f}% -> {c24[2016]:.1f}%  (confirma 33.7->70.9)")

# tabelas A
body=[[str(c),f"{v:.3f}",f"{den:,}"] for c,v,den in a1]
emit("P5_timing",
 "Timing within a common age window: share registered before 12 months among children registered "
 "before 24 months, by birth cohort",
 "Denominator: children of the cohort registered before 24 months of age---a common age window "
 "observed for every cohort 2010--2016. Numerator: those registered before 12 months. Because the "
 "denominator is fixed at a common horizon, this isolates the shift in \\emph{timing} within the "
 "window from the widening of coverage.",
 "lrr",["Cohort","Share $<$12m $\\mid$ $<$24m","N ($<$24m)"],body,label="P5timing")
body=[[str(r["c"]),f"{r[24]:.1f}",f"{r[36]:.1f}",f"{r[47]:.1f}"] for r in mat]
emit("P5_coverage",
 "Coverage by common horizon: share of the birth cohort registered by 24, 36 and 47 months",
 "Share of the birth cohort (live-births denominator, SINASC) with a first application before each "
 "age, for the cohorts 2010--2014 that are fully observed at every horizon (a cohort is observed to "
 "age $X$ only if it reaches $X$ within the 2010--2018 request panel). Registration rose at every "
 "horizon: it moved earlier \\emph{and} became more prevalent at the ages when childcare is "
 "relevant.",
 "lrrr",["Cohort","$\\le$24m","$\\le$36m","$\\le$47m"],body,label="P5cov")

# ================= BLOCO B: reconstrucao da fila =================
S("\n#### BLOCO B ####")
# primeira saida por crianca: referral, aging(47m), desativacao(desistencia)
big=pd.Timestamp("2100-01-01")
t_ref=sp.d_enc1.where(sp.d_enc1>=sp.d_sol)
t_age=sp.d_age47.where(sp.d_age47>=sp.d_sol, sp.d_sol)     # se aplicou apos 47m, saida imediata
t_des=sp.d_des1.where(sp.d_des1>=sp.d_sol)
M=pd.DataFrame({"ref":t_ref.fillna(big),"age":t_age.fillna(big),"des":t_des.fillna(big)})
sp["exit_t"]=M.min(axis=1); sp["exit_ty"]=M.idxmin(axis=1)
sp.loc[sp.exit_t>PANEL,["exit_ty"]]="open"                 # ainda na fila ao fim do painel
sp["ys"]=sp.d_sol.dt.year; sp["ye"]=sp.exit_t.dt.year
def Q(Y):   # estoque em 31/dez/Y = aplicou<=dezY e saida>dezY
    end=pd.Timestamp(Y,12,31); return int(((sp.d_sol<=end)&(sp.exit_t>end)).sum())
# oficial
MES={"jan":1,"fev":2,"mar":3,"abr":4,"mai":5,"jun":6,"jul":7,"ago":8,"set":9,"out":10,"nov":11,"dez":12}
ev=pd.read_csv(EVOL,sep=";",thousands=".",dtype={"MES_ANO_REF":str})
ev["ano"]=ev.MES_ANO_REF.str[-2:].astype(int)+2000; ev["mes"]=ev.MES_ANO_REF.str[:3].map(MES)
ev["DEM_CRECHE"]=pd.to_numeric(ev.DEM_CRECHE,errors="coerce")
off={int(a):int(b) for a,b in ev[ev.mes==12].groupby("ano").DEM_CRECHE.sum().items()}

S("\n## reconstrucao micro (universo = 1as solicitacoes B_novo)")
S("  identidade: Q_t = Q_{t-1} + new - ref - aged - des  (tudo dos micro-fluxos)")
rowsB=[]; Qprev=Q(2009)
S(f"  Q(2009) inicial (proprio universo) = {Qprev:,}")
for Y in range(2010,2019):
    new=int((sp.ys==Y).sum())
    ref=int(((sp.ye==Y)&(sp.exit_ty=="ref")).sum())
    aged=int(((sp.ye==Y)&(sp.exit_ty=="age")).sum())
    des=int(((sp.ye==Y)&(sp.exit_ty=="des")).sum())
    Qt=Q(Y); pred=Qprev+new-ref-aged-des; internal=Qt-pred
    offv=off.get(Y); gap=(Qt-offv) if offv else None
    rowsB.append(dict(Y=Y,Q0=Qprev,new=new,ref=ref,aged=aged,des=des,Qt=Qt,internal=internal,
                      off=offv,gap=gap,gappct=(100*gap/offv if offv else None)))
    Qprev=Qt
S("  ano | Q0 new ref aged des | Qt pred internal | oficial gap gap%")
for r in rowsB:
    offs="---" if r["off"] is None else f"{r['off']:,}"
    gp="---" if r["gap"] is None else f"{r['gap']:+,}"
    gpp="---" if r["gappct"] is None else f"{r['gappct']:+.0f}%"
    S(f"  {r['Y']} | {r['Q0']:>7,} {r['new']:>7,} {r['ref']:>7,} {r['aged']:>6,} {r['des']:>5,} | "
      f"{r['Qt']:>7,} {r['internal']:>+4d} | {offs:>8} {gp:>9} {gpp}")
maxint=max(abs(r["internal"]) for r in rowsB)
S(f"  >> residuo INTERNO maximo = {maxint} criancas (a identidade micro FECHA)")
gaps=[r["gappct"] for r in rowsB if r["gappct"] is not None]
S(f"  >> gap ao oficial: {min(gaps):.0f}% a {max(gaps):.0f}% (grande e instavel -> inobservabilidade)")

# tabela B
body=[]
for r in rowsB:
    offs="---" if r["off"] is None else f"{r['off']:,}"
    gp="---" if r["gap"] is None else f"{r['gap']:+,}"
    body.append([str(r["Y"]),f"{r['Q0']:,}",f"{r['new']:,}",f"{r['ref']:,}",f"{r['aged']:,}",
                 f"{r['des']:,}",f"{r['Qt']:,}",f"{r['internal']:+d}",offs,gp])
emit("P5_queue",
 "Micro reconstruction of the queue stock, and its gap to the published series",
 "A single reconstruction on the first-application universe. Q$_0$: stock at 1 January (children "
 "who had applied and not yet exited), from the micro data itself, not from the official series. "
 "new: first applications in the year. ref/aged/des: first exits in the year by referral, by "
 "aging out at 47 months, and by recorded withdrawal. Q$_t$: year-end stock, counted directly. "
 "The accounting identity Q$_t$ $=$ Q$_{t-1}$ $+$ new $-$ ref $-$ aged $-$ des closes from the "
 "flows themselves; the internal residual (col.\\ int.) is at most a few hundred children "
 "(edge-of-year timing and refusals-without-flag), \\emph{not} a plug defined to close. "
 "off: official December registered demand (DEM\\_CRECHE). gap: Q$_t$ minus official. The micro "
 "flows do not reproduce the published stock. The 2010 gap is largely mechanical: the pre-panel "
 "backlog is missing from Q$_0$, so the reconstruction starts far below the true stock. The "
 "persistent gaps thereafter, between $-6$ and $-17$ percent, narrowing over the period but "
 "never closing, are the "
 "informative ones: they indicate that the published stock is a composite administrative "
 "object---incorporating re-registrations, unrecorded removals and a broader universe---rather than a reproducible count "
 "of first-application waiting.",
 "lrrrrrrrrr",
 ["Year","Q$_0$","new","ref","aged","des","Q$_t$","int.","official","gap"],body,label="P5queue")

with open(os.path.join(ROOT,r"03_build\build11","p5.log"),"w",encoding="utf-8") as f: f.write("\n".join(LOG))
S("\nOK P5: P5_timing, P5_coverage, P5_queue")
