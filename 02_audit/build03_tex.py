# -*- coding: utf-8 -*-
# BUILD03 - formata S1-S6 em .tex (booktabs) + .csv, figuras F6/F7, facts.md (S5).
# Descritivo: sem efeito/impacto/causa/leva a/resulta em.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":11,"figure.dpi":120,"axes.grid":True,"grid.alpha":.3})
STG=(NE_ROOT + r"\03_build\build03\_staging")
TAB=(NE_ROOT + r"\03_build\build03\tables"); os.makedirs(TAB,exist_ok=True)
FIG=(NE_ROOT + r"\03_build\build03\figures"); os.makedirs(FIG,exist_ok=True)
def esc(s):
    s=str(s)
    for a,b in [("&","\\&"),("%","\\%"),("_","\\_"),("<=","$\\leq$"),(">=","$\\geq$")]: s=s.replace(a,b)
    return s
def nf(x,d=1):
    try: x=float(x)
    except: return esc(x)
    if pd.isna(x): return "n/d"
    return f"{x:,.0f}" if d==0 else f"{x:,.{d}f}"
def emit(name,cap,note,cols,header,body):
    L=["% requer \\usepackage{booktabs}. Tabela descritiva.","\\begin{table}[htbp]\\centering",
       f"\\caption{{{cap}}}",f"\\label{{tab:{name}}}","\\small",f"\\begin{{tabular}}{{{cols}}}","\\toprule",
       " & ".join(header)+" \\\\","\\midrule"]
    for r in body: L.append("\\midrule" if r=="MID" else " & ".join(r)+" \\\\")
    L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
    open(os.path.join(TAB,name+".tex"),"w",encoding="utf-8").write("\n".join(L)+"\n")
    print("tex:",name)
def cp(s,d=None): df=pd.read_csv(os.path.join(STG,s)); df.to_csv(os.path.join(TAB,d or s),index=False); return df
FACTS=[]

# S1a
d=cp("S1a_janelas.csv")
emit("S1a_janelas","Janela de observabilidade de uma solicitacao, por coorte de nascimento (painel jan/2010--dez/2018)",
 "Para cada coorte de nascimento, idade minima e maxima (meses) em que uma solicitacao seria plenamente "
 "observavel para toda a coorte, dado o painel: idade minima $=\\max(0,(2010-c)\\times 12)$; idade maxima "
 "$=(2018-c)\\times 12$. Coortes anteriores a 2010 sao truncadas a esquerda; de 2017 em diante, a direita. "
 "",
 "lrrrr",["Coorte nasc.","Idade min.\\ obs.","Idade max.\\ obs.","Plena 0--24","Plena 0--36"],
 [[str(int(r.coorte_nasc)),nf(r.idade_min_obs_meses,0),nf(r.idade_max_obs_meses,0),
   ("sim" if r.plena_0_24 else "nao"),("sim" if r.plena_0_36 else "nao")] for r in d.itertuples()])
FACTS.append("**S1** [build03_cohort.py]: coortes plenamente observaveis do nascimento aos 24 meses = 2010--2016 (7 coortes); ate 36 meses = 2010--2015 (6 coortes). Coortes 2008--2009 sao truncadas a esquerda; 2017--2018 a direita.")

# S2a CENTRAL
d=cp("S2a_frac_0_24.csv")
emit("S2a_frac_0_24","Fracao da coorte de nascimento que fez a primeira solicitacao antes de 6, 12, 18 e 24 meses",
 "Coortes plenamente observaveis de 0 a 24 meses (2010--2016). Denominador = nascidos vivos do municipio "
 "no ano (SINASC/CEInfo); numerador = criancas nascidas no ano com primeira solicitacao antes da idade "
 "indicada (plenamente observavel para estas coortes). Percentuais.",
 "lrrrrrr",["Coorte","Nascidos","Solicitantes","\\% $<$6m","\\% $<$12m","\\% $<$18m","\\% $<$24m"],
 [[str(int(r.coorte_nasc)),nf(r.nascidos,0),nf(r.solicitantes,0),nf(r.frac_ate6m),nf(r.frac_ate12m),nf(r.frac_ate18m),nf(r.frac_ate24m)] for r in d.itertuples()])
