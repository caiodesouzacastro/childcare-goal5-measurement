# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# MANHA, etapa 1.4 (26/10/2026): nivel corrigido das coortes de cobertura incompleta, substitui build17_c1b.py.
# Corrige as duas falhas do FATAIS:
#  (F2) limites contaminados por entrantes de 2019: aqui so entram entradas ate dez./2018 (a fila termina em dez./2018);
#  (F4) imputacao mal calibrada no registro precoce (47,9% imputado contra 55,4% observado): a imputacao antiga sorteava
#       a defasagem entrada - solicitacao sem condicionar na idade de entrada (so truncava). Aqui cada entrante sem
#       solicitacao anterior a entrada recebe a MEDIA DA CELULA (idade na entrada em meses x entrada em fevereiro) entre
#       entrantes cobertos de referencia. Duas referencias, reportadas como faixa:
#         R1 = entrantes cobertos que entraram em 2014-2017 (comportamento da janela);
#         R2 = entrantes cobertos do MESMO ano de entrada (contemporaneos; supoe ausencia ao acaso dentro de ano x idade x mes).
#       Calibracao fora da amostra de R1: entrantes cobertos que entraram em 2013 (nao fazem parte de R1), e o teste antigo
#       (cobertos das coortes 2013-2014). R2 reproduz por construcao os cobertos e nao tem teste fora da amostra.
#  Dupla contagem (nova verificacao): ausentes que tem solicitacao registrada DEPOIS da entrada ja estao no N do spine;
#  aqui eles saem do N (com a sua contribuicao observada) e entram uma vez so, como ausentes.
# Desfechos: encaminhamento e matricula em 365 dias da solicitacao (proporcoes; coortes de 2010-2016 com seguimento
# completo de 365 dias, e a censura antes de 365 dias e nula nas coortes 2010-2016 elegiveis); registro antes de 12 meses
# (% dos nascidos vivos, denominador 96 distritos). Descritivo. Saida: 03_build/build18/nivel_corrigido.csv, nivel_calibracao.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, csv, numpy as np, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; OUT = os.path.join(ROOT, r"03_build\build18"); os.makedirs(OUT, exist_ok=True)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
def save(df, name):
    p = os.path.join(OUT, name); df.to_csv(p, index=False); chk = pd.read_csv(p)
    assert len(chk) == len(df), name; print(f"[gravado e relido] {p} ({len(chk)} linhas)")
key = lambda s: pd.to_numeric(s, errors="coerce").astype("Int64")
rr = list(csv.reader(open(os.path.join(ROOT, r"01_dados_publicos\ceinfo\sinasc_nv_distrito_2006_2026.csv"), encoding="utf-8"), delimiter=";"))
BIRTHS = {int(h): sum(int(x[i]) for x in rr[1:] if x and x[0].strip() not in ("Ignorado", "Total")) for i, h in enumerate(rr[0]) if h.isdigit()}
jc = pd.read_csv(os.path.join(ROOT, r"03_build\build14_cobertura\janela_cif.csv")); co = jc[jc.serie == "coorte"].assign(g=lambda d: d.grupo.astype(int)).set_index("g")
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"),
                     columns=["cd_aluno_sme", "ano_nasc", "idade_sol", "d_sol1", "d_enc1", "d_mat1", "d_age47"])
