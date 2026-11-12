# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD08 - A faixa e escolhida ou atribuida? (Parte A, decisivo p/ §5.6) e aceitacao de
# encaminhamentos rapidos (Parte B). Parte C: reconstrucao mensal -> T13. Descritivo.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
ROOT=NE_ROOT
FILA=NE_ROOT + r"\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
CM=os.path.join(ROOT,r"03_build\build01\_staging\child_master.feather")
B07=os.path.join(ROOT,r"03_build\build07\tables")
OUT=os.path.join(ROOT,r"03_build\build08"); TAB=os.path.join(OUT,"tables")
LOG=[]; FACTS=[]
def S(x): LOG.append(str(x)); print(x)
def w(df,n): df.to_csv(os.path.join(TAB,n),index=False)
BANDLAB={1:"Bercario I",2:"Bercario II",3:"Minigrupo I",4:"Minigrupo II",5:"Pre/other"}
REQ={"BERC1":1,"BERC2":2,"MINI1":3,"MINI2":4}
def band(m):
    if pd.isna(m): return np.nan
    if m<14: return 1
    if m<23: return 2
    if m<35: return 3
    if m<47: return 4
    return 5

S("carregando Fila1018 + child_master...")
fa=pd.read_stata(FILA,columns=["cd_aluno_sme","dt_solicitacao","dt_encaminhamento","dt_matricula",
    "cd_serie_ensino_solicitacao","an_letivo_solicitacao","ano_nasc","mes_nasc"])
for c,n in [("dt_solicitacao","sol"),("dt_encaminhamento","enc"),("dt_matricula","mat")]:
    fa["d_"+n]=pd.to_datetime(fa[c],format="%d/%m/%Y %H:%M:%S",errors="coerce")
# primeira solicitacao por crianca
first=fa.sort_values("d_sol").groupby("cd_aluno_sme").agg(
    d_sol1=("d_sol","min"),serie_sol=("cd_serie_ensino_solicitacao","first"),
    anlet=("an_letivo_solicitacao","first"),ano_nasc=("ano_nasc","first"),mes_nasc=("mes_nasc","first")).reset_index()
enc1=fa[fa.d_enc.notna()].sort_values("d_enc").groupby("cd_aluno_sme").agg(d_enc1=("d_enc","first")).reset_index()
mat1=fa[fa.d_mat.notna()].sort_values("d_mat").groupby("cd_aluno_sme").agg(d_mat1=("d_mat","first")).reset_index()
cm=pd.read_feather(CM,columns=["cd_aluno_sme","idade_sol","agrup_sol","ano_sol","ano_nasc","mes_nasc"])
d=cm.merge(first[["cd_aluno_sme","d_sol1","anlet"]],on="cd_aluno_sme",how="inner").merge(enc1,on="cd_aluno_sme",how="left").merge(mat1,on="cd_aluno_sme",how="left")
d["req"]=d.agrup_sol.map(REQ).fillna(5).astype(int)     # faixa solicitada (5=pre/other)
d["cur_band"]=d.idade_sol.map(band)                      # faixa pela idade na solicitacao
S(f"frame: {len(d):,} criancas.")

# ================= PARTE A =================
S("\n## PARTE A - a faixa e escolhida ou atribuida?")
# A1: crosstab idade(3 em 3) x faixa solicitada
d["idgrp"]=pd.cut(d.idade_sol,bins=list(range(0,49,3))+[999],right=False,
    labels=[f"{i}-{i+2}" for i in range(0,48,3)]+["48+"])
ct=pd.crosstab(d.idgrp,d.req)
ct.columns=[BANDLAB[c] for c in ct.columns]
ct.to_csv(os.path.join(TAB,"A1_idade_x_faixa.csv"))
S("A1: matriz idade-na-solicitacao (linhas, meses) x faixa solicitada (colunas), contagens:")
S(ct.to_string())

# A2: dentro de cada faixa de idade, variacao na faixa solicitada
S("\nA2: por faixa de idade -- n de faixas distintas com >=5% e share da faixa modal:")
rows=[]
for g,sub in d.groupby("idgrp",observed=True):
    dist=sub.req.value_counts(normalize=True)
    nge5=int((dist>=0.05).sum()); modal=dist.iloc[0]*100; modal_band=BANDLAB[dist.index[0]]
    rows.append({"idgrp":g,"n":len(sub),"n_faixas_ge5pct":nge5,"share_modal_pct":modal,"faixa_modal":modal_band})
    S(f"    {str(g):>6}: n={len(sub):>7,}  faixas>=5%={nge5}  modal={modal_band} ({modal:.1f}%)")
A2=pd.DataFrame(rows); w(A2,"A2_variacao_intra_idade.csv")

