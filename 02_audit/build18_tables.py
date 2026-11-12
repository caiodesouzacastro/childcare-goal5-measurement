# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# 30/10/2026 (rodada legendas-instala-2026-10-30): os titulos e as notas das exibicoes (\caption e \tabnote) sao
# TEXTO DO AUTOR, de 30/10/2026, gravado nos .tex. Nao regravar os .tex gerados por este script sem autorizacao do autor.
# Neste script so os titulos foram atualizados; as notas, montadas por concatenacao de constantes e trechos, continuam
# com o texto anterior. A trava (trava_legenda.py, 30/10/2026) impede que uma nova execucao grave essas notas antigas
# por cima das do autor: \caption e \tabnote que difiram do arquivo nao sao regravados, salvo com NE_SOBRESCREVER_LEGENDA=1.
# MANHA, etapa 1.1 (26/10/2026): tabelas do corpo na janela a partir de jul./2012 (coortes 2012-2016) e sob a tese de nivel.
# So le saidas de script e tabelas existentes; nenhum numero e digitado. Substitui build15_tables.py para o corpo
# (V2_coverage continua valida e nao e regerada). Saida: 04_paper/assets/tables/v3/*.tex e 03_build/build18/congelados_v3.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, re, numpy as np, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
from trava_legenda import grava_tex  # trava das legendas (30/10/2026)
ROOT = NE_ROOT; C14 = os.path.join(ROOT, r"03_build\build14_cobertura"); C15 = os.path.join(ROOT, r"03_build\build15")
C17 = os.path.join(ROOT, r"03_build\build17_fatais"); C18 = os.path.join(ROOT, r"03_build\build18")
T = os.path.join(ROOT, r"04_paper\assets\tables"); V3 = os.path.join(T, "v3"); os.makedirs(V3, exist_ok=True)
REC = "\\emph{Source:} SME childcare request record (2010--2018 applications, referral and enrollment dates through November 2019)"
EOL = "SME enrollment records (EOL), first childcare enrollment per child"
def num(x, d=1): return f"{x:,.{d}f}" if d else f"{int(round(x)):,}"
def sg(x, d=3): return (f"+{x:.{d}f}" if x >= 0 else f"$-${abs(x):.{d}f}")
def tabular(spec, header, rows): return "\n".join(["\\begin{tabular}{" + spec + "}", "\\toprule", header + " \\\\", "\\midrule"] + rows + ["\\bottomrule", "\\end{tabular}"])
def panel(t): return f"\\par\\medskip\\textbf{{{t}}}\\par\\smallskip"
def emit(fn, cap, label, parts, note, fit=True):
    L = ["% Gerado por 02_audit/build18_tables.py (26/10/2026). Nao editar a mao.", "\\begin{table}[htbp]\\centering", f"\\caption{{{cap}}}", f"\\label{{tab:{label}}}", "\\footnotesize"]
    for p in parts: L.append(("\\fitbox{%\n" + p + "}") if (fit and p.startswith("\\begin{tabular}")) else p)
    L += [f"\\tabnote{{{note}}}", "\\end{table}"]
    p = os.path.join(V3, fn + ".tex"); s = grava_tex(p, "\n".join(L) + "\n", fn + ".tex")
    assert open(p, encoding="utf-8").read() == s; print("gravado e relido:", fn)
def tabrows(fname, k=0):
    s = open(os.path.join(T, fname), encoding="utf-8").read()
    b = re.findall(r"\\begin\{tabular\}.*?\\end\{tabular\}", s, flags=re.S)[k]
    body = b.split("\\midrule", 1)[1].split("\\bottomrule")[0]
    return [l.strip() for l in body.strip().splitlines() if l.strip() and not l.strip().startswith("\\midrule") and "&" in l]
