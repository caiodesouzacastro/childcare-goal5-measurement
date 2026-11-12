# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# Etapa 2.4 (26/10/2026): rastreio de tres numeros do paragrafo de sec3_coverage.tex (l. 87-90) que so constavam de
# COBERTURA_FILA.md §5, sem script salvo. Descritivo; nao escreve em 04_paper.
# Resultado em 26/10: 37,1% e a parcela entre os ENCAMINHADOS (sobre todos os solicitantes de 2011: 34,1%);
# 32.537 (fev./2013) e 5.371 (fev./2012) reproduzidos exatamente.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
R = (NE_ROOT + r"\03_build")
sp = pd.read_parquet(R + r"\build10\_staging\spine.parquet", columns=["cd_aluno_sme", "d_sol1", "d_enc1"])
s = sp[pd.to_datetime(sp.d_sol1).dt.year == 2011]; e = pd.to_datetime(s.d_enc1); dez12 = (e.dt.year == 2012) & (e.dt.month == 12)
print(f"solicitantes 2011: {len(s):,}; 1o encaminhamento em dez/2012: {100*dez12.mean():.1f}% de todos, {100*dez12.sum()/e.notna().sum():.1f}% dos encaminhados")
ids = set(s.cd_aluno_sme.astype(str))
eol = pd.read_parquet(R + r"\build14_cobertura\eol_creche.parquet", columns=["CD_ALUNO_SME", "DT_IN_MAT"])
eol["id"] = eol.CD_ALUNO_SME.astype(str); eol = eol[eol.id.isin(ids)]
f = eol.assign(d=pd.to_datetime(eol.DT_IN_MAT, errors="coerce")).sort_values("d").groupby("id").d.first()
print("1a entrada no EOL: fev/2013", int(((f.dt.year == 2013) & (f.dt.month == 2)).sum()), "| fev/2012", int(((f.dt.year == 2012) & (f.dt.month == 2)).sum()))
