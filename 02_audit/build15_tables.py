# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# 30/10/2026 (rodada legendas-instala-2026-10-30): os titulos e as notas das exibicoes (\caption e \tabnote) sao
# TEXTO DO AUTOR, de 30/10/2026, gravados nos .tex e tambem neste script. Nao regravar os .tex gerados por este script
# sem autorizacao do autor.
# Trava (trava_legenda.py, 30/10/2026): \caption e \tabnote que difiram do arquivo nao sao regravados, salvo com NE_SOBRESCREVER_LEGENDA=1.
# FASE 2 (25/10/2026): gera as tabelas NOVAS do paper sob a tese da cobertura, so a partir de saidas de script
# (03_build/build14_cobertura, 03_build/build15) e das tabelas existentes (valores copiados por leitura de arquivo).
# Nenhum numero e digitado. Saida: 04_paper/assets/tables/v2/*.tex e 03_build/build15/congelados_tabelas.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, re, numpy as np, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
from trava_legenda import grava_tex  # trava das legendas (30/10/2026)
ROOT = NE_ROOT; C14 = os.path.join(ROOT, r"03_build\build14_cobertura"); C15 = os.path.join(ROOT, r"03_build\build15")
T = os.path.join(ROOT, r"04_paper\assets\tables"); V2 = os.path.join(T, "v2"); os.makedirs(V2, exist_ok=True)
REC = "\\emph{Source:} SME childcare request record (2010--2018 applications, referral and enrollment dates through November 2019)"
EOL = "SME enrollment records (EOL), first childcare enrollment per child, 2003--2019"
def num(x, d=1): return f"{x:,.{d}f}" if d else f"{int(round(x)):,}"
def sg(x, d=3): return (f"+{x:.{d}f}" if x >= 0 else f"$-${abs(x):.{d}f}")
def tabular(spec, header, rows): return "\n".join(["\\begin{tabular}{" + spec + "}", "\\toprule", header + " \\\\", "\\midrule"] + rows + ["\\bottomrule", "\\end{tabular}"])
def panel(t): return f"\\par\\medskip\\textbf{{{t}}}\\par\\smallskip"
def emit(fn, cap, label, parts, note, fit=True):
    L = [f"% Gerado por 02_audit/build15_tables.py (25/10/2026). Nao editar a mao.", "\\begin{table}[htbp]\\centering", f"\\caption{{{cap}}}", f"\\label{{tab:{label}}}", "\\footnotesize"]
    for p in parts: L.append(("\\fitbox{%\n" + p + "}") if (fit and p.startswith("\\begin{tabular}")) else p)
    L += [f"\\tabnote{{{note}}}", "\\end{table}"]
    grava_tex(os.path.join(V2, fn + ".tex"), "\n".join(L) + "\n", fn + ".tex"); print("ok", fn)
def tabrows(fname, k=0):
    s = open(os.path.join(T, fname), encoding="utf-8").read()
    b = re.findall(r"\\begin\{tabular\}.*?\\end\{tabular\}", s, flags=re.S)[k]
    body = b.split("\\midrule", 1)[1].split("\\bottomrule")[0]
    return [l.strip() for l in body.strip().splitlines() if l.strip() and not l.strip().startswith("\\midrule") and "&" in l]
def cells(row): return [c.strip().rstrip("\\").strip() for c in row.split("&")]
FROZ = []
def fz(item, val, src): FROZ.append(dict(item=item, valor=val, origem=src))

