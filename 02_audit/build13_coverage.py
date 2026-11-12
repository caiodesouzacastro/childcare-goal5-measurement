# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# EXT-1: matriculas em creche no municipio de Sao Paulo (3550308), Censo Escolar INEP (microdados_ed_basica, nivel escola).
# Saida: 03_build/build13_coverage/creche_mat_sp.csv  (uma linha por ano x rede)
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
NE_SME = _os_ne.environ.get("NE_DADOS_SME", _os_ne.path.normpath(_os_ne.path.join(NE_ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")))
import sys, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
D=(NE_SME + "/originais/auxiliares_publicos/censo_escolar_inep/")
OUT=(NE_ROOT + "/03_build/build13_coverage/")
COLS=["NU_ANO_CENSO","CO_MUNICIPIO","CO_ENTIDADE","TP_DEPENDENCIA","TP_SITUACAO_FUNCIONAMENTO","IN_CONVENIADA_PP",
      "TP_CONVENIO_PODER_PUBLICO","QT_MAT_INF_CRE","QT_MAT_INF_PRE","QT_MAT_BAS_0_3","QT_MAT_INF"]
def rede(r):
    if r.TP_DEPENDENCIA==3: return "municipal_direta"
    if r.TP_DEPENDENCIA==4 and r.IN_CONVENIADA_PP==1 and r.TP_CONVENIO_PODER_PUBLICO in (1,3): return "privada_conveniada_municipal"
    if r.TP_DEPENDENCIA==4 and r.IN_CONVENIADA_PP==1: return "privada_conveniada_estadual"
    if r.TP_DEPENDENCIA==4: return "privada_nao_conveniada"
    return {1:"federal",2:"estadual"}.get(r.TP_DEPENDENCIA,"outra")
rows=[]
for y in range(int(sys.argv[1]) if len(sys.argv)>1 else 2010, (int(sys.argv[2]) if len(sys.argv)>2 else 2018)+1):
    parts=[]
    for ch in pd.read_csv(D+f"microdados_ed_basica_{y}.csv",sep=";",encoding="latin-1",usecols=COLS,chunksize=100000,low_memory=False):
        parts.append(ch[ch.CO_MUNICIPIO==3550308])
    d=pd.concat(parts)
    for c in COLS[3:]: d[c]=pd.to_numeric(d[c],errors="coerce")
    d["rede"]=d.apply(rede,axis=1)
    g=d.groupby("rede")[["QT_MAT_INF_CRE","QT_MAT_INF_PRE","QT_MAT_BAS_0_3"]].sum(min_count=1).reset_index()
    g["n_escolas_com_creche"]=d[d.QT_MAT_INF_CRE>0].groupby("rede").CO_ENTIDADE.nunique().reindex(g.rede).values
    g.insert(0,"ano",y); rows.append(g)
    print(y, len(d), "escolas;", "creche total", int(d.QT_MAT_INF_CRE.sum()), "| 0-3 total", int(d.QT_MAT_BAS_0_3.sum()),
          "| conveniada sem TP_CONVENIO:", int(((d.TP_DEPENDENCIA==4)&(d.IN_CONVENIADA_PP==1)&d.TP_CONVENIO_PODER_PUBLICO.isna()).sum()), flush=True)
out=pd.concat(rows); out.to_csv(OUT+"creche_mat_sp.csv",index=False); print(out.to_string())