sp["id"] = key(sp.cd_aluno_sme); sp = sp.dropna(subset=["id"]).drop_duplicates("id").set_index("id")
sp["elig"] = sp.d_sol1 <= sp.d_age47
sp["ref1"] = sp.d_enc1.notna() & (sp.d_enc1 >= sp.d_sol1) & ((sp.d_enc1 - sp.d_sol1).dt.days <= 365) & (sp.d_enc1 <= sp.d_age47)
sp["mat1"] = sp.d_mat1.notna() & (sp.d_mat1 >= sp.d_sol1) & ((sp.d_mat1 - sp.d_sol1).dt.days <= 365) & (sp.d_mat1 <= sp.d_age47)
sp["lt12"] = sp.idade_sol < 12
# validacao: proporcoes simples contra a CIF publicada (Tabela 1 / P2_endpoint), coortes elegiveis
for c in (2010, 2012, 2016):
    g = sp[(sp.ano_nasc == c) & sp.elig]
    print(f"validacao coorte {c}: N={len(g):,} (pub {int(co.N[c]):,}) ref1 {g.ref1.mean():.3f} (CIF {co.ref365[c]:.3f}) mat1 {g.mat1.mean():.3f} (CIF {co.mat365[c]:.3f}) "
          f"<12m {100 * (sp[sp.ano_nasc == c].lt12.sum()) / BIRTHS[c]:.1f}")
e = pd.read_parquet(os.path.join(ROOT, r"03_build\build14_cobertura\eol_creche.parquet"), columns=["CD_ALUNO_SME", "AN_LETIVO", "DT_IN_MAT", "ANO_NASC_ALUNO", "MES_NASC_ALUNO"])
e["id"] = key(e.CD_ALUNO_SME); e["an"] = pd.to_numeric(e.AN_LETIVO, errors="coerce"); e["dt"] = pd.to_datetime(e.DT_IN_MAT.str[:19], errors="coerce")
f = e.dropna(subset=["id", "dt"]).sort_values(["id", "an", "dt"]).groupby("id").first()
f["an_n"] = pd.to_numeric(f.ANO_NASC_ALUNO, errors="coerce"); f["me_n"] = pd.to_numeric(f.MES_NASC_ALUNO, errors="coerce")
f["idade"] = (f.dt.dt.year - f.an_n) * 12 + (f.dt.dt.month - f.me_n)
f = f[(f.dt < "2019-01-01") & f.idade.between(0, 47)].copy()                     # (F2) entradas ate 2018
f = f.join(sp[["d_sol1", "elig", "ref1", "mat1", "lt12", "ano_nasc"]], how="left")
f["cob"] = f.d_sol1.notna() & (f.d_sol1 < f.dt); f["fev"] = f.dt.dt.month == 2; f["ano_ent"] = f.dt.dt.year
f["cel"] = f.idade.astype(int).astype(str) + "|" + f.fev.astype(str)
cov = f[f.cob]
R1 = cov[(cov.ano_ent >= 2014) & (cov.ano_ent <= 2017)].groupby("cel")[["lt12", "ref1", "mat1"]].mean()
R2 = cov.groupby(["ano_ent", "cel"])[["lt12", "ref1", "mat1"]].mean()
def imput(g, ref):
    if ref == "R1": m = g[["cel"]].join(R1, on="cel")
    else: m = g[["ano_ent", "cel"]].join(R2, on=["ano_ent", "cel"])
    # celula sem referencia: media da referencia na mesma idade (qualquer mes); depois media geral (registra quantas)
    miss = m.lt12.isna()
    if miss.any():
        alt = (cov[(cov.ano_ent >= 2014) & (cov.ano_ent <= 2017)] if ref == "R1" else cov).assign(i=lambda d: d.idade.astype(int)).groupby("i")[["lt12", "ref1", "mat1"]].mean()
        m.loc[miss, ["lt12", "ref1", "mat1"]] = alt.reindex(g.idade[miss].astype(int).values).values
    return m[["lt12", "ref1", "mat1"]].astype(float), int(miss.sum())
# ---------- calibracao de R1 ----------
cal = []
for lab, g in (("cobertos que entraram em 2013 (fora de R1)", cov[cov.ano_ent == 2013]), ("cobertos das coortes 2013-2014 (teste do FATAIS)", cov[cov.an_n.isin([2013, 2014])])):
    m, nm = imput(g, "R1")
    for v, nome in (("lt12", "solicitou antes de 12 meses"), ("ref1", "encaminhado em 365 dias"), ("mat1", "matriculado em 365 dias")):
        cal.append(dict(grupo=lab, N=len(g), desfecho=nome, observado=round(100 * g[v].mean(), 1), imputado_R1=round(100 * m[v].mean(), 1), celulas_sem_ref=nm))
