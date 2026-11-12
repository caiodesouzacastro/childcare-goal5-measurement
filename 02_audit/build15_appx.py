# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# 30/10/2026 (rodada legendas-instala-2026-10-30): os titulos e as notas das exibicoes (\caption e \tabnote) sao
# TEXTO DO AUTOR, de 30/10/2026, gravado nos .tex. Nao regravar os .tex gerados por este script sem autorizacao do autor.
# Neste script so os titulos foram atualizados; as notas, montadas por concatenacao de constantes e trechos, continuam
# com o texto anterior. A trava (trava_legenda.py, 30/10/2026) impede que uma nova execucao grave essas notas antigas
# por cima das do autor: \caption e \tabnote que difiram do arquivo nao sao regravados, salvo com NE_SOBRESCREVER_LEGENDA=1.
# FASE 2 (25/10/2026): tabelas de APENDICE novas ou substituidas sob a tese da cobertura. So de saidas de script.
# A_calendar.tex (2013-2017, substitui a de 2011-2017), A_C4v2.tex (substitui A_C4), A_T4dv2.tex (substitui A_T4d),
# A_decompyear.tex (nova), A_covtype.tex (nova). Saida em 04_paper/assets/tables/appx/.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, numpy as np, pandas as pd, pyreadstat; sys.stdout.reconfigure(encoding="utf-8")
from trava_legenda import grava_tex  # trava das legendas (30/10/2026)
ROOT = NE_ROOT; AP = os.path.join(os.environ.get("PAPER_ROOT", os.path.join(ROOT, "04_paper")), "assets", "tables", "appx"); C14 = os.path.join(ROOT, r"03_build\build14_cobertura"); C15 = os.path.join(ROOT, r"03_build\build15")
REC = "\\emph{Source:} SME childcare request record (2010--2018 applications, referral and enrollment dates through November 2019)"
def emit(fn, cap, labels, tab, note):
    L = ["% Apendice A. Gerado por 02_audit/build15_appx.py (25/10/2026). Nao editar a mao.", "\\begin{table}[htbp]\\centering", f"\\caption{{{cap}}}"] + [f"\\label{{tab:{l}}}" for l in labels] + ["\\footnotesize", "\\fitbox{%\n" + tab + "}", f"\\tabnote{{{note}}}", "\\end{table}"]
    grava_tex(os.path.join(AP, fn), "\n".join(L) + "\n", fn); print("ok", fn)
def tab(spec, header, rows): return "\n".join(["\\begin{tabular}{" + spec + "}", "\\toprule", header + " \\\\", "\\midrule"] + rows + ["\\bottomrule", "\\end{tabular}"])
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"))
# --- calendario 2013-2017 ---
MES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
sh = {}; nn = {}
for v in ("d_sol1", "d_enc1", "d_mat1"):
    d = pd.to_datetime(sp[v]).dropna(); d = d[(d.dt.year >= 2013) & (d.dt.year <= 2017)]
    sh[v] = d.dt.month.value_counts(normalize=True).sort_index(); nn[v] = len(d)
rows = [f"{MES[m - 1]} & {100 * sh['d_sol1'][m]:.1f} & {100 * sh['d_enc1'][m]:.1f} & {100 * sh['d_mat1'][m]:.1f} \\\\" for m in range(1, 13)]
rows += ["\\midrule", f"N (events) & {nn['d_sol1']:,} & {nn['d_enc1']:,} & {nn['d_mat1']:,} \\\\"]
emit("A_calendar.tex", "First requests, first referrals, and first enrollments by calendar month, 2013--2017 (column \\%)", ["calendar"],
     tab("lrrr", "Month & First applications & First referrals & First enrollments", rows),
     REC + ". \\emph{Sample:} one first application, first referral and first enrollment per child, counted when the event falls in calendar years 2013--2017. \\emph{Variables:} percent of each event type falling in each calendar month; columns sum to 100. \\emph{Exercise:} shares; descriptive.")
# --- C4 na janela (logica do build10.py) ---
cm = pd.read_feather(os.path.join(ROOT, r"03_build\build01\_staging\child_master.feather"), columns=["cd_aluno_sme", "idade_sol", "ano_nasc", "mes_nasc", "d_sol", "ano_sol", "nunca", "prio", "renda"])
cm["cd_aluno_sme"] = cm.cd_aluno_sme.astype(str); s2 = sp[["cd_aluno_sme", "d_enc1", "d_mat1", "d_rec1", "n_enc_after_rec"]].copy(); s2["cd_aluno_sme"] = s2.cd_aluno_sme.astype(str)
q = cm.merge(s2, on="cd_aluno_sme", how="left"); q["d_sol"] = pd.to_datetime(q.d_sol); q = q[q.d_sol >= "2013-01-01"].copy()
q["esp"] = (q.d_enc1 - q.d_sol).dt.days; q["ref"] = q.d_enc1.notna() & (q.esp >= 0)
q["ie"] = (q.d_mat1.dt.year - q.ano_nasc) * 12 + (q.d_mat1.dt.month - q.mes_nasc); q["ma"] = q.d_mat1.notna() & q.ref & (q.d_mat1 >= q.d_enc1)
rows = []
for al, alo, ahi in (("0--5m", 0, 5), ("6--11m", 6, 11), ("12--23m", 12, 23), ("24m+", 24, 999)):
    for slab, slo, shi in (("0--30d", 0, 30), ("31--90d", 31, 90), ("91--180d", 91, 180), (">180d", 181, 10 ** 9)):
        s = q[q.ref & q.idade_sol.between(alo, ahi) & q.esp.between(slo, shi)]; rr = s[s.d_rec1.notna()]
        med = np.nanmedian(s.loc[s.ma, "ie"]) if s.ma.any() else np.nan
        rows.append(f"{al} & {slab} & {len(s):,} & {100 * s.ma.mean():.1f} & {med:.0f} & {100 * (rr.n_enc_after_rec > 0).mean():.1f} \\\\")
