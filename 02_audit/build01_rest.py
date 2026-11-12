# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD01 - T6a (turmas_modulo), T7b (aberturas/fechamentos), T7c (capacidade
# per capita por setor), T8a (trajetoria). Capacidade = MODULO/VAGOFER/cap_berc.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os, csv, collections, datetime as dt
AUD=(NE_ROOT + r"\02_audit")
SRC=(NE_ROOT + r"\01_dados_publicos")
STG=(NE_ROOT + r"\03_build\build01\_staging")
def w(df,n): df.to_csv(os.path.join(STG,n),index=False); print("escrita",n)

AGR={"BERCARIO I":"Bercario I","BERCARIO II":"Bercario II","MINI GRUPO I":"Mini Grupo I","MINI GRUPO II":"Mini Grupo II"}
# ============ T6a: turmas_modulo (MODULO=capacidade autorizada) ============
tm=pd.read_csv(os.path.join(SRC,"turmas_modulo_2016_2017.csv"),sep=";",encoding="latin-1")
tm.columns=[c.strip().upper() for c in tm.columns]
tm=tm[tm["MODALIDADE"].str.strip().str.upper()=="CRECHE"].copy()
tm["agr"]=tm["SERIE"].str.strip().str.upper().map(AGR)
tm=tm.dropna(subset=["agr"])
tm["MODULO"]=pd.to_numeric(tm["MODULO"],errors="coerce")
tm["MATRICULA"]=pd.to_numeric(tm["MATRICULA"],errors="coerce")
tm["ano"]=pd.to_datetime(tm["DATA BASE"],errors="coerce",dayfirst=True).dt.year
tm=tm.dropna(subset=["MODULO","MATRICULA","ano"])
tm=tm[tm["MODULO"]>0]
rows=[]
for (ano,agr),d in tm.groupby(["ano","agr"]):
    rows.append({"ano":int(ano),"agrup":agr,"n_turmas":len(d),
      "MODULO_modal":int(d["MODULO"].mode().iloc[0]),
      "matricula_media":round(d["MATRICULA"].mean(),1),
      "pct_na_capacidade":round(100*(d["MATRICULA"]==d["MODULO"]).mean(),1),
      "pct_acima":round(100*(d["MATRICULA"]>d["MODULO"]).mean(),1),
      "pct_abaixo":round(100*(d["MATRICULA"]<d["MODULO"]).mean(),1)})
ORD={"Bercario I":0,"Bercario II":1,"Mini Grupo I":2,"Mini Grupo II":3}
T6a=pd.DataFrame(rows).sort_values(["ano","agrup"],key=lambda s:s.map(ORD) if s.name=="agrup" else s)
w(T6a,"T6a_modulo.csv")

# ============ T7b: aberturas e fechamentos conveniadas (eventos_conv, DIAG11) ============
# eventos_conv.csv (derivado no DIAG11): tipo ABERTURA/FECHAMENTO, data, vagas.
# Todos sao do setor conveniado/parceiro (parcerias). Fechamentos = encerramentos
# com perda de vagas registrada.
ev=pd.read_csv(os.path.join(AUD,"eventos_conv.csv"))
ev["ano"]=pd.to_datetime(ev["data"],format="mixed",dayfirst=True,errors="coerce").dt.year
ab=ev[ev["tipo"]=="ABERTURA"].groupby("ano").agg(aberturas=("codesc","size"),vagas_abertas=("vagas","sum")).reset_index()
fe=ev[ev["tipo"]=="FECHAMENTO"].groupby("ano").agg(fechamentos=("codesc","size"),vagas_fechadas=("vagas","sum")).reset_index()
T7b=pd.DataFrame({"ano":list(range(2013,2020))}).merge(ab,on="ano",how="left").merge(fe,on="ano",how="left").fillna(0)
for c in ["aberturas","vagas_abertas","fechamentos","vagas_fechadas"]:
    T7b[c]=T7b[c].astype(int)
T7b["saldo_vagas"]=T7b["vagas_abertas"]-T7b["vagas_fechadas"]
w(T7b,"T7b_aber_fech.csv")

# ============ T7c: capacidade Bercario per capita por setor ============
esc=pd.read_csv(os.path.join(AUD,"esc_sem_cap.csv"))  # codesc,sidx,cap_creche,cap_berc,setor,distrito,rede
esc["ano"]=(esc["sidx"]//2).astype(int); esc["sem"]=(esc["sidx"]%2+1).astype(int)
capset=esc[esc["sem"]==1].groupby(["setor","ano"])["cap_berc"].sum().reset_index()
# solicitacoes por setor-ano (child_master + cep_setor)
b=pd.read_feather(os.path.join(STG,"child_master.feather"))
cs=pd.read_stata(os.path.join(AUD,"cep_setor.dta"),columns=["cep","setor_cep"])
cs=cs.drop_duplicates("cep")
b=b.merge(cs,left_on="cep_aluno",right_on="cep",how="left")
solset=b[b["ano_sol"].between(2013,2019)].groupby(["setor_cep","ano_sol"]).size().reset_index(name="n_solic")
solset=solset.rename(columns={"setor_cep":"setor","ano_sol":"ano"})
# renda media por setor (child-weighted)
rendaset=b.groupby("setor_cep")["renda"].mean().reset_index().rename(columns={"setor_cep":"setor","renda":"renda_setor"})
pc=capset.merge(solset,on=["setor","ano"],how="inner")
pc["percap"]=pc["cap_berc"]/pc["n_solic"]
pc=pc.merge(rendaset,on="setor",how="left")
# quartil de renda do setor
setor_q=rendaset.dropna(subset=["renda_setor"]).copy()
setor_q["rqs"]=pd.qcut(setor_q["renda_setor"],4,labels=[1,2,3,4])
pc=pc.merge(setor_q[["setor","rqs"]],on="setor",how="left")
# evolucao da mediana de percap por quartil de renda do setor e ano
t7c=pc.dropna(subset=["rqs"]).groupby(["rqs","ano"])["percap"].median().reset_index()
w(t7c,"T7c_percap.csv")
# distribuicao geral por ano (p25,p50,p75)
t7c_d=pc.groupby("ano")["percap"].agg(p25=lambda s:s.quantile(.25),p50="median",p75=lambda s:s.quantile(.75)).reset_index()
w(t7c_d,"T7c_percap_dist.csv")

# ============ T8a: trajetoria (coortes 2008-2012) ============
tr=pd.read_stata(os.path.join(AUD,"traj_child.dta"))
tr=tr.merge(b[["cd_aluno_sme","rq"]],on="cd_aluno_sme",how="left")
tr=tr[tr["ano_nasc_aluno"].between(2008,2012)]
def trstats(d):
    obs=d[d["tem1ano"]==1]
    return pd.Series({"N":len(d),
        "pct_1ano_obs":100*d["tem1ano"].mean(),
        "pct_ontime":100*obs["ontime"].mean() if len(obs) else np.nan,
        "pct_reprov":100*obs["ever_reprov"].mean() if len(obs) else np.nan})
t8=tr[tr["rq"].notna()].groupby("rq").apply(trstats).reset_index()
w(t8,"T8a_traj.csv")
t8all=trstats(tr).to_frame().T; t8all.insert(0,"rq","Todos")
w(t8all,"T8a_traj_total.csv")
print("OK build01_rest")
