# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# FASE 2, etapas 1.4 e 1.5 (25/10/2026). Descritivo.
# 1.4: onde esta o degrau no registro de encaminhamentos e quanto da coorte de 2013 ele toca.
# 1.5: encaminhamento em 1 ano por semestre de solicitacao, antes e depois da reforma de jul./2016 (Portaria 4.993, 14/07/2016).
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
NE_SME = _os_ne.environ.get("NE_DADOS_SME", _os_ne.path.normpath(_os_ne.path.join(NE_ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")))
import sys, os, numpy as np, pandas as pd, pyreadstat; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; OUT = os.path.join(ROOT, r"03_build\build15")
PANEL = pd.Timestamp("2019-11-28")
fa, _ = pyreadstat.read_dta((NE_SME + r"\processados\derivados_de_brutos\Fila1018.dta"),
                            usecols=["cd_aluno_sme", "dt_encaminhamento", "an_letivo_encaminhamento"])
fa["enc"] = pd.to_datetime(fa.dt_encaminhamento, format="%d/%m/%Y %H:%M:%S", errors="coerce")
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"), columns=["ano_nasc", "d_sol1", "d_enc1", "d_mat1", "d_age47"])
# --- 1.4a: linhas de encaminhamento x primeiros encaminhamentos, por semestre do encaminhamento ---
fa["sem"] = fa.enc.dt.year.astype("Int64").astype(str) + "S" + np.where(fa.enc.dt.month <= 6, "1", "2")
rows = fa[fa.enc.notna()].groupby("sem").size().rename("linhas_enc")
fe = sp[sp.d_enc1.notna()]; fe_sem = (fe.d_enc1.dt.year.astype(str) + "S" + np.where(fe.d_enc1.dt.month <= 6, "1", "2"))
T = pd.concat([rows, fe_sem.value_counts().rename("primeiros_enc")], axis=1).loc[[f"{y}S{h}" for y in range(2010, 2019) for h in (1, 2)]]
T["linhas_por_primeiro"] = (T.linhas_enc / T.primeiros_enc).round(2)
T.to_csv(os.path.join(OUT, "degrau_semestral.csv")); print("1.4a por semestre do encaminhamento:"); print(T.to_string())
# --- 1.4b: quanto da coorte de 2013 (amostra de duracao) solicitou dentro da janela do degrau (jul./2012-dez./2013) ---
c13 = sp[(sp.ano_nasc == 2013) & (sp.d_sol1 <= sp.d_age47)]
inw = (c13.d_sol1 >= "2012-07-01") & (c13.d_sol1 < "2014-01-01")
print(f"\n1.4b coorte 2013, amostra de duracao N={len(c13):,}: solicitou em jul/2012-dez/2013 = {100 * inw.mean():.1f}%")
# --- funcao CIF (Aalen-Johansen; aging out competindo; censura no painel) ---
def cif365(df, t1="d_enc1"):
    df = df[df.d_sol1 <= df.d_age47]
    tr = (df[t1] - df.d_sol1).dt.days.where(df[t1] >= df.d_sol1); ta = (df.d_age47 - df.d_sol1).dt.days; tc = (PANEL - df.d_sol1).dt.days
    Tt = np.fmin(np.fmin(tr.fillna(np.inf), ta), tc).values
    ev = np.where(tr.fillna(np.inf).values <= np.minimum(ta, tc).values, 1, np.where(ta.values <= tc.values, 2, 0))
    o = np.argsort(Tt, kind="mergesort"); Tt, ev = Tt[o], ev[o]; n = len(Tt); S = 1.0; c = 0.0; i = 0
    while i < n and Tt[i] <= 365:
        j = i
        while j < n and Tt[j] == Tt[i]: j += 1
        d1 = (ev[i:j] == 1).sum(); d2 = (ev[i:j] == 2).sum(); r = n - i; c += S * d1 / r; S *= 1 - (d1 + d2) / r; i = j
    return round(c, 3), len(df)
# --- 1.5: por semestre de solicitacao, 2013S1 a 2018S1 (365 dias de seguimento ate nov./2019 exigem solicitacao ate nov./2018) ---
r = []
for y in range(2013, 2019):
    for h in (1, 2):
        if (y, h) == (2018, 2): continue
        a = pd.Timestamp(y, 1 if h == 1 else 7, 1); b = pd.Timestamp(y, 7, 1) if h == 1 else pd.Timestamp(y + 1, 1, 1)
        s = sp[(sp.d_sol1 >= a) & (sp.d_sol1 < b)]
        ref, n = cif365(s); mat, _ = cif365(s, "d_mat1")
        r.append(dict(semestre=f"{y}S{h}", N=n, ref365=ref, mat365=mat, pos_reforma=a >= pd.Timestamp(2016, 7, 1)))
R = pd.DataFrame(r); R.to_csv(os.path.join(OUT, "reforma_semestral.csv"), index=False)
print("\n1.5 encaminhamento e matricula em 365 dias por semestre de solicitacao:"); print(R.to_string(index=False))
pre = R[~R.pos_reforma]; pos = R[R.pos_reforma]
print(f"pre-reforma (2013S1-2016S1): ref {pre.ref365.iloc[0]:.3f} -> {pre.ref365.iloc[-1]:.3f} ({pre.ref365.iloc[-1] - pre.ref365.iloc[0]:+.3f}) | "
      f"pos-reforma (2016S2-2018S1): ref {pos.ref365.iloc[0]:.3f} -> {pos.ref365.iloc[-1]:.3f} ({pos.ref365.iloc[-1] - pos.ref365.iloc[0]:+.3f}) | "
      f"salto 2016S1->2016S2: {pos.ref365.iloc[0] - pre.ref365.iloc[-1]:+.3f}")
# coortes: quanto de cada coorte solicitou depois de jul./2016
for co in range(2013, 2017):
    s = sp[(sp.ano_nasc == co) & (sp.d_sol1 <= sp.d_age47)]
    print(f"coorte {co}: solicitou a partir de jul./2016 = {100 * (s.d_sol1 >= '2016-07-01').mean():.1f}%")
