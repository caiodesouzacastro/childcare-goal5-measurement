# -*- coding: utf-8 -*-
# BUILD01 - formata as tabelas de staging em .tex (booktabs) + .csv limpo em tables/.
# Linguagem descritiva: nenhuma tabela/nota usa efeito, impacto, causa. So associacao/
# diferenca/variacao/composicao.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
STG=(NE_ROOT + r"\03_build\build01\_staging")
TAB=(NE_ROOT + r"\03_build\build01\tables")
os.makedirs(TAB,exist_ok=True)
YEARS=[str(y) for y in range(2010,2019)]

def esc(s):
    s=str(s)
    for a,b in [("$","\\$"),("&","\\&"),("%","\\%"),("_","\\_"),("<=","$\\leq$"),(">=","$\\geq$"),
                ("<","$<$"),(">","$>$")]:
        s=s.replace(a,b)
    return s

# traducao de rotulos visiveis (cabecalhos/rotulos de linha) que vem dos CSV de staging.
# Nomes das faixas etarias ficam em portugues (institucionais); "Mini Grupo"->"Minigrupo".
TR={
 # modalidade / faixa (colunas rede, modalidade, agrup dos CSV)
 "Mini Grupo I":"Minigrupo I","Mini Grupo II":"Minigrupo II",
 "Direta":"Direct","Indireta":"Indirect","Conveniada":"Partner",
 # T1 (coluna metrica)
 "N solicitacoes":"N applications","% feminino":"% female","% Branca":"% White",
 "% Preta":"% Black","% Parda":"% Brown","% Amarela":"% Asian","% Indigena":"% Indigenous",
 "% Outra/ND":"% Other/NA","Idade mediana solic. (meses)":"Median age at application (months)",
 "% com prioridade":"% with priority","Renda mediana do CEP (R$)":"Median postcode income (R$)",
 "N mediano de CEIs <=2km":"Median N of centres <=2km",
 "% matriculado em 365d":"% enrolled within 365d","% nunca matriculado":"% never enrolled",
 # T4d (coluna variavel)
 "Idade na solicitacao (meses)":"Age at application (months)","Renda do CEP (R$)":"Postcode income (R$)",
 "Grupo IPVS (1-6)":"IPVS group (1-6)","N de CEIs <=2km":"N of centres <=2km",
 "Dist. ao CEI mais proximo (km)":"Distance to nearest centre (km)","Ano de solicitacao":"Year of application",
 # T5a (coluna rank)
 "fora (>2km / s coord)":"Outside",
}
def tr(s): return TR.get(str(s).strip(),s)

def numfmt(x,dec=1,thou=True):
    if pd.isna(x) or x=="" or (isinstance(x,str) and not x.replace(".","").replace("-","").replace(",","").isdigit()):
        try: x=float(x)
        except: return esc(x) if not (isinstance(x,float) and pd.isna(x)) else "n/d"
    try: xv=float(x)
    except: return esc(x)
    if pd.isna(xv): return "n/d"
    if dec==0:
        s=f"{xv:,.0f}"
    else:
        s=f"{xv:,.{dec}f}"
    return s

def emit(name, caption, note, colspec, header, body, label=None):
    label=label or name
    lines=[]
    lines.append("% requer \\usepackage{booktabs}. Tabela descritiva; sem interpretacao causal.")
    lines.append("\\begin{table}[htbp]\\centering")
    lines.append(f"\\caption{{{caption}}}")
    lines.append(f"\\label{{tab:{label}}}")
    lines.append("\\small")
    lines.append("\\setlength{\\tabcolsep}{4pt}")   # aperta colunas (largura)
    lines.append(f"\\begin{{tabular}}{{{colspec}}}")
    lines.append("\\toprule")
    if isinstance(header[0],(list,tuple)):
        for h in header: lines.append(" & ".join(h)+" \\\\")
        lines.append("\\midrule")
    else:
        lines.append(" & ".join(header)+" \\\\")
        lines.append("\\midrule")
    for row in body:
        if row=="MID": lines.append("\\midrule"); continue
        lines.append(" & ".join(row)+" \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append(f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}")
    lines.append("\\end{table}")
    with open(os.path.join(TAB,name+".tex"),"w",encoding="utf-8") as f:
        f.write("\n".join(lines)+"\n")
    print("tex:",name)

def copycsv(src,dst):
    pd.read_csv(os.path.join(STG,src)).to_csv(os.path.join(TAB,dst),index=False)

FACTS=[]
def fact(s): FACTS.append(s)