def cells(row): return [c.strip().rstrip("\\").strip() for c in row.split("&")]
FROZ = []
def fz(item, val, src): FROZ.append(dict(item=item, valor=val, origem=src))
COH = ("2012", "2013", "2014", "2015", "2016")
J = pd.read_csv(os.path.join(C18, "janela2012_nums.csv")).set_index("item").valor
def jv(prefix): return [v for k, v in J.items() if k.startswith(prefix)][0]

# ================= 1. COMPLETUDE POR SEMESTRE DE SOLICITACAO (corpo, nova) =================
cs = pd.read_csv(os.path.join(C17, "c2_completude_semestre.csv"))
cs = cs[cs.semestre <= "2017S2"]
rC = [" & ".join([r.semestre, num(r.R_registradas_que_entraram, 0), num(r.M_ausentes_estimadas, 0), num(r.completude_solicitacao), num(r.enc_registrado), "yes" if r.completo else "no"]) + " \\\\" for r in cs.itertuples()]
for r in cs.itertuples(): fz(f"completude {r.semestre}: (a) / (b)", f"{r.completude_solicitacao} / {r.enc_registrado}", "c2_completude_semestre.csv (build17_c2.py)")
cc = pd.read_csv(os.path.join(C17, "c2_coorte_semestres.csv"))
rK = [" & ".join([str(r.coorte), num(r.solicitantes, 0), num(r.pct_sol_antes_2012S2), num(r.completude_ponderada)]) + " \\\\" for r in cc.itertuples()]
for r in cc.itertuples(): fz(f"coorte {r.coorte}: % solicitacoes antes de jul./2012; completude ponderada", f"{r.pct_sol_antes_2012S2} / {r.completude_ponderada}", "c2_coorte_semestres.csv")
ref = cs[cs.semestre.str[:4].astype(int).between(2014, 2016)]
thr_a = ref.completude_solicitacao.mean() - 2; thr_b = ref.enc_registrado.mean() - 2
fz("limiares da regra (a) / (b)", f"{thr_a:.1f} / {thr_b:.1f}", "c2_completude_semestre.csv (media 2014S1-2016S2 menos 2)")
emit("V3_completeness", "Completeness of the request record by request semester, children first enrolled in 2010--2018", "completeness",
     [panel("Panel A. By semester of first application"),
      tabular("lrrrrc", "Semester & \\shortstack[r]{Entrants with a\\\\prior request} & \\shortstack[r]{Entrants without one,\\\\assigned} & \\shortstack[r]{Completeness\\\\(\\%)} & \\shortstack[r]{Referral\\\\recorded (\\%)} & \\shortstack[c]{Meets\\\\the rule}", rC),
      panel("Panel B. By birth cohort"),
      tabular("lrrr", "Birth cohort & Applicants & Applications before July 2012 (\\%) & Completeness, weighted (\\%)", rK)],
     REC + "; " + EOL + ", entries 2010--2018. \\emph{Sample:} children whose first childcare enrollment falls in 2010--2018. \\emph{Variables:} entrants with a prior request, children whose first recorded request falls in the semester and precedes their first enrollment; entrants without one, children with no request recorded before their first enrollment, distributed over the semesters in which they would have applied using the distribution of the time from request to entry among entrants of 2014--2017 who have a request (separately for February and other months; medians 314 and 232 days); completeness, the first over the sum of both; referral recorded, among applicants of the semester who entered care after applying, the percent with a referral recorded in the request record within 60 days after entry. Panel B weights the semester completeness by the semester distribution of each cohort's first applications. \\emph{Exercise:} the rule, fixed before the computation, calls a semester complete if both completeness and referral recording are within 2 points of their 2014S1--2016S2 means (thresholds " + f"{thr_a:.1f} and {thr_b:.1f}" + " percent). Using the lag distribution of 2014 entrants only, or of 2016--2017 entrants only, completeness is 92.6 to 93.3 percent in 2012S1 and 97.9 to 98.1 percent in 2012S2. Descriptive; it assumes that children absent from the record had the same lag as those present.")