FACTS.append(f"**S2a (central)** [build03_cohort.py]: a fracao de nascidos com primeira solicitacao antes dos 24 meses sobe de {d.iloc[0].frac_ate24m:.1f}\\% (coorte 2010) para {d.iloc[-1].frac_ate24m:.1f}\\% (2016); antes dos 12 meses, de {d.iloc[0].frac_ate12m:.1f}\\% para {d.iloc[-1].frac_ate12m:.1f}\\%; antes dos 6 meses, {d.iloc[0].frac_ate6m:.1f}\\% para {d.iloc[-1].frac_ate6m:.1f}\\%. Denominador = nascidos vivos (SINASC).")

# S2b
d=cp("S2b_frac_0_36.csv")
emit("S2b_frac_0_36","Fracao da coorte de nascimento com primeira solicitacao antes de 6/12/18/24/36 meses",
 "Coortes plenamente observaveis de 0 a 36 meses (2010--2015). Mesmo denominador (nascidos vivos) e "
 "construcao da Tabela~\\ref{tab:S2a_frac_0_24}.",
 "lrrrrrr",["Coorte","Nascidos","\\% $<$6m","\\% $<$12m","\\% $<$18m","\\% $<$24m","\\% $<$36m"],
 [[str(int(r.coorte_nasc)),nf(r.nascidos,0),nf(r.frac_ate6m),nf(r.frac_ate12m),nf(r.frac_ate18m),nf(r.frac_ate24m),nf(r.frac_ate36m)] for r in d.itertuples()])

# S2c
d=cp("S2c_cond24.csv")
emit("S2c_cond24","Idade na primeira solicitacao, condicional a ter solicitado antes dos 24 meses, por coorte",
 "Coortes plenamente observaveis 0--24 (2010--2016). Media e mediana da idade (meses) na primeira "
 "solicitacao entre as criancas que solicitaram antes dos 24 meses --- truncamento identico para todas as "
 "coortes.",
 "lrrr",["Coorte","N (\\textless 24m)","Idade media","Idade mediana"],
 [[str(int(r.coorte_nasc)),nf(r.N_cond,0),nf(r.idade_media,2),nf(r.idade_mediana,1)] for r in d.itertuples()])
FACTS.append(f"**S2c** [build03_cohort.py]: entre quem solicitou antes dos 24 meses (truncamento identico), a idade media na solicitacao cai de {d.iloc[0].idade_media:.1f} meses (2010) para {d.iloc[-1].idade_media:.1f} (2016); mediana {d.iloc[0].idade_mediana:.0f} para {d.iloc[-1].idade_mediana:.0f}.")

# S2d
d=cp("S2d_km.csv")
emit("S2d_km","Kaplan--Meier do tempo do nascimento ate a primeira solicitacao, por coorte",
 "Coortes plenamente observaveis 0--24 (2010--2016). $S(t)$ = fracao ainda sem solicitacao em $t$ meses de "
 "idade; nao-solicitantes censurados (risco = nascidos vivos). Para estas coortes nao ha censura antes de "
 "24 meses. Mediana KM = idade em que $S$ cruza 0,5.",
 "lrrrrr",["Coorte","S(6)","S(12)","S(18)","S(24)","Mediana KM (m)"],
 [[str(int(r.coorte_nasc)),nf(r.S6,3),nf(r.S12,3),nf(r.S18,3),nf(r.S24,3),nf(r.mediana_KM_meses,0)] for r in d.itertuples()])
FACTS.append(f"**S2d** [build03_cohort.py]: a mediana KM do tempo do nascimento a primeira solicitacao cai de {d.iloc[0].mediana_KM_meses:.0f} meses (coorte 2010) para {d.iloc[-1].mediana_KM_meses:.0f} (2016); $S(24)$ de {d.iloc[0].S24:.3f} a {d.iloc[-1].S24:.3f}.")

# S3a / S3b
d=cp("S3a_decomp.csv")
emit("S3a_decomp","Decomposition of age at entry by birth cohort (means, entry at or before 48 months)",
 "Identity: age at entry = age at application + wait/30.44. Restricted to birth cohorts fully observable for entry up to 48 months (2010--2014) and to enrolled children entering at or before 48 months, so that truncation is identical across cohorts. All quantities in months since birth. The check column is (age at application) + (wait) - (age at entry).",
 "lrrrrr",["Birth cohort","N","Age at application","Wait","Age at entry","check"],
 [[str(int(r.coorte_nasc)),nf(r.N,0),nf(r.idade_sol,2),nf(r.espera,2),nf(r.idade_ent,2),nf(r.check,3)] for r in d.itertuples()])