CAL = pd.DataFrame(cal); print(CAL.to_string(index=False)); save(CAL, "nivel_calibracao.csv")
# ---------- niveis corrigidos ----------
rows = []
for c in range(2010, 2017):
    g = f[(f.an_n == c) & ~f.cob]; M = len(g)
    inN = g[g.d_sol1.notna() & (g.elig == True)]; k = len(inN)                 # ausentes ja no N (solicitacao depois da entrada)
    base = sp[(sp.ano_nasc == c) & sp.elig]; N = len(base); births = BIRTHS[c]
    row = dict(coorte=c, N=N, M_ausentes=M, M_pct_N=round(100 * M / N, 1), M_ja_no_N=k)
    for v, lab in (("ref1", "ref"), ("mat1", "mat")):
        obs = base[v].sum(); obs_k = inN[v].sum(); den = N - k + M
        row[f"{lab}_obs"] = round(obs / N, 3)
        row[f"{lab}_inf"] = round((obs - obs_k) / den, 3); row[f"{lab}_sup"] = round((obs - obs_k + M) / den, 3)
        for R in ("R1", "R2"):
            m, nm = imput(g, R); row[f"{lab}_{R}"] = round((obs - obs_k + m[v].sum()) / den, 3); row[f"sem_ref_{R}"] = nm
    already = g.lt12.fillna(False).astype(bool)                                  # ausente com solicitacao registrada antes de 12 meses: ja contado
    r12 = 100 * sp[sp.ano_nasc == c].lt12.sum() / births
    row["reg12_obs"] = round(r12, 1); row["reg12_sup"] = round(r12 + 100 * (~already).sum() / births, 1)
    for R in ("R1", "R2"):
        m, _ = imput(g, R); row[f"reg12_{R}"] = round(r12 + 100 * m.lt12[~already.values].sum() / births, 1)
    rows.append(row)
L = pd.DataFrame(rows); print(L.to_string(index=False)); save(L, "nivel_corrigido.csv")
# ---------- artefato nos ganhos (2010 -> 2016 e 2012 -> 2016) ----------
L = L.set_index("coorte"); A = []
for c0 in (2010, 2011, 2012):
    for lab, d in (("ref", 3), ("mat", 3), ("reg12", 1)):
        o = L[f"{lab}_obs"][2016] - L[f"{lab}_obs"][c0]
        out = dict(inicio=c0, medida=lab, ganho_observado=round(o, d))
        for R in ("R1", "R2"):
            g_ = L[f"{lab}_{R}"][2016] - L[f"{lab}_{R}"][c0]; out[f"ganho_{R}"] = round(g_, d); out[f"artefato_{R}"] = round(o - g_, d); out[f"artefato_pct_{R}"] = round(100 * (o - g_) / o, 0)
        if lab != "reg12":
            out["ganho_lim_2016obs"] = f"[{L[f'{lab}_obs'][2016] - L[f'{lab}_sup'][c0]:.3f}, {L[f'{lab}_obs'][2016] - L[f'{lab}_inf'][c0]:.3f}]"
            out["ganho_lim_ambos"] = f"[{L[f'{lab}_inf'][2016] - L[f'{lab}_sup'][c0]:.3f}, {L[f'{lab}_sup'][2016] - L[f'{lab}_inf'][c0]:.3f}]"
        else:
            out["ganho_lim_2016obs"] = f"[{L['reg12_obs'][2016] - L['reg12_sup'][c0]:.1f}, {o:.1f}]"
            out["ganho_lim_ambos"] = f"[{L['reg12_obs'][2016] - L['reg12_sup'][c0]:.1f}, {L['reg12_sup'][2016] - L['reg12_obs'][c0]:.1f}]"
        A.append(out)
A = pd.DataFrame(A); print(A.to_string(index=False)); save(A, "nivel_artefato.csv")