fz("sensibilidade 2012S1 / 2012S2", "92.6-93.3 / 97.9-98.1", "build17_fatais_c2.log")

# ================= 2. NIVEL OBSERVADO E CORRIGIDO (corpo, substitui V2_naive) =================
L = pd.read_csv(os.path.join(C18, "nivel_corrigido.csv")).set_index("coorte")
A = pd.read_csv(os.path.join(C18, "nivel_artefato.csv"))
eo = pd.read_csv(os.path.join(C15, "eol_coorte_den96.csv")).set_index("coorte").EOL_antes_24m
n4 = {int(cells(r)[0]): cells(r) for r in tabrows("N4_enrolled.tex")}
def rng(a, b, d=3):
    lo, hi = min(a, b), max(a, b)
    return f"{lo:.{d}f}" if round(lo, d) == round(hi, d) else f"{lo:.{d}f}--{hi:.{d}f}"
rL = []
for c in (2010, 2011, 2012, 2013, 2016):
    r = L.loc[c]
    rL.append(" & ".join([str(c), f"{num(r.M_ausentes, 0)} ({r.M_pct_N:.1f})",
                         f"{r.ref_obs:.3f}", f"[{r.ref_inf:.3f}, {r.ref_sup:.3f}]", rng(r.ref_R1, r.ref_R2),
                         f"{r.mat_obs:.3f}", f"[{r.mat_inf:.3f}, {r.mat_sup:.3f}]", rng(r.mat_R1, r.mat_R2),
                         f"{r.reg12_obs:.1f}", f"{r.reg12_sup:.1f}", rng(r.reg12_R1, r.reg12_R2, 1),
                         n4[c][3], num(eo[c])]) + " \\\\")
    fz(f"nivel coorte {c}: M (%N); ref obs [inf,sup] R1-R2; mat idem; reg12 obs sup R1-R2; <24m fila/EOL",
       f"{r.M_ausentes} ({r.M_pct_N}); {r.ref_obs} [{r.ref_inf},{r.ref_sup}] {r.ref_R1}-{r.ref_R2}; {r.mat_obs} [{r.mat_inf},{r.mat_sup}] {r.mat_R1}-{r.mat_R2}; {r.reg12_obs} {r.reg12_sup} {r.reg12_R1}-{r.reg12_R2}; {n4[c][3]}/{eo[c]}",
       "build18/nivel_corrigido.csv; N4_enrolled.tex; eol_coorte_den96.csv")
CL = (2010, 2011, 2012, 2013, 2016)   # Painel A transposto (coortes nas colunas), legivel sem reduzir a fonte
def lrow(lab, sub, f): return " & ".join([lab, sub] + [f(L.loc[c], c) for c in CL]) + " \\\\"
rLT = [lrow("Missing entrants", "N (\\% of applicants)", lambda r, c: f"{num(r.M_ausentes, 0)} ({r.M_pct_N:.1f})"), "\\midrule",
       lrow("One-year referral", "Observed", lambda r, c: f"{r.ref_obs:.3f}"), lrow("", "Bounds", lambda r, c: f"[{r.ref_inf:.3f}, {r.ref_sup:.3f}]"),
       lrow("", "Corrected", lambda r, c: rng(r.ref_R1, r.ref_R2)), "\\midrule",
       lrow("One-year enrollment", "Observed", lambda r, c: f"{r.mat_obs:.3f}"), lrow("", "Bounds", lambda r, c: f"[{r.mat_inf:.3f}, {r.mat_sup:.3f}]"),
       lrow("", "Corrected", lambda r, c: rng(r.mat_R1, r.mat_R2)), "\\midrule",
       lrow("Registered $<$12m (\\% births)", "Observed", lambda r, c: f"{r.reg12_obs:.1f}"), lrow("", "Maximum", lambda r, c: f"{r.reg12_sup:.1f}"),
       lrow("", "Corrected", lambda r, c: rng(r.reg12_R1, r.reg12_R2, 1)), "\\midrule",
       lrow("Enrolled $<$24m (\\% births)", "Request record", lambda r, c: n4[c][3]), lrow("", "Enrollment records", lambda r, c: num(eo[c]))]