# ================= T1 =================
d=pd.read_csv(os.path.join(STG,"T1_fila.csv"))
cols=["2010","2012","2014","2016","2018","Total"]   # anos alternados (largura); csv completo
intmetrics={"N solicitacoes"}
dec0metrics={"Renda mediana do CEP (R$)","N mediano de CEIs <=2km","Idade mediana solic. (meses)"}
body=[]
for _,r in d.iterrows():
    m=r["metrica"]
    vals=[]
    for c in cols:
        if m=="N solicitacoes": vals.append(numfmt(r[c],0))
        elif m in dec0metrics: vals.append(numfmt(r[c],0))
        else: vals.append(numfmt(r[c],1))
    body.append([esc(tr(m))]+vals)
header=["Characteristic"]+[esc(c) for c in cols]
emit("T1_fila","Characteristics of childcare placement requests, by year of application, 2010--2018",
     "Universe: 1,524,560 requests, one per child, first application only. Year of application is the calendar year of the request date. The Total column includes 51,106 applications from 2006--2009 not shown in separate columns. Postcode income is mean household income in the census tract (2010 Census) matched to the postcode. The shares enrolled within 365 days and never enrolled refer to enrolment in any childcare centre before the end of the panel. Odd years are reported in the online appendix.",
     "l"+"r"*len(cols), header, body)
copycsv("T1_fila.csv","T1_fila.csv")
fact(f"**T1** [build01_child_tables.py]: universo de 1.524.560 solicitacoes. Idade mediana na solicitacao cai de {d.loc[d.metrica=='Idade mediana solic. (meses)','2010'].values[0]:.0f} meses (2010) para {d.loc[d.metrica=='Idade mediana solic. (meses)','2018'].values[0]:.0f} (2018). % nunca matriculado: {d.loc[d.metrica=='% nunca matriculado','2010'].values[0]:.1f}% (2010), minimo {d.loc[d.metrica=='% nunca matriculado','2015'].values[0]:.1f}% (2015), {d.loc[d.metrica=='% nunca matriculado','2018'].values[0]:.1f}% (2018, censura a direita). Renda mediana do CEP ~R$ {d.loc[d.metrica=='Renda mediana do CEP (R$)','Total'].values[0]:.0f}; n mediano de CEIs <=2km = {d.loc[d.metrica=='N mediano de CEIs <=2km','Total'].values[0]:.0f}.")

# ================= T2 =================
def emit_panel(fn_csv, name, caption, note, valdec=0):
    df=pd.read_csv(os.path.join(STG,fn_csv))
    semcols=[c for c in df.columns if c not in ("agrup","rede") and str(c).endswith("s1")]  # so 1os semestres (largura)
    header=["Age band","Contractual mode"]+[esc(c) for c in semcols]
    body=[]
    prev=None
    for _,r in df.iterrows():
        ag=esc(tr(r["agrup"])) if r["agrup"]!=prev else ""
        prev=r["agrup"]
        body.append([ag,esc(tr(r["rede"]))]+[numfmt(r[c],valdec) for c in semcols])
    emit(name,caption,note,"ll"+"r"*len(semcols),header,body)
    copycsv(fn_csv,name+".csv")
    return df
NOTE_MOD="Contractual mode: Direct = municipally operated network (REDE=DIR, including CEU CEI); Partner = non-direct (contracted) network (REDE=CON, grouping partner-run and indirect centres). Authorized capacity is the sum of offered places (VAGOFER) from the class profile; enrolment is never used. 2018S1 is a June snapshot. Second-semester columns are reported in the online appendix."
capdf=emit_panel("T2a_capacidade.csv","T2a_capacidade",
    "Panel A. Authorized places by age band and contractual mode",NOTE_MOD,0)
emit_panel("T2b_nescolas.csv","T2b_nescolas",
    "Panel B. Number of centres with at least one childcare class, by age band and contractual mode",NOTE_MOD,0)
emit_panel("T2c_nturmas.csv","T2c_nturmas",
    "Panel C. Number of childcare classes by age band and contractual mode",NOTE_MOD,0)
# facts T2
tot=capdf.groupby("agrup")[[c for c in capdf.columns if c not in ("agrup","rede")]].sum()
fact("**T2** [build01_perfil.py]: capacidade autorizada total (VAGOFER, DIR+CON) por agrupamento, 2013s1->2019s1: "+
     "; ".join(f"{ag} {int(tot.loc[ag,'2013s1']):,}->{int(tot.loc[ag,'2019s1']):,}" for ag in ["Bercario I","Bercario II","Mini Grupo I","Mini Grupo II"])+".")

# ================= T3 =================
d=pd.read_csv(os.path.join(STG,"T3_decomp.csv"))
header=["Ano solic.","(1) N","(2) Idade solic.","(3) Espera","(4) Idade entrada","(5)=(2)+(3)-(4)"]
body=[[str(int(r["ano_sol"])),numfmt(r["N"],0),numfmt(r["idade_sol"],2),numfmt(r["espera"],2),
       numfmt(r["idade_ent"],2),numfmt(r["check"],3)] for _,r in d.iterrows()]