# ================= 1. COBERTURA (corpo) =================
e = pd.read_parquet(os.path.join(C14, "eol_creche.parquet"), columns=["CD_ALUNO_SME", "AN_LETIVO", "DT_IN_MAT", "CD_UNIDADE_EDUCACAO", "TIPO_ESCOLA"])
e["id"] = pd.to_numeric(e.CD_ALUNO_SME, errors="coerce").astype("Int64"); e["an"] = pd.to_numeric(e.AN_LETIVO); e["dt"] = pd.to_datetime(e.DT_IN_MAT.str[:10], errors="coerce")
f = e.sort_values(["id", "an", "dt"]).groupby("id").first()
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"), columns=["cd_aluno_sme"])
ids = set(pd.to_numeric(sp.cd_aluno_sme, errors="coerce").astype("Int64"))
f["cob"] = f.index.isin(ids); f["ano"] = f.an.astype(int); f["fev"] = f.dt.dt.month == 2
rA = []
for y in range(2010, 2019):
    g = f[f.ano == y]; fe = g[g.fev]; ot = g[~g.fev]
    u = fe.groupby("CD_UNIDADE_EDUCACAO").cob.agg(["size", "mean"]); u = u[u["size"] >= 20]
    rA.append([str(y), num(len(g), 0), num(100 * g.cob.mean()), num(100 * fe.cob.mean()), num(100 * ot.cob.mean()) if len(ot) >= 100 else "--",
               num(len(u), 0), f"{u['mean'].median():.2f}", num(100 * (u['mean'] >= .9).mean())])
    fz(f"cobertura entrantes {y}", rA[-1][2], "build15_tables.py (= cob_por_ano.csv)"); fz(f"cobertura fev {y}", rA[-1][3], "build15_tables.py")
    fz(f"cobertura outros meses {y}", rA[-1][4], "build15_tables.py"); fz(f"unidades fev {y}: N/p50/%>=90", f"{rA[-1][5]} / {rA[-1][6]} / {rA[-1][7]}", "build15_tables.py")
# EOL por coorte com o MESMO denominador do paper (soma dos 96 distritos do SINASC), nao a linha Total
import csv as _csv
_rr = list(_csv.reader(open(os.path.join(ROOT, r"01_dados_publicos\ceinfo\sinasc_nv_distrito_2006_2026.csv"), encoding="utf-8"), delimiter=";"))
_h = _rr[0]; _dd = [x for x in _rr[1:] if x and x[0].strip() not in ("Ignorado", "Total")]; _Bd = {int(h): sum(int(x[i]) for x in _dd) for i, h in enumerate(_h) if h.isdigit()}
_e = pd.read_parquet(os.path.join(C14, "eol_creche.parquet"), columns=["CD_ALUNO_SME", "AN_LETIVO", "DT_IN_MAT", "ANO_NASC_ALUNO", "MES_NASC_ALUNO"])
_e["id"] = pd.to_numeric(_e.CD_ALUNO_SME, errors="coerce"); _e["an"] = pd.to_numeric(_e.AN_LETIVO); _e["dt"] = pd.to_datetime(_e.DT_IN_MAT.str[:10], errors="coerce")
_f = _e.sort_values(["id", "an", "dt"]).groupby("id").first()
_f["idade"] = (_f.dt.dt.year - pd.to_numeric(_f.ANO_NASC_ALUNO, errors="coerce")) * 12 + (_f.dt.dt.month - pd.to_numeric(_f.MES_NASC_ALUNO, errors="coerce"))
_f["coorte"] = pd.to_numeric(_f.ANO_NASC_ALUNO, errors="coerce")
eo = pd.DataFrame([dict(coorte=c, EOL_antes_24m=round(100 * ((_f.coorte == c) & _f.idade.between(0, 60) & (_f.idade < 24)).sum() / _Bd[c], 1)) for c in range(2010, 2017)])
eo.to_csv(os.path.join(C15, "eol_coorte_den96.csv"), index=False)
n4 = {int(cells(r)[0]): cells(r) for r in tabrows("N4_enrolled.tex")}
rB = []
for _, r in eo.iterrows():
    co = int(r.coorte); fila24 = float(n4[co][3]); rB.append([str(co), num(fila24), num(r.EOL_antes_24m), sg(fila24 - r.EOL_antes_24m, 1)])
    fz(f"matriculados <24m coorte {co}: fila / EOL", f"{fila24} / {r.EOL_antes_24m}", "N4_enrolled.tex; cob_eol_coorte.csv")