def arow(c0, med):
    return A[(A.inicio == c0) & (A.medida == med)].iloc[0]
rows = []
for lab, med, d in (("One-year referral", "ref", 3), ("One-year enrollment", "mat", 3), ("Registered $<$12m (\\% births)", "reg12", 1)):
    a = arow(2010, med); lo, hi = [float(x) for x in a.ganho_lim_2016obs.strip("[]").split(",")]
    o = a.ganho_observado; art_lo, art_hi = o - hi, o - lo
    rows.append(" & ".join([lab, "2010--2016", f"{o:.{d}f}", rng(a.ganho_R1, a.ganho_R2, d), f"[{lo:.{d}f}, {hi:.{d}f}]",
                            f"{min(a.artefato_pct_R1, a.artefato_pct_R2):.0f}--{max(a.artefato_pct_R1, a.artefato_pct_R2):.0f}",
                            f"{100 * art_lo / o:.0f} to {100 * art_hi / o:.0f}".replace("-", "$-$")]) + " \\\\")
    fz(f"artefato 2010-2016 {med}: observado; corrigido R1-R2; limites; % R1-R2; % limites", f"{o}; {a.ganho_R1}-{a.ganho_R2}; {a.ganho_lim_2016obs}; {a.artefato_pct_R1}-{a.artefato_pct_R2}; {100 * art_lo / o:.0f} a {100 * art_hi / o:.0f}", "build18/nivel_artefato.csv")
o24 = float(n4[2016][3]) - float(n4[2010][3]); e24 = eo[2016] - eo[2010]
rows.append(" & ".join(["Enrolled $<$24m (\\% births)", "2010--2016", f"{o24:.1f}", f"{e24:.1f}", "--", f"{100 * (o24 - e24) / o24:.0f}", "--"]) + " \\\\")
fz("matriculados <24m 2010-2016: fila / EOL / % artefato", f"{o24:.1f} / {e24:.1f} / {100 * (o24 - e24) / o24:.1f}", "N4_enrolled.tex; eol_coorte_den96.csv")
rows.append("\\midrule")
for lab, med, d in (("One-year referral", "ref", 3), ("Registered $<$12m (\\% births)", "reg12", 1)):
    a = arow(2012, med); lo, hi = [float(x) for x in a.ganho_lim_2016obs.strip("[]").split(",")]
    rows.append(" & ".join([lab, "2012--2016", f"{a.ganho_observado:.{d}f}", rng(a.ganho_R1, a.ganho_R2, d), f"[{lo:.{d}f}, {hi:.{d}f}]", f"{min(a.artefato_pct_R1, a.artefato_pct_R2):.0f}".replace("-", "$-$"), "--"]) + " \\\\")
    fz(f"artefato 2012-2016 {med}", f"{a.ganho_observado}; {a.ganho_R1}-{a.ganho_R2}; {a.ganho_lim_2016obs}; {a.artefato_pct_R1}", "build18/nivel_artefato.csv")
o24w = float(n4[2016][3]) - float(n4[2012][3]); e24w = eo[2016] - eo[2012]
rows.append(" & ".join(["Enrolled $<$24m (\\% births)", "2012--2016", f"{o24w:.1f}", f"{e24w:.1f}", "--", f"{100 * (o24w - e24w) / o24w:.0f}".replace("-", "$-$"), "--"]) + " \\\\")
fz("matriculados <24m 2012-2016: fila / EOL", f"{o24w:.1f} / {e24w:.1f}", "N4_enrolled.tex; eol_coorte_den96.csv")
cal = pd.read_csv(os.path.join(C18, "nivel_calibracao.csv")); c13 = cal[cal.grupo.str.startswith("cobertos que entraram em 2013")].set_index("desfecho")
caltxt = (f"{c13.imputado_R1['solicitou antes de 12 meses']:.1f} against {c13.observado['solicitou antes de 12 meses']:.1f} percent registered before 12 months, "
          f"{c13.imputado_R1['encaminhado em 365 dias']:.1f} against {c13.observado['encaminhado em 365 dias']:.1f} referred within a year and "
          f"{c13.imputado_R1['matriculado em 365 dias']:.1f} against {c13.observado['matriculado em 365 dias']:.1f} enrolled within a year")