emit("T3_decomp","Decomposicao da idade de entrada em creche (medias, criancas matriculadas), por ano de solicitacao",
     "Identidade contabil: idade de entrada = idade na solicitacao + espera/30,44. Todas as colunas em meses, exceto (1). Espera = (dt\\_mat\\_first $-$ dt\\_sol) em dias / 30,44. Coluna (5) e a verificacao da identidade nas medias (deve ser $\\approx 0$); diferencas residuais vem do arredondamento mes-a-mes das idades vs. espera em dias. Amostra: criancas que se matricularam.",
     "lrrrrr",header,body)
copycsv("T3_decomp.csv","T3_decomp.csv")
# medianas panel
dm=pd.read_csv(os.path.join(STG,"T3_medianas.csv"))
bodym=[[str(int(r["ano_sol"])),numfmt(r["idade_sol"],1),numfmt(r["espera"],1),numfmt(r["idade_ent"],1)] for _,r in dm.iterrows()]
emit("T3_medianas","Idade de entrada, idade na solicitacao e espera (MEDIANAS, criancas matriculadas), por ano",
     "Painel de referencia em medianas. A identidade contabil da decomposicao vale apenas para medias (Tabela~\\ref{tab:T3_decomp}); as medianas nao somam exatamente. Meses.",
     "lrrr",["Ano solic.","Idade solic.","Espera","Idade entrada"],bodym)
copycsv("T3_medianas.csv","T3_medianas.csv")
fact(f"**T3** [build01_child_tables.py]: idade media de entrada cai de {d.iloc[0]['idade_ent']:.2f} meses (2010) para {d.iloc[-1]['idade_ent']:.2f} (2018); idade media na solicitacao {d.iloc[0]['idade_sol']:.2f}->{d.iloc[-1]['idade_sol']:.2f}; espera media {d.iloc[0]['espera']:.2f}->{d.iloc[-1]['espera']:.2f}. Verificacao da identidade |col5|<={d['check'].abs().max():.3f} mes.")

# T3b
db=pd.read_csv(os.path.join(STG,"T3b_cumulativa.csv"))
header=["Ano","$\\Delta$ Idade solic.","$\\Delta$ Espera","$\\Delta$ Idade entrada","Frac. idade solic.","Frac. espera"]
body=[[str(int(r["ano_sol"])),numfmt(r["d_idade_sol"],2),numfmt(r["d_espera"],2),numfmt(r["d_idade_ent"],2),
       numfmt(r["frac_idade_sol"],3) if pd.notna(r["frac_idade_sol"]) else "n/d",
       numfmt(r["frac_espera"],3) if pd.notna(r["frac_espera"]) else "n/d"] for _,r in db.iterrows()]
emit("T3b_cumulativa","Variacao acumulada desde 2010 dos componentes da idade de entrada e fracao atribuida a cada um",
     "$\\Delta$ = diferenca da media em relacao a 2010 (meses). Pela identidade, $\\Delta$Idade entrada $=$ $\\Delta$Idade solic. $+$ $\\Delta$Espera; a fracao de cada componente e $\\Delta$componente / $\\Delta$Idade entrada. Decomposicao contabil, sem interpretacao causal.",
     "lrrrrr",header,body)
copycsv("T3b_cumulativa.csv","T3b_cumulativa.csv")
last=db.iloc[-1]
fact(f"**T3b** [build01_child_tables.py]: entre 2010 e 2018 a idade media de entrada caiu {last['d_idade_ent']:.2f} meses; {last['frac_idade_sol']*100:.0f}% dessa queda corresponde a solicitacao mais precoce e {last['frac_espera']*100:.0f}% a menor espera.")

# T3c / T3d (pivot idade_ent + componentes; salvar csv e emitir tabela de idade_ent por grupo x ano)
def emit_group_decomp(fn,name,gcol,glabel,caption,note,glabels=None):
    df=pd.read_csv(os.path.join(STG,fn))
    copycsv(fn,name+".csv")
    # tabela: idade de entrada media por grupo x ano (compacta)
    piv=df.pivot(index=gcol,columns="ano_sol",values="idade_ent")
    header=[esc(glabel)]+[str(c) for c in piv.columns]
    body=[]
    for g in piv.index:
        lab=glabels.get(g,str(g)) if glabels else str(g)
        body.append([esc(lab)]+[numfmt(piv.loc[g,c],1) for c in piv.columns])
    emit(name,caption,note,"l"+"r"*len(piv.columns),header,body)
    return df
