# -*- coding: utf-8 -*-
# SAIDA C, etapa 2 (26/10/2026): serie publicada da demanda registrada de creche, direto das publicacoes da SME
# (Decreto 47.155/2006), baixadas em 04_paper/referee_EE_2026-10/fontes_saidaC/serie_SME/ (pagina "Demanda Escolar").
# (1) XLS 2017-2026: linha TOTAL; colunas de matricula de creche, matricula em processo de creche e demanda de creche,
#     com as subcolunas que aparecem a partir de set/2019 (com/sem opcao por unidade especifica; espera ate/mais de 30 dias).
# (2) PDF 2007-2016: linha TOTAL via pdftotext, para conferir a serie de dados abertos (evolucaodemanda.csv, T12).
# Descritivo. Nao estima nada.
# Saidas: 03_build/build19/serie_sme_xls.csv, serie_sme_pdf_totais.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, re, subprocess, warnings; warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd
ROOT = NE_ROOT
SRC = os.path.join(ROOT, r"04_paper\referee_EE_2026-10\fontes_saidaC\serie_SME")
OUT = os.path.join(ROOT, r"03_build\build19"); os.makedirs(OUT, exist_ok=True)
pd.set_option("display.width", 250)
M = pd.read_csv(os.path.join(SRC, "_mapa_arquivos.csv")).dropna(subset=["ano"])
M["ano"] = M.ano.astype(int); M["mes"] = M.mes.astype(int)

def norm(s): return re.sub(r"\s+", " ", str(s)).strip()

R = []
for _, r in M[M.tipo == "xls"].iterrows():
    x = pd.read_excel(os.path.join(SRC, r.arquivo), header=None)
    top = [norm(v) for v in x.iloc[0].tolist()]; sub = [norm(v) for v in x.iloc[1].tolist()]
    # bloco de cada coluna = ultimo rotulo nao vazio da linha 0 a esquerda
    blk, cur = [], ""
    for v in top:
        if v not in ("nan", ""): cur = v
        blk.append(cur)
    tot = x[x[0].astype(str).str.strip().str.upper() == "TOTAL"]
    assert len(tot) == 1, r.arquivo
    t = tot.iloc[0]
    d = dict(ano=r.ano, mes=r.mes, arquivo=r.arquivo)
    dem = {}
    for j, (b, s) in enumerate(zip(blk, sub)):
        if not s.startswith("Creche"): continue
        v = pd.to_numeric(t[j], errors="coerce")
        if b.startswith("Matrículas") or b.startswith("Matr\ufffdculas") or b.lower().startswith("matr") and "processo" not in b.lower():
            d["matric_creche"] = v
        elif "processo" in b.lower():
            d["mat_processo_creche"] = v
        elif b.lower().startswith("demanda"):
            dem[s] = v
    if len(dem) == 1:
        d["dem_total"] = list(dem.values())[0]
    else:
        lab = {k: k for k in dem}
        tot_key = [k for k in dem if "Total" in k]
        parts = {k: v for k, v in dem.items() if "Total" not in k}
        d["dem_total"] = dem[tot_key[0]] if tot_key else sum(parts.values())
        d["dem_soma_partes"] = sum(parts.values())
        for k, v in parts.items():
            key = "dem_" + re.search(r"\((\d)\)", k).group(1)
            d[key] = v
    d["notas"] = " | ".join(norm(v) for v in x[0].tolist() if str(v).startswith("("))
    R.append(d)
X = pd.DataFrame(R).sort_values(["ano", "mes"]).reset_index(drop=True)
print(X.drop(columns=["arquivo", "notas"]).to_string(index=False))
chk = X.dropna(subset=["dem_soma_partes"])
print("\nconferencia soma das partes = total:", (chk.dem_soma_partes == chk.dem_total).sum(), "de", len(chk))
p = os.path.join(OUT, "serie_sme_xls.csv"); X.to_csv(p, index=False, encoding="utf-8"); assert len(pd.read_csv(p)) == len(X); print("[gravado e relido]", p)

# (2) PDFs: linha TOTAL. Os PDFs antigos tem colunas desalinhadas; guardamos os numeros da linha na ordem em que aparecem.
P = []
for _, r in M[(M.tipo == "pdf")].iterrows():
    f = os.path.join(SRC, r.arquivo)
    try:
        txt = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", f, "-"], capture_output=True, text=True, encoding="utf-8").stdout
    except Exception as e:
        P.append(dict(ano=r.ano, mes=r.mes, arquivo=r.arquivo, linha_total="ERRO " + str(e))); continue
    lin = [l for l in txt.splitlines() if re.match(r"^\s*TOTAL\b", l, re.I)]
    nums = re.findall(r"\d{1,3}(?:\.\d{3})+|\d+", lin[-1]) if lin else []
    P.append(dict(ano=r.ano, mes=r.mes, arquivo=r.arquivo, n_linhas_total=len(lin),
                  numeros=" ".join(nums), linha_total=norm(lin[-1]) if lin else ""))
P = pd.DataFrame(P).sort_values(["ano", "mes"]).reset_index(drop=True)
p = os.path.join(OUT, "serie_sme_pdf_totais.csv"); P.to_csv(p, index=False, encoding="utf-8"); assert len(pd.read_csv(p)) == len(P); print("[gravado e relido]", p)
print(P[["ano", "mes", "arquivo", "n_linhas_total", "numeros"]].to_string(index=False))