fz("calibracao fora da amostra (entrantes cobertos de 2013): <12m / ref / mat, imputado contra observado", caltxt, "build18/nivel_calibracao.csv")
emit("V3_level", "Observed and corrected levels for birth cohorts with incomplete coverage", "level",
     [panel("Panel A. Level of each statistic, by birth cohort"),
      tabular("llrrrrr", "Statistic & & 2010 & 2011 & 2012 & 2013 & 2016", rLT),
      panel("Panel B. Change over the cohorts and the part due to coverage"),
      tabular("llrrrrr", "Measure & Cohorts & Observed & Corrected & Bounds on the & \\multicolumn{2}{c}{Coverage share (\\%)} \\\\\n & & change & change & corrected change & estimate & bounds", rows)],
     REC + "; " + EOL + ", entries through December 2018; live births (SINASC). \\emph{Sample:} applicants with eligible time in each birth cohort (N), plus missing entrants: children of the cohort who entered childcare at 0--47 months with no request recorded before entry (those among them with a later request are removed from N and counted once, as missing). \\emph{Variables:} referral and enrollment within 365 days of the first application; registered before 12 months and enrolled before 24 months, as a percent of live births. Bounds: no missing entrant (lower) or every missing entrant (upper) had the outcome; Max., every missing entrant registered before 12 months. Corrected: each missing entrant receives the mean outcome of entrants with a request in the same cell of age at entry (months) and entry month (February or other), taken either from entrants of 2014--2017 or from entrants of the same year; the range spans the two. Out of sample, the first reference gives " + caltxt + " for entrants of 2013. In Panel B the bounds on the corrected change hold the 2016 cohort at its observed level; the coverage share is (observed $-$ corrected)/observed; for enrollment before 24 months the corrected change is the change in the enrollment records. \\emph{Exercise:} descriptive; the corrected levels assume that missing entrants resemble entrants with a request in the same cell.")