emit_group_decomp("T3c_renda.csv","T3c_renda","rq","Quartil de renda",
    "Idade media de entrada em creche (meses) por quartil de renda do CEP e ano de solicitacao",
    "Quartis de renda do CEP (Censo 2010) ponderados pela crianca (Q1 = mais baixa). Criancas matriculadas. O arquivo T3c\\_renda.csv traz tambem idade na solicitacao, espera e verificacao por celula.",
    {1:"Q1 (mais baixa)",2:"Q2",3:"Q3",4:"Q4 (mais alta)"})
AGRLAB={"BERC1":"Bercario I","BERC2":"Bercario II","MINI1":"Mini Grupo I","MINI2":"Mini Grupo II"}
emit_group_decomp("T3d_agrup.csv","T3d_agrup","agrup_sol",AGRLAB,
    "Idade media de entrada em creche (meses) por agrupamento solicitado e ano",
    "Agrupamento solicitado a partir de cd\\_serie\\_ensino\\_solicitacao (Berc.\\ I=\\{1,2,3\\}, Berc.\\ II=\\{4,5,6\\}, Mini I=\\{11,27\\}, Mini II=\\{28,29\\}). Criancas matriculadas.")

# ================= T4 =================
def emit_incidence(fn,name,gcol,glabel,caption,note,glabels=None):
    df=pd.read_csv(os.path.join(STG,fn)); copycsv(fn,name+".csv")
    # tabela composta: para cada grupo, 4 metricas empilhadas nao cabe; mostramos
    # % nunca atendido por grupo x ano (principal) e csv traz o resto
    piv=df.pivot(index=gcol,columns="ano_sol",values="pnunca")
    header=[glabel]+[str(c) for c in piv.columns]
    body=[]
    for g in piv.index:
        lab=glabels.get(g,str(g)) if glabels else str(int(g)) if isinstance(g,(int,float)) else str(g)
        body.append([esc(str(lab))]+[numfmt(piv.loc[g,c],1) for c in piv.columns])
    emit(name,caption,note,"l"+"r"*len(piv.columns),header,body)
    return df
emit_incidence("T4a_renda.csv","T4a_renda","rq","Quartil renda",
    "Percentual nunca matriculado por quartil de renda do CEP e ano de solicitacao",
    "Celulas = \\% de solicitacoes daquele quartil-ano sem matricula em creche ate o fim do painel. O csv associado traz tambem espera mediana (dias), \\% atendido em 180d e em 365d por celula. Quartis de renda ponderados pela crianca.")
emit_incidence("T4b_ipvs.csv","T4b_ipvs","ipvs_q","Quartil IPVS",
    "Percentual nunca matriculado por quartil de IPVS e ano de solicitacao",
    "IPVS 2010 (grupo 1--6) associado ao CEP pelo setor censitario; quartis ponderados pela crianca. Casamento CEP--IPVS em 99,5\\% dos CEP. Demais metricas no csv.")
emit_incidence("T4c_nelig.csv","T4c_nelig","nelig_dec","Decil n. CEIs",
    "Percentual nunca matriculado por decil do numero de CEIs elegiveis (<=2km) e ano",
    "Decis do numero de CEIs a $\\leq$2km do CEP (D1 = menos CEIs). Demais metricas no csv.")
# T4d
dd=pd.read_csv(os.path.join(STG,"T4d_never.csv"))
header=["Variable","Never enrolled","Enrolled","Difference","(SE)"]
body=[]
for _,r in dd.iterrows():
    dec=0 if "R$" in r["variavel"] else (0 if "Ano" in r["variavel"] else 2)
    body.append([esc(tr(r["variavel"])),numfmt(r["nunca_mat"],dec if dec else 2),numfmt(r["matriculou"],dec if dec else 2),
                 numfmt(r["diferenca"],2),f"({numfmt(r['ep'],3)})"])
emit("T4d_never","Requests that never resulted in enrolment, compared with all others",
     "203,715 requests never followed by enrolment, compared with 1,320,845 that were. The difference is the mean among the never-enrolled minus the mean among the enrolled; standard errors in parentheses, computed from group variances. Priority shares in percentage points and year in years. Descriptive; no causal interpretation.",
     "lrrrr",header,body)
copycsv("T4d_never.csv","T4d_never.csv")
fact(f"**T4d** [build01_child_tables.py]: os 203.715 nunca matriculados, vs. matriculados, solicitam mais tarde (idade media {dd.iloc[0]['nunca_mat']:.1f} vs {dd.iloc[0]['matriculou']:.1f} meses), tem renda do CEP levemente maior (R$ {dd.iloc[1]['nunca_mat']:.0f} vs {dd.iloc[1]['matriculou']:.0f}; dif R$ {dd.iloc[1]['diferenca']:.0f}, EP {dd.iloc[1]['ep']:.1f}), menos CEIs proximos ({dd.iloc[3]['nunca_mat']:.1f} vs {dd.iloc[3]['matriculou']:.1f}) e muito menos prioridade ({dd.iloc[5]['nunca_mat']:.1f}% vs {dd.iloc[5]['matriculou']:.1f}%).")

