# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD07 - intencao (faixa corrente vs futura) e fluxo (aceitacao, contabilidade da fila).
# Responde as duas criticas centrais do 2o parecer. Descritivo. Nao modifica build01-06.
# Reaproveita child_master.feather + Fila1018.dta + evolucaodemanda.csv.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":11,"figure.dpi":120})
ROOT=NE_ROOT
FILA=NE_ROOT + r"\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
CM=os.path.join(ROOT,r"03_build\build01\_staging\child_master.feather")
EXT=os.path.join(ROOT,r"03_build\build04\_ext\evolucaodemanda.csv")
OUT=os.path.join(ROOT,r"03_build\build07"); TAB=os.path.join(OUT,"tables"); FIG=os.path.join(OUT,"figures")
os.makedirs(TAB,exist_ok=True); os.makedirs(FIG,exist_ok=True)
LOG=[]; FACTS=[]
def S(x): LOG.append(str(x)); print(x)
def w(df,n): df.to_csv(os.path.join(TAB,n),index=False)

# ---------------- carga e frame por crianca ----------------
S("carregando Fila1018 + child_master...")
fa=pd.read_stata(FILA,columns=["cd_aluno_sme","dt_solicitacao","dt_encaminhamento","dt_matricula",
    "cd_serie_ensino_solicitacao","cd_serie_ensino_encaminhamento"])
for c,n in [("dt_solicitacao","sol"),("dt_encaminhamento","enc"),("dt_matricula","mat")]:
    fa["d_"+n]=pd.to_datetime(fa[c],format="%d/%m/%Y %H:%M:%S",errors="coerce")
sol=fa.sort_values("d_sol").groupby("cd_aluno_sme").agg(d_sol1=("d_sol","min"),
    serie_sol=("cd_serie_ensino_solicitacao","first")).reset_index()
enc=fa[fa.d_enc.notna()].sort_values("d_enc").groupby("cd_aluno_sme").agg(
    d_enc1=("d_enc","first"),serie_enc=("cd_serie_ensino_encaminhamento","first")).reset_index()
mat=fa[fa.d_mat.notna()].sort_values("d_mat").groupby("cd_aluno_sme").agg(d_mat1=("d_mat","first")).reset_index()
p=sol.merge(enc,on="cd_aluno_sme",how="left").merge(mat,on="cd_aluno_sme",how="left")
cm=pd.read_feather(CM,columns=["cd_aluno_sme","ano_nasc","mes_nasc","idade_sol","agrup_sol","ano_sol"])
d=cm.merge(p,on="cd_aluno_sme",how="inner")
S(f"frame: {len(d):,} criancas.")

# ---------------- bandas ----------------
REQ={"BERC1":1,"BERC2":2,"MINI1":3,"MINI2":4}
LAB={1:"Bercario I",2:"Bercario II",3:"Minigrupo I",4:"Minigrupo II",5:"Post-creche"}
MINAGE={1:0,2:14,3:23,4:35}   # idade minima da faixa (meses)
def cur_band(idade):
    if idade<14: return 1
    if idade<23: return 2
    if idade<35: return 3
    if idade<47: return 4
    return 5
d["cur"]=d.idade_sol.map(cur_band)
d["req"]=d.agrup_sol.map(REQ)          # NaN se None (nao-creche)
def classify(r):
    if pd.isna(r.req): return "NONCRECHE"
    if r.req==r.cur: return "CURRENT"
    if r.req>r.cur: return "FUTURE"
    return "PAST"
d["cls"]=d.apply(classify,axis=1)

# ================= PARTE A =================
S("\n## PARTE A - faixa corrente vs futura")
S("A1: variavel = cd_serie_ensino_solicitacao (Fila) -> agrup_sol (child_master). Mapa creche: "
  "1=Bercario I, 4=Bercario II, 27=Minigrupo I, 28=Minigrupo II. Series 8/14/16/18/23/25 = niveis "
  "acima da creche (pre-escola; idade mediana 37-68m), classificadas NONCRECHE.")
