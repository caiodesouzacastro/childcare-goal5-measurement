# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD01 - tabelas descritivas da fila no nivel da crianca (T1, T3, T4, T5).
# Spine = B_novo (universo 1.524.560, 1a solicitacao por crianca).
# Extras de Fila1018 (agregados por crianca): sexo, raca, prioridade, serie
# solicitada, escola de matricula. Covariaveis por CEP: renda (censo), IPVS,
# n de CEIs <=2km, rank/distancia do CEI de matricula.
# NENHUMA variavel de capacidade aqui; "espera" = dt_mat_first - dt_sol (dias).
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os

AUD = (NE_ROOT + r"\02_audit")
STG = (NE_ROOT + r"\03_build\build01\_staging")
FILA= NE_ROOT + r"\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
EP  = pd.Timestamp("1960-01-01")
os.makedirs(STG, exist_ok=True)

def dparse(s):
    return pd.to_datetime(s, format="%d/%m/%Y %H:%M:%S", errors="coerce")

SERIE_MAP = {1:"BERC1",2:"BERC1",3:"BERC1",4:"BERC2",5:"BERC2",6:"BERC2",
             11:"MINI1",27:"MINI1",28:"MINI2",29:"MINI2"}  # 23-26 = Infantil (pre)

# ---------- 1) agregacao por crianca de Fila1018 ----------
print("lendo Fila1018 (3,3M linhas)...")
usecols=["cd_aluno_sme","dt_solicitacao","dt_matricula","cd_esc_matricula",
         "cd_sexo_aluno","tp_raca_cor","tipo_prioridade_encaminhamento","cd_serie_ensino_solicitacao"]
first_rows=[]; mat_rows=[]
for ch in pd.read_stata(FILA, columns=usecols, chunksize=300000):
    ch["dsol"]=dparse(ch["dt_solicitacao"])
    ch["dmat"]=dparse(ch["dt_matricula"])
    # candidatas a 1a solicitacao
    f=ch.dropna(subset=["dsol"])[["cd_aluno_sme","dsol","cd_sexo_aluno","tp_raca_cor",
        "tipo_prioridade_encaminhamento","cd_serie_ensino_solicitacao"]].copy()
    first_rows.append(f)
    # candidatas a matricula (escola onde matriculou)
    m=ch.dropna(subset=["dmat"])[["cd_aluno_sme","dmat","cd_esc_matricula"]].copy()
    mat_rows.append(m)
F=pd.concat(first_rows,ignore_index=True)
M=pd.concat(mat_rows,ignore_index=True)
del first_rows,mat_rows
# 1a solicitacao por crianca
F=F.sort_values(["cd_aluno_sme","dsol"]).groupby("cd_aluno_sme",as_index=False).first()
# 1a matricula por crianca -> escola atribuida
M=M.sort_values(["cd_aluno_sme","dmat"]).groupby("cd_aluno_sme",as_index=False).first()
F["agrup_sol"]=F["cd_serie_ensino_solicitacao"].map(SERIE_MAP)
print("criancas c/ 1a solicitacao:",len(F)," c/ matricula:",len(M))

# ---------- 2) spine B_novo ----------
b=pd.read_stata(os.path.join(AUD,"B_novo.dta"),
    columns=["cd_aluno_sme","cep_aluno","ano_nasc","mes_nasc","dt_sol","ano_sol","dt_mat_first","ever_mat"])
b=b.merge(F[["cd_aluno_sme","cd_sexo_aluno","tp_raca_cor","tipo_prioridade_encaminhamento","agrup_sol"]],
          on="cd_aluno_sme",how="left")
b=b.merge(M[["cd_aluno_sme","cd_esc_matricula"]],on="cd_aluno_sme",how="left")

