# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD02 - formata R1-R4 em .tex (booktabs) + .csv, figura R4b, e facts.md (R5).
# Descritivo: sem efeito/impacto/causa/leva a/resulta em.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":11,"figure.dpi":120,"axes.grid":True,"grid.alpha":.3})
STG=(NE_ROOT + r"\03_build\build02\_staging")
TAB=(NE_ROOT + r"\03_build\build02\tables"); os.makedirs(TAB,exist_ok=True)
FIG=(NE_ROOT + r"\03_build\build02\figures"); os.makedirs(FIG,exist_ok=True)

def esc(s):
    s=str(s)
    for a,b in [("&","\\&"),("%","\\%"),("_","\\_"),("<=","$\\leq$"),(">=","$\\geq$"),("<","$<$"),(">","$>$")]:
        s=s.replace(a,b)
    return s
def nf(x,d=1):
    try: x=float(x)
    except: return esc(x)
    if pd.isna(x): return "n/d"
    return f"{x:,.0f}" if d==0 else f"{x:,.{d}f}"
def emit(name,caption,note,colspec,header,body):
    L=["% requer \\usepackage{booktabs}. Tabela descritiva.","\\begin{table}[htbp]\\centering",
       f"\\caption{{{caption}}}",f"\\label{{tab:{name}}}","\\small",f"\\begin{{tabular}}{{{colspec}}}","\\toprule",
       " & ".join(header)+" \\\\","\\midrule"]
    for r in body:
        L.append("\\midrule" if r=="MID" else " & ".join(r)+" \\\\")
    L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
    open(os.path.join(TAB,name+".tex"),"w",encoding="utf-8").write("\n".join(L)+"\n")
    print("tex:",name)
def cp(src,dst=None):
    df=pd.read_csv(os.path.join(STG,src)); df.to_csv(os.path.join(TAB,dst or src),index=False); return df
FACTS=[]

# ---- R1b ----
d=cp("R1b_followup.csv")
emit("R1b_followup","Cobertura de acompanhamento dentro do painel, por ano de solicitacao",
 "Painel encerra em 2019-11-28 (ultima data de encaminhamento observada). Cobertura = fracao de "
 "solicitacoes cujo ano de solicitacao esta a pelo menos 180/365/730 dias do fim do painel. O ultimo "
 "ano com acompanhamento de 730 dias completo e 2016.",
 "lrrrr",["Ano solic.","N","\\% $\\geq$180d","\\% $\\geq$365d","\\% $\\geq$730d"],
 [[str(int(r.ano_sol)),nf(r.N,0),nf(r.pct_fu180),nf(r.pct_fu365),nf(r.pct_fu730)] for r in d.itertuples()])

# ---- R2a ----
d=cp("R2a_janela180.csv")
emit("R2a_janela180","Encaminhamento em janela fixa de 180 dias, por ano de solicitacao",
 "Janela fixa comparavel entre coortes: espera\\_180 = min(espera ate encaminhamento, 180); nao "
 "encaminhado em 180d entra como 180. Remove a variacao de truncamento entre coortes.",
 "lrrr",["Ano solic.","N","\\% enc.\\ em 180d","Espera\\_180 media (dias)"],
 [[str(int(r.ano_sol)),nf(r.N,0),nf(r.pct_enc180),nf(r.espera_180_media)] for r in d.itertuples()])
FACTS.append(f"**R2a** [build02_build.py]: com janela fixa de 180 dias, a fracao encaminhada em 180d varia de {d.iloc[0].pct_enc180:.0f}\\% (2010) a {d.iloc[-1].pct_enc180:.0f}\\% (2018); a espera\\_180 media fica entre {d.espera_180_media.min():.0f} e {d.espera_180_media.max():.0f} dias.")