# A2 distribuicao
A2=d.cls.value_counts().reindex(["CURRENT","FUTURE","PAST","NONCRECHE"]).fillna(0).astype(int)
S("A2: distribuicao (todas as 1as solicitacoes):")
for k,v in A2.items(): S(f"     {k}: {v:,} ({100*v/len(d):.1f}%)")
w(A2.rename("n").reset_index().rename(columns={"index":"classe"}),"A2_classificacao.csv")
FACTS.append(f"**A2** [build07.py]: das 1as solicitacoes, {100*A2['CURRENT']/len(d):.0f}\\% sao para a faixa "
  f"CORRENTE (a que a idade implica), {100*A2['FUTURE']/len(d):.0f}\\% para faixa FUTURA (mais velha que a idade), "
  f"{100*A2['PAST']/len(d):.0f}\\% para faixa mais nova, e {100*A2['NONCRECHE']/len(d):.0f}\\% para nivel acima da creche.")

# A3 fracao CURRENT por ano e por coorte
def frac_cur(sub): return 100*(sub.cls=="CURRENT").mean()
A3a=d[d.ano_sol.between(2010,2018)].groupby("ano_sol").apply(lambda s:pd.Series({
    "n":len(s),"frac_current":frac_cur(s),"frac_future":100*(s.cls=="FUTURE").mean(),
    "frac_noncreche":100*(s.cls=="NONCRECHE").mean()})).reset_index()
w(A3a,"A3_por_ano.csv")
A3c=d[d.ano_nasc.between(2010,2016)].groupby("ano_nasc").apply(lambda s:pd.Series({
    "n":len(s),"frac_current":frac_cur(s),"frac_future":100*(s.cls=="FUTURE").mean(),
    "frac_noncreche":100*(s.cls=="NONCRECHE").mean()})).reset_index()
w(A3c,"A3_por_coorte.csv")
S("A3: fracao para FAIXA CORRENTE, por ano de solicitacao:")
for _,r in A3a.iterrows(): S(f"     {int(r.ano_sol)}: current={r.frac_current:.1f}%  future={r.frac_future:.1f}%  noncreche={r.frac_noncreche:.1f}%")
S("A3: por coorte de nascimento:")
for _,r in A3c.iterrows(): S(f"     {int(r.ano_nasc)}: current={r.frac_current:.1f}%  future={r.frac_future:.1f}%")
FACTS.append(f"**A3** [build07.py]: a fracao das 1as solicitacoes para a faixa CORRENTE {'sobe' if A3a.frac_current.iloc[-1]>A3a.frac_current.iloc[0] else 'cai'} "
  f"de {A3a.frac_current.iloc[0]:.1f}\\% (2010) para {A3a.frac_current.iloc[-1]:.1f}\\% (2018); "
  f"por coorte, {A3c.frac_current.iloc[0]:.1f}\\% (2010) -> {A3c.frac_current.iloc[-1]:.1f}\\% (2016).")

# A4 por faixa de idade na solicitacao
d["idband"]=pd.cut(d.idade_sol,[-99,5,11,23,10**4],labels=["0-5m","6-11m","12-23m","24m+"])
A4=d.groupby("idband").apply(lambda s:pd.Series({"n":len(s),
    "frac_current":frac_cur(s),"frac_future":100*(s.cls=="FUTURE").mean(),
    "frac_noncreche":100*(s.cls=="NONCRECHE").mean(),
    "frac_bercI_req":100*(s.req==1).mean()})).reset_index()
w(A4,"A4_por_idade.csv")
S("A4: por faixa de idade na solicitacao (frac current / future / noncreche / pediu BercI):")
for _,r in A4.iterrows(): S(f"     {r.idband}: n={int(r.n):,}  current={r.frac_current:.1f}%  future={r.frac_future:.1f}%  noncreche={r.frac_noncreche:.1f}%  pediu_BercI={r.frac_bercI_req:.1f}%")
very=d[d.idade_sol.between(0,5)]
FACTS.append(f"**A4** [build07.py]: entre as solicitacoes muito precoces (0--5 meses), {100*(very.req==1).mean():.0f}\\% "
  f"pedem Bercario I (faixa corrente) e {100*(very.cls=='FUTURE').mean():.0f}\\% pedem faixa futura; "
  f"quase toda solicitacao precoce e para vaga imediata, nao reserva.")

# A5 estatistica central restrita a faixa corrente
nasc={2010:174116,2011:176268,2012:175679,2013:172718,2014:175293,2015:175789,2016:167005}
rows=[]
for c in range(2010,2017):
    sub=d[d.ano_nasc==c]
    full=100*(sub.idade_sol<12).sum()/nasc[c]
    cur=100*((sub.idade_sol<12)&(sub.cls=="CURRENT")).sum()/nasc[c]
    rows.append({"coorte":c,"nascidos":nasc[c],"frac12_full":full,"frac12_faixa_corrente":cur})
