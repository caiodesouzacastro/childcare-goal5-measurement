# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# FATAIS, Etapa 3 (26/10/2026), complemento de build17_c1.py: nivel corrigido das coortes de cobertura incompleta.
# (1) Limites (como em build17_c1.py, mas so com entradas ate 2018, porque a fila termina em dez./2018).
# (2) Imputacao sob hipotese explicita: cada entrante do EOL sem solicitacao anterior a entrada recebe a defasagem
#     entrada - solicitacao dos entrantes cobertos de 2014-2017 (fevereiro e demais meses separados), condicionada a nao
#     exceder a idade na entrada. Daí: P(solicitou antes de 12 meses) e P(defasagem <= 365 dias), esta ultima como
#     aproximacao do encaminhamento em 1 ano (o encaminhamento precede a entrada). Calibracao: a mesma regra aplicada aos
#     entrantes COBERTOS das coortes 2013-2014, comparada com o observado. Descritivo. Saida: c1_nivel_corrigido.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, numpy as np, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; OUT = os.path.join(ROOT, r"03_build\build17_fatais")
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
def save(df, name):
    p = os.path.join(OUT, name); df.to_csv(p, index=False); chk = pd.read_csv(p)
    assert len(chk) == len(df), name; print(f"[gravado e relido] {p} ({len(chk)} linhas)")
key = lambda s: pd.to_numeric(s, errors="coerce").astype("Int64")
jc = pd.read_csv(os.path.join(ROOT, r"03_build\build14_cobertura\janela_cif.csv")); co = jc[jc.serie == "coorte"].assign(g=lambda d: d.grupo.astype(int)).set_index("g")
r12 = pd.read_csv(os.path.join(ROOT, r"03_build\build03\_staging\S2a_frac_0_24.csv")).set_index("coorte_nasc")
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"), columns=["cd_aluno_sme", "d_sol1", "d_enc1", "d_birth"])
sp["id"] = key(sp.cd_aluno_sme)
e = pd.read_parquet(os.path.join(ROOT, r"03_build\build14_cobertura\eol_creche.parquet"), columns=["CD_ALUNO_SME", "AN_LETIVO", "DT_IN_MAT", "ANO_NASC_ALUNO", "MES_NASC_ALUNO"])
e["id"] = key(e.CD_ALUNO_SME); e["an"] = pd.to_numeric(e.AN_LETIVO, errors="coerce"); e["dt"] = pd.to_datetime(e.DT_IN_MAT.str[:19], errors="coerce")
f = e.dropna(subset=["id", "dt"]).sort_values(["id", "an", "dt"]).groupby("id").first()
f["an_n"] = pd.to_numeric(f.ANO_NASC_ALUNO, errors="coerce"); f["me_n"] = pd.to_numeric(f.MES_NASC_ALUNO, errors="coerce")
f["nasc"] = pd.to_datetime(dict(year=f.an_n, month=f.me_n, day=1), errors="coerce")
f["idade_d"] = (f.dt - f.nasc).dt.days
f = f.join(sp.set_index("id")[["d_sol1", "d_enc1"]], how="left")
f["cob"] = f.d_sol1.notna() & (f.d_sol1 < f.dt); f["fev"] = f.dt.dt.month == 2
f = f[(f.dt < "2019-01-01") & f.idade_d.between(0, 47 * 30.44)]
base = f[f.cob & (f.dt >= "2014-01-01") & (f.dt < "2018-01-01")]
LAG = {k: np.sort((g.dt - g.d_sol1).dt.total_seconds().values / 86400) for k, g in base.groupby("fev")}
def imput(g):
    p12 = np.zeros(len(g)); p365 = np.zeros(len(g))
    for k in (True, False):
        m = (g.fev == k).values; L = LAG[k]; a = g.idade_d.values[m].astype(float)
        n_le_a = np.searchsorted(L, a, "right")                            # defasagem <= idade na entrada
        n_le_a12 = np.searchsorted(L, np.maximum(a - 365.25, 0), "right")  # solicitou com idade >= 12m  <=> defasagem <= a-365
        n_le_365 = np.searchsorted(L, np.minimum(365, a), "right")
        ok = n_le_a > 0
        p12[m] = np.where(ok, (n_le_a - np.where(a > 365.25, n_le_a12, 0)) / np.maximum(n_le_a, 1), np.nan)
        p365[m] = np.where(ok, n_le_365 / np.maximum(n_le_a, 1), np.nan)
    return p12, p365
# calibracao nos cobertos das coortes 2013-2014
cal = f[f.cob & f.an_n.isin([2013, 2014])].copy(); a12, a365 = imput(cal)
obs12 = ((cal.d_sol1 - cal.nasc).dt.days < 365.25).mean(); obs365 = (cal.d_enc1.notna() & ((cal.d_enc1 - cal.d_sol1).dt.days <= 365)).mean()
print(f"calibracao (entrantes cobertos, coortes 2013-2014, N={len(cal):,}): solicitou <12m observado {100 * obs12:.1f}% vs imputado {100 * np.nanmean(a12):.1f}% | "
      f"encaminhado em 1 ano observado {100 * obs365:.1f}% vs imputado {100 * np.nanmean(a365):.1f}%")
rows = []
for c in range(2010, 2017):
    g = f[(f.an_n == c) & ~f.cob]; M = len(g); N = int(co.N[c]); p = co.ref365[c]; nasc = r12.nascidos[c]
    q12, q365 = imput(g); i12 = np.nansum(q12); i365 = np.nansum(q365)
    rows.append(dict(coorte=c, N=N, ausentes_M=M, ref365=p, ref365_inf=round(p * N / (N + M), 3), ref365_sup=round((p * N + M) / (N + M), 3),
                     ref365_imputado=round((p * N + i365) / (N + M), 3), frac_ausentes_enc_1ano_imput=round(i365 / max(M, 1), 2),
                     reg12m=round(r12.frac_ate12m[c], 1), reg12m_sup=round(r12.frac_ate12m[c] + 100 * M / nasc, 1),
                     reg12m_imputado=round(r12.frac_ate12m[c] + 100 * i12 / nasc, 1), frac_ausentes_sol_12m_imput=round(i12 / max(M, 1), 2)))
R = pd.DataFrame(rows); print(R.to_string(index=False)); save(R, "c1_nivel_corrigido.csv")