emit("V2_coverage", "Coverage of the supplied request record among children entering childcare, 2010--2018", "coverage",
     [panel("Panel A. Entrants in each year found in the request record"),
      tabular("lrrrrrrr", "Year of entry & Entrants & In record (\\%) & February (\\%) & Other months (\\%) & Centers & Median center & Centers $\\geq$90\\% (\\%)", [" & ".join(x) + " \\\\" for x in rA]),
      panel("Panel B. Share of each birth cohort enrolled before 24 months, by source (\\% of live births)"),
      tabular("lrrr", "Birth cohort & Request record & Enrollment records & Difference", [" & ".join(x) + " \\\\" for x in rB])],
     "\\emph{Sources:} SME childcare request record (applications dated 2010--2018, with referral and enrollment dates through November 2019); SME enrollment records (Escola On-Line, EOL). \\emph{Sample:} children whose first childcare enrollment falls in each year from 2010 to 2018. \\emph{Unit:} child. Coverage is the share of first entrants who can be matched to a first application in the supplied request files. It measures the completeness of the files available for this analysis, not necessarily that of SME's underlying administrative system. Figure~\\ref{fig:coverage} shows the monthly pattern.")

# ================= 2. INGENUA x CORRIGIDA (corpo) =================
cif = pd.read_csv(os.path.join(C14, "janela_cif.csv")); co = cif[cif.serie == "coorte"].set_index("grupo"); ya = cif[cif.serie == "ano_solicitacao"].set_index("grupo")
co.index = co.index.astype(str); ya.index = ya.index.astype(str)
p3 = {cells(r)[0]: cells(r) for r in tabrows("P3_series.tex")}
std = p3["Applicant composition"]; S10, S13, S16 = float(std[1]), float(std[4]), float(std[7])
n4c = {k: float(v[5]) for k, v in n4.items()}
dist = pd.read_csv(os.path.join(C14, "janela_distritos.csv"), index_col=0)
def chg(a, b, d=3): return f"{a:.{d}f} $\\rightarrow$ {b:.{d}f}"
rows = [
 ["One-year referral, by birth cohort", chg(co.ref365["2010"], co.ref365["2016"]) + f" ({sg(co.ref365['2016'] - co.ref365['2010'])})", chg(co.ref365["2013"], co.ref365["2016"]) + f" ({sg(co.ref365['2016'] - co.ref365['2013'])})"],
 ["One-year referral, by year of application", chg(ya.ref365["2010"], ya.ref365["2017"]) + f" ({sg(ya.ref365['2017'] - ya.ref365['2010'])})", chg(ya.ref365["2013"], ya.ref365["2017"]) + f" ({sg(ya.ref365['2017'] - ya.ref365['2013'])})"],
 ["One-year enrollment, by birth cohort", chg(co.mat365["2010"], co.mat365["2016"]) + f" ({sg(co.mat365['2016'] - co.mat365['2010'])})", chg(co.mat365["2013"], co.mat365["2016"]) + f" ({sg(co.mat365['2016'] - co.mat365['2013'])})"],
 ["One-year referral, composition held at 2013", chg(S10, S16) + f" ({sg(S16 - S10)})", chg(S13, S16) + f" ({sg(S16 - S13)})"],
 ["Registered before 12 months (\\% of births)", chg(n4c[2010], n4c[2016], 1) + f" ({sg(n4c[2016] - n4c[2010], 1)})", chg(n4c[2013], n4c[2016], 1) + f" ({sg(n4c[2016] - n4c[2013], 1)})"],
 ["Districts where early registration rose", f"{int(dist.loc['2010-2016','sobe'])} of {int(dist.loc['2010-2016','distritos'])}; median {sg(dist.loc['2010-2016','mediana'])}",
  f"{int(dist.loc['2013-2016','sobe'])} of {int(dist.loc['2013-2016','distritos'])}; median {sg(dist.loc['2013-2016','mediana'])}"],
]
for r in rows: fz("ingenua x corrigida: " + r[0], r[1] + " || " + r[2], "janela_cif.csv; P3_series.tex; N4_enrolled.tex; janela_distritos.csv")
emit("V2_naive", "The full extract and the window of complete coverage", "naive",
     [tabular("lll", "Measure & Full extract & Complete coverage", [" & ".join(r) + " \\\\" for r in rows])],
     REC + "; live births (SINASC). \\emph{Sample:} full extract, birth cohorts 2010--2016 or applications 2010--2017; complete coverage, birth cohorts 2013--2016 or applications 2013--2017 (Section~\\ref{sec:coverage}). \\emph{Variables:} one-year referral and enrollment, cumulative incidence within 365 days of the first application with aging out as a competing event, among applicants with eligible time; composition held at 2013, cohorts reweighted to the 2013 cohort's joint distribution of age at application, priority, postcode-income quartile, district and semester of application; registered before 12 months, children with a first application before 12 months as a share of live births; districts, change in the share registered before 12 months among children registered before 24 months, by district of residence. \\emph{Exercise:} the first column reproduces the full-extract estimates; the second restricts them to the years in which the record covers almost all entrants. Descriptive.", fit=True)

