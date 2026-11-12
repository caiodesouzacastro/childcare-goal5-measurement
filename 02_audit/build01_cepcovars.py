# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD01 - covariaveis por CEP: renda (censo 2010) e grupo IPVS 2010.
# renda: cep_renda_pop_2010.dta (V005 do Basico do censo, ja unido a CEP por setor).
# IPVS : BaseIPVS2010.csv (v7=setor censitario 15 dig, v10=grupo IPVS 1-7),
#        unido ao CEP pelo cod_setor presente em cep_renda_pop_2010.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os

BA  = NE_ROOT + r"\dados_restritos\Ciro\01_dados\processados\bases_analise"
IPV = NE_ROOT + r"\dados_restritos\Ciro\_arquivo_antigo\Dados - SME - antigo\IPVS\BaseIPVS2010.csv"
OUT = (NE_ROOT + r"\03_build\build01\_staging\cep_covars.csv")

# --- renda por CEP ---
ren = pd.read_stata(os.path.join(BA,"cep_renda_pop_2010.dta"), columns=["cep","renda","populacao","cod_setor"])
ren = ren.dropna(subset=["cep"])
ren["cep"] = ren["cep"].astype("int64")
ren["cod_setor"] = pd.to_numeric(ren["cod_setor"], errors="coerce")
ren = ren.dropna(subset=["cod_setor"])
ren["cod_setor"] = ren["cod_setor"].astype("int64")
ren = ren.drop_duplicates(subset=["cep"])
print("CEPs com renda:", len(ren), " renda mediana:", round(ren["renda"].median(),2))

# --- IPVS por setor censitario (municipio SP = 3550308) ---
ipvs = pd.read_csv(IPV, sep=";", encoding="latin-1", usecols=["v1","v7","v10"], dtype=str)
ipvs = ipvs[ipvs["v1"]=="3550308"].copy()
ipvs["setor"] = pd.to_numeric(ipvs["v7"], errors="coerce")
ipvs["ipvs_grupo"] = pd.to_numeric(ipvs["v10"], errors="coerce")
ipvs = ipvs.dropna(subset=["setor","ipvs_grupo"])
ipvs["setor"] = ipvs["setor"].astype("int64")
ipvs["ipvs_grupo"] = ipvs["ipvs_grupo"].astype(int)
ipvs = ipvs.drop_duplicates(subset=["setor"])[["setor","ipvs_grupo"]]
print("setores SP no IPVS:", len(ipvs), " grupos:", sorted(ipvs["ipvs_grupo"].unique()))

# --- merge setor -> ipvs no arquivo de CEP ---
m = ren.merge(ipvs, left_on="cod_setor", right_on="setor", how="left")
match = m["ipvs_grupo"].notna().mean()
print(f"CEPs com IPVS casado por setor: {m['ipvs_grupo'].notna().sum()} ({match:.1%})")

out = m[["cep","renda","ipvs_grupo"]].copy()
out.to_csv(OUT, index=False)
print("cep_covars.csv escrito:", len(out), "->", OUT)