A5=pd.DataFrame(rows); w(A5,"A5_coorte_faixa_corrente.csv")
S("A5: fracao da coorte com 1a solic <12m -- TODAS vs so FAIXA CORRENTE (denom=SINASC):")
for _,r in A5.iterrows(): S(f"     coorte {int(r.coorte)}: todas={r.frac12_full:.1f}%  faixa_corrente={r.frac12_faixa_corrente:.1f}%")
FACTS.append(f"**A5** [build07.py]: restringindo a solicitacoes para a faixa corrente, a subida da fracao da coorte "
  f"com 1a solicitacao antes de 12 meses persiste: {A5.frac12_faixa_corrente.iloc[0]:.1f}\\% (2010) -> "
  f"{A5.frac12_faixa_corrente.iloc[-1]:.1f}\\% (2016), vs {A5.frac12_full.iloc[0]:.1f}\\% -> {A5.frac12_full.iloc[-1]:.1f}\\% sem restricao.")

# ================= PARTE B =================
S("\n## PARTE B - quem e chamado aceita?")
d["gap_em"]=(d.d_mat1-d.d_enc1).dt.days      # encaminhamento -> matricula (dias)
d["ano_sol"]=d.d_sol1.dt.year
ref=d[d.d_enc1.notna()].copy()               # encaminhados
# B1 percentis do gap por ano
B1=ref[ref.gap_em.notna()&(ref.gap_em>=0)].groupby(ref.d_enc1.dt.year).agg(
    n=("gap_em","size"),p25=("gap_em",lambda s:s.quantile(.25)),p50=("gap_em","median"),
    p75=("gap_em",lambda s:s.quantile(.75)),p90=("gap_em",lambda s:s.quantile(.9))).reset_index().rename(columns={"d_enc1":"ano_enc"})
w(B1,"B1_gap_ano.csv")
S("B1: intervalo encaminhamento->matricula (dias), percentis por ano de encaminhamento:")
for _,r in B1[B1.ano_enc.between(2010,2018)].iterrows(): S(f"     {int(r.ano_enc)}: n={int(r.n):,}  p25={r.p25:.0f} p50={r.p50:.0f} p75={r.p75:.0f} p90={r.p90:.0f}")
# B2 fracao nao-matriculado em 30/60/90d (entre encaminhados)
def notmat(sub,k):
    g=sub.gap_em
    return 100*(~((g>=0)&(g<=k))).mean()   # nao matriculou dentro de k dias (inclui nunca)
B2=ref[ref.d_enc1.dt.year.between(2010,2018)].groupby(ref.d_enc1.dt.year).apply(lambda s:pd.Series({
    "n":len(s),"nao_30d":notmat(s,30),"nao_60d":notmat(s,60),"nao_90d":notmat(s,90),
    "nunca_mat":100*s.d_mat1.isna().mean()})).reset_index().rename(columns={"d_enc1":"ano_enc"})
w(B2,"B2_naomat_ano.csv")
S("B2: fracao de encaminhamentos SEM matricula em 30/60/90 dias (e nunca), por ano:")
for _,r in B2.iterrows(): S(f"     {int(r.ano_enc)}: nao30={r.nao_30d:.1f}% nao60={r.nao_60d:.1f}% nao90={r.nao_90d:.1f}% nunca={r.nunca_mat:.1f}%")
# B3 por faixa de idade na solicitacao (DECISIVA)
B3=ref.groupby("idband").apply(lambda s:pd.Series({
    "n":len(s),"gap_p50":s.gap_em[(s.gap_em>=0)].median(),
    "nao_90d":notmat(s,90),"nunca_mat":100*s.d_mat1.isna().mean()})).reset_index()
w(B3,"B3_por_idade.csv")
S("B3 (DECISIVA): gap mediano e nao-matricula por faixa de IDADE NA SOLICITACAO:")
for _,r in B3.iterrows(): S(f"     {r.idband}: n={int(r.n):,}  gap_med={r.gap_p50:.0f}d  nao90={r.nao_90d:.1f}%  nunca={r.nunca_mat:.1f}%")
FACTS.append(f"**B3** [build07.py]: entre encaminhados, os que se inscreveram muito cedo (0--5m) tem gap mediano "
  f"encaminhamento->matricula de {B3[B3.idband=='0-5m'].gap_p50.iloc[0]:.0f} dias e {B3[B3.idband=='0-5m'].nunca_mat.iloc[0]:.0f}\\% "
  f"nunca matriculam, vs gap {B3[B3.idband=='24m+'].gap_p50.iloc[0]:.0f} e {B3[B3.idband=='24m+'].nunca_mat.iloc[0]:.0f}\\% para os de 24m+.")
