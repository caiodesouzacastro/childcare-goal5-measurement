# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# COBERTURA_FILA (25/10/2026), item 5: o arquivo de 2011 da Fila1018 e estoque ou fluxo?
# Descritivo. Saida: 03_build/build14_cobertura/f2011_*.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
NE_SME = _os_ne.environ.get("NE_DADOS_SME", _os_ne.path.normpath(_os_ne.path.join(NE_ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")))
import sys, os, numpy as np, pandas as pd, pyreadstat; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; OUT = os.path.join(ROOT, r"03_build\build14_cobertura")
F = (NE_SME + r"\processados\derivados_de_brutos\Fila1018.dta")
fa, _ = pyreadstat.read_dta(F, usecols=["cd_aluno_sme", "ano", "dt_solicitacao", "dt_encaminhamento", "dt_matricula"])
FMT = "%d/%m/%Y %H:%M:%S"
for c, n in (("dt_solicitacao", "sol"), ("dt_encaminhamento", "enc"), ("dt_matricula", "mat")): fa[n] = pd.to_datetime(fa[c], format=FMT, errors="coerce")
fa["ano"] = pd.to_numeric(fa.ano, errors="coerce").astype(int)
# 1) por arquivo: ano da solicitacao e do encaminhamento relativos ao ano do arquivo
r = []
for y, g in fa.groupby("ano"):
    d = (g.enc - g.sol).dt.days
    r.append(dict(arquivo=y, linhas=len(g), pct_sol_no_ano=100 * (g.sol.dt.year == y).mean(), pct_sol_antes=100 * (g.sol.dt.year < y).mean(),
                  pct_enc_no_ano=100 * (g.enc.dt.year == y).mean(), pct_enc_ano_seguinte=100 * (g.enc.dt.year == y + 1).mean(),
                  pct_enc_2_ou_mais=100 * (g.enc.dt.year >= y + 2).mean(), pct_sem_enc=100 * g.enc.isna().mean(),
                  enc_max=str(g.enc.max().date()) if g.enc.notna().any() else "", mediana_dias_sol_enc=d.median(),
                  pct_mais_365=100 * (d > 365).mean() / d.notna().mean() if d.notna().any() else np.nan))
A = pd.DataFrame(r); A.to_csv(os.path.join(OUT, "f2011_por_arquivo.csv"), index=False)
pd.set_option("display.width", 250); print(A.round(1).to_string(index=False))
# 2) solicitacoes feitas em 2011: em quais arquivos aparecem
s11 = fa[fa.sol.dt.year == 2011]
inf = s11.groupby("cd_aluno_sme").ano.agg(lambda x: "+".join(str(v) for v in sorted(set(x)))).value_counts().head(8)
print("\ncriancas com solicitacao datada de 2011, por conjunto de arquivos em que aparecem:"); print(inf.to_string())
# 3) universo do paper: 1as solicitacoes por mes (2010-2013) e mes do 1o encaminhamento de quem solicitou em 2011
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"), columns=["d_sol1", "d_enc1", "d_age47"])
m = sp[sp.d_sol1.dt.year.between(2010, 2013)]
mm = m.groupby(m.d_sol1.dt.to_period("M")).agg(N=("d_sol1", "size"), med_dias=("d_enc1", lambda x: ((x - m.loc[x.index, "d_sol1"]).dt.days).median()),
                                              pct_enc_30d=("d_enc1", lambda x: 100 * (((x - m.loc[x.index, "d_sol1"]).dt.days.between(0, 30))).mean()))
mm.to_csv(os.path.join(OUT, "f2011_mensal_paper.csv")); print("\n1as solicitacoes do paper por mes (N, mediana de dias ate o 1o encaminhamento, % encaminhado em 30 dias):"); print(mm.round(1).to_string())
s = sp[sp.d_sol1.dt.year == 2011]
em = s.d_enc1.dt.to_period("M").value_counts(normalize=True).sort_index()
print("\nquem fez a 1a solicitacao em 2011: mes do 1o encaminhamento (% dos solicitantes; meses com >=2%):"); print((100 * em[em >= 0.02]).round(1).to_string())
print("sem encaminhamento:", f"{100 * s.d_enc1.isna().mean():.1f}%")
