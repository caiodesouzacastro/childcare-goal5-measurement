# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# DIAG15 - artefato administrativo no inicio do painel (2010-2012)?
# Testa se a subida da inscricao precoce (S2a) antes de 2013 e comportamento ou
# registro em lote / digitalizacao. Descritivo. Nao modifica build01/02/03; D: intocavel.
# Nao usa dt_corte*, rvar, trat_ber_*. Reaproveita child_master.feather + Fila1018.dta (raw).
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os, unicodedata, re

ROOT=NE_ROOT
FILA=NE_ROOT + r"\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
CM=os.path.join(ROOT,r"03_build\build01\_staging\child_master.feather")
PERFIL=os.path.join(ROOT,r"03_build\build01\_staging\perfil_turma.csv")
CEPRENDA=NE_ROOT + r"\dados_restritos\Ciro\01_dados\processados\bases_analise\cep_renda_pop_2010.dta"
TAB=os.path.join(ROOT,r"03_build\build04\tables"); os.makedirs(TAB,exist_ok=True)
def fixhex(s): return re.sub(r'<([0-9a-fA-F]{2})>', lambda m: bytes([int(m.group(1),16)]).decode('latin-1'), str(s))
def norm(s):
    s=fixhex(s)
    return "".join(c for c in unicodedata.normalize("NFD",str(s).strip().upper()) if unicodedata.category(c)!="Mn")
def w(df,n): df.to_csv(os.path.join(TAB,n),index=False); print("  csv ->",n)
SUM=[]  # linhas do resumo para o markdown
def S(x): SUM.append(x); print(x)

# ---------------- carga ----------------
print("carregando child_master + Fila1018 (raw)...")
cm=pd.read_feather(CM,columns=["cd_aluno_sme","ano_nasc","idade_sol","ano_sol","tp_raca_cor",
    "cd_sexo_aluno","tipo_prioridade_encaminhamento","cep_aluno","renda","nelig"])
fa=pd.read_stata(FILA)
fa["_dt"]=pd.to_datetime(fa.dt_solicitacao,format="%d/%m/%Y %H:%M:%S",errors="coerce")
fa["_hms"]=fa._dt.dt.hour*3600+fa._dt.dt.minute*60+fa._dt.dt.second
# primeira solicitacao por crianca (min _dt)
fa=fa.sort_values("_dt").drop_duplicates("cd_aluno_sme",keep="first")
fa=fa[["cd_aluno_sme","_dt","_hms","cpf_resp_aluno","cd_esc_solicitacao"]]
d=cm.merge(fa,on="cd_aluno_sme",how="left")
d["ym"]=d._dt.dt.to_period("M").astype(str)
d["asol"]=d._dt.dt.year               # ano da 1a solicitacao (pelo timestamp)
d["msol"]=d._dt.dt.month
S(f"# DIAG15 base: {len(d):,} criancas (1 por crianca = 1a solicitacao). match fila={d._dt.notna().mean()*100:.2f}%")

# batch: n de criancas com timestamp exato (data+hora:min:seg) identico
d["batch_n"]=d.groupby("_dt")["cd_aluno_sme"].transform("size")
d.loc[d._dt.isna(),"batch_n"]=1

# ============================================================ PARTE A
S("\n## PARTE A - forma do inicio do painel")
# A1: serie mensal jan2010-dez2013
mA=d[(d._dt>=pd.Timestamp(2010,1,1))&(d._dt<=pd.Timestamp(2013,12,31))].copy()
A1=mA.groupby("ym").agg(N=("cd_aluno_sme","size"),idade_med=("idade_sol","median"),
    frac_lt12=("idade_sol",lambda s:100*(s<12).mean())).reset_index()
w(A1,"D15_A1_mensal.csv")
S(f"A1: serie mensal 2010-2013 ({len(A1)} meses). N medio/mes={A1.N.mean():.0f}; "
  f"min={A1.N.min():.0f} ({A1.loc[A1.N.idxmin(),'ym']}); max={A1.N.max():.0f} ({A1.loc[A1.N.idxmax(),'ym']}).")