# B4 nao-matricula por ano de solicitacao
B4=ref[ref.ano_sol.between(2010,2018)].groupby("ano_sol").apply(lambda s:pd.Series({
    "n":len(s),"nao_90d":notmat(s,90),"nunca_mat":100*s.d_mat1.isna().mean()})).reset_index()
w(B4,"B4_por_ano.csv")
S("B4: nao-matricula apos encaminhamento por ano de solicitacao:")
for _,r in B4.iterrows(): S(f"     {int(r.ano_sol)}: nao90={r.nao_90d:.1f}%  nunca={r.nunca_mat:.1f}%")
# B5 idade no encaminhamento vs idade minima da faixa solicitada
ref["idade_enc"]=((ref.d_enc1.dt.year-ref.ano_nasc)*12+(ref.d_enc1.dt.month-ref.mes_nasc))
ref["min_faixa"]=ref.req.map(MINAGE)
ref["diff_minfaixa"]=ref.idade_enc-ref.min_faixa
b5=ref[ref.min_faixa.notna()]
B5=pd.DataFrame([{"p10":b5.diff_minfaixa.quantile(.1),"p25":b5.diff_minfaixa.quantile(.25),
    "p50":b5.diff_minfaixa.median(),"p75":b5.diff_minfaixa.quantile(.75),"p90":b5.diff_minfaixa.quantile(.9),
    "frac_neg":100*(b5.diff_minfaixa<0).mean()}])
w(B5,"B5_idade_enc.csv")
S(f"B5: idade no encaminhamento menos idade minima da faixa solicitada (meses): "
  f"p25={B5.p25.iloc[0]:.0f} mediana={B5.p50.iloc[0]:.0f} p75={B5.p75.iloc[0]:.0f}; "
  f"{B5.frac_neg.iloc[0]:.0f}% encaminhados ANTES da idade minima da faixa.")

# ================= PARTE C =================
S("\n## PARTE C - contabilidade mensal da fila")
d["sol_mi"]=d.d_sol1.dt.year*12+(d.d_sol1.dt.month-1)
d["enc_mi"]=(d.d_enc1.dt.year*12+(d.d_enc1.dt.month-1))
d["birth_mi"]=d.ano_nasc*12+(d.mes_nasc-1)
d["age47_mi"]=d.birth_mi+47
BIG=10**9
enc_mi=d.enc_mi.fillna(BIG).astype("int64").values
sol_mi=d.sol_mi.astype("int64").values
age47=d.age47_mi.astype("int64").values
MI0=2010*12; MIEND=2018*12+11; months=list(range(MI0,MIEND+1))
def cum_le(arr,m): return int((arr<=m).sum())
# versao sem censura (exit=enc) e com censura (exit=min(enc,age47))
exit_unc=enc_mi
exit_cen=np.minimum(enc_mi,age47)
rows=[]
for m in months:
    ent=cum_le(sol_mi,m)
    rows.append({"mi":m,"ano":m//12,"mes":m%12+1,
        "novas_sol":int((sol_mi==m).sum()),"encaminhamentos":int((enc_mi==m).sum()),
        "estoque_sem_cens":ent-cum_le(exit_unc,m),"estoque_com_cens":ent-cum_le(exit_cen,m)})
C1=pd.DataFrame(rows); C1["data"]=pd.to_datetime(dict(year=C1.ano,month=C1.mes,day=1)); w(C1,"C1_mensal.csv")
S(f"C1: serie mensal 2010-2018 ({len(C1)} meses). estoque(com censura) dez/2010={C1[(C1.ano==2010)&(C1.mes==12)].estoque_com_cens.iloc[0]:,} "
  f"-> dez/2018={C1[(C1.ano==2018)&(C1.mes==12)].estoque_com_cens.iloc[0]:,}.")