# ================= 3. SERVICO (corpo) =================
e1 = {cells(r)[0]: cells(r) for r in tabrows("E1_cohort.tex")}; p2 = {cells(r)[0]: cells(r) for r in tabrows("P2_endpoint.tex")}
rS = [" & ".join([c, e1[c][1], e1[c][2], e1[c][3], e1[c][4], e1[c][5], e1[c][6], e1[c][7], p2[c][3], p2[c][4]]) + " \\\\" for c in ("2013", "2014", "2015", "2016")]
e1y = {cells(r)[0]: cells(r) for r in tabrows("appx/A_E1year.tex")}
rY = [" & ".join([y, e1y[y][1], e1y[y][3], f"{ya.mat365[y]:.3f}", e1y[y][7]]) + " \\\\" for y in ("2013", "2014", "2015", "2016", "2017")]
rf = pd.read_csv(os.path.join(C15, "reforma_semestral.csv"))
rR = [" & ".join([r.semestre, num(r.N, 0), f"{r.ref365:.3f}", f"{r.mat365:.3f}"]) + " \\\\" for r in rf.itertuples()]
for c in ("2013", "2016"): fz(f"Tabela servico coorte {c}", " ".join(e1[c][1:]) + " | mat " + p2[c][3] + " RMST " + p2[c][4], "E1_cohort.tex; P2_endpoint.tex")
for r in rf.itertuples(): fz(f"encaminhamento 365d por semestre {r.semestre}", f"{r.ref365:.3f} / mat {r.mat365:.3f} (N {r.N:,})", "reforma_semestral.csv")
emit("V2_service", "One-year referral and enrollment in the window of complete coverage", "service",
     [panel("Panel A. By birth cohort"),
      tabular("lrrrrrrrrr", "Birth cohort & N & ref$_{180}$ & ref$_{365}$ & ref$_{730}$ & age$_{365}$ & RMST$_{365}$ & Median & enr$_{365}$ & RMST enr.", rS),
      panel("Panel B. By year of application"),
      tabular("lrrrr", "Year of application & N & ref$_{365}$ & enr$_{365}$ & Median", rY),
      panel("Panel C. By semester of application, before and after the July 2016 allocation ordinance"),
      tabular("lrrr", "Semester of application & N & ref$_{365}$ & enr$_{365}$", rR)],
     REC + ". \\emph{Sample:} applicants with eligible time (first application at or before 47 months); Panel A, birth cohorts 2013--2016; Panels B and C, first applications 2013--2017 and 2013S1--2018S1 (later applications lack 365 days of follow-up). \\emph{Variables:} time from first application in days; ref$_{t}$, cumulative incidence of referral by day $t$; age$_{365}$, cumulative incidence of aging out (reaching 47 months unreferred) by day 365; RMST, restricted mean days without the event within 365; Median, day on which referral incidence reaches 0.5; enr, the same with enrollment as the terminal event. Panel C: the ordinance of 14 July 2016 formalized automated matching (Section~\\ref{sec:institutions}); semesters from 2016S2 are after it. \\emph{Exercise:} Aalen--Johansen estimator with aging out as the competing event; descriptive.")