S("A1 primeiros 6 meses (ym,N,idade_med,frac_lt12):")
for _,r in A1.head(6).iterrows(): S(f"    {r.ym}  N={int(r.N):>6}  idade_med={r.idade_med:>4.0f}  frac<12m={r.frac_lt12:>5.1f}")
S(f"A1 frac<12m: jan2010={A1.iloc[0].frac_lt12:.1f} -> dez2012={A1[A1.ym=='2012-12'].frac_lt12.values[0]:.1f} -> dez2013={A1[A1.ym=='2013-12'].frac_lt12.values[0]:.1f}")

# A2: pre-2010 (dt_solicitacao 2006-2009)
pre=d[d._dt<pd.Timestamp(2010,1,1)].copy()
A2=pre.assign(ano=pre._dt.dt.year).groupby("ano").agg(N=("cd_aluno_sme","size"),
    idade_med=("idade_sol","median"),frac_com_hora=("_hms",lambda s:100*(s>0).mean())).reset_index()
w(A2,"D15_A2_pre2010.csv")
S(f"A2: {len(pre):,} solicitacoes com data 2006-2009 (aparecem com a data ORIGINAL, nao de importacao).")
for _,r in A2.iterrows(): S(f"    {int(r.ano)}: N={int(r.N):>6}  idade_med={r.idade_med:>4.0f}m  frac_com_hora={r.frac_com_hora:>5.1f}%")

# A3: top-5 meses 2010-2012 por volume
mm=d[(d._dt>=pd.Timestamp(2010,1,1))&(d._dt<=pd.Timestamp(2012,12,31))].copy()
A3=mm.groupby("ym").agg(N=("cd_aluno_sme","size"),idade_med=("idade_sol","median"),
    frac_lt12=("idade_sol",lambda s:100*(s<12).mean()),
    frac_batch10=("batch_n",lambda s:100*(s>=10).mean())).reset_index().sort_values("N",ascending=False)
w(A3,"D15_A3_topmeses.csv")
S("A3: 5 maiores meses 2010-2012 (ym,N,idade_med,frac<12m,frac_em_lote>=10):")
for _,r in A3.head(5).iterrows(): S(f"    {r.ym}  N={int(r.N):>6}  idade_med={r.idade_med:>3.0f}  frac<12m={r.frac_lt12:>5.1f}  frac_lote10={r.frac_batch10:>5.1f}")

# ============================================================ PARTE B
S("\n## PARTE B - registro em lote (timestamp compartilhado)")
def fr(s,k): return 100*(s>=k).mean()
B1=d[d.asol.between(2010,2018)].groupby("asol").agg(
    N=("cd_aluno_sme","size"),
    frac_sh2=("batch_n",lambda s:fr(s,2)),frac_sh10=("batch_n",lambda s:fr(s,10)),
    frac_sh50=("batch_n",lambda s:fr(s,50)),frac_sh100=("batch_n",lambda s:fr(s,100))).reset_index()
w(B1,"D15_B1_lote_share.csv")
S("B1: frac de 1as-solicitacoes com timestamp compartilhado por >=2/10/50/100 criancas, por ano:")
for _,r in B1.iterrows(): S(f"    {int(r.asol)}: N={int(r.N):>6}  >=2:{r.frac_sh2:>5.1f}%  >=10:{r.frac_sh10:>5.1f}%  >=50:{r.frac_sh50:>5.1f}%  >=100:{r.frac_sh100:>5.1f}%")
# B2 tamanho do lote
B2=d[d.asol.between(2010,2018)].groupby("asol").agg(
    batch_med=("batch_n","median"),batch_p90=("batch_n",lambda s:s.quantile(.9)),
    batch_max=("batch_n","max")).reset_index()
w(B2,"D15_B2_lote_tam.csv")
S("B2: tamanho do lote (n criancas c/ timestamp exato) por ano (mediana,p90,max):")
for _,r in B2.iterrows(): S(f"    {int(r.asol)}: mediana={r.batch_med:>3.0f}  p90={r.batch_p90:>5.0f}  max={int(r.batch_max):>6}")
# B3 idade lote vs individual
d["grp"]=np.where(d.batch_n>=10,"lote10","individual")
B3=d[d.asol.between(2010,2018)].groupby(["asol","grp"]).idade_sol.median().unstack().reset_index()
w(B3,"D15_B3_idade_lote.csv")
S("B3: idade mediana na 1a solicitacao, lote(>=10) vs individual, por ano:")
for _,r in B3.iterrows():
    lote=r.get("lote10",np.nan); ind=r.get("individual",np.nan)
    S(f"    {int(r.asol)}: lote10={lote if pd.isna(lote) else f'{lote:.0f}'}  individual={ind:.0f}")
