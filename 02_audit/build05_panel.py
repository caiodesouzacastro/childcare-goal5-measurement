# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD05 - painel de irmaos (aprendizado sobre a fila na familia). Construcao do painel.
# Descritivo. Nao modifica build01/02/03/04. Reaproveita child_master + Fila1018 (cpf_resp).
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os, unicodedata, re
ROOT=NE_ROOT
FILA=NE_ROOT + r"\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
CM=os.path.join(ROOT,r"03_build\build01\_staging\child_master.feather")
CEPRENDA=NE_ROOT + r"\dados_restritos\Ciro\01_dados\processados\bases_analise\cep_renda_pop_2010.dta"
OUT=os.path.join(ROOT,r"03_build\build05"); os.makedirs(OUT,exist_ok=True)
def fixhex(s): return re.sub(r'<([0-9a-fA-F]{2})>', lambda m: bytes([int(m.group(1),16)]).decode('latin-1'), str(s))
def norm(s):
    s=fixhex(s); return "".join(c for c in unicodedata.normalize("NFD",str(s).strip().upper()) if unicodedata.category(c)!="Mn")

print("carregando Fila1018 (raw)...")
fa=pd.read_stata(FILA)
for c,fmt in [("dt_solicitacao","sol"),("dt_encaminhamento","enc"),("dt_matricula","mat")]:
    fa["d_"+fmt]=pd.to_datetime(fa[c],format="%d/%m/%Y %H:%M:%S",errors="coerce")
# por crianca: 1a solicitacao, 1o encaminhamento, 1a matricula (com escolas)
def first_by(df,dcol,cols):
    s=df[df[dcol].notna()].sort_values(dcol).groupby("cd_aluno_sme").first()
    return s[cols]
sol=fa.sort_values("d_sol").groupby("cd_aluno_sme").agg(
    cpf=("cpf_resp_aluno","first"),d_sol1=("d_sol","min"),
    esc_sol1=("cd_esc_solicitacao","first")).reset_index()
enc=first_by(fa,"d_enc",["d_enc","cd_esc_encaminhamento"]).rename(columns={"d_enc":"d_enc1","cd_esc_encaminhamento":"esc_enc1"}).reset_index()
mat=first_by(fa,"d_mat",["d_mat","cd_esc_matricula"]).rename(columns={"d_mat":"d_mat1","cd_esc_matricula":"esc_mat1"}).reset_index()
p=sol.merge(enc,on="cd_aluno_sme",how="left").merge(mat,on="cd_aluno_sme",how="left")
print("criancas na fila:",len(p))

cm=pd.read_feather(CM,columns=["cd_aluno_sme","ano_nasc","mes_nasc","idade_sol","ever_mat","nunca",
    "renda","tipo_prioridade_encaminhamento","cep_aluno","cd_esc_matricula"])
d=cm.merge(p,on="cd_aluno_sme",how="inner")
d["espera_enc"]=(d.d_enc1-d.d_sol1).dt.days      # sol -> 1o encaminhamento (dias); nan se nunca encaminhado
d["referido"]=d.d_enc1.notna().astype(int)
d["nasc_idx"]=d.ano_nasc*12+d.mes_nasc           # indice mensal de nascimento
# distrito
cr=pd.read_stata(CEPRENDA,columns=["cep","nm_distrit"]).dropna(subset=["cep"]).drop_duplicates("cep")
c2d=dict(zip(cr.cep.astype("int64"),cr.nm_distrit.map(norm)))
d["distrito"]=d.cep_aluno.astype("int64").map(c2d)
# cpf valido
d["cpf_ok"]=(d.cpf.notna())&(d.cpf>0)
d.to_parquet(os.path.join(OUT,"_panel_criancas.parquet"))
print("painel salvo:",len(d),"criancas |",d.cpf_ok.mean().round(4),"com cpf valido")
print("espera_enc (dias) mediana:",d.espera_enc.median(),"| referido frac:",d.referido.mean().round(3))
