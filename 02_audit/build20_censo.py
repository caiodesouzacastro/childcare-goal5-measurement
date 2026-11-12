# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# SAIDA C, escrita (26/10/2026): matriculas em creche no municipio de Sao Paulo (3550308), Censo Escolar INEP, 2007-2024.
# Mesmo metodo de build13_coverage.py (mesmas colunas, mesma regra de rede). 2007-2019: CSVs locais na pasta compartilhada;
# 2020-2024: zips baixados do INEP em 03_build/build20/_inep (download.inep.gov.br/dados_abertos/microdados_censo_escolar_AAAA.zip).
# Confere 2010-2018 contra creche_mat_sp.csv (build13). Saida: 03_build/build20/creche_mat_sp_2007_2024.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
NE_SME = _os_ne.environ.get("NE_DADOS_SME", _os_ne.path.normpath(_os_ne.path.join(NE_ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")))
import sys, os, io, zipfile, re; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd
D = (NE_SME + "/originais/auxiliares_publicos/censo_escolar_inep/")
Z = (NE_ROOT + "/03_build/build20/_inep/")
OUT = (NE_ROOT + "/03_build/build20/")
COLS = ["NU_ANO_CENSO", "CO_MUNICIPIO", "CO_ENTIDADE", "TP_DEPENDENCIA", "TP_SITUACAO_FUNCIONAMENTO", "IN_CONVENIADA_PP",
        "TP_CONVENIO_PODER_PUBLICO", "QT_MAT_INF_CRE", "QT_MAT_INF_PRE", "QT_MAT_BAS_0_3", "QT_MAT_INF"]
def rede(r):
    if r.TP_DEPENDENCIA == 3: return "municipal_direta"
    if r.TP_DEPENDENCIA == 4 and r.IN_CONVENIADA_PP == 1 and r.TP_CONVENIO_PODER_PUBLICO in (1, 3): return "privada_conveniada_municipal"
    if r.TP_DEPENDENCIA == 4 and r.IN_CONVENIADA_PP == 1: return "privada_conveniada_estadual"
    if r.TP_DEPENDENCIA == 4: return "privada_nao_conveniada"
    return {1: "federal", 2: "estadual"}.get(r.TP_DEPENDENCIA, "outra")
def fonte(y):
    p = D + f"microdados_ed_basica_{y}.csv"
    if os.path.exists(p): return p, None
    zp = Z + f"microdados_censo_escolar_{y}.zip"
    zf = zipfile.ZipFile(zp)
    nm = [n for n in zf.namelist() if re.search(rf"microdados_ed_basica_{y}\.csv$", n, re.I)]
    assert len(nm) == 1, (y, [n for n in zf.namelist() if n.lower().endswith(".csv")])
    return zf, nm[0]
rows = []
for y in range(2007, 2025):
    src, member = fonte(y)
    hdr = pd.read_csv(src.open(member) if member else src, sep=";", encoding="latin-1", nrows=0).columns.tolist()
    use = [c for c in COLS if c in hdr]; falta = [c for c in COLS if c not in hdr]
    parts = []
    for ch in pd.read_csv(src.open(member) if member else src, sep=";", encoding="latin-1", usecols=use, chunksize=100000, low_memory=False):
        parts.append(ch[ch.CO_MUNICIPIO == 3550308])
    d = pd.concat(parts)
    for c in falta: d[c] = pd.NA
    for c in COLS[3:]: d[c] = pd.to_numeric(d[c], errors="coerce")
    d["rede"] = d.apply(rede, axis=1)
    g = d.groupby("rede")[["QT_MAT_INF_CRE", "QT_MAT_INF_PRE", "QT_MAT_BAS_0_3"]].sum(min_count=1).reset_index()
    g.insert(0, "ano", y); g["fonte"] = "local" if member is None else "zip INEP"; rows.append(g)
    print(y, "escolas", len(d), "| creche total", int(d.QT_MAT_INF_CRE.sum()), "| mun+conv",
          int(d[d.rede.isin(["municipal_direta", "privada_conveniada_municipal"])].QT_MAT_INF_CRE.sum()),
          "| 0-3 total", int(d.QT_MAT_BAS_0_3.sum()) if d.QT_MAT_BAS_0_3.notna().any() else "NA",
          "| colunas ausentes:", falta, "| conveniada sem TP_CONVENIO:",
          int(((d.TP_DEPENDENCIA == 4) & (d.IN_CONVENIADA_PP == 1) & d.TP_CONVENIO_PODER_PUBLICO.isna()).sum()), flush=True)
out = pd.concat(rows)
p = OUT + "creche_mat_sp_2007_2024.csv"; out.to_csv(p, index=False); assert len(pd.read_csv(p)) == len(out); print("[gravado e relido]", p)
old = pd.read_csv((NE_ROOT + "/03_build/build13_coverage/creche_mat_sp.csv"))
a = old.groupby("ano")[["QT_MAT_INF_CRE", "QT_MAT_BAS_0_3"]].sum(); b = out[out.ano.between(2010, 2018)].groupby("ano")[["QT_MAT_INF_CRE", "QT_MAT_BAS_0_3"]].sum()
print("confere 2010-2018 contra build13 (diferenca):\n", (b - a).to_string())
