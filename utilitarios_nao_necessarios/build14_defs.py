# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# COBERTURA_FILA (25/10/2026), item 1: reconciliacao de definicao entre a taxa da outra frente (U6) e a do paper.
# Escada: (A) U6 reimplementada do zero sobre a Fila1018 -> (B..E) troca um elemento da definicao por vez -> paper.
# Descritivo. Saida: 03_build/build14_cobertura/defs_ladder.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
NE_SME = _os_ne.environ.get("NE_DADOS_SME", _os_ne.path.normpath(_os_ne.path.join(NE_ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")))
import sys, os, numpy as np, pandas as pd, pyreadstat; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; OUT = os.path.join(ROOT, r"03_build\build14_cobertura"); os.makedirs(OUT, exist_ok=True)
F = (NE_SME + r"\processados\derivados_de_brutos\Fila1018.dta")
CRE = {1, 4, 8, 27, 28}                      # codigos de creche (D-U3 da outra frente)
PANEL = pd.Timestamp("2019-11-28")
cols = ["cd_aluno_sme", "ano", "dt_solicitacao", "cd_serie_ensino_solicitacao", "dt_encaminhamento", "cd_serie_ensino_encaminhamento",
        "dt_matricula", "ano_nasc", "mes_nasc"]
fa, _ = pyreadstat.read_dta(F, usecols=cols); print("Fila1018 linhas:", f"{len(fa):,}", flush=True)
FMT = "%d/%m/%Y %H:%M:%S"
for c, n in (("dt_solicitacao", "sol"), ("dt_encaminhamento", "enc"), ("dt_matricula", "mat")): fa[n] = pd.to_datetime(fa[c], format=FMT, errors="coerce")
for c in ("cd_serie_ensino_solicitacao", "cd_serie_ensino_encaminhamento", "ano_nasc", "mes_nasc"): fa[c] = pd.to_numeric(fa[c], errors="coerce")
fa = fa.drop(columns=["dt_solicitacao", "dt_encaminhamento", "dt_matricula"])
# ---------- (A) U6: 1a solicitacao de creche por crianca; encaminhamento p/ codigo de creche em 0-365 dias ----------
s = fa[fa.sol.notna() & fa.cd_serie_ensino_solicitacao.isin(CRE)].groupby("cd_aluno_sme").sol.min().rename("sol_cre")
e = fa[fa.enc.notna() & fa.cd_serie_ensino_encaminhamento.isin(CRE)][["cd_aluno_sme", "enc"]].merge(s, on="cd_aluno_sme")
e = e[(e.enc >= e.sol_cre) & ((e.enc - e.sol_cre).dt.days <= 365)]
A = s.to_frame(); A["enc365"] = A.index.isin(e.cd_aluno_sme); A["ano"] = A.sol_cre.dt.year
uA = A[A.ano.between(2010, 2017)].groupby("ano").agg(N=("enc365", "size"), enc=("enc365", "sum")); uA["pct"] = 100 * uA.enc / uA.N
print("\n(A) U6 reimplementada (compare: 2010 51,9 | 2011 35,1 | 2012 61,2 | 2013 63,0 | 2014 67,3 | 2015 76,8 | 2016 75,7 | 2017 90,1)"); print(uA.round(1).to_string())
# ---------- universo do paper (spine) ----------
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"),
                     columns=["cd_aluno_sme", "ano_nasc", "d_sol1", "d_enc1", "d_mat1", "d_age47", "serie_sol1"])
sp["cd_aluno_sme"] = sp.cd_aluno_sme.astype(str); A.index = A.index.astype(str)
sp["serie_sol1"] = pd.to_numeric(sp.serie_sol1, errors="coerce")
print("\nspine: N =", f"{len(sp):,}", "| 1a solicitacao com codigo de creche:", f"{sp.serie_sol1.isin(CRE).mean():.4f}",
      "| criancas do U6 que estao no spine:", f"{A.index.isin(sp.cd_aluno_sme).mean():.4f}")
def prop365(df, t0, t1):  # proporcao simples, sem risco competitivo
    d = (df[t1] - df[t0]).dt.days; return ((d >= 0) & (d <= 365)).mean()
def cif365(df, t0, t1):   # Aalen-Johansen: encaminhamento vs aging out (47m), censura no fim do painel; so quem tem tempo elegivel
    df = df[df[t0] <= df.d_age47]
    tr = (df[t1] - df[t0]).dt.days.where(df[t1] >= df[t0]); ta = (df.d_age47 - df[t0]).dt.days; tc = (PANEL - df[t0]).dt.days
    T = np.fmin(np.fmin(tr.fillna(np.inf), ta), tc).values; ev = np.where(tr.fillna(np.inf).values <= np.minimum(ta, tc).values, 1, np.where(ta.values <= tc.values, 2, 0))
    o = np.argsort(T, kind="mergesort"); T, ev = T[o], ev[o]; n = len(T); S = 1.0; cif = 0.0; i = 0
    while i < n and T[i] <= 365:
        j = i
        while j < n and T[j] == T[i]: j += 1
        d1 = (ev[i:j] == 1).sum(); d2 = (ev[i:j] == 2).sum(); r = n - i
        cif += S * d1 / r; S *= 1 - (d1 + d2) / r; i = j
    return cif, len(df)
rows = []
for y in range(2010, 2018):
    a = A[A.ano == y]
    r = dict(ano=y, A_U6=100 * a.enc365.mean(), N_A=len(a))
    # (B) universo do paper (1a solicitacao de qualquer codigo), indexado pelo ano da 1a solicitacao, proporcao simples 0-365
    b = sp[sp.d_sol1.dt.year == y]; r["B_spine_prop"] = 100 * prop365(b, "d_sol1", "d_enc1"); r["N_B"] = len(b)
    # (C) idem (B), so quem tinha tempo elegivel (solicitou ate 47 meses)
    c = b[b.d_sol1 <= b.d_age47]; r["C_elegiveis_prop"] = 100 * prop365(c, "d_sol1", "d_enc1"); r["N_C"] = len(c)
    # (D) idem (C), Aalen-Johansen com aging out competindo e censura no painel -> definicao do paper, por ANO de solicitacao
    v, n = cif365(b, "d_sol1", "d_enc1"); r["D_paper_por_ano"] = 100 * v
    # (E) definicao do paper aplicada ao UNIVERSO DA OUTRA FRENTE (1a solicitacao de creche, encaminhamento de creche)
    a2 = a.join(sp.set_index("cd_aluno_sme")[["d_age47"]], how="inner").copy()
    ee = e.groupby("cd_aluno_sme").enc.min(); ee.index = ee.index.astype(str); a2["enc_cre"] = ee.reindex(a2.index)
    allenc = fa[fa.enc.notna() & fa.cd_serie_ensino_encaminhamento.isin(CRE)].groupby("cd_aluno_sme").enc.min(); allenc.index = allenc.index.astype(str)
    a2["enc_cre_any"] = allenc.reindex(a2.index); a2.loc[a2.enc_cre_any < a2.sol_cre, "enc_cre_any"] = pd.NaT
    v2, n2 = cif365(a2, "sol_cre", "enc_cre_any"); r["E_paper_no_universo_U6"] = 100 * v2; r["N_E"] = n2
    rows.append(r)
L = pd.DataFrame(rows); L.to_csv(os.path.join(OUT, "defs_ladder.csv"), index=False)
pd.set_option("display.width", 250); print("\nEscada de definicoes (%):"); print(L.round(1).to_string(index=False))
# paper por coorte de nascimento (Tabela 1) para comparacao
print("\nPaper, por coorte de nascimento (Tabela 1, ref365): 2010 56,3 | 2011 53,0 | 2012 63,1 | 2013 75,3 | 2014 76,1 | 2015 81,4 | 2016 87,6")
