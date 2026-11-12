# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# FATAIS, Etapa 1 (26/10/2026): C3, teste de portao. O registro de solicitacao de 2013 em diante e prospectivo
# (o pedido existe antes do encaminhamento/matricula) ou retroativo (criado no ato da matricula)?
# Descritivo; nao escreve em 04_paper. Saidas: 03_build/build17_fatais/c3_*.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
NE_SME = _os_ne.environ.get("NE_DADOS_SME", _os_ne.path.normpath(_os_ne.path.join(NE_ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")))
import sys, os, numpy as np, pandas as pd, pyreadstat; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; OUT = os.path.join(ROOT, r"03_build\build17_fatais"); os.makedirs(OUT, exist_ok=True)
FILA = (NE_SME + r"\processados\derivados_de_brutos\Fila1018.dta")
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
def save(df, name):
    p = os.path.join(OUT, name); df.to_csv(p, index=False)
    chk = pd.read_csv(p)                                   # M8: rele o arquivo
    assert len(chk) == len(df), f"releitura falhou {name}"; print(f"[gravado e relido] {p} ({len(chk)} linhas)")
def key(s): return pd.to_numeric(s, errors="coerce").astype("Int64")

sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"),
                     columns=["cd_aluno_sme", "ano_nasc", "d_sol1", "d_enc1", "d_mat1", "d_des1", "d_rec1", "d_age47"])
sp["id"] = key(sp.cd_aluno_sme); sp["y"] = sp.d_sol1.dt.year
print("spine:", f"{len(sp):,}", "criancas")

# ---------- 1.1 / 1.2: distribuicao dos intervalos por ano da 1a solicitacao ----------
def dist(d, ymask, name):
    rows = []
    for y in range(2010, 2019):
        g = d[ymask == y].dropna()
        days = g.dt.total_seconds() / 86400
        r = dict(medida=name, ano_sol=y, N=len(g))
        if len(g):
            for q in (10, 25, 50, 75, 90): r[f"P{q}"] = round(np.percentile(days, q), 1)
            r["neg_%"] = round(100 * (days < 0).mean(), 2)
            r["lt1d_%"] = round(100 * ((days >= 0) & (days < 1)).mean(), 2)
            for X in (7, 15, 30): r[f"lt{X}d_%"] = round(100 * ((days >= 0) & (days < X)).mean(), 2)
        rows.append(r)
    return rows
R = []
for col, name in (("d_enc1", "sol->enc"), ("d_mat1", "sol->mat")):
    d = sp[col] - sp.d_sol1
    rows = dist(d, sp.y, name)
    same = (sp[col].dt.normalize() == sp.d_sol1.dt.normalize())
    for r in rows:
        m = (sp.y == r["ano_sol"]) & sp[col].notna(); r["mesmo_dia_%"] = round(100 * same[m].mean(), 2) if m.any() else np.nan
    R += rows
D11 = pd.DataFrame(R); print("\n1.1 intervalos em dias (P10..P90), % negativos, % no mesmo dia de calendario, % em [0,X) dias:"); print(D11.to_string(index=False))
save(D11, "c3_intervalos_fila.csv")

# ---------- 1.1b: intervalo solicitacao -> 1a entrada no EOL (registro independente) ----------
e = pd.read_parquet(os.path.join(ROOT, r"03_build\build14_cobertura\eol_creche.parquet"), columns=["CD_ALUNO_SME", "AN_LETIVO", "DT_IN_MAT"])
e["id"] = key(e.CD_ALUNO_SME); e["an"] = pd.to_numeric(e.AN_LETIVO, errors="coerce"); e["dt"] = pd.to_datetime(e.DT_IN_MAT.str[:19], errors="coerce")
first = e.dropna(subset=["id"]).sort_values(["id", "an", "dt"]).groupby("id").first()
first["ano_ent"] = first.an.astype(int)
x = first.join(sp.set_index("id")[["d_sol1"]], how="left")
rows = []
for y in range(2010, 2019):
    g = x[x.ano_ent == y]; cov = g[g.d_sol1.notna()]; d = (cov.dt - cov.d_sol1).dt.total_seconds() / 86400
    r = dict(ano_entrada=y, entrantes=len(g), no_registro=len(cov), pct_no_registro=round(100 * len(cov) / len(g), 1))
    for q in (10, 25, 50, 75, 90): r[f"P{q}_dias"] = round(np.percentile(d, q), 1)
    r["sol_depois_entrada_%"] = round(100 * (d < 0).mean(), 2)
    r["mesmo_dia_%"] = round(100 * (cov.dt.dt.normalize() == cov.d_sol1.dt.normalize()).mean(), 2)
    for X in (7, 30, 90): r[f"antecede_mais_{X}d_%"] = round(100 * (d > X).mean(), 2)
    r["antecede_mais_0d_%_dos_entrantes"] = round(100 * (d > 0).sum() / len(g), 1)
    rows.append(r)
D11b = pd.DataFrame(rows); print("\n1.1b entrantes em creche no EOL: intervalo (entrada EOL - 1a solicitacao), dias. ATENCAO: ate 2011 a data do EOL e o inicio do ano letivo:")
print(D11b.to_string(index=False)); save(D11b, "c3_sol_x_eol.csv")
# meses da 1a solicitacao dos entrantes de fevereiro de 2013 e 2014 (se o pedido fosse criado na matricula, cairia em jan-fev do proprio ano)
for y in (2012, 2013, 2014, 2016):
    g = x[(x.ano_ent == y) & (x.dt.dt.month == 2) & x.d_sol1.notna()]
    per = g.d_sol1.dt.to_period("M").astype(str); v = (100 * per.value_counts(normalize=True)).round(1)
    jf = 100 * ((g.d_sol1.dt.year == y) & (g.d_sol1.dt.month <= 2)).mean()
    print(f"entrantes de fev/{y} no registro (N={len(g):,}): 1a solicitacao em jan-fev/{y}: {jf:.1f}% | principais meses:", v.head(6).to_dict())

# ---------- 1.3: solicitantes que nunca foram encaminhados nem matriculados ----------
inEOL = set(first.index)
rows = []
for y in range(2010, 2019):
    g = sp[sp.y == y]
    never = g.d_enc1.isna() & g.d_mat1.isna()
    rows.append(dict(ano_sol=y, N=len(g), nunca_enc_nem_mat_pct=round(100 * never.mean(), 1), nunca_enc_nem_mat_N=int(never.sum()),
                     nunca_mat_pct=round(100 * g.d_mat1.isna().mean(), 1),
                     nunca_creche_EOL_pct=round(100 * (~g.id.isin(inEOL)).mean(), 1),
                     nunca_nada_e_fora_EOL_pct=round(100 * (never & ~g.id.isin(inEOL)).mean(), 1),
                     desistencia_registrada_pct=round(100 * g.d_des1.notna().mean(), 1)))
D13 = pd.DataFrame(rows); print("\n1.3 por ano da 1a solicitacao:"); print(D13.to_string(index=False)); save(D13, "c3_nunca.csv")

# ---------- 1.4: encaminhamento para escola diferente da matricula; recusas ----------
cols = ["cd_aluno_sme", "dt_solicitacao", "cd_esc_solicitacao", "dt_encaminhamento", "cd_esc_encaminhamento", "dt_matricula", "cd_esc_matricula", "dt_recusa"]
fa, _ = pyreadstat.read_dta(FILA, usecols=cols); print("\nFila1018:", f"{len(fa):,}", "linhas")
FMT = "%d/%m/%Y %H:%M:%S"
for c in ("dt_solicitacao", "dt_encaminhamento", "dt_matricula", "dt_recusa"):
    fa[c] = pd.to_datetime(fa[c].replace("", None), format=FMT, errors="coerce")
fa["id"] = key(fa.cd_aluno_sme)
chk = fa.groupby("id").dt_solicitacao.min().reindex(sp.id.dropna()).values
same = (pd.Series(chk) == sp.d_sol1.values).mean()
print(f"conferencia: 1a solicitacao recalculada neste Fila1018 = d_sol1 do spine em {100 * same:.2f}% das criancas")
y1 = sp.set_index("id").y; fa["y"] = fa.id.map(y1)
rows = []
for y in range(2010, 2019):
    f = fa[fa.y == y]; n_ch = f.id.nunique()
    both = f.dt_encaminhamento.notna() & f.dt_matricula.notna()
    diff_row = both & (f.cd_esc_encaminhamento != f.cd_esc_matricula)
    enc_no_mat = f.dt_encaminhamento.notna() & f.dt_matricula.isna()
    rec = f.dt_recusa.notna()
    sol_ne_enc = f.dt_encaminhamento.notna() & (f.cd_esc_solicitacao != f.cd_esc_encaminhamento)
    # crianca: encaminhada a alguma escola em que nunca se matriculou
    ce = f[f.dt_encaminhamento.notna()].groupby("id").cd_esc_encaminhamento.apply(set)
    cm = f[f.dt_matricula.notna()].groupby("id").cd_esc_matricula.apply(set).reindex(ce.index)
    enc_outra = sum(1 for a, b in zip(ce.values, cm.values) if not isinstance(b, set) or len(a - b) > 0)
    nreq = f.groupby("id").size()
    rows.append(dict(ano_sol=y, criancas=n_ch, linhas=len(f),
                     linhas_enc_e_mat_escola_diferente_pct=round(100 * diff_row.sum() / max(1, both.sum()), 2), linhas_enc_e_mat_escola_diferente_N=int(diff_row.sum()),
                     linhas_enc_sem_mat_N=int(enc_no_mat.sum()),
                     criancas_enc_a_escola_onde_nunca_matriculou_pct=round(100 * enc_outra / n_ch, 1),
                     criancas_com_recusa_pct=round(100 * f[rec].id.nunique() / n_ch, 1), recusas_N=int(rec.sum()),
                     enc_escola_diferente_da_pedida_pct=round(100 * sol_ne_enc.sum() / max(1, f.dt_encaminhamento.notna().sum()), 1),
                     criancas_2mais_solicitacoes_pct=round(100 * (nreq >= 2).mean(), 1)))
D14 = pd.DataFrame(rows); print("\n1.4 por ano da 1a solicitacao da crianca:"); print(D14.to_string(index=False)); save(D14, "c3_escolas_recusas.csv")