# ================= 4. ESPECIFICACOES (corpo) =================
rob = {cells(r)[0]: cells(r) for r in tabrows("P2_robust.tex")}
def gain(a, b): return f"{float(a):.3f} & {float(b):.3f} & {sg(float(b) - float(a))}"
bt = open(os.path.join(C15, "p3boot_2013_2016.log"), encoding="utf-8").read()
ci_std = re.search(r"Applicant std Delta=\+([\d.]+)\s+se=([\d.]+)\s+IC95=\[\+([\d.]+), \+([\d.]+)\]", bt).groups()
ci_raw = re.search(r"Raw\s+Delta=\+([\d.]+)\s+se=([\d.]+)\s+IC95=\[\+([\d.]+), \+([\d.]+)\]", bt).groups()
p3l = open(os.path.join(C15, "p3_2013_2016.log"), encoding="utf-8").read()
g2, g3 = re.search(r"grossa: S2=\+([\d.]+)\s+S3=\+([\d.]+)", p3l).groups(); f2, f3 = re.search(r"fina:\s+S2=\+([\d.]+)\s+S3=\+([\d.]+)", p3l).groups()
dec = re.search(r"solicitante ([+-][\d.]+), oferta ([+-][\d.]+), operacional ([+-][\d.]+)", p3l).groups()
s3 = p3["Applicant + service environment"]
rows = [
 ["Base: referral, aging out competing", gain(rob["2013"][1], rob["2016"][1]), "--"],
 ["Recorded withdrawal as a further competing event", gain(rob["2013"][2], rob["2016"][2]), "--"],
 ["Children who applied after 47 months counted as aging out", gain(rob["2013"][5], rob["2016"][5]), "--"],
 ["Applications in the first calendar semester only", gain(rob["2013"][4], rob["2016"][4]), "--"],
 ["Applications dated July 2012--December 2013 excluded", gain(rob["2013"][3], rob["2016"][3]), "--"],
 ["Window starting with the 2014 cohort", gain(rob["2014"][1], rob["2016"][1]), "--"],
 ["Enrollment as the terminal event", gain(p2["2013"][3], p2["2016"][3]), "--"],
 ["Composition held at 2013 (main cells)", gain(std[4], std[7]), f"[+{ci_std[2]}, +{ci_std[3]}]"],
 ["Composition held at 2013, coarse / fine cells", f"-- & -- & +{g2} / +{f2}", "--"],
 ["Composition and service environment held fixed", f"{float(s3[4]):.3f} & {float(s3[7]):.3f} & {dec[2]}", f"coarse +{g3}, fine +{f3}"],
 ["Unweighted, bootstrap interval", gain(rob["2013"][1], rob["2016"][1]), f"[+{ci_raw[2]}, +{ci_raw[3]}]"],
]
for r in rows: fz("especificacao: " + r[0], r[1] + " | " + r[2], "P2_robust.tex; P2_endpoint.tex; P3_series.tex; build15/p3boot_2013_2016.log; build15/p3_2013_2016.log")
fz("decomposicao exata 2013-2016: composicao / oferta / residual", " / ".join(dec), "build15/p3_2013_2016.log")
emit("V2_specs", "The 2013--2016 gain in one-year referral under alternative specifications", "specs",
     [tabular("lrrrl", "Specification & 2013 & 2016 & $\\Delta$ & Interval or range", [" & ".join(r) + " \\\\" for r in rows])],
     REC + ". \\emph{Sample:} applicants of birth cohorts 2013--2016 with eligible time, except where a row says otherwise. \\emph{Variables:} cumulative incidence of referral (or enrollment) within 365 days of the first application. \\emph{Exercise:} $\\Delta$ is computed from unrounded incidences. Aalen--Johansen estimator; reweighting to the 2013 cohort's joint distribution of applicant attributes (main cells: age at application, priority, postcode-income quartile, district, semester; coarse: age, priority, income; fine: eight age bins, priority, income, district, month), weights trimmed at the 1st and 99th percentiles; service environment adds the number of centers open within 2\\,km at the application date. Intervals: 1,000 bootstrap replications resampling children within the 2013 and 2016 cohorts, weights recomputed in each, percentile interval, seed 20260726; they reflect sampling variability only. In the exact decomposition of the raw change, composition contributes " + dec[0] + " and the service environment " + dec[1] + ", leaving " + dec[2] + ". Descriptive.")