# ================= T5 =================
d=pd.read_csv(os.path.join(STG,"T5a_rank.csv"))
cols=YEARS+["Total"]
header=["Distance rank"]+[esc(c) for c in cols]
body=[[esc(tr(r["rank"]))]+[numfmt(r[c],1) for c in cols] for _,r in d.iterrows()]
emit("T5a_rank","Distance rank of the centre of enrolment, by year (percent of enrolled children)",
     "Rank is the position of the centre of enrolment in the list of centres near the child's postcode, ordered by distance (1 = nearest). ``Outside'' means the centre of enrolment is beyond approximately two kilometres from the postcode or lacks coordinates in the register of geolocated centres; together these account for 39.0 percent of enrolments. The definition differs from that used in earlier diagnostics, which took a different reference centre.",
     "l"+"r"*len(cols),header,body)
copycsv("T5a_rank.csv","T5a_rank.csv")
fact(f"**T5a** [build01_child_tables.py]: {d[d['rank']=='1']['Total'].values[0]:.1f}% das criancas matriculam-se no CEI mais proximo; {d[d['rank']=='fora (>2km / s coord)']['Total'].values[0]:.1f}% num CEI alem de ~2km ou sem coordenada.")
# T5b
db_y=pd.read_csv(os.path.join(STG,"T5b_dist_ano.csv"))
db_r=pd.read_csv(os.path.join(STG,"T5b_dist_renda.csv"))
header=["Ano"]+[str(int(r["ano_sol"])) for _,r in db_y.iterrows()]
body=[["Dist. mediana (km)"]+[numfmt(r["dist_med_km"],3) for _,r in db_y.iterrows()]]
rrow=["Quartil renda"]+["Q"+str(int(r["rq"])) for _,r in db_r.iterrows()]
drow=["Dist. mediana (km)"]+[numfmt(r["dist_med_km"],3) for _,r in db_r.iterrows()]
emit("T5b_distancia","Distancia mediana (km) ao CEI de matricula, por ano e por quartil de renda",
     "Distancia CEP--CEI de matricula, apenas para matriculas dentro do conjunto geolocalizado. Painel superior por ano; inferior por quartil de renda do CEP.",
     "l"+"r"*max(len(db_y),len(db_r)),
     header+[""]*(max(len(db_y),len(db_r))-len(db_y)),
     [body[0]+[""]*(max(len(db_y),len(db_r))-len(db_y)),"MID",
      rrow+[""]*(max(len(db_y),len(db_r))-len(db_r)),
      drow+[""]*(max(len(db_y),len(db_r))-len(db_r))])
db_y.to_csv(os.path.join(TAB,"T5b_dist_ano.csv"),index=False); db_r.to_csv(os.path.join(TAB,"T5b_dist_renda.csv"),index=False)
# T5c
dc=pd.read_csv(os.path.join(STG,"T5c_modal_ano.csv"))
header=["Year","Direct","Indirect","Partner"]
body=[[str(int(r["ano_sol"])),numfmt(r["Direta"],1),numfmt(r["Indireta"],1),numfmt(r["Conveniada"],1)] for _,r in dc.iterrows()]
emit("T5c_modal","Composition of enrolment by contractual mode of the centre, by year (percent of enrolled children)",
     "Contractual mode of the centre of enrolment, classified by TIPOESC in the profile: Direct (CEI DIRET, CEU CEI), Indirect (CEI INDIR), Partner (CR.P.CONV). Rows sum to 100 percent across the three modes. The file T5c\\_modal\\_renda.csv reports the same composition by income quartile.",
     "lrrr",header,body)
copycsv("T5c_modal_ano.csv","T5c_modal_ano.csv"); copycsv("T5c_modal_renda.csv","T5c_modal_renda.csv")
fact(f"**T5c** [build01_child_tables.py]: a modalidade das matriculas passa de Direta {dc.iloc[0]['Direta']:.1f}% / Conveniada {dc.iloc[0]['Conveniada']:.1f}% (2010) para Direta {dc.iloc[-1]['Direta']:.1f}% / Conveniada {dc.iloc[-1]['Conveniada']:.1f}% (2018).")

# ================= T6 =================
d=pd.read_csv(os.path.join(STG,"T6a_modulo.csv"))
header=["Year","Age band","Classes","Module","Mean enrol.","\\% at cap.","\\% above"]
body=[]
for _,r in d.iterrows():
    body.append([str(int(r["ano"])),esc(tr(r["agrup"])),numfmt(r["n_turmas"],0),numfmt(r["MODULO_modal"],0),
                 numfmt(r["matricula_media"],1),numfmt(r["pct_na_capacidade"],1),numfmt(r["pct_acima"],1)])