sb=cp("S3b_split.csv"); r=sb.iloc[0]
emit("S3b_split","Split of the change in age at entry across birth cohorts, 2010--2014",
 "Change in means between the 2010 and 2014 birth cohorts, in months. By the accounting identity, the change in age at entry splits into age at application and waiting. Descriptive.",
 "lrr",["Component","Months","\\% of change"],
 [["Age at entry (total)",nf(r.d_idade_entrada,2),"100"],"MID",
  ["Age at application",nf(r.d_idade_sol,2),nf(100*r.frac_sol,0)],
  ["Wait",nf(r.d_espera,2),nf(100*r.frac_espera,0)]])
FACTS.append(f"**S3** [build03_cohort.py]: nas coortes de nascimento 2010--2014 (entrada $\\leq$48m), a idade media de entrada varia {r.d_idade_entrada:.2f} meses, repartida em {100*r.frac_sol:.0f}\\% solicitacao e {100*r.frac_espera:.0f}\\% espera.")

# S4a / S4b
d=cp("S4a_espera_coorte.csv")
emit("S4a_espera_coorte","Median time from application to referral (Kaplan--Meier), by birth cohort",
 "Birth cohorts fully observable from birth to 24 months (2010--2016). Kaplan--Meier median time in days from first application to first referral; children never referred are censored.",
 "lrr",["Birth cohort","Median wait KM (days)","N"],
 [[str(int(r.coorte_nasc)),nf(r.espera_mediana_KM_dias,0),nf(r.N,0)] for r in d.itertuples()])
d=cp("S4b_espera_renda.csv")
emit("S4b_espera_renda","Median time from application to referral (Kaplan--Meier), by birth cohort and postcode income quartile",
 "Kaplan--Meier median time in days from application to referral, by postcode income quartile (Q1 lowest). Birth cohorts 2010--2016.",
 "lrrrr",["Birth cohort","Q1","Q2","Q3","Q4"],
 [[str(int(r.coorte_nasc)),nf(r.Q1,0),nf(r.Q2,0),nf(r.Q3,0),nf(r.Q4,0)] for r in d.itertuples()])
FACTS.append(f"**S4** [build03_cohort.py]: a espera mediana KM ao encaminhamento por coorte de nascimento nao cai de forma monotona (2010={d.iloc[0].Q1:.0f}d no Q1); em toda coorte o quartil de renda mais alto espera menos que o mais baixo.")

# S6a
d=cp("S6a_nascidos_municipio.csv")
peak=d.loc[d["nascidos_vivos"].idxmax()]
emit("S6a_nascidos_municipio","Live births in the municipality of S\\~ao Paulo, by year, 2006--2018",
 "Live births by district of residence, tabulated by the municipal health secretariat, summed over 96 districts. The ``unknown district'' row and the ``total'' row are excluded, and the partial final year of the source is dropped.",
 "lrr",["Year","Live births","\\% vs.\\ 2018"],
 [[str(int(r.ano)),nf(r.nascidos_vivos,0),nf(r.var_pct_vs_2018,1)] for r in d.itertuples()])
FACTS.append(f"**S6a** [build03_demog.py]: nascidos vivos no municipio tem pico de {int(peak['nascidos_vivos']):,} em {int(peak['ano'])} e {int(d[d.ano==2018]['nascidos_vivos'].iloc[0]):,} em 2018 --- variacao pico$\\to$2018 de {100*(d[d.ano==2018]['nascidos_vivos'].iloc[0]/peak['nascidos_vivos']-1):.1f}\\%. 96 distritos (excluidas as linhas Ignorado e Total; 2026 parcial descartado).")

# S6b
d=cp("S6b_nascidos_renda.csv")
emit("S6b_nascidos_renda","Live births by district income quartile and year, 2006--2018",
 "Districts are grouped into quartiles by mean household income (2010 Census; Q1 lowest). District-to-income match: 96 of 96, by district name.",
 "lrrrr",["Year","Q1","Q2","Q3","Q4"],
 [[str(int(r.ano)),nf(r.Q1,0),nf(r.Q2,0),nf(r.Q3,0),nf(r.Q4,0)] for r in d.itertuples()])
