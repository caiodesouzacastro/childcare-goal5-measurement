# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# OQ-5 (25/10/2026): a tab:C6 (build10.py) tem 64 e nao 96 distritos porque os nomes acentuados do arquivo
# cep_renda_pop_2010.dta chegam como escapes literais ("S<C3>O MIGUEL") e nao casam com o evolucaodemanda.csv.
# Este script REPRODUZ a C6 do build10 (mesma especificacao) e a reestima com a decodificacao corrigida.
# Descritivo; NAO altera a tabela do paper. Saida: 03_build/build13_coverage/c6_fix.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
NE_SME = _os_ne.environ.get("NE_DADOS_SME", _os_ne.path.normpath(_os_ne.path.join(NE_ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")))
import sys, os, re, unicodedata, pandas as pd, numpy as np; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = NE_ROOT
def _demean(M, codes, tol=1e-10, maxit=1000):
    M = M.copy()
    for _ in range(maxit):
        prev = M.copy()
        for g in codes:
            cnt = np.bincount(g)
            for j in range(M.shape[1]): M[:, j] -= (np.bincount(g, weights=M[:, j]) / cnt)[g]
        if np.max(np.abs(M - prev)) < tol: break
    return M
def areg(df, y, x, fe, cl):
    sub = df.dropna(subset=[y, x] + fe + [cl]).copy()
    codes = [sub[c].astype("category").cat.codes.values for c in fe]
    r = _demean(sub[[y, x]].astype(float).values, codes); yr, Xr = r[:, 0], r[:, 1:]
    XtXi = np.linalg.inv(Xr.T @ Xr); b = XtXi @ (Xr.T @ yr); e = yr - Xr @ b
    g = pd.DataFrame(Xr * e[:, None]); g["cl"] = sub[cl].values; gs = g.groupby("cl").sum().values; G = len(gs)
    V = XtXi @ (gs.T @ gs) @ XtXi * (G / (G - 1)); return b[0], np.sqrt(V[0, 0]), len(sub), sub[cl].nunique()
def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFD", str(s).strip().upper()) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", s)
def unesc(s): return re.sub(r"<([0-9A-Fa-f]{2})>", lambda m: bytes([int(m.group(1), 16)]).decode("latin-1"), str(s))
cm = pd.read_feather(os.path.join(ROOT, r"03_build\build01\_staging\child_master.feather"), columns=["ano_nasc", "idade_sol", "cep_aluno"])
rd = pd.read_stata((NE_SME + r"\processados\bases_analise\cep_renda_pop_2010.dta"), columns=["cep", "nm_distrit"])
MES = {"jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6, "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12}
ev = pd.read_csv(os.path.join(ROOT, r"03_build\build04\_ext\evolucaodemanda.csv"), sep=";", thousands=".", dtype={"MES_ANO_REF": str})
ev["ano"] = ev.MES_ANO_REF.str[-2:].astype(int) + 2000; ev["mes"] = ev.MES_ANO_REF.str[:3].map(MES)
ev["dn"] = ev["DISTRITO"].map(norm); ev["MAT_CRECHE"] = pd.to_numeric(ev["MAT_CRECHE"], errors="coerce")
m = ev[ev.mes == 12].groupby(["dn", "ano"])["MAT_CRECHE"].sum().reset_index().sort_values(["dn", "ano"])
m["gcap"] = np.log(m.MAT_CRECHE) - np.log(m.groupby("dn").MAT_CRECHE.shift(1))
out = []
for versao, f in (("build10 (original)", norm), ("corrigida", lambda s: norm(unesc(s)))):
    cep2d = dict(zip(rd.cep.astype("int64"), rd.nm_distrit.map(f)))
    d = cm.copy(); d["dn"] = d.cep_aluno.astype("int64").map(cep2d)
    c = d[d.ano_nasc.between(2010, 2016) & d.dn.notna()].copy(); c["early"] = (c.idade_sol < 12).astype(int)
    g = c.groupby(["dn", "ano_nasc"]).early.mean().reset_index()
    for lg in (-1, 0, 1):
        mm = m[["dn", "ano", "gcap"]].copy(); mm["ano_nasc"] = mm.ano - lg
        g = g.merge(mm.rename(columns={"gcap": f"gcap_l{lg}"})[["dn", "ano_nasc", f"gcap_l{lg}"]], on=["dn", "ano_nasc"], how="left")
    g = g.dropna(subset=["gcap_l0"])
    for lg, lab in ((0, "contemporaneous"), (1, "lag"), (-1, "lead")):
        b, se, n, nd = areg(g, "early", f"gcap_l{lg}", ["dn", "ano_nasc"], "dn")
        out.append(dict(versao=versao, timing=lab, coef=round(b, 4), se=round(se, 4), N=n, distritos=nd))
o = pd.DataFrame(out); o.to_csv(os.path.join(ROOT, r"03_build\build13_coverage\c6_fix.csv"), index=False); print(o.to_string())
# 25/10/2026: versao corrigida aprovada pelo autor (OQ-5, defeito). Tabular para a tab:C6 (Apendice A).
fx = o[o.versao == "corrigida"].set_index("timing")
LAB = [("contemporaneous", "contemporaneous (birth year)"), ("lag", "lag (expansion year before)"), ("lead", "lead (expansion year after)")]
def sg(v): return f"+{v:.3f}" if v >= 0 else f"$-${abs(v):.3f}"
T = ["% Gerado por 02_audit/build13_c6fix.py (versao corrigida, 96 distritos). Substitui C6_local.tex (build10, 64 distritos).",
     "\\begin{tabular}{lrrr}", "\\toprule", "Timing & Coef. & (SE) & N \\\\", "\\midrule"]
T += [f"{lab} & {sg(fx.loc[k,'coef'])} & ({fx.loc[k,'se']:.3f}) & {int(fx.loc[k,'N']):,} \\\\" for k, lab in LAB]
T += ["\\bottomrule", "\\end{tabular}"]
open(os.path.join(ROOT, r"04_paper\assets\tables\C6_local_fix.tex"), "w", encoding="utf-8").write("\n".join(T) + "\n")
print("\n".join(T))