emit("T6a_modulo","Class module and occupancy of childcare classes, 2016 and 2017",
     "MODULO is the authorized class size; enrolment is the number of children. Share at capacity: enrolment equals the module; above: enrolment exceeds it. The share below the module is the complement of the two shares shown. Modal modules: 7, 9, 12 and 25 children by band. Capacity is never derived from enrolment.",
     "llrrrrr",header,body)
copycsv("T6a_modulo.csv","T6a_modulo.csv")
fact("**T6a** [build01_rest.py]: turmas na capacidade (matricula=MODULO) em 2017: Berc.I 89,4%, Berc.II 75,6%, Mini I 62,3%, Mini II 23,3% (Mini II, modulo 25, com 75,5% abaixo da capacidade).")
# T6b
d=pd.read_csv(os.path.join(STG,"T6b_ratio.csv"))
semcols=[c for c in d.columns if c!="agrup" and str(c).endswith("s1")]  # so 1os semestres (largura)
header=["Age band"]+[esc(c) for c in semcols]
body=[[esc(tr(r["agrup"]))]+[numfmt(r[c],3) for c in semcols] for _,r in d.iterrows()]
emit("T6b_ratio","Ratio of enrolment to authorized places, by age band and semester",
     "Ratio of total enrolment (MATRIC) to total offered places (VAGOFER) in the class profile. The denominator is authorized capacity; enrolment enters only the numerator of this descriptive occupancy ratio and never the definition of capacity. 2018S1 is a mid-year snapshot. Second-semester columns are reported in the online appendix.",
     "l"+"r"*len(semcols),header,body)
copycsv("T6b_ratio.csv","T6b_ratio.csv")
# T6c
d=pd.read_csv(os.path.join(STG,"T6c_turmas_por_escola.csv"))
ycols=[c for c in d.columns if c not in ("rede","agrup")]
header=["Contractual mode","Age band"]+ycols
body=[]; prev=None
for _,r in d.iterrows():
    md=esc(tr(r["rede"])) if r["rede"]!=prev else ""; prev=r["rede"]
    body.append([md,esc(tr(r["agrup"]))]+[numfmt(r[c],2) for c in ycols])
emit("T6c_turmas_por_escola","Average number of childcare classes per centre and age band, by contractual mode and year (first semester)",
     "Mean number of classes in the band, across centres with at least one class in that band. First semester of each year.",
     "ll"+"r"*len(ycols),header,body)
copycsv("T6c_turmas_por_escola.csv","T6c_turmas_por_escola.csv")

# ================= T7 =================
d=pd.read_csv(os.path.join(STG,"T7a_ceis_operacao.csv"))
ycols=[c for c in d.columns if c!="modalidade"]
header=["Contractual mode"]+ycols
body=[[esc(tr(r["modalidade"]))]+[numfmt(r[c],0) for c in ycols] for _,r in d.iterrows()]
emit("T7a_ceis","Childcare centres in operation, by contractual mode and year (first semester)",
     "A centre is counted as operating if it has at least one childcare class in the first-semester profile. Direct = REDE DIR; Partner = REDE CON (partner-run and indirect).",
     "l"+"r"*len(ycols),header,body)
copycsv("T7a_ceis_operacao.csv","T7a_ceis.csv")
fact("**T7a** [build01_perfil.py]: CEIs em operacao passam de 1.641 (2013) para 2.406 (2019); a rede direta fica ~400--450 e a conveniada cresce de 1.223 para 2.004.")
# T7b
d=pd.read_csv(os.path.join(STG,"T7b_aber_fech.csv"))
header=["Year","Openings","Places opened","Closures","Places closed","Net places"]
body=[[str(int(r["ano"])),numfmt(r["aberturas"],0),numfmt(r["vagas_abertas"],0),numfmt(r["fechamentos"],0),
       numfmt(r["vagas_fechadas"],0),numfmt(r["saldo_vagas"],0)] for _,r in d.iterrows()]
emit("T7b_aber_fech","Openings and closures of partner childcare contracts, by year",
     "Events in the partner sector. An opening is a centre's first contract; a closure is a termination with an associated loss of places. Only a fraction of contractual terminations correspond to a loss of capacity in the class profile; the closures reported here are those with places attached. Net = places opened minus places closed.",
     "lrrrrr",header,body)