# datas e idades
b["d_sol"]=EP+pd.to_timedelta(b["dt_sol"],unit="D")
b["d_mat"]=EP+pd.to_timedelta(b["dt_mat_first"],unit="D")
b["idade_sol"]=(b["d_sol"].dt.year-b["ano_nasc"])*12+(b["d_sol"].dt.month-b["mes_nasc"])
b["idade_ent"]=(b["d_mat"].dt.year-b["ano_nasc"])*12+(b["d_mat"].dt.month-b["mes_nasc"])
b["espera_d"]=b["dt_mat_first"]-b["dt_sol"]
b["espera_m"]=b["espera_d"]/30.44
b["mat180"]=((b["ever_mat"]==1)&(b["espera_d"]<=180)).astype(int)
b["mat365"]=((b["ever_mat"]==1)&(b["espera_d"]<=365)).astype(int)
b["nunca"]=(b["ever_mat"]==0).astype(int)
b["fem"]=(b["cd_sexo_aluno"]=="F").astype(int)
b["prio"]=(b["tipo_prioridade_encaminhamento"].notna()).astype(int)
# raca: 1 Branca,2 Preta,3 Parda,4 Amarela,5 Indigena,6 Nao decl,7 Nao informado
RACA={1:"Branca",2:"Preta",3:"Parda",4:"Amarela",5:"Indigena"}
b["raca"]=b["tp_raca_cor"].map(RACA).fillna("Outra/ND")
b["negra"]=b["tp_raca_cor"].isin([2,3]).astype(int)   # preta+parda

# ---------- 3) covariaveis por CEP ----------
cov=pd.read_csv(os.path.join(STG,"cep_covars.csv"))  # cep,renda,ipvs_grupo
b=b.merge(cov,left_on="cep_aluno",right_on="cep",how="left")

pairs=pd.read_stata(os.path.join(AUD,"cep_cei_pairs_novo.dta"),columns=["cep","ceicode","dist_km"])
# rank de distancia por cep
pairs=pairs.sort_values(["cep","dist_km"])
pairs["rank"]=pairs.groupby("cep").cumcount()+1
# n de CEIs <=2km por cep
nelig=pairs[pairs["dist_km"]<=2.0].groupby("cep").size().rename("nelig").reset_index()
# distancia ao mais proximo
nearest=pairs[pairs["rank"]==1][["cep","dist_km"]].rename(columns={"dist_km":"dist_nearest"})
b=b.merge(nelig,left_on="cep_aluno",right_on="cep",how="left",suffixes=("","_n"))
b=b.merge(nearest,left_on="cep_aluno",right_on="cep",how="left",suffixes=("","_nn"))
b["nelig"]=b["nelig"].fillna(0).astype(int)
# rank/dist do CEI de matricula (atribuido)
pr=pairs[["cep","ceicode","dist_km","rank"]].rename(columns={"dist_km":"dist_assigned","rank":"rank_assigned"})
b=b.merge(pr,left_on=["cep_aluno","cd_esc_matricula"],right_on=["cep","ceicode"],how="left",suffixes=("","_a"))

# quartis (ponderados pela crianca) de renda e decis de nelig; grupos IPVS
b["rq"]=pd.qcut(b["renda"],4,labels=[1,2,3,4]) if b["renda"].notna().any() else np.nan
b["nelig_dec"]=pd.qcut(b["nelig"].where(b["nelig"]>0),10,labels=range(1,11),duplicates="drop")
b["ipvs_q"]=pd.qcut(b["ipvs_grupo"].where(b["ipvs_grupo"].between(1,7)),4,labels=[1,2,3,4],duplicates="drop")

b.to_feather(os.path.join(STG,"child_master.feather"))
print("master salvo. N=",len(b)," ever_mat=1:",int(b['ever_mat'].sum()),
      " renda casada:",round(b['renda'].notna().mean(),3)," rank_assigned casado:",round(b['rank_assigned'].notna().mean(),3))
print("=== ano_sol 2010-2018 total:", int(b['ano_sol'].between(2010,2018).sum()))