# ================= 5. TIMING (corpo) =================
pt = {cells(r)[0]: cells(r) for r in tabrows("P5_timing.tex")}; n3 = {cells(r)[0]: cells(r) for r in tabrows("N3_district.tex")}
v2 = pd.read_csv(os.path.join(C14, "v2nums.csv"))
r6 = v2[v2.item.str.startswith("registro antes de 6")].janela_limpa.iloc[0]   # '26.1 -> 33.4 (2013->2016)'
import csv
rr = list(csv.reader(open(os.path.join(ROOT, r"01_dados_publicos\ceinfo\sinasc_nv_distrito_2006_2026.csv"), encoding="utf-8"), delimiter=";"))
hdr = rr[0]; dd = [x for x in rr[1:] if x and x[0].strip() not in ("Ignorado", "Total")]; Bd = {int(h): sum(int(x[i]) for x in dd) for i, h in enumerate(hdr) if h.isdigit()}
spt = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"), columns=["ano_nasc", "idade_sol"])
rT = []
for c in ("2013", "2014", "2015", "2016"):
    s = spt[spt.ano_nasc == int(c)]; b = Bd[int(c)]
    lt6, lt12, lt24 = (100 * (s.idade_sol < k).sum() / b for k in (6, 12, 24))
    rT.append(" & ".join([c, num(b, 0), num(lt6), num(lt12), num(lt24), pt[c][1], n3[c][3], n3[c][4]]) + " \\\\")
    fz(f"timing coorte {c}: <6/<12/<24 (% nascidos), <12|<24, pesos 2010, pesos 2016", f"{lt6:.1f} {lt12:.1f} {lt24:.1f} | {pt[c][1]} {n3[c][3]} {n3[c][4]}", "build15_tables.py (spine+SINASC; valida N4); P5_timing.tex; N3_district.tex")
emit("V2_timing", "Registration timing in the window of complete coverage", "timing",
     [tabular("lrrrrrrr", "Birth cohort & Live births & $<$6m & $<$12m & $<$24m & $<$12m among $<$24m & 2010 district mix & 2016 district mix", rT)],
     REC + "; live births by district of residence (SINASC). \\emph{Sample:} birth cohorts 2013--2016, each observed from birth to 24 months. \\emph{Variables:} $<$6m, $<$12m, $<$24m: children with a first application before that age, \\% of live births; $<$12m among $<$24m: share registered before 12 months among children registered before 24 months; the last two columns average district-specific shares with the district weights of the 2010 or the 2016 cohort. Between the 2013 and 2016 cohorts the share registered before 12 months among those registered before 24 months rose in " +
     f"{int(dist.loc['2013-2016','sobe'])} of {int(dist.loc['2013-2016','distritos'])} districts (median within-district change {sg(dist.loc['2013-2016','mediana'])}, range {sg(dist.loc['2013-2016','minimo'])} to {sg(dist.loc['2013-2016','maximo'])}). \\emph{{Exercise:}} shares; descriptive.")

# ================= 6. COBERTURA POR COORTE (corpo, indicador) =================
rN = []
for c in ("2013", "2014", "2015", "2016"):
    v = n4[int(c)]; eol = eo[eo.coorte == int(c)].iloc[0]
    rN.append(" & ".join([c, v[1], v[2], v[3], v[4] if v[4] else "--", num(eol.EOL_antes_24m)]) + " \\\\")
emit("V2_cohortcov", "Share of each birth cohort enrolled by age, window of complete coverage", "cohortcov",
     [tabular("lrrrrr", "Birth cohort & Live births & Enrolled $<$12m & $<$24m & $<$36m & $<$24m (enrollment records)", rN)],
     REC + "; " + EOL + "; live births (SINASC). \\emph{Sample:} birth cohorts 2013--2016. \\emph{Variables:} children with a first enrollment before the stated age, \\% of live births; the last column uses the enrollment records instead of the request record. Cohorts are shown only where the age window is fully observed. \\emph{Exercise:} shares; descriptive.")
pd.DataFrame(FROZ).to_csv(os.path.join(C15, "congelados_tabelas.csv"), index=False); print("congelados:", len(FROZ))