# ================= 3. SERVICO (corpo) =================
e1 = {cells(r)[0]: cells(r) for r in tabrows("E1_cohort.tex")}; p2 = {cells(r)[0]: cells(r) for r in tabrows("P2_endpoint.tex")}
rS = [" & ".join([c, e1[c][1], e1[c][2], e1[c][3], e1[c][4], e1[c][5], e1[c][6], e1[c][7], p2[c][3], p2[c][4]]) + " \\\\" for c in COH]
cif = pd.read_csv(os.path.join(C14, "janela_cif.csv")); ya = cif[cif.serie == "ano_solicitacao"].set_index("grupo"); ya.index = ya.index.astype(str)
e1y = {cells(r)[0]: cells(r) for r in tabrows("appx/A_E1year.tex")}
rY = [" & ".join([y, e1y[y][1], e1y[y][3], f"{ya.mat365[y]:.3f}", e1y[y][7]]) + " \\\\" for y in ("2013", "2014", "2015", "2016", "2017")]
rf = pd.read_csv(os.path.join(C15, "reforma_semestral.csv"))
s2 = [x.strip() for x in jv("solicitacoes 2012S2").split("/")]
rR = [" & ".join(["2012S2", s2[2], s2[0], s2[1]]) + " \\\\"] + [" & ".join([r.semestre, num(r.N, 0), f"{r.ref365:.3f}", f"{r.mat365:.3f}"]) + " \\\\" for r in rf.itertuples()]
for c in COH: fz(f"Tabela servico coorte {c}", " ".join(e1[c][1:]) + " | mat " + p2[c][3] + " RMST " + p2[c][4], "E1_cohort.tex; P2_endpoint.tex")
fz("encaminhamento 365d 2012S2", " / ".join(s2), "build18/janela2012_nums.csv")
for r in rf.itertuples(): fz(f"encaminhamento 365d por semestre {r.semestre}", f"{r.ref365:.3f} / mat {r.mat365:.3f} (N {r.N:,})", "reforma_semestral.csv")
emit("V3_service", "Referral and enrollment within one year in the window of complete coverage among requesters with eligible time, 2012--2016 cohorts (Panel A) and 2013--2017 requests (Panel B)", "service",
     [panel("Panel A. By birth cohort"),
      tabular("lrrrrrrrrr", "Birth cohort & N & ref$_{180}$ & ref$_{365}$ & ref$_{730}$ & age$_{365}$ & RMST$_{365}$ & Median & enr$_{365}$ & RMST enr.", rS),
      panel("Panel B. By calendar year of application"),
      tabular("lrrrr", "Year of application & N & ref$_{365}$ & enr$_{365}$ & Median", rY),
      panel("Panel C. By semester of application, before and after the July 2016 allocation ordinance"),
      tabular("lrrr", "Semester of application & N & ref$_{365}$ & enr$_{365}$", rR)],
     REC + ". \\emph{Sample:} applicants with eligible time (first application at or before 47 months); Panel A, birth cohorts 2012--2016; Panel B, first applications in the calendar years 2013--2017 (the window begins in July 2012, so 2013 is its first full year); Panel C, 2012S2--2018S1 (later applications lack 365 days of follow-up). \\emph{Variables:} time from first application in days; ref$_{t}$, cumulative incidence of referral by day $t$; age$_{365}$, cumulative incidence of aging out (reaching 47 months unreferred) by day 365; RMST, restricted mean days without the event within 365; Median, day on which referral incidence reaches 0.5; enr, the same with enrollment as the terminal event. Panel C: the ordinance of 14 July 2016 formalized automated matching (Section~\\ref{sec:institutions}); semesters from 2016S2 are after it. \\emph{Exercise:} Aalen--Johansen estimator with aging out as the competing event; descriptive.")

