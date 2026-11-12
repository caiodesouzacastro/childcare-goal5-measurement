# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD10 spine - uma passada no Fila1018: por crianca, primeiras datas de
# solicitacao/encaminhamento/matricula/desistencia/recusa + cpf + serie.
# Merge com covariaveis do child_master. Salva _staging/spine.parquet.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
ROOT=NE_ROOT
FILA=NE_ROOT + r"\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
CM=os.path.join(ROOT,r"03_build\build01\_staging\child_master.feather")
STG=os.path.join(ROOT,r"03_build\build10\_staging"); os.makedirs(STG,exist_ok=True)

print("carregando Fila1018 (datas + cpf + serie)...")
fa=pd.read_stata(FILA,columns=["cd_aluno_sme","dt_solicitacao","dt_encaminhamento",
    "dt_matricula","dt_desistencia","dt_recusa","cd_serie_ensino_solicitacao",
    "cpf_resp_aluno"])
print(f"  {len(fa):,} linhas.")
FMT="%d/%m/%Y %H:%M:%S"
for c,n in [("dt_solicitacao","sol"),("dt_encaminhamento","enc"),
            ("dt_matricula","mat"),("dt_desistencia","des"),("dt_recusa","rec")]:
    fa[n]=pd.to_datetime(fa[c],format=FMT,errors="coerce")

g=fa.groupby("cd_aluno_sme")
def firstmin(col): return g[col].min()
sp=pd.DataFrame({
    "d_sol1":firstmin("sol"),
    "d_enc1":firstmin("enc"),
    "d_mat1":firstmin("mat"),
    "d_des1":firstmin("des"),
    "d_rec1":firstmin("rec"),
}).reset_index()
# serie da 1a solicitacao (na linha de menor dt_solicitacao)
idx=fa.sort_values("sol").groupby("cd_aluno_sme").head(1)[["cd_aluno_sme","cd_serie_ensino_solicitacao","cpf_resp_aluno"]]
idx=idx.rename(columns={"cd_serie_ensino_solicitacao":"serie_sol1","cpf_resp_aluno":"cpf"})
sp=sp.merge(idx,on="cd_aluno_sme",how="left")
# houve encaminhamento APOS a 1a recusa? (para C4)
enc=fa[fa["enc"].notna()][["cd_aluno_sme","enc"]]
rec1=sp[["cd_aluno_sme","d_rec1"]].dropna()
m=enc.merge(rec1,on="cd_aluno_sme")
reenc=m[m["enc"]>m["d_rec1"]].groupby("cd_aluno_sme").size().rename("n_enc_after_rec")
sp=sp.merge(reenc,on="cd_aluno_sme",how="left")
sp["n_enc_after_rec"]=sp["n_enc_after_rec"].fillna(0).astype(int)

# --- covariaveis do child_master (universo do paper) ---
cm=pd.read_feather(CM,columns=["cd_aluno_sme","ano_nasc","mes_nasc","idade_sol",
    "ano_sol","cep_aluno","nelig","negra","fem","prio","renda","rq","ipvs_q",
    "agrup_sol","cd_esc_matricula","dt_mat_first","ever_mat"])
sp=cm.merge(sp,on="cd_aluno_sme",how="left")   # restringe ao universo do paper
print(f"  spine (universo paper) = {len(sp):,} criancas.")

# data de nascimento (dia 1) e data dos 47 meses (fim de elegibilidade creche)
sp["d_birth"]=pd.to_datetime(dict(year=sp.ano_nasc,month=sp.mes_nasc,day=1),errors="coerce")
sp["d_age47"]=sp["d_birth"]+pd.DateOffset(months=47)
print("  d_enc1 non-null:", sp.d_enc1.notna().sum(),
      "| d_mat1:", sp.d_mat1.notna().sum(),
      "| d_des1:", sp.d_des1.notna().sum(),
      "| d_rec1:", sp.d_rec1.notna().sum())
sp.to_parquet(os.path.join(STG,"spine.parquet"))
print("OK spine.parquet")