# B4 coorte frac<12m full vs sem lote
nasc={2010:174116,2011:176268,2012:175679,2013:172718,2014:175293,2015:175789,2016:167005}
rows=[]
for c in range(2010,2017):
    sub=d[d.ano_nasc==c]
    full=100*((sub.idade_sol<12).sum())/nasc[c]
    nob=100*((sub.idade_sol<12)&(sub.batch_n<10)).sum()/nasc[c]
    rows.append({"coorte":c,"nascidos":nasc[c],"frac12_full":full,"frac12_sem_lote10":nob,
                 "frac_lote10_na_coorte":100*(sub.batch_n>=10).mean()})
B4=pd.DataFrame(rows); w(B4,"D15_B4_coorte_sem_lote.csv")
S("B4: frac da coorte de nascimento com 1a solic <12m -- COMPLETA vs SEM LOTES(>=10). denom=SINASC:")
for _,r in B4.iterrows(): S(f"    coorte {int(r.coorte)}: full={r.frac12_full:>5.1f}  sem_lote={r.frac12_sem_lote10:>5.1f}  (%lote na coorte={r.frac_lote10_na_coorte:.1f})")
S(f"B4 subida 2010->2012: full {B4.iloc[0].frac12_full:.1f}->{B4.iloc[2].frac12_full:.1f} (+{B4.iloc[2].frac12_full-B4.iloc[0].frac12_full:.1f}); "
  f"sem_lote {B4.iloc[0].frac12_sem_lote10:.1f}->{B4.iloc[2].frac12_sem_lote10:.1f} (+{B4.iloc[2].frac12_sem_lote10-B4.iloc[0].frac12_sem_lote10:.1f})")

# ============================================================ PARTE C
S("\n## PARTE C - marcadores administrativos")
d["cpf_ok"]=(d.cpf_resp_aluno.notna())&(d.cpf_resp_aluno>0)
d["sexo_ok"]=d.cd_sexo_aluno.isin(["F","M"])
d["cep_ok"]=d.renda.notna()          # cep casado ao setor censitario (renda existe)
d["raca_decl"]=d.tp_raca_cor.isin([1,2,3,4,5])   # 6/7 = nao declarada/sem info (assumido)
d["prio_ok"]=d.tipo_prioridade_encaminhamento.notna()
C=d[d.asol.between(2010,2018)].groupby("asol").agg(
    N=("cd_aluno_sme","size"),frac_cpf=("cpf_ok",lambda s:100*s.mean()),
    frac_sexo=("sexo_ok",lambda s:100*s.mean()),frac_cep=("cep_ok",lambda s:100*s.mean()),
    frac_raca_decl=("raca_decl",lambda s:100*s.mean()),frac_prio=("prio_ok",lambda s:100*s.mean())).reset_index()
w(C,"D15_C_marcadores.csv")
S("C1/C2: frac preenchido por ano (cpf, sexo, cep-casado, raca-declarada, prioridade):")
for _,r in C.iterrows(): S(f"    {int(r.asol)}: cpf={r.frac_cpf:>5.1f}  sexo={r.frac_sexo:>5.1f}  cep={r.frac_cep:>5.1f}  raca_decl={r.frac_raca_decl:>5.1f}  prio={r.frac_prio:>5.1f}")
# C3 prioridade por ano 2010-2012 (composicao)
c3=d[d.asol.between(2010,2012)].copy()
c3["prio_cat"]=c3.tipo_prioridade_encaminhamento.fillna(0).astype(int).astype(str)
C3=c3.groupby(["asol","prio_cat"]).size().unstack(fill_value=0)
C3p=(100*C3.div(C3.sum(1),axis=0)).round(2).reset_index()
w(C3p,"D15_C3_prioridade.csv")
S("C3: composicao de tipo_prioridade (%), 2010-2012 (0=nan/sem prioridade):")
S("    "+C3p.to_string(index=False).replace("\n","\n    "))
# C4 unidade de cadastro (cd_esc_solicitacao)
c4=d[d.asol.between(2010,2018)].copy()
u=c4.groupby("asol").agg(n_units=("cd_esc_solicitacao","nunique"),N=("cd_aluno_sme","size")).reset_index()
# dispersao da frac<12m entre unidades (por ano) - desvio-padrao ponderado grosseiro
disp=[]
for y in range(2010,2019):
    g=c4[c4.asol==y].groupby("cd_esc_solicitacao").agg(n=("cd_aluno_sme","size"),f=("idade_sol",lambda s:(s<12).mean()))
    g=g[g.n>=50]
    disp.append({"asol":y,"n_units_ge50":len(g),"frac12_p25":100*g.f.quantile(.25),"frac12_med":100*g.f.median(),"frac12_p75":100*g.f.quantile(.75)})