# ---- R2b ----
d=cp("R2b_km.csv")
emit("R2b_km","Kaplan--Meier median time to referral, treating aging out of eligibility as censoring. Reported as a diagnostic only: censoring a competing event estimates a hypothetical net distribution, not the queue's realized experience. The paper's duration results use the competing-risks estimates of Section~\\ref{sec:incidence} (cumulative incidence and restricted mean time).",
 "Estimator diagnostic, not the main analysis: this Kaplan--Meier censors aging out of eligibility rather than treating it as a competing event, and therefore estimates a hypothetical net distribution. The main duration results use cumulative incidence and restricted mean time. The survivor function S(t) is the fraction not yet referred at t days. Children never referred are treated as censored at the end of the panel, not as absent. Censoring increases for the 2017 and 2018 cohorts. Cells are left blank where the panel does not provide the full follow-up horizon.",
 "lrrrrr",["Year of application","S(90)","S(180)","S(365)","S(730)","Median KM (days)"],
 [[str(int(r.ano_sol)),nf(r.S90,3),nf(r.S180,3),nf(r.S365,3),("" if int(r.ano_sol)>=2017 else nf(r.S730,3)),nf(r.mediana_KM_dias,0)] for r in d.itertuples()])
FACTS.append(f"**R2b** [build02_build.py]: mediana KM do tempo ate encaminhamento cai de {d.iloc[0].mediana_KM_dias:.0f} dias (2010) para {d[d.ano_sol==2017].mediana_KM_dias.values[0]:.0f} (2017); $S(180)$ passa de {d.iloc[0].S180:.2f} a {d[d.ano_sol==2017].S180.values[0]:.2f}. A coorte 2018 (mediana 96) esta parcialmente truncada.")

# ---- R2c ----
d=cp("R2c_decomp730.csv")
emit("R2c_decomp730","Decomposicao da idade de entrada (medias) --- SO coortes com 730 dias completos (2010--2016)",
 "Identidade: idade de entrada = idade na solicitacao + espera/30,44. Meses, exceto N. Coluna check = "
 "(2)+(3)$-$(4). Restricao a coortes com acompanhamento completo de 730 dias remove o truncamento a "
 "direita. Criancas matriculadas.",
 "lrrrrr",["Ano solic.","N","Idade solic.","Espera","Idade entrada","check"],
 [[str(int(r.ano_sol)),nf(r.N,0),nf(r.idade_sol,2),nf(r.espera,2),nf(r.idade_ent,2),nf(r.check,3)] for r in d.itertuples()])
d_ent=d.iloc[-1].idade_ent-d.iloc[0].idade_ent; d_sol=d.iloc[-1].idade_sol-d.iloc[0].idade_sol; d_esp=d.iloc[-1].espera-d.iloc[0].espera
FACTS.append(f"**R2c** [build02_build.py]: em 2010--2016 (acompanhamento completo), a idade media de entrada cai {d_ent:.2f} meses; idade na solicitacao {d_sol:.2f}; espera {d_esp:.2f}. A queda da espera quase desaparece quando se removem as coortes truncadas.")

# ---- R3a ----
d=cp("R3a_coorte.csv")
emit("R3a_coorte","Idade na primeira solicitacao por coorte de nascimento (2008--2016)",
 "Coorte de nascimento = ano\\_nasc. Todas as solicitacoes (matriculadas ou nao). Meses.",
 "lrrr",["Coorte nasc.","N","Idade media (meses)","Idade mediana"],
 [[str(int(r.coorte_nasc)),nf(r.N,0),nf(r.idade_sol_media,1),nf(r.idade_sol_mediana,0)] for r in d.itertuples()])
FACTS.append(f"**R3a** [build02_build.py]: a idade media na 1a solicitacao cai de {d.iloc[0].idade_sol_media:.1f} meses na coorte 2008 para {d.iloc[-1].idade_sol_media:.1f} na coorte 2016 --- tendencia por coorte de nascimento (transicao estoque$\\to$fluxo).")

# ---- R3b ----
d=cp("R3b_precoce.csv")
emit("R3b_precoce","Fracao de cada coorte de nascimento inscrita antes de 6, 12 e 24 meses",
 "Percentual de criancas da coorte com primeira solicitacao antes da idade indicada.",
 "lrrrr",["Coorte nasc.","N","\\% $<$6m","\\% $<$12m","\\% $<$24m"],
 [[str(int(r.coorte_nasc)),nf(r.N,0),nf(r.pct_ate6m),nf(r.pct_ate12m),nf(r.pct_ate24m)] for r in d.itertuples()])
FACTS.append(f"**R3b** [build02_build.py]: a fracao inscrita antes dos 12 meses sobe de {d.iloc[0].pct_ate12m:.1f}\\% (coorte 2008) para {d.iloc[-1].pct_ate12m:.1f}\\% (2016); antes dos 24 meses, de {d.iloc[0].pct_ate24m:.1f}\\% a {d.iloc[-1].pct_ate24m:.1f}\\%.")