# ================= 4. ESPECIFICACOES (corpo) =================
rob = {cells(r)[0]: cells(r) for r in tabrows("P2_robust.tex")}
def gain(a, b): return f"{float(a):.3f} & {float(b):.3f} & {sg(float(b) - float(a))}"
bt = open(os.path.join(C18, "p3boot_2012_2016.log"), encoding="utf-8").read()
ci_std = re.search(r"Applicant std Delta=\+([\d.]+)\s+se=([\d.]+)\s+IC95=\[\+([\d.]+), \+([\d.]+)\]", bt).groups()
ci_raw = re.search(r"Raw\s+Delta=\+([\d.]+)\s+se=([\d.]+)\s+IC95=\[\+([\d.]+), \+([\d.]+)\]", bt).groups()
p3l = open(os.path.join(C18, "p3_2012_2016.log"), encoding="utf-8").read()
v2a = re.search(r"S2 solicitante:\s+CIF365 2012=([\d.]+) 2016=([\d.]+)", p3l).groups(); v3a = re.search(r"S3 solicitante\+oferta: CIF365 2012=([\d.]+) 2016=([\d.]+)", p3l).groups()
g2, g3 = re.search(r"grossa: S2=\+([\d.]+)\s+S3=\+([\d.]+)", p3l).groups(); f2, f3 = re.search(r"fina:\s+S2=\+([\d.]+)\s+S3=\+([\d.]+)", p3l).groups()
dec = re.search(r"solicitante ([+-][\d.]+), oferta ([+-][\d.]+), operacional ([+-][\d.]+)", p3l).groups()
s12 = [x.strip() for x in jv("coorte 2012, so solicitacoes").split("/")]
rows = [
 ["Base: referral, aging out competing", gain(rob["2012"][1], rob["2016"][1]), "--"],
 ["Recorded withdrawal as a further competing event", gain(rob["2012"][2], rob["2016"][2]), "--"],
 ["Children who applied after 47 months counted as aging out", gain(rob["2012"][5], rob["2016"][5]), "--"],
 ["Applications in the first calendar semester only", gain(rob["2012"][4], rob["2016"][4]), "--"],
 ["Applications dated July 2012--December 2013 excluded", gain(rob["2012"][3], rob["2016"][3]), "--"],
 ["2012 cohort restricted to applications from July 2012", gain(s12[0], rob["2016"][1]), "--"],
 ["Enrollment as the terminal event", gain(p2["2012"][3], p2["2016"][3]), "--"],
 ["Composition held at 2012 (main cells)", f"{float(v2a[0]):.3f} & {float(v2a[1]):.3f} & +{ci_std[0][:5]}", f"[+{float(ci_std[2]):.3f}, +{float(ci_std[3]):.3f}]"],
 ["Composition held at 2012, coarse / fine cells", f"-- & -- & +{g2} / +{f2}", "--"],
 ["Composition and service environment held fixed", f"{float(v3a[0]):.3f} & {float(v3a[1]):.3f} & {dec[2]}", f"coarse +{g3}, fine +{f3}"],
 ["Unweighted, bootstrap interval", gain(rob["2012"][1], rob["2016"][1]), f"[+{float(ci_raw[2]):.3f}, +{float(ci_raw[3]):.3f}]"],
 "MID",
 ["Window starting with the 2013 cohort", gain(rob["2013"][1], rob["2016"][1]), "--"],
 ["Window starting with the 2014 cohort", gain(rob["2014"][1], rob["2016"][1]), "--"],
]
for r in rows:
    if r != "MID": fz("especificacao 2012: " + r[0], r[1] + " | " + r[2], "P2_robust.tex; P2_endpoint.tex; build18/p3_2012_2016.log; build18/p3boot_2012_2016.log; build18/janela2012_nums.csv")
fz("decomposicao exata 2012-2016: composicao / oferta / residual", " / ".join(dec), "build18/p3_2012_2016.log")
emit("V3_specs", "Gain in one-year referral between the 2012 and 2016 cohorts under alternative specifications, including two that move the start of the window of complete coverage", "specs",
     [tabular("lrrrl", "Specification & 2012 & 2016 & $\\Delta$ & Interval or range", ["\\midrule" if r == "MID" else " & ".join(r) + " \\\\" for r in rows])],
     REC + ". \\emph{Sample:} applicants of birth cohorts 2012--2016 with eligible time, except where a row says otherwise; the last two rows move the start of the window and report the change from the 2013 or 2014 cohort. \\emph{Variables:} cumulative incidence of referral (or enrollment) within 365 days of the first application. \\emph{Exercise:} $\\Delta$ is computed from unrounded incidences. Aalen--Johansen estimator; reweighting to the 2012 cohort's joint distribution of applicant attributes (main cells: age at application, priority, postcode-income quartile, district, semester; coarse: age, priority, income; fine: eight age bins, priority, income, district, month), weights trimmed at the 1st and 99th percentiles; service environment adds the number of centers open within 2\\,km at the application date. Intervals: 1,000 bootstrap replications resampling children within the 2012 and 2016 cohorts, weights recomputed in each, percentile interval, seed 20260726; they reflect sampling variability only. In the exact decomposition of the raw change, composition contributes " + dec[0].replace("-", "$-$") + " and the service environment " + dec[1] + ", leaving " + dec[2] + ". Descriptive.")