copycsv("T7b_aber_fech.csv","T7b_aber_fech.csv")
fact("**T7b** [build01_rest.py]: aberturas de parcerias somam ~2.070 escolas em 2013--2019 (pico 692 em 2015, 96.397 vagas); fechamentos com vagas crescem de 23 (2015) a 110 (2018, 14.505 vagas) e 84 (2019, 12.158). Saldo de vagas positivo todos os anos.")
# T7c
d=pd.read_csv(os.path.join(STG,"T7c_percap.csv"))
piv=d.pivot(index="rqs",columns="ano",values="percap")
header=["Sector income quartile"]+[str(c) for c in piv.columns]
body=[["Q"+str(int(g))+ (" (lowest)" if g==1 else " (highest)" if g==4 else "")]+[numfmt(piv.loc[g,c],3) for c in piv.columns] for g in piv.index]
emit("T7c_percap","Authorized infant-band places per application, median across educational sectors, by sector income quartile and year",
     "By sector and year: authorized places in the two infant bands, first-semester profile, divided by the number of childcare applications recorded in that sector and year. The table reports the median across sectors within each income quartile of the sector. The distribution is in T7c\\_percap\\_dist.csv.",
     "l"+"r"*len(piv.columns),header,body)
copycsv("T7c_percap.csv","T7c_percap.csv"); copycsv("T7c_percap_dist.csv","T7c_percap_dist.csv")
fact("**T7c** [build01_rest.py]: a capacidade autorizada de Bercario por solicitacao (mediana entre setores) sobe de ~0,31--0,45 (2013) para ~0,62--0,65 (2018), convergindo entre quartis de renda do setor.")

# ================= T8 =================
d=pd.read_csv(os.path.join(STG,"T8a_traj.csv"))
dt_=pd.read_csv(os.path.join(STG,"T8a_traj_total.csv"))
header=["Quartil renda","N","\\% com 1o ano obs.","\\% on-time","\\% com repetencia"]
body=[]
for _,r in d.iterrows():
    body.append(["Q"+str(int(r["rq"])),numfmt(r["N"],0),numfmt(r["pct_1ano_obs"],1),numfmt(r["pct_ontime"],1),numfmt(r["pct_reprov"],1)])
body.append("MID")
r=dt_.iloc[0]
body.append(["Todos",numfmt(r["N"],0),numfmt(r["pct_1ano_obs"],1),numfmt(r["pct_ontime"],1),numfmt(r["pct_reprov"],1)])
emit("T8a_traj","Trajetoria posterior das coortes 2008--2012 por quartil de renda do CEP (descritivo)",
     "Coortes por ano de nascimento 2008--2012 (traj\\_child). \\% com 1o ano observado = fracao com 1o ano do fundamental observado no periodo; \\% on-time e \\% com repetencia calculados entre os observados. Quartil de renda do CEP herdado da fila. Descritivo; nao interpretavel como efeito.",
     "lrrrr",header,body)
copycsv("T8a_traj.csv","T8a_traj.csv")
# T8b: nao disponivel
with open(os.path.join(TAB,"T8b_proficiencia.tex"),"w",encoding="utf-8") as f:
    f.write("% T8b -- proficiencia PSP por idade de entrada/modalidade/renda.\n"
            "% NAO DISPONIVEL: os arquivos de PSP reutilizaveis (psp2017/2018/2019, p18/p19_2ano)\n"
            "% contem apenas indicadores de participacao, sem as notas de proficiencia (mat/port).\n"
            "% As notas so existem no pipeline RDD invalidado (trat_PSP_rdd), cujo uso e vedado\n"
            "% por esta tarefa. Celula: nao disponivel.\n")
fact("**T8a** [build01_rest.py]: coortes 2008--2012, % com 1o ano observado 28--33%; on-time ~99,3% e repetencia 2,5--3,3% (levemente maior no quartil de renda mais baixo: 3,33% Q1 vs 2,47% Q4).")
fact("**T8b**: NAO DISPONIVEL -- as notas de proficiencia da PSP (mat/port) nao estao nos arquivos reutilizaveis (so ha indicadores de participacao); os escores so existem no pipeline RDD invalidado, vedado nesta tarefa.")

