# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD01 - figuras F1-F5 (pdf) + dados (csv). Descritivo.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":11,"figure.dpi":120,"axes.grid":True,"grid.alpha":.3})
STG=(NE_ROOT + r"\03_build\build01\_staging")
FIG=(NE_ROOT + r"\03_build\build01\figures")
os.makedirs(FIG,exist_ok=True)
def savedata(df,n): df.to_csv(os.path.join(FIG,n),index=False)

b=pd.read_feather(os.path.join(STG,"child_master.feather"))
YEARS=list(range(2010,2019))

# --- F1: idade entrada / idade solicitacao / espera media, por ano ---
d=pd.read_csv(os.path.join(STG,"T3_decomp.csv"))
fig,ax=plt.subplots(figsize=(7,4.3))
ax.plot(d["ano_sol"],d["idade_ent"],"-o",label="Idade media de entrada",color="#1f3b73")
ax.plot(d["ano_sol"],d["idade_sol"],"-s",label="Idade media na solicitacao",color="#c0392b")
ax.plot(d["ano_sol"],d["espera"],"-^",label="Espera media",color="#27ae60")
ax.set_xlabel("Ano da solicitacao"); ax.set_ylabel("Meses")
ax.set_title("Idade de entrada, idade na solicitacao e espera (criancas matriculadas)")
ax.legend(); ax.set_xticks(YEARS); fig.tight_layout()
fig.savefig(os.path.join(FIG,"F1_idade_decomposicao.pdf")); plt.close(fig)
savedata(d[["ano_sol","idade_ent","idade_sol","espera"]],"F1_data.csv")

# --- F2: capacidade autorizada total por agrupamento 2013-2019 ---
cap=pd.read_csv(os.path.join(STG,"T2a_capacidade.csv"))
semcols=[c for c in cap.columns if c not in ("agrup","rede")]
tot=cap.groupby("agrup")[semcols].sum().reset_index()
fig,ax=plt.subplots(figsize=(7.5,4.3))
x=np.arange(len(semcols))
for agr in ["Bercario I","Bercario II","Mini Grupo I","Mini Grupo II"]:
    row=tot[tot["agrup"]==agr]
    if len(row): ax.plot(x,row[semcols].values.flatten(),"-o",ms=3,label=agr)
ax.set_xticks(x); ax.set_xticklabels(semcols,rotation=45,ha="right",fontsize=8)
ax.set_ylabel("Vagas autorizadas (VAGOFER)"); ax.set_title("Capacidade autorizada por agrupamento")
ax.legend(); fig.tight_layout()
fig.savefig(os.path.join(FIG,"F2_capacidade_agrup.pdf")); plt.close(fig)
savedata(tot,"F2_data.csv")

# --- F3: % nunca atendido por quartil de renda e ano ---
sub=b[b["ano_sol"].isin(YEARS)&b["rq"].notna()]
piv=sub.groupby(["rq","ano_sol"])["nunca"].mean().mul(100).reset_index()
fig,ax=plt.subplots(figsize=(7,4.3))
for q in [1,2,3,4]:
    dd=piv[piv["rq"]==q]
    ax.plot(dd["ano_sol"],dd["nunca"],"-o",ms=4,label=f"Quartil renda {q}"+(" (mais baixa)" if q==1 else " (mais alta)" if q==4 else ""))
ax.set_xlabel("Ano da solicitacao"); ax.set_ylabel("% nunca matriculado")
ax.set_title("Percentual nunca matriculado por quartil de renda do CEP")
ax.legend(); ax.set_xticks(YEARS); fig.tight_layout()
fig.savefig(os.path.join(FIG,"F3_nunca_renda.pdf")); plt.close(fig)
savedata(piv.rename(columns={"nunca":"pct_nunca"}),"F3_data.csv")

# --- F4: histograma n de CEIs elegiveis (<=2km) ---
fig,ax=plt.subplots(figsize=(7,4.3))
vals=b["nelig"].clip(upper=120)
ax.hist(vals,bins=range(0,122,4),color="#34618e",edgecolor="white")
ax.axvline(b["nelig"].median(),color="#c0392b",ls="--",label=f"mediana = {int(b['nelig'].median())}")
ax.set_xlabel("N de CEIs a <=2km do CEP"); ax.set_ylabel("N de criancas")
ax.set_title("Distribuicao do tamanho do conjunto elegivel (CEIs <=2km)")
ax.legend(); fig.tight_layout()
fig.savefig(os.path.join(FIG,"F4_hist_nelig.pdf")); plt.close(fig)
savedata(b["nelig"].value_counts().sort_index().rename_axis("nelig").reset_index(name="n_criancas"),"F4_data.csv")

# --- F5: distribuicao do rank do CEI atribuido ---
r=pd.read_csv(os.path.join(STG,"T5a_rank.csv"))
fig,ax=plt.subplots(figsize=(7,4.3))
ax.bar(r["rank"],r["Total"],color="#7d5ba6",edgecolor="white")
ax.set_xlabel("Rank de distancia do CEI de matricula (1 = mais proximo)")
ax.set_ylabel("% das criancas matriculadas")
ax.set_title("Distribuicao do rank de distancia do CEI de matricula")
plt.xticks(rotation=20,ha="right",fontsize=8); fig.tight_layout()
fig.savefig(os.path.join(FIG,"F5_rank_distancia.pdf")); plt.close(fig)
savedata(r[["rank","Total"]],"F5_data.csv")
print("figuras OK:", os.listdir(FIG))