q1c=100*(d["Q1"].iloc[-1]/d["Q1"].max()-1); q4c=100*(d["Q4"].iloc[-1]/d["Q4"].max()-1)
FACTS.append(f"**S6b** [build03_demog.py]: a queda de nascidos vivos do pico ate 2018 e semelhante entre distritos pobres e ricos --- Q1 (mais pobre) {q1c:.1f}\\% vs.\\ Q4 (mais rico) {q4c:.1f}\\% (Q3 = -10,0\\%, o maior).")

# S6c
d=cp("S6c_cobertura.csv")
emit("S6c_cobertura","Ratio of authorized childcare places to the population aged 0--3, by year and district income quartile",
 "Authorized capacity is the sum of offered childcare places (VAGOFER) in the first-semester profile; enrolment is never used. The pool aged 0--3 in year Y is the sum of live births in Y, Y-1, Y-2 and Y-3. Coverage is capacity divided by pool. Quartiles by district income. Coverage for the second and third income quartiles is reported in the accompanying csv.",
 "lrrrrr",["Year","Capacity (mun.)","Pool 0--3 (mun.)","Coverage (mun.)","Coverage Q1","Coverage Q4"],
 [[str(int(r.ano)),nf(r.capacidade_mun,0),nf(r.pool_0_3_mun,0),nf(r.cobertura_mun,3),nf(r.cobertura_Q1,3),nf(r.cobertura_Q4,3)] for r in d.itertuples()])
FACTS.append(f"**S6c** [build03_demog.py]: a razao capacidade autorizada / pool 0--3 no municipio sobe de {d.iloc[0].cobertura_mun:.3f} (2013) para {d.iloc[-1].cobertura_mun:.3f} (2019).")

# S6d
d=cp("S6d_decomp.csv"); r=d.iloc[0]
emit("S6d_decomp","Decomposition of the change in coverage between 2013 and 2019",
 "Coverage is capacity divided by pool. The gain is coverage in 2019 minus coverage in 2013. The capacity component holds the pool fixed at its 2013 level; the pool component holds capacity fixed at its 2019 level. Descriptive.",
 "lrr",["Component","Value (coverage)","\\% of gain"],
 [["Total gain 2013--2019",nf(r.ganho_total,3),"100"],"MID",
  ["Capacity growth",nf(r.comp_crescimento_capacidade,3),nf(100*r.frac_capacidade,0)],
  ["Pool 0--3 contraction",nf(r.comp_contracao_pool,3),nf(100*r.frac_pool,0)]])
FACTS.append(f"**S6d** [build03_demog.py]: o ganho de cobertura 2013$\\to$2019 ({r.ganho_total:.3f}) reparte-se em {100*r.frac_capacidade:.0f}\\% crescimento da capacidade e {100*r.frac_pool:.0f}\\% contracao do pool 0--3.")

# ---------- F6 ----------
d=pd.read_csv(os.path.join(STG,"S2a_frac_0_24.csv"))
fig,ax=plt.subplots(figsize=(7,4.3))
ax.plot(d.coorte_nasc,d.frac_ate12m,"-o",label="Applied before 12 months",color="#c0392b")
ax.plot(d.coorte_nasc,d.frac_ate24m,"-s",label="Applied before 24 months",color="#1f3b73")
ax.set_xlabel("Birth cohort"); ax.set_ylabel("Share of cohort")
ax.set_title("Share of birth cohort applying before 12 and 24 months")
ax.legend(); ax.set_xticks(range(2010,2017)); fig.tight_layout()
fig.savefig(os.path.join(FIG,"F6_solicitacao_precoce.pdf")); plt.close(fig)
d[["coorte_nasc","frac_ate12m","frac_ate24m"]].to_csv(os.path.join(FIG,"F6_data.csv"),index=False)
print("fig F6")

# ---------- F7 ----------
d=pd.read_csv(os.path.join(STG,"S6c_cobertura.csv"))
fig,ax=plt.subplots(figsize=(7,4.3))
ax.plot(d.ano,d.capacidade_mun/1000,"-o",label="Authorized capacity (thousand places)",color="#27ae60")
ax.plot(d.ano,d.pool_0_3_mun/1000,"-s",label="Population aged 0-3 (thousand children)",color="#7d5ba6")
ax.set_xlabel("Year"); ax.set_ylabel("Thousands")
ax.set_title("Authorized childcare capacity and the population aged 0-3")
ax.legend(); ax.set_xticks(range(2013,2020)); fig.tight_layout()
fig.savefig(os.path.join(FIG,"F7_capacidade_pool.pdf")); plt.close(fig)
d[["ano","capacidade_mun","pool_0_3_mun","cobertura_mun"]].to_csv(os.path.join(FIG,"F7_data.csv"),index=False)
print("fig F7")

