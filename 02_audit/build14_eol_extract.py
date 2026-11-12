# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# COBERTURA_FILA (25/10/2026), item 2: extrato PROPRIO do EOL (independente do codigo da outra frente).
# Le os CSVs brutos de matricula do EOL, so as colunas usadas, e guarda as linhas de creche.
# Saida: 03_build/build14_cobertura/eol_creche.parquet (+ eol_modalidades.csv com a contagem de MODALIDADE por ano)
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
NE_SME = _os_ne.environ.get("NE_DADOS_SME", _os_ne.path.normpath(_os_ne.path.join(NE_ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")))
import sys, os, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
SRC = (NE_SME + r"\originais\matriculas_EOL")
OUT = (NE_ROOT + r"\03_build\build14_cobertura"); os.makedirs(OUT, exist_ok=True)
COLS = ["AN_LETIVO", "CD_UNIDADE_EDUCACAO", "TIPO_ESCOLA", "CD_SERIE", "DESC_SERIE", "MODALIDADE", "CD_ALUNO_SME",
        "ANO_NASC_ALUNO", "MES_NASC_ALUNO", "DT_IN_MAT", "SITUACAO_MAT"]
parts, mods = [], []
for y in range(2003, 2020):
    f = os.path.join(SRC, f"Microdados_EOL_Matriculas_Ano_{y}.csv"); n = 0
    first = open(f, "rb").readline(); sep = "|" if first.count(b"|") > first.count(b";") else ";"   # 2019 usa ";"
    for ch in pd.read_csv(f, sep=sep, encoding="latin-1", usecols=COLS, dtype=str, chunksize=500000, on_bad_lines="warn"):
        n += len(ch)
        m = ch.MODALIDADE.fillna("").str.strip().str.upper()
        mods.append(m.value_counts().rename_axis("modalidade").reset_index(name="n").assign(ano=y))
        parts.append(ch[m == "CRECHE"].copy())
    print(y, "linhas lidas:", f"{n:,}", "| creche acumulado:", f"{sum(len(p) for p in parts):,}", flush=True)
e = pd.concat(parts, ignore_index=True)
for c in COLS: e[c] = e[c].astype(str).str.strip()
e.to_parquet(os.path.join(OUT, "eol_creche.parquet"), index=False)
pd.concat(mods).groupby(["ano", "modalidade"]).n.sum().reset_index().to_csv(os.path.join(OUT, "eol_modalidades.csv"), index=False)
print("linhas creche:", f"{len(e):,}", "| criancas:", f"{e.CD_ALUNO_SME.nunique():,}")