# A3: regra 31/03 - idade em 31/03 do an_letivo
d["idade_3103"]=(d.anlet-d.ano_nasc)*12 + (3-d.mes_nasc)
d["band_3103"]=d.idade_3103.map(band)
# concordancia: req vs cur_band (idade na solic) e req vs band_3103
sub=d[(d.req.between(1,4))&(d.anlet.between(2010,2019))].copy()
ag_cur=100*(sub.req==sub.cur_band).mean()
ag_3103=100*(sub.req==sub.band_3103).mean()
S(f"\nA3: concordancia da faixa SOLICITADA com:")
S(f"    faixa pela idade na data da solicitacao: {ag_cur:.1f}%")
S(f"    faixa pela idade em 31/03 do ano letivo (regra de corte): {ag_3103:.1f}%")
w(pd.DataFrame([{"criterio":"idade na solicitacao","concordancia_pct":ag_cur},
   {"criterio":"idade em 31/03 (regra)","concordancia_pct":ag_3103}]),"A3_concordancia.csv")

# A4: grupo "faixa ja ultrapassada / nao-corrente" em 2010
d2010=d[d.ano_sol==2010]
naocorr=d2010[d2010.req!=d2010.cur_band]
S(f"\nA4: em 2010, {100*len(naocorr)/len(d2010):.1f}% das 1as solicitacoes NAO sao para a faixa corrente (idade na solic).")
S(f"    idade mediana desse grupo: {naocorr.idade_sol.median():.0f}m; faixas pedidas: "
  +", ".join(f"{BANDLAB[b]}={100*(naocorr.req==b).mean():.0f}%" for b in [1,2,3,4,5]))
# reclassificar com 31/03
naocorr_3103=d2010[(d2010.req!=d2010.band_3103)]
S(f"    usando a regra 31/03, a fracao nao-corrente em 2010 cai para {100*len(naocorr_3103)/len(d2010):.1f}% "
  f"(concordancia sobe de {100*(d2010.req==d2010.cur_band).mean():.1f}% para {100*(d2010.req==d2010.band_3103).mean():.1f}%).")
w(pd.DataFrame([{"ano":2010,"pct_naocorrente_idadesolic":100*len(naocorr)/len(d2010),
   "pct_naocorrente_regra3103":100*len(naocorr_3103)/len(d2010),
   "idade_med_naocorr":naocorr.idade_sol.median()}]),"A4_2010_naocorrente.csv")

# A5 veredito
S(f"\nA5 VEREDITO: concordancia req~idade-solic={ag_cur:.0f}%, req~regra-31/03={ag_3103:.0f}%. "
  f"A faixa segue a regra de corte de 31/03 (data de nascimento + ano letivo), nao a idade corrente nem escolha livre.")
FACTS.append(f"**A (faixa)** [build08_faixa.py]: a faixa solicitada concorda {ag_3103:.0f}\\% com a faixa implicada pela "
  f"idade da crianca em 31/03 do ano letivo (regra de corte), vs {ag_cur:.0f}\\% com a idade na data da solicitacao. "
  f"A faixa e determinada pela regra (nascimento + ano letivo), nao por escolha da familia nem mecanicamente pela idade "
  f"corrente; a escolha da familia esta no ANO LETIVO e no momento de inscrever, nao no rotulo da faixa.")

# ================= PARTE B =================
S("\n## PARTE B - aceitacao de encaminhamentos rapidos")
ref=d[d.d_enc1.notna()].copy()
ref["sol_enc_d"]=(ref.d_enc1-ref.d_sol1).dt.days
ref["enrolled"]=ref.d_mat1.notna()
ref["idgrp4"]=pd.cut(ref.idade_sol,[-99,5,11,23,10**4],labels=["0-5m","6-11m","12-23m","24m+"])
ref["spd"]=pd.cut(ref.sol_enc_d,[-1,15,30,60,180,10**5],labels=["<=15d","16-30d","31-60d","61-180d",">180d"])
# B2 matriz taxa de matricula
S("B2 (DECISIVA): taxa de matricula apos encaminhamento (%) por idade-na-solic x rapidez (N em parenteses):")
mat_rate=ref.pivot_table(index="idgrp4",columns="spd",values="enrolled",aggfunc="mean",observed=True)*100
mat_n=ref.pivot_table(index="idgrp4",columns="spd",values="enrolled",aggfunc="size",observed=True)
for i in mat_rate.index:
    S("    "+f"{str(i):>6}: "+"  ".join(f"{c}={mat_rate.loc[i,c]:.0f}%(n={int(mat_n.loc[i,c]):,})" for c in mat_rate.columns))
mat_rate.round(1).to_csv(os.path.join(TAB,"B2_taxa_matricula.csv")); mat_n.to_csv(os.path.join(TAB,"B2_N.csv"))
# B3 celula critica
crit=ref[(ref.idgrp4=="0-5m")&(ref.sol_enc_d<=30)]
late_fast=ref[(ref.idgrp4=="24m+")&(ref.sol_enc_d<=30)]
S(f"\nB3: celula critica (0-5m, encaminhado <=30d): taxa de matricula={100*crit.enrolled.mean():.1f}% (n={len(crit):,}); "
  f"geral={100*ref.enrolled.mean():.1f}%; inscritas tarde (24m+) encaminhadas <=30d={100*late_fast.enrolled.mean():.1f}%.")