# ---------- facts.md ----------
b01=(-19.09,0.80,0.20); b02=(-15.11,0.987,0.014)
sb=pd.read_csv(os.path.join(STG,"S3b_split.csv")).iloc[0]
b03=(sb.d_idade_entrada,sb.frac_sol,sb.frac_espera)
with open((NE_ROOT + r"\03_build\build03\facts.md"),"w",encoding="utf-8") as f:
    f.write("# BUILD03 -- facts.md (correcao de truncamento por coorte de nascimento; contexto demografico)\n\n")
    f.write("Descritivo (associacao/diferenca/variacao/composicao). Reaproveita child\\_master (BUILD01), "
            "child\\_dtenc (BUILD02) e SINASC/CEInfo. Escrito so em 03\\_build\\\\build03 e 02\\_audit; "
            "build01/build02 e <D>\\\\ intocados.\n\n")
    f.write("## Numeros por secao\n\n")
    for s in FACTS: f.write("- "+s+"\n\n")
    f.write("## S5 -- as tres versoes lado a lado (repartição da queda da idade de entrada)\n\n")
    f.write("| Quantidade | BUILD01 | BUILD02 | BUILD03 |\n|---|---|---|---|\n")
    f.write("| Unidade / janela | ano de solicitacao 2010--2018 | ano de solicitacao 2010--2016 (730d completo) | coorte de nascimento 2010--2014 (entrada $\\leq$48m) |\n")
    f.write(f"| Queda/variacao da idade de entrada (meses) | {b01[0]:.2f} | {b02[0]:.2f} | {b03[0]:.2f} |\n")
    f.write(f"| Fracao da solicitacao | {100*b01[1]:.0f}\\% | {100*b02[1]:.0f}\\% | {100*b03[1]:.0f}\\% |\n")
    f.write(f"| Fracao da espera | {100*b01[2]:.0f}\\% | {100*b02[2]:.0f}\\% | {100*b03[2]:.0f}\\% |\n\n")
    f.write("**Quantas coortes sustentam o numero final e qual o intervalo:** o numero do BUILD03 vem de "
            "**5 coortes de nascimento (2010--2014)**, as plenamente observaveis para a entrada ate 48 meses. "
            "As estatisticas centrais de solicitacao (S2) usam **7 coortes (2010--2016)**, plenas de 0 a 24 "
            "meses. A magnitude da ``queda'' difere entre as tres builds porque a unidade e a janela diferem "
            "(ano de solicitacao vs.\\ coorte de nascimento); a quantidade comparavel e a **repartição**: a "
            "solicitacao mais precoce responde por 80\\% (BUILD01), 99\\% (BUILD02) e 93\\% (BUILD03), e a "
            "espera por 20\\%, 1\\% e 7\\%. As tres concordam qualitativamente: a variacao da idade de entrada "
            "e dominada pela solicitacao mais precoce, nao pela espera; o BUILD03, por coorte de nascimento e "
            "com truncamento controlado nas duas pontas, situa a parcela da espera em ~7\\%.\n\n")
    f.write("## O que nao saiu\n\n")
    f.write("- Coortes de nascimento 2008--2009 (truncadas a esquerda) e 2017--2018 (a direita) ficam fora "
            "das estatisticas limpas (S2--S4); aparecem so na Tabela S1a de janelas.\n")
    f.write("- ``Fracao da coorte'' usa nascidos vivos (SINASC) como denominador e solicitantes (fila) como "
            "numerador; as duas fontes nao sao ligadas no nivel da crianca, entao a fracao supoe que os "
            "solicitantes de uma coorte nasceram no municipio naquele ano (aproximacao).\n")
    f.write("- S6c/S6d usam capacidade do perfil (VAGOFER, semestre 1) e pool de nascidos; a capacidade por "
            "distrito depende do casamento perfil--distrito (96/96) e do semestre 1 de cada ano.\n")
print("\nTODAS AS TABELAS + figuras + facts.md OK")