# ================= 5. TIMING (corpo) =================
pt = {cells(r)[0]: cells(r) for r in tabrows("P5_timing.tex")}; n3 = {cells(r)[0]: cells(r) for r in tabrows("N3_district.tex")}
import csv
rr = list(csv.reader(open(os.path.join(ROOT, r"01_dados_publicos\ceinfo\sinasc_nv_distrito_2006_2026.csv"), encoding="utf-8"), delimiter=";"))
hdr = rr[0]; dd = [x for x in rr[1:] if x and x[0].strip() not in ("Ignorado", "Total")]; Bd = {int(h): sum(int(x[i]) for x in dd) for i, h in enumerate(hdr) if h.isdigit()}
spt = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"), columns=["ano_nasc", "idade_sol"])
rT = []
for c in COH:
    s = spt[spt.ano_nasc == int(c)]; b = Bd[int(c)]
    lt6, lt12, lt24 = (100 * (s.idade_sol < k).sum() / b for k in (6, 12, 24))
    rT.append(" & ".join([c, num(b, 0), num(lt6), num(lt12), num(lt24), pt[c][1], n3[c][3], n3[c][4]]) + " \\\\")
    fz(f"timing coorte {c}: <6/<12/<24 (% nascidos), <12|<24, pesos 2010, pesos 2016", f"{lt6:.1f} {lt12:.1f} {lt24:.1f} | {pt[c][1]} {n3[c][3]} {n3[c][4]}", "build18_tables.py (spine+SINASC); P5_timing.tex; N3_district.tex")
dj = [x.strip() for x in jv("distritos 2012-2016").split("/")]
fz("distritos 2012-2016: N / sobe / mediana / min / max", " / ".join(dj), "build18/janela2012_nums.csv")
emit("V3_timing", "Timing of registration in the window of complete coverage", "timing",
     [tabular("lrrrrrrr", "Birth cohort & Live births & $<$6m & $<$12m & $<$24m & $<$12m among $<$24m & 2010 district mix & 2016 district mix", rT)],
     REC + "; live births by district of residence (SINASC). \\emph{Sample:} birth cohorts 2012--2016, each observed from birth to 24 months. \\emph{Variables:} $<$6m, $<$12m, $<$24m: children with a first application before that age, \\% of live births; $<$12m among $<$24m: share registered before 12 months among children registered before 24 months; the last two columns average district-specific shares with the district weights of the 2010 or the 2016 cohort. Between the 2012 and 2016 cohorts the share registered before 12 months among those registered before 24 months rose in " +
     f"{dj[1]} of {dj[0]} districts (median within-district change {dj[2]}, range {dj[3]} to {dj[4]})".replace("-0", "$-$0") + ". \\emph{Exercise:} shares; descriptive.")

# ================= 6. COBERTURA POR COORTE (corpo, indicador) =================
rN = []
for c in COH:
    v = n4[int(c)]; rN.append(" & ".join([c, v[1], v[2], v[3], v[4] if v[4] else "--", num(eo[int(c)])]) + " \\\\")
    fz(f"matriculados por idade coorte {c}: <12/<24/<36 fila; <24 EOL", f"{v[2]} / {v[3]} / {v[4]} ; {eo[int(c)]}", "N4_enrolled.tex; eol_coorte_den96.csv")
emit("V3_cohortcov", "Share of each birth cohort enrolled by a given age, window of complete coverage", "cohortcov",
     [tabular("lrrrrr", "Birth cohort & Live births & Enrolled $<$12m & $<$24m & $<$36m & $<$24m (enrollment records)", rN)],
     REC + "; " + EOL + ", 2003--2019; live births (SINASC). \\emph{Sample:} birth cohorts 2012--2016. \\emph{Variables:} children with a first enrollment before the stated age, \\% of live births; the last column uses the enrollment records instead of the request record. Cohorts are shown only where the age window is fully observed. \\emph{Exercise:} shares; descriptive.")
F = pd.DataFrame(FROZ); p = os.path.join(C18, "congelados_v3.csv"); F.to_csv(p, index=False); assert len(pd.read_csv(p)) == len(F); print("congelados_v3:", len(F))
