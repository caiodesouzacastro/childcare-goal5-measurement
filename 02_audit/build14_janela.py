# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# COBERTURA_FILA (25/10/2026), item 4: resultados na janela limpa. Cada bloco primeiro REPRODUZ o numero publicado
# (validacao da implementacao) e so depois calcula a janela limpa. Descritivo. Saida: 03_build/build14_cobertura/janela_*.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, numpy as np, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; OUT = os.path.join(ROOT, r"03_build\build14_cobertura")
PANEL = pd.Timestamp("2019-11-28")
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"), columns=["cd_aluno_sme", "ano_nasc", "d_sol1", "d_enc1", "d_mat1", "d_age47"])
def cif365(df, t1):
    df = df[df.d_sol1 <= df.d_age47]
    tr = (df[t1] - df.d_sol1).dt.days.where(df[t1] >= df.d_sol1); ta = (df.d_age47 - df.d_sol1).dt.days; tc = (PANEL - df.d_sol1).dt.days
    T = np.fmin(np.fmin(tr.fillna(np.inf), ta), tc).values
    ev = np.where(tr.fillna(np.inf).values <= np.minimum(ta, tc).values, 1, np.where(ta.values <= tc.values, 2, 0))
    o = np.argsort(T, kind="mergesort"); T, ev = T[o], ev[o]; n = len(T); S = 1.0; c = 0.0; i = 0
    while i < n and T[i] <= 365:
        j = i
        while j < n and T[j] == T[i]: j += 1
        d1 = (ev[i:j] == 1).sum(); d2 = (ev[i:j] == 2).sum(); r = n - i; c += S * d1 / r; S *= 1 - (d1 + d2) / r; i = j
    return round(c, 3), len(df)
rows = []
# (a) por coorte de nascimento: reproduz a Tabela 1 (ref) e a Panel B (matricula)
for co in range(2010, 2017):
    s = sp[sp.ano_nasc == co]; a, n = cif365(s, "d_enc1"); b, _ = cif365(s, "d_mat1")
    rows.append(dict(serie="coorte", grupo=co, N=n, ref365=a, mat365=b))
# (b) por ano de solicitacao: reproduz a Tabela A20 (ref) e acrescenta matricula
for y in range(2010, 2019):
    s = sp[sp.d_sol1.dt.year == y]; a, n = cif365(s, "d_enc1"); b, _ = cif365(s, "d_mat1")
    rows.append(dict(serie="ano_solicitacao", grupo=y, N=n, ref365=a, mat365=b))
# (c) janela alternativa: solicitacoes a partir de 1/mar/2012
s = sp[(sp.d_sol1 >= "2012-03-01") & (sp.d_sol1 < "2013-01-01")]; a, n = cif365(s, "d_enc1"); b, _ = cif365(s, "d_mat1")
rows.append(dict(serie="ano_solicitacao", grupo="2012 (mar-dez)", N=n, ref365=a, mat365=b))
R = pd.DataFrame(rows); R.to_csv(os.path.join(OUT, "janela_cif.csv"), index=False); print(R.to_string(index=False))
print("validacao, Tabela 1 (ref365 por coorte): 0.563 0.530 0.631 0.753 0.761 0.814 0.876 | Panel B (mat): 0.468 0.427 0.523 0.644 0.639 0.686 0.747")
print("validacao, Tabela A20 (ref365 por ano): 0.510 0.351 0.640 0.646 0.684 0.786 0.767 0.903")
# (d) decomposicao por ano de solicitacao (identidade entrada = solicitacao + espera), entre matriculados
cm = pd.read_feather(os.path.join(ROOT, r"03_build\build01\_staging\child_master.feather"), columns=["ano_sol", "ever_mat", "idade_sol", "idade_ent"])
e = cm[cm.ever_mat == 1]
def dec(y0, y1):
    a = e[e.ano_sol == y0]; z = e[e.ano_sol == y1]; de = z.idade_ent.mean() - a.idade_ent.mean(); ds = z.idade_sol.mean() - a.idade_sol.mean()
    return dict(janela=f"{y0}-{y1}", d_entrada=round(de, 2), d_solicitacao=round(ds, 2), d_espera=round(de - ds, 2), share_solic=f"{100 * ds / de:.0f}%")
D = pd.DataFrame([dec(2010, 2018), dec(2010, 2016), dec(2013, 2016), dec(2013, 2017), dec(2013, 2018)]); D.to_csv(os.path.join(OUT, "janela_decomp.csv"), index=False)
print("\nDecomposicao por ano de solicitacao, matriculados (validacao: 2010-2018 -19.09/80%; 2010-2016 -15.11/99%):"); print(D.to_string(index=False))