# ================= T10 (apendice metodologico) =================
# Numeros dos DIAG01-11 (resumo dos diagnosticos anteriores + DIAG11.md).
desenhos=[
 ("Corte da fila (RDD por escola)","Descontinuidade artificial (rvar/dt_corte por escola)","Corte nao e regra de elegibilidade; densidade e desfechos saltam por construcao","Manipulacao/nao-aleatoriedade do corte (McCrary)","DIAG01: corte definido ex-post pela propria alocacao"),
 ("Leave-one-out do corte","Variacao no corte deixando uma escola de fora","Sem primeiro estagio exogeno; corte co-determinado com a demanda","Placebos nao nulos","DIAG02: corte segue a fila, nao a oferta"),
 ("Abertura de CEI perto de casa (IV)","Novos CEIs <=1km apos a solicitacao","Abertura correlacionada com demanda local reprimida","Exposicao pre-solicitacao ja preve desfechos","DIAG05: oferta responde ao territorio"),
 ("Regra de corte etario 31/03","Idade em 31/03 do ano da vaga","Descontinuidade fraca/endogena a serie solicitada","Primeiro estagio fraco; composicao muda no limiar","DIAG06: regra nao vincula alocacao"),
 ("Alocacao (quase-aleatoria) entre escolas","Qual CEI dentro do conjunto elegivel","Alocacao nao e aleatoria; segue distancia e vaga","Balanco falha; distancia preve escola","DIAG08: fila ordena por distancia/prioridade"),
 ("Choque de capacidade (VAGOFER/parceria)","Reducoes/fechamentos de vagas no conjunto elegivel","Primeiro estagio pequeno, some sob setor$\\times$semestre; fechamentos selecionados por repasse","Placebo pre-solicitacao $\\geq$ coeficiente da janela real; b(pre) espera +4,87 vs +3,29","DIAG11: choque segue tendencia de setor"),
]
header=["Desenho","Fonte de variacao","Teste que falhou","Estatistica-chave","Diagnostico de origem"]
def esc10(s):
    s=str(s)
    for a,b in [("&","\\&"),("%","\\%"),("_","\\_")]: s=s.replace(a,b)  # nao escapa $ (math intencional em T10)
    return s
body=[[esc10(a),esc10(b),esc10(c),esc10(d),esc10(e)] for a,b,c,d,e in desenhos]
emit("T10_desenhos","Apendice metodologico: desenhos de identificacao testados e por que nao geram variacao exogena",
     "Sintese dos diagnosticos DIAG01--DIAG11. ``Primeiro estagio obtido'' e ``teste que falhou'' resumem cada exercicio; a estatistica-chave cita o resultado mais informativo. O sistema de fila centralizada alinha oferta, distancia e prioridade a demanda, de modo que nenhuma fonte de variacao testada e exogena aos desfechos. Fonte: DIAG01--DIAG11 (C:\\textbackslash Users\\textbackslash <usuario>\\textbackslash Downloads).",
     "p{2.4cm}p{2.6cm}p{3.2cm}p{2.8cm}p{2.4cm}",header,body)
pd.DataFrame(desenhos,columns=["desenho","fonte_variacao","teste_falhou","estatistica_chave","diagnostico"]).to_csv(os.path.join(TAB,"T10_desenhos.csv"),index=False)

# ================= facts.md =================
with open((NE_ROOT + r"\03_build\build01\facts.md"),"w",encoding="utf-8") as f:
    f.write("# BUILD01 -- facts.md\n\n")
    f.write("Fonte de cada numero das tabelas e figuras do BUILD01. Paper descritivo: "
            "a redacao deve usar apenas linguagem de associacao/diferenca/variacao/composicao "
            "(evitar termos de causalidade).\n\n")
    f.write("**Regras cumpridas:** capacidade sempre de VAGOFER/MODULO/CAPREAL/vagas\\_contratadas "
            "(nunca de matricula); nada em Dropbox\\\\ (exceto \\_audit\\\\) ou <D>\\\\ foi modificado; "
            "nenhum artefato do pipeline invalidado (rvar, dt\\_corte, trat\\_ber\\*) foi usado.\n\n")
    f.write("## Numeros por tabela\n\n")
    for s in FACTS: f.write("- "+s+"\n\n")
    f.write("## O que NAO saiu\n\n")
    f.write("- **T8b (proficiencia PSP)**: nao disponivel. Os arquivos reutilizaveis de PSP so tem "
            "indicadores de participacao; as notas de mat/port so existem no pipeline RDD invalidado, vedado.\n")
    f.write("- **T5a rank**: 39,5% das matriculas caem em ``fora'' (CEI >2km ou sem coordenada no cadastro "
            "geolocalizado de 2.313 CEIs); o rank so e calculado dentro do conjunto geolocalizado.\n")
    f.write("- **Serie do perfil**: termina em 2019s1 (dez/2019 incompativel); 2018s1 vem do snapshot jun/2018.\n")
    f.write("- **Anos pre-2010**: 51.106 solicitacoes de 2006--2009 entram so na coluna Total de T1.\n")
    f.write("- **IPVS**: casado a 99,5% dos CEP via setor censitario; grupos 0--6 (grupo 0 tratado como ausente).\n")
    f.write("- **Modalidade em T2/T7a**: ``Conveniada''=REDE CON agrupa parceiras e indiretas "
            "(o perfil so separa DIR/CON); a separacao em 3 vias (Direta/Indireta/Conveniada) so aparece em T5c.\n")
print("\nTODAS AS TABELAS + facts.md ESCRITAS")
