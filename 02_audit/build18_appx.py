# -*- coding: utf-8 -*-
# 30/10/2026 (rodada legendas-instala-2026-10-30): os titulos e as notas das exibicoes (\caption e \tabnote) sao
# TEXTO DO AUTOR, de 30/10/2026, gravados nos .tex e tambem neste script. Nao regravar os .tex gerados por este script
# sem autorizacao do autor.
# Trava (trava_legenda.py, 30/10/2026): \caption e \tabnote que difiram do arquivo nao sao regravados, salvo com NE_SOBRESCREVER_LEGENDA=1.
# MANHA, etapa 1.2-1.3 (26/10/2026): tabela de apendice com o teste de prospectividade do registro (C3 do FATAIS).
# So le os CSVs de build17_c3.py. Nenhum numero digitado. Saida: 04_paper/assets/tables/appx/A_prospect.tex; acrescenta
# a linha ao appx_index.csv (com .bak) e os valores ao congelados_v3.csv.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, shutil, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
from trava_legenda import grava_tex  # trava das legendas (30/10/2026)
ROOT = NE_ROOT; C17 = os.path.join(ROOT, r"03_build\build17_fatais"); C18 = os.path.join(ROOT, r"03_build\build18")
AP = os.path.join(ROOT, r"04_paper\assets\tables\appx")
x = pd.read_csv(os.path.join(C17, "c3_sol_x_eol.csv")); x = x[x.ano_entrada >= 2012]
x["zero_sete"] = 100 - x["sol_depois_entrada_%"] - x["antecede_mais_7d_%"]
n = pd.read_csv(os.path.join(C17, "c3_nunca.csv")).set_index("ano_sol"); e = pd.read_csv(os.path.join(C17, "c3_escolas_recusas.csv")).set_index("ano_sol")
rA = [f"{int(r.ano_entrada)} & {int(r.entrantes):,} & {r.pct_no_registro:.1f} & {r.P50_dias:.0f} & {r['sol_depois_entrada_%']:.2f} & {r.zero_sete:.1f} & {r['antecede_mais_30d_%']:.1f} \\\\" for _, r in x.iterrows()]
rB = [f"{y} & {int(n.N[y]):,} & {n.nunca_mat_pct[y]:.1f} & {n.nunca_creche_EOL_pct[y]:.1f} & {e.criancas_com_recusa_pct[y]:.1f} & {e.criancas_enc_a_escola_onde_nunca_matriculou_pct[y]:.1f} & {e.enc_escola_diferente_da_pedida_pct[y]:.1f} \\\\" for y in range(2012, 2018)]
def tab(spec, h, rows): return "\n".join(["\\fitbox{%", "\\begin{tabular}{" + spec + "}", "\\toprule", h + " \\\\", "\\midrule"] + rows + ["\\bottomrule", "\\end{tabular}}"])
s = "\n".join(["% Gerado por 02_audit/build18_appx.py (26/10/2026). Nao editar a mao.", "\\begin{table}[htbp]\\centering",
    "\\caption{Is the request record prospective? Timing of requests relative to entry, and outcomes that a record created at enrollment would not contain}", "\\label{tab:prospect}", "\\footnotesize",
    "\\par\\medskip\\textbf{Panel A. Entrants by year of first childcare enrollment}\\par\\smallskip",
    tab("lrrrrrr", "Year of entry & Entrants & \\shortstack[r]{In record\\\\(\\%)} & \\shortstack[r]{Median days,\\\\request to entry} & \\shortstack[r]{Request after\\\\entry (\\%)} & \\shortstack[r]{Request 0--7 days\\\\before entry (\\%)} & \\shortstack[r]{Request $>$30 days\\\\before entry (\\%)}", rA),
    "\\par\\medskip\\textbf{Panel B. Applicants by year of first application}\\par\\smallskip",
    tab("lrrrrrr", "\\shortstack[r]{Year of\\\\application} & Applicants & \\shortstack[r]{Never\\\\enrolled (\\%)} & \\shortstack[r]{Never in care,\\\\EOL (\\%)} & \\shortstack[r]{Recorded\\\\refusal (\\%)} & \\shortstack[r]{Center never\\\\attended (\\%)} & \\shortstack[r]{Center not\\\\requested (\\%)}", rB),
    "\\tabnote{\\emph{Sources:} SME childcare request record (applications dated 2010--2018, with referral and enrollment dates through November 2019); SME enrollment records (EOL), first childcare enrollment per child. \\emph{Samples:} Panel A, children by year of first childcare enrollment, with the percentage columns after the second computed among those found in the record; Panel B, children by year of first application. Days to entry run from the first recorded request to the first enrollment. ``Request after entry'' means that the first request is dated after the first enrollment, and ``0--7 days'' that the request precedes entry by at most seven days, the same day included. ``Never enrolled'' indicates no enrollment in the request record by November 2019; ``never in care'' indicates no childcare enrollment in EOL. ``Recorded refusal'' indicates at least one recorded refusal, and ``center never attended'' at least one referral to a center where the child never enrolled. ``Center not requested'' is the percentage of referral rows whose center differs from the one requested. Before 2012, EOL dates almost every entry to the start of the school year, so Panel A starts in 2012. The shares are descriptive.}",
    "\\end{table}"]) + "\n"
p = os.path.join(AP, "A_prospect.tex"); s = grava_tex(p, s, "A_prospect.tex"); assert open(p, encoding="utf-8").read() == s; print("gravado e relido:", p)
print("\n".join(rA)); print("\n".join(rB))
ix = os.path.join(AP, "appx_index.csv"); L = open(ix, encoding="utf-8").read()
if "A_prospect.tex" not in L:
    shutil.copy(ix, ix + ".bak-2026-10-26-manha"); L2 = L.rstrip("\n") + "\nA_prospect.tex,prospect\n"; open(ix, "w", encoding="utf-8").write(L2)
    assert open(ix, encoding="utf-8").read() == L2; print("appx_index.csv: + A_prospect.tex (relido)")
cz = os.path.join(C18, "congelados_v3.csv"); F = pd.read_csv(cz); F = F[~F.item.str.startswith("prospectivo")]
add = [dict(item=f"prospectivo entrada {int(r.ano_entrada)}: entrantes / % registro / mediana / depois / 0-7 / >30", valor=f"{r.entrantes} / {r.pct_no_registro} / {r.P50_dias} / {r['sol_depois_entrada_%']} / {r.zero_sete:.1f} / {r['antecede_mais_30d_%']}", origem="c3_sol_x_eol.csv") for _, r in x.iterrows()]
add += [dict(item=f"prospectivo solicitacao {y}: N / nunca mat / nunca EOL / recusa / enc escola nunca / enc != pedida", valor=f"{int(n.N[y])} / {n.nunca_mat_pct[y]} / {n.nunca_creche_EOL_pct[y]} / {e.criancas_com_recusa_pct[y]} / {e.criancas_enc_a_escola_onde_nunca_matriculou_pct[y]} / {e.enc_escola_diferente_da_pedida_pct[y]}", origem="c3_nunca.csv; c3_escolas_recusas.csv") for y in range(2012, 2018)]
F = pd.concat([F, pd.DataFrame(add)]); F.to_csv(cz, index=False); assert len(pd.read_csv(cz)) == len(F); print("congelados_v3:", len(F))