# ---- R3c ----
d=cp("R3c_shiftshare.csv"); r=d.iloc[0]
emit("R3c_shiftshare","Decomposicao encadeada (ano a ano) da variacao da idade media na solicitacao, 2010--2018",
 "Identidade exata ano a ano: $\\Delta$media $= \\sum_c (s_1-s_0)\\frac{\\mu_0+\\mu_1}{2}$ (componente de "
 "composicao por coorte) $+ \\sum_c \\frac{s_0+s_1}{2}(\\mu_1-\\mu_0)$ (componente dentro de coorte), somada "
 "sobre pares de anos consecutivos. Os dois componentes sao grandes e de sinais opostos: a entrada anual de "
 "coortes de nascimento mais jovens puxa a media para baixo (composicao) enquanto o envelhecimento do estoque "
 "nao inscrito de cada coorte a puxa para cima (dentro de coorte); a variacao liquida e o pequeno residuo. "
 "Meses.",
 "lrr",["Componente","Meses","\\% da variacao total"],
 [["Variacao total",nf(r.total_change,2),"100"],"MID",
  ["Composicao por coorte",nf(r.composicao_coorte,2),nf(100*r.frac_composicao,0)],
  ["Dentro de coorte",nf(r.within_coorte,2),nf(100*r.frac_within,0)]])
FACTS.append(f"**R3c** [build02_build.py]: a variacao liquida da idade media na solicitacao (2010--2018, {r.total_change:.1f} meses) e o residuo de dois componentes grandes e opostos --- composicao por coorte {r.composicao_coorte:.1f} (entrada de coortes jovens) e dentro de coorte {r.within_coorte:+.1f} (envelhecimento do estoque nao inscrito). A queda e um fenomeno de composicao/maturacao do painel, nao uma mudanca limpa dentro de coorte.")

# ---- R3d ----
d=cp("R3d_backlog.csv")
emit("R3d_backlog","Fracao das solicitacoes feitas por criancas com mais de 24 e 36 meses (proxy de backlog)",
 "Percentual das solicitacoes do ano feitas por criancas acima de 24 (e 36) meses --- proxy do estoque "
 "de demanda represada.",
 "lrr",["Ano solic.","\\% $>$24m","\\% $>$36m"],
 [[str(int(r.ano_sol)),nf(r.pct_maior24m),nf(r.pct_maior36m)] for r in d.itertuples()])
FACTS.append(f"**R3d** [build02_build.py]: a fracao de solicitacoes por criancas com mais de 24 meses cai de {d.iloc[0].pct_maior24m:.0f}\\% (2010) para {d.iloc[-1].pct_maior24m:.0f}\\% (2018) --- o estoque de demanda represada e absorvido ao longo do painel.")

# ---- R4a ----
d=cp("R4a_final.csv"); r=d.iloc[0]
emit("R4a_final","Decomposicao corrigida da idade de entrada (2010--2016, acompanhamento completo)",
 "Versao final de T3: restrita a coortes com 730 dias de acompanhamento (remove truncamento). A queda da "
 "idade de entrada reparte-se em idade na solicitacao e espera; a parcela da idade na solicitacao e ainda "
 "subdividida (decomposicao encadeada) em composicao por coorte e dentro de coorte. Meses.",
 "lrr",["Componente da queda da idade de entrada","Meses","\\% do total"],
 [["Idade de entrada (total)",nf(r.d_idade_entrada,2),"100"],"MID",
  ["Idade na solicitacao",nf(r.d_idade_sol,2),nf(100*r.frac_sol_total,0)],
  ["\\quad --- composicao por coorte",nf(r.sol_composicao,2),nf(100*r.frac_sol_comp,0)],
  ["\\quad --- dentro de coorte",nf(r.sol_within,2),nf(100*r.frac_sol_within,0)],
  ["Espera",nf(r.d_espera,2),nf(100*r.frac_espera,0)]])