# C2 vs oficial DEM_CRECHE (trimestral)
# IMPORTANTE: thousands="." (separador de milhar BR). NAO usar dtype=str na coluna DEM,
# senao "2.392" (=2392) e lido como 2.392. Ver DIAG16.
ev=pd.read_csv(EXT,sep=";",thousands=".",dtype={"MES_ANO_REF":str})
MES={"jan":1,"fev":2,"mar":3,"abr":4,"mai":5,"jun":6,"jul":7,"ago":8,"set":9,"out":10,"nov":11,"dez":12}
ev["dem"]=pd.to_numeric(ev.DEM_CRECHE,errors="coerce")
ev["ano"]=ev.MES_ANO_REF.str[-2:].astype(int)+2000; ev["mes"]=ev.MES_ANO_REF.str[:3].map(MES)
off=ev.groupby(["ano","mes"]).dem.sum().reset_index()
off=off[(off.ano>=2010)&(off.ano<=2018)]
C2=off.merge(C1[["ano","mes","estoque_com_cens","estoque_sem_cens"]],on=["ano","mes"],how="inner")
C2["razao_cens"]=C2.estoque_com_cens/C2.dem; C2["razao_semcens"]=C2.estoque_sem_cens/C2.dem
w(C2,"C2_vs_oficial.csv")
S("C2: estoque construido (com censura) vs oficial DEM_CRECHE, por trimestre (razao):")
for _,r in C2.iterrows(): S(f"     {int(r.ano)}q{int(r.mes)}: constr={int(r.estoque_com_cens):,}  oficial={int(r.dem):,}  razao={r.razao_cens:.2f}")
FACTS.append(f"**C2** [build07.py]: com o DEM\\_CRECHE lido corretamente (separador de milhar; ver DIAG16), o estoque "
  f"construido (microdados, com censura por idade) e o oficial tem correlacao {C2.estoque_com_cens.corr(C2.dem):.2f} "
  f"e razao mediana {C2.razao_cens.median():.2f} (constr/oficial); ambas as series sao sazonais (pico set., vale dez.).")

# C3 diferenca (saidas nao observadas) por ano
off_dez=C2[C2.mes==12]
C3=off_dez.assign(dif_semcens=off_dez.estoque_sem_cens-off_dez.dem,
    dif_cens=off_dez.estoque_com_cens-off_dez.dem,
    pct_semcens=100*(off_dez.estoque_sem_cens-off_dez.dem)/off_dez.dem)[["ano","dem","estoque_sem_cens","estoque_com_cens","dif_semcens","dif_cens","pct_semcens"]]
w(C3,"C3_diferenca.csv")
S("C3: diferenca estoque construido - oficial (dez), nivel e %:")
for _,r in C3.iterrows(): S(f"     {int(r.ano)}: sem_cens={int(r.estoque_sem_cens):,} com_cens={int(r.estoque_com_cens):,} oficial={int(r.dem):,} | dif_semcens={int(r.dif_semcens):,} ({r.pct_semcens:.0f}%)")

# C4 as duas series (ja em C1); reporta diferenca anual (dez)
C4=C1[C1.mes==12][["ano","estoque_sem_cens","estoque_com_cens"]].copy()
C4["dif_censura"]=C4.estoque_sem_cens-C4.estoque_com_cens
w(C4,"C4_censura.csv")
S("C4: estoque sem vs com censura por idade (dez); diferenca = saidas por idade acumuladas:")
for _,r in C4.iterrows(): S(f"     {int(r.ano)}: sem_cens={int(r.estoque_sem_cens):,} com_cens={int(r.estoque_com_cens):,} dif={int(r.dif_censura):,}")

# C5 decomposicao anual do estoque (com censura): Delta = sol - enc - saidas_idade + residuo
ageout_mi=np.where(age47<enc_mi,age47,BIG)   # sai por idade so se envelhece antes de encaminhar
rows=[]
prev=None
for y in range(2010,2019):
    dec=y*12+11
    stock=cum_le(sol_mi,dec)-cum_le(exit_cen,dec)
    sol_y=int((d.sol_mi.between(y*12,dec)).sum())
    enc_y=int(((enc_mi>=y*12)&(enc_mi<=dec)&(enc_mi<=age47)).sum())   # encaminhamentos que sao saida (antes de envelhecer)
    ageo_y=int(((ageout_mi>=y*12)&(ageout_mi<=dec)).sum())
    delta=stock-prev if prev is not None else np.nan
    resid=delta-(sol_y-enc_y-ageo_y) if prev is not None else np.nan
    rows.append({"ano":y,"estoque_dez":stock,"delta":delta,"solicitacoes":sol_y,
        "encaminhamentos":enc_y,"saidas_idade":ageo_y,"residuo":resid})
    prev=stock
