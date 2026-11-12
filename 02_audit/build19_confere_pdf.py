# -*- coding: utf-8 -*-
# SAIDA C (26/10/2026): confere a serie de dados abertos (evolucaodemanda.csv, usada em T12) contra os PDFs originais
# da SME (fontes_saidaC/serie_SME). Para cada mes com PDF, procura no texto do PDF o total municipal de DEM_CRECHE
# e de MAT_CRECHE dos dados abertos, formatados com ponto de milhar. Achou = o PDF imprime o mesmo total.
# Tambem junta a serie aberta (2006-2017) com a dos XLS (2017-2026) e grava a serie publicada completa.
# Saidas: 03_build/build19/confere_pdf.csv, serie_publicada_completa.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, re, subprocess; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd
ROOT = NE_ROOT
SRC = os.path.join(ROOT, r"04_paper\referee_EE_2026-10\fontes_saidaC\serie_SME")
OUT = os.path.join(ROOT, r"03_build\build19")
MES = {"jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6, "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12}
df = pd.read_csv(os.path.join(ROOT, r"03_build\build04\_ext\evolucaodemanda.csv"), sep=";", thousands=".", dtype={"MES_ANO_REF": str})
df["ano"] = df.MES_ANO_REF.str[-2:].astype(int) + 2000; df["mes"] = df.MES_ANO_REF.str[:3].str.lower().map(MES)
for c in ("DEM_CRECHE", "MAT_CRECHE", "MAT_PROC_CRECHE"): df[c] = pd.to_numeric(df[c], errors="coerce")
A = df.groupby(["ano", "mes"])[["DEM_CRECHE", "MAT_CRECHE", "MAT_PROC_CRECHE"]].sum().reset_index()
print("dados abertos: meses", len(A), "de", A.ano.min(), "a", A.ano.max())
print(A.to_string(index=False))
fmt = lambda v: f"{int(v):,}".replace(",", ".")
M = pd.read_csv(os.path.join(SRC, "_mapa_arquivos.csv")).dropna(subset=["ano"]); M = M[M.tipo == "pdf"]
M["ano"] = M.ano.astype(int); M["mes"] = M.mes.astype(int)
R = []
for _, r in M.iterrows():
    a = A[(A.ano == r.ano) & (A.mes == r.mes)]
    if a.empty: R.append(dict(ano=r.ano, mes=r.mes, arquivo=r.arquivo, aberto="sem mes nos dados abertos")); continue
    txt = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", os.path.join(SRC, r.arquivo), "-"], capture_output=True, text=True, encoding="utf-8").stdout
    flat = re.sub(r"\s+", " ", txt)
    d, m = a.iloc[0].DEM_CRECHE, a.iloc[0].MAT_CRECHE
    R.append(dict(ano=r.ano, mes=r.mes, arquivo=r.arquivo, dem_aberto=int(d), dem_no_pdf=fmt(d) in flat or str(int(d)) in flat,
                  mat_aberto=int(m), mat_no_pdf=fmt(m) in flat or str(int(m)) in flat, chars_pdf=len(txt)))
C = pd.DataFrame(R).sort_values(["ano", "mes"])
print(C.to_string(index=False))
c2 = C.dropna(subset=["dem_aberto"])
print(f"\nPDFs com mes nos dados abertos: {len(c2)}; total de demanda achado no PDF: {int(c2.dem_no_pdf.sum())}; total de matricula achado: {int(c2.mat_no_pdf.sum())}")
p = os.path.join(OUT, "confere_pdf.csv"); C.to_csv(p, index=False); assert len(pd.read_csv(p)) == len(C); print("[gravado e relido]", p)
# serie completa: dados abertos ate 2016 (e 2017 para conferir), XLS de 2017 em diante
X = pd.read_csv(os.path.join(OUT, "serie_sme_xls.csv"))
x17 = X[X.ano == 2017].set_index("mes").dem_total; a17 = A[A.ano == 2017].set_index("mes").DEM_CRECHE
print("2017, XLS vs aberto:", {m: (int(x17[m]), int(a17.get(m, -1))) for m in x17.index})
S = pd.concat([A[A.ano <= 2016].rename(columns={"DEM_CRECHE": "dem_total", "MAT_CRECHE": "matric_creche", "MAT_PROC_CRECHE": "mat_processo_creche"}).assign(fonte="dados abertos (evolucaodemanda)"),
               X.assign(fonte="XLS SME")], ignore_index=True)[["ano", "mes", "dem_total", "dem_1", "dem_2", "dem_3", "matric_creche", "mat_processo_creche", "fonte", "notas"]]
p = os.path.join(OUT, "serie_publicada_completa.csv"); S.to_csv(p, index=False); assert len(pd.read_csv(p)) == len(S); print("[gravado e relido]", p, len(S), "linhas")
