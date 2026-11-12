# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# Item 3 (25/10/2026): de onde vem o "about a third of applications share their second" do REPLICATION_NOTES?
# Reproduz o universo da V14 (verificacao_final.py:331-339) e decompoe os empates de timestamp dentro da celula
# centro x faixa x ano letivo: mesma crianca (linhas repetidas) x criancas diferentes do mesmo responsavel (CPF)
# x criancas de responsaveis diferentes. Descritivo. Saida: 03_build/build13_coverage/ties_v14.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
NE_SME = _os_ne.environ.get("NE_DADOS_SME", _os_ne.path.normpath(_os_ne.path.join(NE_ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")))
import sys, os, pandas as pd, numpy as np, pyreadstat; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT
F = (NE_SME + r"\processados\derivados_de_brutos\Fila1018.dta")
cols = ["cd_aluno_sme", "dt_solicitacao", "dt_encaminhamento", "cd_esc_encaminhamento", "an_letivo_encaminhamento",
        "cd_serie_ensino_encaminhamento", "tipo_prioridade_encaminhamento", "cpf_resp_aluno"]
fa, _ = pyreadstat.read_dta(F, usecols=cols); print("linhas Fila1018:", f"{len(fa):,}", flush=True)
FMT = "%d/%m/%Y %H:%M:%S"
fa["sol"] = pd.to_datetime(fa.dt_solicitacao, format=FMT, errors="coerce"); fa["enc"] = pd.to_datetime(fa.dt_encaminhamento, format=FMT, errors="coerce")
fa = fa.drop(columns=["dt_solicitacao", "dt_encaminhamento"])
emp = lambda s: s.isna() | (s.astype(str).str.strip() == "")
r = fa[fa.enc.notna() & ~emp(fa.cd_esc_encaminhamento) & emp(fa.tipo_prioridade_encaminhamento)].copy()
r["serie"] = pd.to_numeric(r.cd_serie_ensino_encaminhamento, errors="coerce"); r = r[r.serie.isin([1, 4, 27, 28])]
r["cell"] = r.cd_esc_encaminhamento.astype(str) + "|" + r.serie.astype(int).astype(str) + "|" + r.an_letivo_encaminhamento.astype(str)
r["ncell"] = r.groupby("cell").cell.transform("size"); big = r[r.ncell >= 5].copy()
print("universo V14 (linhas de encaminhamento nao prioritario, celulas >=5):", f"{len(big):,}", "(REPLICATION_NOTES: 1,884,018)", flush=True)
g = big.groupby(["cell", "sol"])
big["n_tie"] = g.sol.transform("size"); big["n_kids"] = g.cd_aluno_sme.transform("nunique")
big["cpf"] = big.cpf_resp_aluno.astype(str).str.strip().replace({"": np.nan, "nan": np.nan})
big["n_cpf"] = g.cpf.transform("nunique")
tied = big.n_tie >= 2
res = {"linhas_universo": len(big), "share_linhas_empatadas": tied.mean(),
       "empate_so_mesma_crianca": (tied & (big.n_kids == 1)).mean(),
       "empate_criancas_diferentes": (tied & (big.n_kids >= 2)).mean()}
dk = big[tied & (big.n_kids >= 2)]
res["dif_criancas_mesmo_cpf_unico"] = ((dk.n_cpf == 1) & (dk.n_kids >= 2)).sum() / len(big)
res["dif_criancas_cpfs_diferentes"] = (dk.n_cpf >= 2).sum() / len(big)
# tamanho dos grupos com criancas diferentes
grp = dk.groupby(["cell", "sol"]).agg(k=("cd_aluno_sme", "nunique"), c=("cpf", "nunique")).reset_index()
res["grupos_criancas_dif"] = len(grp); res["grupo_mediana_criancas"] = grp.k.median(); res["grupo_p99_criancas"] = grp.k.quantile(.99)
res["grupos_com_>=10_criancas"] = int((grp.k >= 10).sum())
# para contraste: primeiras solicitacoes (uma por crianca) com segundo compartilhado na cidade
first = fa[fa.sol.notna()].sort_values("sol").groupby("cd_aluno_sme").sol.first()
res["primeiras_solic"] = len(first); res["share_primeiras_segundo_compartilhado"] = (first.map(first.value_counts()) >= 2).mean()
# linhas repetidas por crianca no universo inteiro
res["linhas_por_crianca_fila"] = len(fa) / fa.cd_aluno_sme.nunique()
o = pd.Series(res); print(o.to_string())
o.to_csv(os.path.join(ROOT, r"03_build\build13_coverage\ties_v14.csv"), header=["valor"])
