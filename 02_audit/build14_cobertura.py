# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# COBERTURA_FILA (25/10/2026), itens 2 e 3: cobertura da fila no universo de entrantes em creche do EOL,
# reproduzida com extrato proprio (build14_eol_extract.py) e com a base do paper (spine + Fila1018).
# Descritivo. Saidas: 03_build/build14_cobertura/cob_*.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
NE_SME = _os_ne.environ.get("NE_DADOS_SME", _os_ne.path.normpath(_os_ne.path.join(NE_ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")))
import sys, os, numpy as np, pandas as pd, pyreadstat; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; OUT = os.path.join(ROOT, r"03_build\build14_cobertura")
pd.set_option("display.width", 250)
def key(s): return pd.to_numeric(s, errors="coerce").astype("Int64")
# ---------- EOL: primeira creche por crianca ----------
e = pd.read_parquet(os.path.join(OUT, "eol_creche.parquet"))
e["id"] = key(e.CD_ALUNO_SME); e["an"] = pd.to_numeric(e.AN_LETIVO, errors="coerce")
e["dt"] = pd.to_datetime(e.DT_IN_MAT.str[:10], errors="coerce")
e["an_n"] = pd.to_numeric(e.ANO_NASC_ALUNO, errors="coerce"); e["me_n"] = pd.to_numeric(e.MES_NASC_ALUNO, errors="coerce")
print("EOL creche: linhas", f"{len(e):,}", "| criancas", f"{e.id.nunique():,}", "| id nulo", int(e.id.isna().sum()), "| DT_IN_MAT nao convertida", int(e.dt.isna().sum()), flush=True)
first = e.dropna(subset=["id"]).sort_values(["id", "an", "dt"]).groupby("id").first()
first["ano_ent"] = first.an.astype(int); first["mes_ent"] = first.dt.dt.month
first["idade_ent"] = (first.dt.dt.year - first.an_n) * 12 + (first.dt.dt.month - first.me_n)
# ---------- Fila1018 (qualquer registro) e universo do paper ----------
fa, _ = pyreadstat.read_dta((NE_SME + r"\processados\derivados_de_brutos\Fila1018.dta"), usecols=["cd_aluno_sme"])
fila_ids = set(key(fa.cd_aluno_sme).dropna().unique()); del fa
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"), columns=["cd_aluno_sme", "ano_nasc", "d_sol1", "d_enc1", "d_mat1"])
sp["id"] = key(sp.cd_aluno_sme); spi = sp.set_index("id")
first["na_fila"] = first.index.isin(fila_ids); first["no_paper"] = first.index.isin(spi.index)
first["d_sol1"] = spi.d_sol1.reindex(first.index).values
first["sol_antes"] = first.d_sol1.notna() & (first.d_sol1 < first.dt)
# ---------- (2a) serie de cobertura por ano de entrada ----------
c = first[first.ano_ent.between(2008, 2019)].groupby("ano_ent").agg(N=("na_fila", "size"), na_fila=("na_fila", "mean"), no_paper=("no_paper", "mean"), sol_antes=("sol_antes", "mean"))
for k in ("na_fila", "no_paper", "sol_antes"): c[k] = (100 * c[k]).round(1)
c.to_csv(os.path.join(OUT, "cob_por_ano.csv")); print("\n(2a) cobertura por ano de entrada (%):"); print(c.to_string())
# ---------- (2b) padrao de fevereiro ----------
m = first[first.ano_ent.between(2010, 2014)].copy(); m["fev"] = m.mes_ent == 2
b = m.groupby(["ano_ent", "fev"]).agg(N=("no_paper", "size"), no_paper=("no_paper", "mean")); b["no_paper"] = (100 * b.no_paper).round(1)
b.to_csv(os.path.join(OUT, "cob_fevereiro.csv")); print("\n(2b) cobertura (universo do paper) por fevereiro x outros meses:"); print(b.to_string())
aus = m[~m.no_paper]
print("\n% dos AUSENTES que entraram em fevereiro:", (100 * aus.groupby("ano_ent").fev.mean()).round(1).to_dict())
m12 = first[first.ano_ent == 2012].groupby("mes_ent").agg(N=("no_paper", "size"), no_paper=("no_paper", "mean")); m12["no_paper"] = (100 * m12.no_paper).round(1)
print("2012 por mes de entrada:"); print(m12.T.to_string())
# ---------- (2c) perfil etario dos ausentes ----------
ok = m[m.idade_ent.between(0, 60)]
pf = ok.groupby(["ano_ent", "no_paper"]).idade_ent.describe(percentiles=[.1, .5, .9])[["count", "mean", "10%", "50%", "90%"]].round(1)
pf.to_csv(os.path.join(OUT, "cob_idade.csv")); print("\n(2c) idade na entrada (meses; 0-60) por ano x presenca no universo do paper:"); print(pf.to_string())
print("idades fora de 0-60 meses excluidas:", int((~m.idade_ent.between(0, 60)).sum()))
# ---------- (3) exposicao por coorte de nascimento ----------
r = []
for co in range(2010, 2017):
    s = sp[sp.ano_nasc == co]
    r.append(dict(coorte=co, N=len(s), pct_sol_antes_2013=100 * (s.d_sol1 < "2013-01-01").mean(), pct_sol_antes_mar2012=100 * (s.d_sol1 < "2012-03-01").mean(),
                  pct_mat_antes_2013=100 * (s.d_mat1 < "2013-01-01").sum() / max(1, s.d_mat1.notna().sum())))
ex = pd.DataFrame(r).round(1); ex.to_csv(os.path.join(OUT, "cob_exposicao_coorte.csv", ), index=False); print("\n(3) exposicao por coorte (universo do paper):"); print(ex.to_string(index=False))
# EOL x paper: % da coorte (nascidos vivos) que entrou em creche antes de 12/24/36 meses
import csv
rows = list(csv.reader(open(os.path.join(ROOT, r"01_dados_publicos\ceinfo\sinasc_nv_distrito_2006_2026.csv"), encoding="utf-8"), delimiter=";"))
tot = [r_ for r_ in rows if r_ and r_[0].strip() == "Total"][0]; hdr = rows[0]; births = {int(h): int(tot[i]) for i, h in enumerate(hdr) if h.isdigit()}
first["coorte"] = first.an_n
r2 = []
for co in range(2010, 2017):
    f = first[(first.coorte == co) & first.idade_ent.between(0, 60)]
    d = dict(coorte=co, nascidos=births.get(co))
    for X in (12, 24, 36): d[f"EOL_antes_{X}m"] = round(100 * (f.idade_ent < X).sum() / births[co], 1)
    r2.append(d)
eo = pd.DataFrame(r2); eo.to_csv(os.path.join(OUT, "cob_eol_coorte.csv"), index=False)
print("\nEOL: % dos nascidos vivos com 1a creche antes de X meses (compare N4 do paper: <24m 7,4 | 22,8 | 33,2 | 43,4 | 44,1 | 46,6 | 53,8):"); print(eo.to_string(index=False))
print("ATENCAO: ate 2011 a DT_IN_MAT do EOL e a data do ano letivo (fevereiro), nao a entrada real; a idade na entrada pre-2012 e medida em fevereiro.")
# ---------- (5) solicitantes do paper: entrada no EOL x datas da fila (teste do "2011 como estoque") ----------
sp2 = sp.set_index("id").join(first[["ano_ent", "mes_ent", "dt"]], how="left")
r5 = []
for y in range(2010, 2018):
    s = sp2[sp2.d_sol1.dt.year == y]
    ent = s[s.dt.notna() & (s.dt >= s.d_sol1.dt.normalize())]          # entrou em creche no EOL depois de solicitar
    sem_reg = ent.d_mat1.isna() | (ent.d_mat1 > ent.dt + pd.Timedelta(days=60))   # a fila nao registra a matricula ate 60 dias apos a entrada no EOL
    gap = (ent.d_enc1 - ent.dt).dt.days
    r5.append(dict(ano_sol=y, N=len(s), pct_entrou_EOL=round(100 * len(ent) / len(s), 1),
                   pct_entrou_EOL_365d=round(100 * ((ent.dt - ent.d_sol1).dt.days <= 365).sum() / len(s), 1),
                   pct_fila_sem_matricula_coerente=round(100 * sem_reg.mean(), 1),
                   pct_enc_fila_mais_de_60d_apos_entrada=round(100 * ((gap > 60) | ent.d_enc1.isna()).mean(), 1)))
f5 = pd.DataFrame(r5); f5.to_csv(os.path.join(OUT, "cob_sol_x_eol.csv"), index=False)
print("\n(5) solicitantes do paper por ano da 1a solicitacao: entrada em creche no EOL x datas da fila:"); print(f5.to_string(index=False))
s11 = sp2[(sp2.d_sol1.dt.year == 2011) & sp2.dt.notna() & (sp2.dt >= sp2.d_sol1.dt.normalize())]
x = s11.groupby([s11.ano_ent, s11.mes_ent]).size().sort_values(ascending=False).head(6)
print("solicitantes de 2011 que entraram em creche no EOL: principais (ano, mes) de entrada:"); print(x.to_string())
fev12 = s11[(s11.ano_ent == 2012) & (s11.mes_ent == 2)]
print("dos que entraram em fev/2012:", len(fev12), "| 1o encaminhamento na fila em dez/2012 ou depois:",
      f"{100 * ((fev12.d_enc1 >= '2012-12-01') | fev12.d_enc1.isna()).mean():.1f}%", "| matricula na fila ausente ou depois de dez/2012:",
      f"{100 * ((fev12.d_mat1 >= '2012-12-01') | fev12.d_mat1.isna()).mean():.1f}%")
