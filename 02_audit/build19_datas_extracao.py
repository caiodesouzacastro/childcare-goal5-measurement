# -*- coding: utf-8 -*-
# SAIDA C (26/10/2026): data de extracao impressa em cada publicacao da SME ("Sistema EOL - dd/mm/aaaa", no rodape
# "FONTE"). Mostra que a "foto de dezembro" nao e tirada sempre em 31/12. Descritivo.
# Saida: 03_build/build19/datas_extracao.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import os, re, subprocess, sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd
SRC = (NE_ROOT + r"\04_paper\referee_EE_2026-10\fontes_saidaC\serie_SME")
OUT = (NE_ROOT + r"\03_build\build19")
M = pd.read_csv(os.path.join(SRC, "_mapa_arquivos.csv")).dropna(subset=["ano"]); M = M[M.tipo == "pdf"]
R = []
for _, r in M.iterrows():
    t = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", os.path.join(SRC, r.arquivo), "-"], capture_output=True, text=True, encoding="utf-8").stdout
    d = sorted(set(re.findall(r"Sistema EOL\s*-\s*(\d{2}/\d{2}/\d{4})", t)))
    R.append(dict(ano=int(r.ano), mes=int(r.mes), arquivo=r.arquivo, data_extracao=";".join(d), ajustado="Ajustado" in t))
R = pd.DataFrame(R).sort_values(["ano", "mes"])
p = os.path.join(OUT, "datas_extracao.csv"); R.to_csv(p, index=False); assert len(pd.read_csv(p)) == len(R); print("[gravado e relido]", p)
dz = R[R.mes == 12]; print(dz[["ano", "data_extracao", "ajustado"]].to_string(index=False))
dd = dz[dz.data_extracao != ""]
print(f"publicacoes de dezembro com data impressa: {len(dd)}; em 31/12: {(dd.data_extracao.str.startswith('31/12')).sum()}; "
      f"datas: {sorted(dd.data_extracao.tolist())}")