# ---- R4b figura ----
d=pd.read_csv(os.path.join(STG,"R2c_decomp730.csv"))
fig,ax=plt.subplots(figsize=(7,4.3))
ax.plot(d.ano_sol,d.idade_ent,"-o",label="Idade media de entrada",color="#1f3b73")
ax.plot(d.ano_sol,d.idade_sol,"-s",label="Idade media na solicitacao",color="#c0392b")
ax.plot(d.ano_sol,d.espera,"-^",label="Espera media",color="#27ae60")
ax.set_xlabel("Ano da solicitacao"); ax.set_ylabel("Meses")
ax.set_title("Decomposicao corrigida (coortes 2010--2016, acompanhamento completo)")
ax.legend(); ax.set_xticks(range(2010,2017)); fig.tight_layout()
fig.savefig(os.path.join(FIG,"F1_corrigida.pdf")); plt.close(fig)
d.to_csv(os.path.join(FIG,"F1_corrigida_data.csv"),index=False)
print("figura R4b: F1_corrigida.pdf")

# ---- facts.md com R5 ----
b01_dent=-19.09; b01_sol=0.80; b01_esp=0.20
c_dent=r.d_idade_entrada; c_sol=r.frac_sol_total; c_esp=r.frac_espera
with open((NE_ROOT + r"\03_build\build02\facts.md"),"w",encoding="utf-8") as f:
    f.write("# BUILD02 -- facts.md (robustez de T3)\n\n")
    f.write("Descritivo (associacao/diferenca/variacao/composicao). Reaproveita B\\_novo e "
            "child\\_master (BUILD01) + primeira data de encaminhamento de Fila1018. Nada modificado "
            "em Dropbox\\\\ (fora de \\_audit\\\\) ou <D>\\\\.\n\n")
    f.write("## R1a -- fim do painel\n\n")
    f.write("- Ultima data observada: dt\\_solicitacao **2018-12-17**; dt\\_encaminhamento **2019-11-28**; "
            "dt\\_matricula **2019-11-27**. Solicitacoes so vao ate dez/2018; encaminhamentos/matriculas "
            "seguem ate nov/2019. Ultimo ano com acompanhamento de 730 dias completo: **2016**.\n\n")
    f.write("## Numeros por tabela\n\n")
    for s in FACTS: f.write("- "+s+"\n\n")
    f.write("## R5 -- BUILD01 vs corrigido (lado a lado)\n\n")
    f.write("| Quantidade | BUILD01 (2010--2018) | Corrigido (2010--2016, 730d) |\n|---|---|---|\n")
    f.write(f"| Queda total da idade de entrada | {b01_dent:.2f} meses | {c_dent:.2f} meses |\n")
    f.write(f"| Fracao vinda da solicitacao | {100*b01_sol:.0f}\\% | {100*c_sol:.0f}\\% |\n")
    f.write(f"| Fracao vinda da espera | {100*b01_esp:.0f}\\% | {100*c_esp:.0f}\\% |\n\n")
    f.write("**A conclusao qualitativa se mantem e se fortalece.** A queda da idade de entrada continua "
            "dominada pela solicitacao mais precoce, nao pela menor espera. A parcela de ~20\\% atribuida a "
            "espera no BUILD01 era, em grande parte, **artefato de truncamento a direita**: a forte queda da "
            "espera concentrava-se nas coortes 2017--2018, ainda sem acompanhamento completo (Tabela R2c). "
            "Restrito a coortes completas (2010--2016), a espera responde por ~1\\% e a solicitacao por ~99\\%.\n\n")
    f.write("**Ressalva de interpretacao (R3).** A propria queda da idade na solicitacao e majoritariamente "
            "**composicional**: reflete a transicao de um estoque (demanda represada de criancas mais velhas: "
            "62\\% das solicitacoes de 2010 eram de $>$24 meses) para um fluxo (recem-nascidos: 25\\% em 2018), "
            "com as coortes de nascimento sucessivas se inscrevendo cada vez mais cedo (idade media por coorte "
            "39,3 $\\to$ 9,4 meses de 2008 a 2016). Nao e uma mudanca de comportamento medida limpa dentro de "
            "uma mesma coorte --- coortes de 2010 e 2018 quase nao se sobrepoem.\n\n")
    f.write("## O que nao saiu\n\n- Coortes de nascimento 2017+ nao entram (sem tempo de painel suficiente).\n"
            "- $S(730)$ das coortes 2017--2018 (R2b) e pouco informativo por censura.\n")
print("facts.md + tabelas OK")