C5=pd.DataFrame(rows); w(C5,"C5_decomp.csv")
S("C5: decomposicao anual do estoque (com censura): Delta = sol - enc - saidas_idade + residuo:")
for _,r in C5.iterrows():
    dl="--" if pd.isna(r.delta) else f"{int(r.delta):+,}"
    rs="--" if pd.isna(r.residuo) else f"{int(r.residuo):+,}"
    S(f"     {int(r.ano)}: estoque={int(r.estoque_dez):,} delta={dl} sol={int(r.solicitacoes):,} enc={int(r.encaminhamentos):,} saidas_idade={int(r.saidas_idade):,} resid={rs}")

# ---------------- figuras ----------------
# F11 estoque construido (mensal) vs oficial (trimestral)
fig,ax=plt.subplots(figsize=(7.4,4.4))
ax.plot(C1.data,C1.estoque_com_cens/1000,"-",color="#1f3b73",lw=1.3,label="Constructed stock (microdata, age-censored)")
ax.plot(C1.data,C1.estoque_sem_cens/1000,"--",color="#6b8cce",lw=1.0,label="Constructed stock (no age censoring)")
od=pd.to_datetime(dict(year=C2.ano,month=C2.mes,day=1))
ax.plot(od,C2.dem/1000,"s",color="#c0392b",ms=5,label="Official registered demand")
ax.set_xlabel("Month"); ax.set_ylabel("Children on the list (thousands)")
ax.set_title("Constructed queue stock vs official registered demand, 2010–2018")
ax.legend(fontsize=8); ax.grid(True,alpha=.3); fig.tight_layout()
fig.savefig(os.path.join(FIG,"F11_estoque.pdf")); plt.close(fig)
C1[["ano","mes","estoque_com_cens","estoque_sem_cens"]].to_csv(os.path.join(FIG,"F11_data.csv"),index=False)
print("fig F11")
# F12 fracao faixa corrente por ano
fig,ax=plt.subplots(figsize=(7,4.3))
ax.plot(A3a.ano_sol,A3a.frac_current,"-o",color="#1b7837",label="Current band")
ax.plot(A3a.ano_sol,A3a.frac_future,"-s",color="#c0392b",label="Future band")
ax.plot(A3a.ano_sol,A3a.frac_noncreche,"-^",color="#7d5ba6",label="Above creche (pre-school)")
ax.set_xlabel("Year of application"); ax.set_ylabel("Share of first applications (%)")
ax.set_title("Requested band relative to the child's age, by year")
ax.set_ylim(0,100); ax.legend(); ax.grid(True,alpha=.3); fig.tight_layout()
fig.savefig(os.path.join(FIG,"F12_faixa_corrente.pdf")); plt.close(fig)
A3a.to_csv(os.path.join(FIG,"F12_data.csv"),index=False)
print("fig F12")

# ---------------- tex ----------------
def nf(x,d=1):
    try: x=float(x)
    except: return str(x)
    return f"{x:,.0f}" if d==0 else f"{x:,.{d}f}"
def emit(name,cap,note,cols,header,body):
    L=["% requer booktabs. Descritivo.","\\begin{table}[htbp]\\centering",f"\\caption{{{cap}}}",
       f"\\label{{tab:{name}}}","\\small","\\setlength{\\tabcolsep}{4pt}",f"\\begin{{tabular}}{{{cols}}}","\\toprule",
       " & ".join(header)+" \\\\","\\midrule"]
    for r in body: L.append(" & ".join(r)+" \\\\")
    L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
    open(os.path.join(TAB,name+".tex"),"w",encoding="utf-8").write("\n".join(L)+"\n"); print("tex:",name)

emit("A3_faixa_ano","Share of first applications for the current age band, by year of application",
 "The current band is the one the child's age at application implies (Bercario I 0--13 months, II 14--22, Minigrupo I 23--34, II 35--46). Future = a band older than the child's age; above creche = a pre-school level. Descriptive.",
 "lrrrr",["Year","N","\\% current","\\% future","\\% above creche"],
 [[str(int(r.ano_sol)),nf(r.n,0),nf(r.frac_current),nf(r.frac_future),nf(r.frac_noncreche)] for _,r in A3a.iterrows()])