FACTS.append(f"**B (aceite)** [build08_faixa.py]: entre inscritas com 0--5 meses e encaminhadas em ate 30 dias, "
  f"{100*crit.enrolled.mean():.0f}\\% matriculam (vs {100*ref.enrolled.mean():.0f}\\% geral) --- nao ha recusa de vaga "
  f"por 'ainda nao precisar'. Encaminhamento rapido de bebe inscrito cedo termina em matricula, nao em recusa.")
# B4 re-encaminhamento dos que nao matriculam apos encaminhamento rapido
encall=fa[fa.d_enc.notna()][["cd_aluno_sme","d_enc"]].sort_values("d_enc")
enc_by=encall.groupby("cd_aluno_sme")["d_enc"].apply(list)
crit_no=crit[~crit.enrolled]
def second_enc(r):
    L=enc_by.get(r.cd_aluno_sme,[])
    aft=[e for e in L if e>r.d_enc1]
    return (aft[0]-r.d_enc1).days if aft else np.nan
crit_no=crit_no.copy(); crit_no["days_2nd"]=crit_no.apply(second_enc,axis=1)
S(f"\nB4: dos {len(crit_no):,} (0-5m, enc<=30d) que NAO matriculam: {100*crit_no.days_2nd.notna().mean():.0f}% recebem 2o "
  f"encaminhamento (mediana {crit_no.days_2nd.median():.0f} dias depois).")
w(pd.DataFrame([{"n_criticos_nao_matric":len(crit_no),"pct_reencaminhados":100*crit_no.days_2nd.notna().mean(),
   "dias_med_2o_enc":crit_no.days_2nd.median()}]),"B4_reencaminhamento.csv")
# B5 idade na matricula dos que aceitam
crit_yes=crit[crit.enrolled].copy()
crit_yes["idade_mat"]=((crit_yes.d_mat1.dt.year-crit_yes.ano_nasc)*12+(crit_yes.d_mat1.dt.month-crit_yes.mes_nasc))
S(f"B5: das (0-5m, enc<=30d) que MATRICULAM, idade na matricula: mediana {crit_yes.idade_mat.median():.0f}m, "
  f"p25={crit_yes.idade_mat.quantile(.25):.0f}, p75={crit_yes.idade_mat.quantile(.75):.0f}; "
  f"{100*(crit_yes.idade_mat<=6).mean():.0f}% matriculam com <=6 meses (demanda corrente inequivoca).")
w(crit_yes.idade_mat.describe().to_frame().T,"B5_idade_matricula.csv")

# ================= PARTE C: T13 =================
S("\n## PARTE C - T13 reconstrucao mensal (anual)")
c5=pd.read_csv(os.path.join(B07,"C5_decomp.csv"))
c2=pd.read_csv(os.path.join(B07,"C2_vs_oficial.csv"))
raz_med=c2.razao_cens.median()
def nf(x):
    try: return f"{float(x):,.0f}"
    except: return "--"
cap="Monthly reconstruction of the queue from microdata, annual totals"
note=(f"Built from the request microdata (Fila1018). New first applications, first referrals, and age exits (children "
      f"reaching 47 months without a referral) by calendar year; the constructed stock is the number with an application "
      f"and no referral at year-end, censoring those who have aged out. The constructed stock is an \\emph{{upper bound}}: "
      f"withdrawals and administrative removals are not observed in the extract, so it exceeds the administration's net "
      f"count. Against the official series (DEM\\_CRECHE), its median ratio is {raz_med:.2f}. Descriptive.")
L=["% requer booktabs. Descritivo.","\\begin{table}[htbp]\\centering",f"\\caption{{{cap}}}",
   "\\label{tab:T13}","\\small","\\setlength{\\tabcolsep}{5pt}","\\begin{tabular}{lrrrr}","\\toprule",
   "Year & New applications & Referrals & Age exits & Stock (year-end) \\\\","\\midrule"]
for _,r in c5.iterrows():
    L.append(f"{int(r.ano)} & {nf(r.solicitacoes)} & {nf(r.encaminhamentos)} & {nf(r.saidas_idade)} & {nf(r.estoque_dez)} \\\\")
L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
open(os.path.join(TAB,"T13_reconstrucao.tex"),"w",encoding="utf-8").write("\n".join(L)+"\n")
c5.to_csv(os.path.join(TAB,"T13_reconstrucao.csv"),index=False)
S(f"T13 gerado. razao mediana construido/oficial = {raz_med:.2f}.")

with open(os.path.join(OUT,"facts.md"),"w",encoding="utf-8") as f:
    f.write("# BUILD08 -- facts.md (faixa escolhida vs atribuida; aceitacao de encaminhamentos)\n\n")
    for s in FACTS: f.write("- "+s+"\n\n")
with open(os.path.join(OUT,"build08.log"),"w",encoding="utf-8") as f: f.write("\n".join(LOG))
print("\nfacts.md + build08.log + tabelas OK")