C4=u.merge(pd.DataFrame(disp),on="asol"); w(C4,"D15_C4_unidades.csv")
S("C4: cd_esc_solicitacao -- n unidades distintas e dispersao da frac<12m entre unidades (n>=50):")
for _,r in C4.iterrows(): S(f"    {int(r.asol)}: n_units={int(r.n_units):>5}  (n>=50:{int(r.n_units_ge50):>4})  frac<12m entre-unid p25/med/p75={r.frac12_p25:.0f}/{r.frac12_med:.0f}/{r.frac12_p75:.0f}")

# ============================================================ PARTE D
S("\n## PARTE D - a subida e uniforme no espaco?")
cr=pd.read_stata(CEPRENDA,columns=["cep","nm_distrit","renda","populacao"])
cr=cr.dropna(subset=["cep"]).drop_duplicates("cep")
cep2dist=dict(zip(cr.cep.astype("int64"),cr.nm_distrit.map(norm)))
d["dist"]=d.cep_aluno.astype("int64").map(cep2dist)
S(f"D: CEP->distrito casado em {100*d.dist.notna().mean():.1f}% das criancas.")
# frac<12m por coorte x distrito
dd=d[(d.ano_nasc.between(2010,2016))&(d.dist.notna())].copy()
piv=dd.assign(lt12=(dd.idade_sol<12)).groupby(["dist","ano_nasc"]).lt12.mean().mul(100).unstack()
piv=piv.dropna(subset=[2010,2011,2012])
piv["salto_10_12"]=piv[2012]-piv[2010]
w(piv.reset_index(),"D15_D1_distrito_coorte.csv")
S(f"D1: {len(piv)} distritos com dados 2010-2012. salto frac<12m 2010->2012 entre distritos:")
S(f"    distritos com salto>0: {(piv.salto_10_12>0).sum()}/{len(piv)} ({100*(piv.salto_10_12>0).mean():.0f}%). "
  f"salto: min={piv.salto_10_12.min():.1f}, p25={piv.salto_10_12.quantile(.25):.1f}, mediana={piv.salto_10_12.median():.1f}, p75={piv.salto_10_12.quantile(.75):.1f}, max={piv.salto_10_12.max():.1f}")
sm=piv.salto_10_12.sort_values()
S("D2: 5 menores saltos: "+", ".join(f"{i}={v:.0f}" for i,v in sm.head(5).items()))
S("D2: 5 maiores saltos: "+", ".join(f"{i}={v:.0f}" for i,v in sm.tail(5).items()))
# D3 correlacoes com renda, nCEIs 2013, capacidade 2013
pt=pd.read_csv(PERFIL); pt["dn"]=pt["distrito"].map(norm)
cap13=pt[(pt["ano"]==2013)&(pt["sem"]==1)].groupby("dn").agg(cap13=("vagofer","sum"),nceis13=("codesc","nunique"))
crn=cr.assign(dn=cr.nm_distrit.map(norm)).groupby("dn").apply(lambda g:np.average(g.renda,weights=g.populacao.fillna(1)) if g.populacao.sum()>0 else g.renda.mean()).rename("renda_dist")
D3=piv[["salto_10_12"]].join(cap13).join(crn)
w(D3.reset_index(),"D15_D3_correlacoes.csv")
cor=D3.corr(numeric_only=True)["salto_10_12"].drop("salto_10_12")
S("D3: correlacao (Pearson) do salto 2010->2012 do distrito com:")
for k,v in cor.items(): S(f"    {k}: r={v:.3f}")

# ---------------- resumo p/ markdown ----------------
with open(os.path.join(TAB,"_DIAG15_resumo.txt"),"w",encoding="utf-8") as f:
    f.write("\n".join(SUM))
print("\n== resumo salvo em tables/_DIAG15_resumo.txt ==")
print("OK build04_diag15 (Partes A-D)")