emit("A4_faixa_idade","Requested band relative to age, by age at application",
 "Share of first applications by age at application. Current, future and above-creche as in the companion table; ``requested Bercario I'' is the share whose requested band is the youngest. Descriptive.",
 "lrrrrr",["Age at application","N","\\% current","\\% future","\\% above creche","\\% req.\\ Berc.\\ I"],
 [[str(r.idband),nf(r.n,0),nf(r.frac_current),nf(r.frac_future),nf(r.frac_noncreche),nf(r.frac_bercI_req)] for _,r in A4.iterrows()])
emit("A5_faixa_corrente","Share of the birth cohort applying before 12 months, all applications and current-band only",
 "Denominator: live births (SINASC). Numerator: children of the cohort with a first application before age 12 months; the last column restricts to applications for the current age band. Descriptive.",
 "lrrr",["Birth cohort","Live births","All (\\%)","Current band (\\%)"],
 [[str(int(r.coorte)),nf(r.nascidos,0),nf(r.frac12_full),nf(r.frac12_faixa_corrente)] for _,r in A5.iterrows()])
emit("B3_aceitacao_idade","Time to enrolment and non-enrolment after referral, by age at application",
 "Among children referred at least once. Gap = days from first referral to first enrolment (median, among those enrolled). ``Not within 90 days'' and ``never enrolled'' are shares of the referred. Descriptive.",
 "lrrrr",["Age at application","N referred","Median gap (d)","\\% not in 90d","\\% never enrolled"],
 [[str(r.idband),nf(r.n,0),nf(r.gap_p50,0),nf(r.nao_90d),nf(r.nunca_mat)] for _,r in B3.iterrows()])
emit("B4_naomat_ano","Non-enrolment after referral, by year of application",
 "Among children referred at least once, the share not enrolled within 90 days of referral and the share never enrolled. Descriptive.",
 "lrrr",["Year","N referred","\\% not in 90d","\\% never enrolled"],
 [[str(int(r.ano_sol)),nf(r.n,0),nf(r.nao_90d),nf(r.nunca_mat)] for _,r in B4.iterrows()])
emit("C2_estoque_vs_oficial","Constructed queue stock versus official registered demand, by quarter",
 "Constructed stock: children with a first application and no referral by quarter-end, censoring those who reach 47 months (age exit), from the microdata. Official: DEM\\_CRECHE summed over districts (open data). Ratio = constructed/official. Descriptive.",
 "lrrr",["Quarter","Constructed","Official","Ratio"],
 [[f"{int(r.ano)}Q{int(r.mes)}",nf(r.estoque_com_cens,0),nf(r.dem,0),nf(r.razao_cens,2)] for _,r in C2.iterrows()])
emit("C5_decomposicao","Annual decomposition of the constructed queue stock",
 "Change in the age-censored constructed stock decomposed as new first applications minus referrals (exits before ageing out) minus age exits (children reaching 47 months without a referral). The residual reflects referrals after age exit and within-month timing. Descriptive.",
 "lrrrrrr",["Year","Stock (Dec)","$\\Delta$","Applications","Referrals","Age exits","Residual"],
 [[str(int(r.ano)),nf(r.estoque_dez,0),("--" if pd.isna(r.delta) else f"{int(r.delta):+,}"),nf(r.solicitacoes,0),nf(r.encaminhamentos,0),nf(r.saidas_idade,0),("--" if pd.isna(r.residuo) else f"{int(r.residuo):+,}")] for _,r in C5.iterrows()])

# ---------------- facts.md + log ----------------
with open(os.path.join(OUT,"facts.md"),"w",encoding="utf-8") as f:
    f.write("# BUILD07 -- facts.md (intencao: faixa corrente vs futura; fluxo: aceitacao e contabilidade da fila)\n\n")
    f.write("Descritivo. Reaproveita child\\_master + Fila1018 + evolucaodemanda.csv. Nao modifica build01-06.\n\n## Numeros\n\n")
    for s in FACTS: f.write("- "+s+"\n\n")
with open(os.path.join(OUT,"build07.log"),"w",encoding="utf-8") as f: f.write("\n".join(LOG))
print("\nfacts.md + build07.log + tabelas + F11/F12 OK")
