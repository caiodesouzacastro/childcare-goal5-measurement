# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# OQ-5, item 1c (25/10/2026): teste mecanico de TODOS os merges/agrupamentos do pipeline que usam chave textual
# (nome de distrito). Para cada um, aplica a MESMA normalizacao do script de origem e conta quantas unidades casam.
# Descritivo; nao altera nada. Saida: 03_build/build13_coverage/textkeys_test.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
NE_SME = _os_ne.environ.get("NE_DADOS_SME", _os_ne.path.normpath(_os_ne.path.join(NE_ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")))
import sys, os, re, csv, unicodedata, importlib.util, pandas as pd, numpy as np; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; A = os.path.join(ROOT, "02_audit")
def plain(s):   # build10.py, build_p3*.py, build12_revision.py (nz), build_p5.py (nz), verificacao_final.py (nz)
    s = "".join(c for c in unicodedata.normalize("NFD", str(s).strip().upper()) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s)
def fixhex(s): return re.sub(r"<([0-9a-fA-F]{2})>", lambda m: bytes([int(m.group(1), 16)]).decode("latin-1"), str(s))
def withfix(s): return "".join(c for c in unicodedata.normalize("NFD", fixhex(s).strip().upper()) if unicodedata.category(c) != "Mn")  # build03_*, build04_diag15, build05_panel
spec = importlib.util.spec_from_file_location("lib", os.path.join(A, "lib.py")); lib = importlib.util.module_from_spec(spec)
try: spec.loader.exec_module(lib); libnorm = lib.norm
except Exception as e: libnorm = None; print("lib.py nao carregou:", e)
# fontes
sin = [r[0].strip() for r in list(csv.reader(open(os.path.join(ROOT, r"01_dados_publicos\ceinfo\sinasc_nv_distrito_2006_2026.csv"), encoding="utf-8"), delimiter=";"))[1:] if r and r[0].strip() not in ("Ignorado", "Total")]
cep = pd.read_stata((NE_SME + r"\processados\bases_analise\cep_renda_pop_2010.dta"), columns=["cep", "nm_distrit"])
cepn = cep.nm_distrit.dropna().unique()
evd = pd.read_csv(os.path.join(ROOT, r"03_build\build04\_ext\evolucaodemanda.csv"), sep=";", thousands=".", dtype={"MES_ANO_REF": str}).DISTRITO.dropna().unique()
per = pd.read_csv(os.path.join(ROOT, r"03_build\build01\_staging\perfil_turma.csv"), usecols=["distrito"]).distrito.dropna().unique()
pan = pd.read_parquet(os.path.join(ROOT, r"03_build\build05\_panel_criancas.parquet"), columns=["distrito"]).distrito
print(f"fontes: SINASC {len(sin)} | CEP {len(cepn)} | evolucaodemanda {len(evd)} | perfil {len(per)} | painel build05 {pan.dropna().nunique()}")
rows = []
def test(merge, script, uso, A_, fa, B_, fb):
    a = {fa(x) for x in A_}; b = {fb(x) for x in B_}; m = len(a & b)
    rows.append(dict(merge=merge, script=script, uso_no_paper=uso, n_A=len(a), n_B=len(b), casam=m, perda_A=len(a) - m,
                     exemplos_sem_par=", ".join(sorted(a - b)[:4])))
test("CEP -> evolucaodemanda (C6)", "build10.py", "tab:C6 (versao submetida)", cepn, plain, evd, plain)
test("CEP -> evolucaodemanda (C6 corrigida)", "build13_c6fix.py", "tab:C6 (atual)", cepn, lambda s: plain(fixhex(s)), evd, plain)
test("CEP -> evolucaodemanda (V11)", "verificacao_final.py", "nenhum (checagem)", cepn, plain, evd, plain)
test("CEP -> SINASC (renda por distrito, S6b)", "build03_demog.py", "tab:S6b_nascidos_renda", cepn, withfix, sin, withfix)
test("perfil -> SINASC (capacidade/pool, S6c)", "build03_demog.py", "tab:S6c_cobertura", per, withfix, sin, withfix)
test("CEP -> SINASC (quartil de renda, S8)", "build03_s7s8.py", "tab:S8a/S8b/S8c", cepn, withfix, sin, withfix)
test("CEP -> perfil (D15 distrito)", "build04_diag15.py", "nenhum no corpo (diagnostico D15)", cepn, withfix, per, withfix)
test("CEP -> painel (distrito da crianca)", "build05_panel.py", "N3 (tab:districtmix), irmaos", cepn, withfix, evd, plain)
if libnorm:
    for nm, src in (("CEP", cepn), ("perfil", per)):
        test(f"{nm} -> SINASC (lib.norm)", "d14_*.py", "Apendice B, linha 12", src, libnorm, sin, libnorm)
o = pd.DataFrame(rows); o.to_csv(os.path.join(ROOT, r"03_build\build13_coverage\textkeys_test.csv"), index=False)
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70); print(o.to_string(index=False))
# cobertura por crianca: CEP do painel com distrito
print(f"painel build05: crianca com distrito = {pan.notna().mean():.4f}; distritos distintos = {pan.dropna().nunique()}")
