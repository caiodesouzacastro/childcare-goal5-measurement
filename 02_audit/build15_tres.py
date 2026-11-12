# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# FASE 2, etapa 1.1 (25/10/2026): os tres numeros que nao reproduziram, recalculados com a LOGICA ORIGINAL
# (build08_faixa.py A3, build07.py A2, build10.py C4), primeiro na amostra publicada e depois em solicitacoes 2013+.
# Copia fiel das definicoes; muda so o caminho dos arquivos (a maquina atual). Saida: 03_build/build15/tres.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
NE_SME = _os_ne.environ.get("NE_DADOS_SME", _os_ne.path.normpath(_os_ne.path.join(NE_ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")))
import sys, os, numpy as np, pandas as pd, pyreadstat; sys.stdout.reconfigure(encoding="utf-8")
ROOT = NE_ROOT; OUT = os.path.join(ROOT, r"03_build\build15"); os.makedirs(OUT, exist_ok=True)
FILA = (NE_SME + r"\processados\derivados_de_brutos\Fila1018.dta")
fa, _ = pyreadstat.read_dta(FILA, usecols=["cd_aluno_sme", "dt_solicitacao", "cd_serie_ensino_solicitacao", "an_letivo_solicitacao"])
fa["d_sol"] = pd.to_datetime(fa.dt_solicitacao, format="%d/%m/%Y %H:%M:%S", errors="coerce")
first = fa.sort_values("d_sol").groupby("cd_aluno_sme").agg(d_sol1=("d_sol", "min"), anlet=("an_letivo_solicitacao", "first")).reset_index()
first["anlet"] = pd.to_numeric(first.anlet, errors="coerce")
cm = pd.read_feather(os.path.join(ROOT, r"03_build\build01\_staging\child_master.feather"),
                     columns=["cd_aluno_sme", "idade_sol", "agrup_sol", "ano_sol", "ano_nasc", "mes_nasc", "d_sol"])
cm["cd_aluno_sme"] = cm.cd_aluno_sme.astype(str); first["cd_aluno_sme"] = first.cd_aluno_sme.astype(str)
d = cm.merge(first, on="cd_aluno_sme", how="inner")
print("frame:", f"{len(d):,}", flush=True)
REQ = {"BERC1": 1, "BERC2": 2, "MINI1": 3, "MINI2": 4}
def band(m):
    if pd.isna(m): return np.nan
    return 1 if m < 14 else 2 if m < 23 else 3 if m < 35 else 4 if m < 47 else 5
rows = []
for lab, flt in (("publicado", d.d_sol1.notna()), ("solicitacoes 2013+", d.d_sol1 >= "2013-01-01")):
    x = d[flt].copy()
    # build08 A3: faixa solicitada x faixa pela idade em 31/03 do ano letivo
    x["req8"] = x.agrup_sol.map(REQ).fillna(5).astype(int)
    x["idade_3103"] = (x.anlet - x.ano_nasc) * 12 + (3 - x.mes_nasc); x["band_3103"] = x.idade_3103.map(band); x["cur8"] = x.idade_sol.map(band)
    sub = x[(x.req8.between(1, 4)) & (x.anlet.between(2010, 2019))]
    # build07 A2: classes sobre TODAS as 1as solicitacoes
    x["req7"] = x.agrup_sol.map(REQ); x["cur7"] = x.idade_sol.map(band)
    cls = np.where(x.req7.isna(), "NONCRECHE", np.where(x.req7 == x.cur7, "CURRENT", np.where(x.req7 > x.cur7, "FUTURE", "PAST")))
    rows.append(dict(amostra=lab, N_A3=len(sub), concord_3103=round(100 * (sub.req8 == sub.band_3103).mean(), 1),
                     concord_idade_solic=round(100 * (sub.req8 == sub.cur8).mean(), 1), N_A2=len(x), futura_pct=round(100 * (cls == "FUTURE").mean(), 2)))
# build10 C4 (d = child_master + spine; d_sol do child_master)
sp = pd.read_parquet(os.path.join(ROOT, r"03_build\build10\_staging\spine.parquet"), columns=["cd_aluno_sme", "d_enc1", "d_mat1", "d_rec1", "n_enc_after_rec"])
sp["cd_aluno_sme"] = sp.cd_aluno_sme.astype(str)
q = cm.merge(sp, on="cd_aluno_sme", how="left")
q["d_sol"] = pd.to_datetime(q.d_sol)
q["esp_enc"] = (q.d_enc1 - q.d_sol).dt.days; q["referred"] = q.d_enc1.notna() & (q.esp_enc >= 0)
q["mat_after_enc"] = q.d_mat1.notna() & q.referred & (q.d_mat1 >= q.d_enc1)
c4 = []
for lab, flt in (("publicado", q.d_sol.notna()), ("solicitacoes 2013+", q.d_sol >= "2013-01-01")):
    z = q[flt]; cells = []
    for alo, ahi in ((0, 5), (6, 11), (12, 23), (24, 999)):
        for slo, shi in ((0, 30), (31, 90), (91, 180), (181, 10 ** 9)):
            s = z[z.referred & z.idade_sol.between(alo, ahi) & z.esp_enc.between(slo, shi)]; rr = s[s.d_rec1.notna()]
            cells.append((alo, slo, len(s), 100 * s.mat_after_enc.mean(), 100 * (rr.n_enc_after_rec > 0).mean() if len(rr) else np.nan))
    c4.append(dict(amostra=lab, celula_0_5m_0_30d_N=cells[0][2], celula_0_5m_0_30d_taxa=round(cells[0][3], 1),
                   taxa_min=round(min(c[3] for c in cells), 1), taxa_max=round(max(c[3] for c in cells), 1),
                   rerref_min=round(np.nanmin([c[4] for c in cells]), 1), rerref_max=round(np.nanmax([c[4] for c in cells]), 1)))
A = pd.DataFrame(rows); C = pd.DataFrame(c4)
A.to_csv(os.path.join(OUT, "tres_faixa.csv"), index=False); C.to_csv(os.path.join(OUT, "tres_c4.csv"), index=False)
pd.set_option("display.width", 250); print(A.to_string(index=False)); print(C.to_string(index=False))
print("PUBLICADO: concordancia 31/03 = 83 (build08 A); futura = 1 (build07 A2); C4 celula 0-5m/0-30d N=25,297, 94.5; faixa 82-95 (81.7-95.0); re-ref 53-87")