emit("A_C4v2.tex", "Enrollment and repeat referral among referred children by age at request and days to first referral, first requests 2013--2018", ["C4"],
     tab("llrrrr", "Age at application & Referral speed & N & Enrollment rate \\% & Median age at enr. & Re-ref.\\ \\%", rows),
     REC + ". \\emph{Sample:} referred children whose first application is dated 2013 or later. \\emph{Variables:} speed, days from application to first referral; enrollment rate, percent enrolled at or after the first referral; median age at enrollment, months; re-referral, among children who recorded a formal refusal, percent referred again. \\emph{Exercise:} cell shares; descriptive.")
# --- T4d na janela ---
cc = cm[cm.ano_sol.between(2013, 2017)]
nv, en = cc[cc.nunca == 1], cc[cc.nunca == 0]
rows = [f"N & {len(nv):,} & {len(en):,} \\\\", f"Age at application (months) & {nv.idade_sol.mean():.1f} & {en.idade_sol.mean():.1f} \\\\",
        f"With legal priority (\\%) & {100 * nv.prio.mean():.1f} & {100 * en.prio.mean():.1f} \\\\", f"Postcode income (R\\$) & {nv.renda.mean():,.0f} & {en.renda.mean():,.0f} \\\\"]
emit("A_T4dv2.tex", "Children who never enrolled compared with children who enrolled, first requests 2013--2017 (881,957 children)", ["T4d_never"],
     tab("lrr", "Variable & Never enrolled & Enrolled", rows),
     REC + ". \\emph{Sample:} first applications dated 2013--2017 (" + f"{len(cc):,}" + " children). \\emph{Variables:} never enrolled, no enrollment in a municipal center before the end of the panel; postcode income, mean household income of the census tract (2010 Census). \\emph{Exercise:} means; descriptive. The groups differ by construction in age at application and priority, so the differences are not interpreted.")
# --- decomposicao por ano de solicitacao ---
D = pd.read_csv(os.path.join(C14, "janela_decomp.csv"))
rows = [f"{r.janela.replace('-', '--')} & {r.d_entrada:+.2f} & {r.d_solicitacao:+.2f} & {r.d_espera:+.2f} & {r.share_solic.replace('%', '')}\\% \\\\".replace("+-", "$-$").replace("-", "$-$", 0) for r in D.itertuples()]
rows = [x.replace(" & -", " & $-$") for x in rows]
emit("A_decompyear.tex", "Change in mean age at entry among enrolled children, by year of first application", ["decompyear"],
     tab("lrrrr", "Years of application & $\\Delta$ entry age & $\\Delta$ application age & $\\Delta$ wait & Application share", rows),
     REC + ". \\emph{Sample:} children who ever enrolled in a municipal center, by calendar year of first application. \\emph{Variables:} months; entry age is age at the first enrollment, application age at the first application, wait the difference. \\emph{Exercise:} accounting identity in means (entry age $=$ application age $+$ wait); descriptive. Rows starting in 2010 use applications made when the record covered under three fifths of entrants (Section~\\ref{sec:coverage}); rows ending in 2018 have shorter follow-up.")
# --- cobertura de fevereiro por tipo de centro ---
t = pd.read_csv(os.path.join(C14, "cob_fev_tipo.csv"), header=[0, 1], index_col=0)
rows = []
for tipo in t.index:
    m = [t[("mean", str(y))].get(tipo) for y in (2011, 2012, 2013, 2014)]; n = [t[("size", str(y))].get(tipo) for y in (2011, 2012, 2013, 2014)]
    rows.append(f"{tipo.strip()} & " + " & ".join("--" if pd.isna(x) else f"{100 * x:.1f}" for x in m) + " & " + " & ".join("--" if pd.isna(x) else f"{int(x):,}" for x in n) + " \\\\")
emit("A_covtype.tex", "Percentage of children first enrolled in February who have a request in the request record, by year and center type, for types with at least 200 February entrants in 2012", ["covtype"],
     tab("lrrrrrrrr", "Type of center & 2011 & 2012 & 2013 & 2014 & N 2011 & N 2012 & N 2013 & N 2014", rows),
     REC + "; SME enrollment records (EOL). \\emph{Sample:} children whose first childcare enrollment is dated February of the year; types with at least 200 February entrants in 2012. \\emph{Variables:} percent of entrants with a first request in the request record; type of center as recorded in the enrollment records (CEI DIRET, direct; CEI INDIR, indirect; CR.P.CONV, partner; CEU, unified education centers; EMEI, pre-school units with childcare classes). \\emph{Exercise:} shares; descriptive.")
