# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# FUSAO (26/10/2026): robustezes 1 a 3 da triagem (FECHAMENTO_C.md, itens (C) 1-3), autorizadas pelo autor. Descritivo.
# (R1) Braco A com outros denominadores: populacao 0-3 do Censo 2022 (IBGE/SIDRA 9514, data de referencia 31/7/2022) e
#      nascidos vivos de residentes (SINASC/CEInfo) nos quatro anos anteriores a data do Censo Escolar (maio):
#      pool(Y) = 7/12 NV(Y-4) + NV(Y-3) + NV(Y-2) + NV(Y-1) + 5/12 NV(Y)  [nascidos de jun/(Y-4) a mai/Y]
#      e a definicao do paper antigo, NV(Y-3)+...+NV(Y). Reconciliacao: matricula EOL de dezembro (SME) x Censo de maio
#      (municipal + conveniada) do mesmo ano e do ano seguinte.
# (R2) Decomposicao da variacao do estoque reconstruido (spine) entre fins de trimestre, 2013-2018:
#      S(t2) - S(t1) = novos - encaminhados - aging out - desistencias; e a fracao dos encaminhamentos de dezembro
#      feitos ate a data de extracao impressa na publicacao de dezembro.
# (R3) Estoque medio anual (media das contagens trimestrais publicadas) e a parcela atendida media no ano; variacao
#      2013->2017 e 1o ano >= 75% por mes e pela media.
# Saidas: 03_build/build22/robustez_*.csv e robustez.log; tentativa 3: tabelas 04_paper/assets/tables/c/C_armA_rob_body.tex e C_decomp_body.tex
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, json; sys.stdout.reconfigure(encoding="utf-8")
import numpy as np, pandas as pd
ROOT = (NE_ROOT + "/"); OUT = ROOT + "03_build/build22/"; os.makedirs(OUT, exist_ok=True)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
def save(df, n):
    p = OUT + n; df.to_csv(p, index=False); assert len(pd.read_csv(p)) == len(df); print("[gravado e relido]", p)

# ======================= (R1)
print("=" * 30, "(R1) braco A com outros denominadores")
B = pd.read_csv(ROOT + "03_build/build20/bracos_ano.csv")
J = json.load(open(ROOT + "04_paper/referee_EE_2026-10/fontes_saidaC/censo2022/sidra9514_sp_idade.json", encoding="utf-8"))
ages = {r["D5N"]: int(r["V"]) for r in J[1:] if r["D4N"] == "Total" and r["D6N"] == "Total"}
c22 = sum(ages[k] for k in ("Menos de 1 ano", "1 ano", "2 anos", "3 anos"))
print("Censo 2022, SP, 0-3 anos:", {k: ages[k] for k in ("Menos de 1 ano", "1 ano", "2 anos", "3 anos")}, "soma", c22, "| 0 a 4 anos:", ages.get("0 a 4 anos"))
seade22 = int(B.loc[B.ano == 2022, "pop_0a3"].iloc[0])
print(f"SEADE 2022 (interpolado): {seade22} | Censo 2022: {c22} | SEADE/Censo - 1 = {100 * (seade22 / c22 - 1):+.1f}%")
nv = pd.read_csv(ROOT + "01_dados_publicos/ceinfo/sinasc_nv_distrito_2006_2026.csv", sep=";", encoding="latin-1")
nv = nv[nv.iloc[:, 0] == "Total"].iloc[0]
NV = {int(c): int(nv[c]) for c in nv.index[1:] if c.isdigit()}
print("NV total por ano:", NV)
R1 = B[["ano", "pop_0a3", "matA_total", "matA_munconv", "matA_idade_total", "A_total", "A_munconv", "A_idade_total", "mat_eol_dez"]].copy()
def pool_w(y): return 7 / 12 * NV[y - 4] + NV[y - 3] + NV[y - 2] + NV[y - 1] + 5 / 12 * NV[y] if y - 4 in NV else np.nan
def pool_o(y): return NV[y - 3] + NV[y - 2] + NV[y - 1] + NV[y] if y - 3 in NV else np.nan
R1["pool_nv_maio"] = R1.ano.map(pool_w); R1["pool_nv_antigo"] = R1.ano.map(pool_o)
R1["pop_ancorada_c22"] = R1.pop_0a3 * c22 / seade22   # SEADE reescalado pela razao Censo/SEADE de 2022
for d in ("pool_nv_maio", "pool_nv_antigo", "pop_ancorada_c22"):
    R1["A_total_" + d] = 100 * R1.matA_total / R1[d]
    R1["A_idade_" + d] = 100 * R1.matA_idade_total / R1[d]
    R1["A_munconv_" + d] = 100 * R1.matA_munconv / R1[d]
R1["A_total_censo22"] = np.where(R1.ano == 2022, 100 * R1.matA_total / c22, np.nan)
R1["A_idade_censo22"] = np.where(R1.ano == 2022, 100 * R1.matA_idade_total / c22, np.nan)
R1["pool_sobre_seade"] = R1.pool_nv_maio / R1.pop_0a3
show = ["ano", "pop_0a3", "pool_nv_maio", "pool_sobre_seade", "A_total", "A_total_pool_nv_maio", "A_total_pool_nv_antigo",
        "A_total_pop_ancorada_c22", "A_idade_total", "A_idade_pool_nv_maio", "A_munconv", "A_munconv_pool_nv_maio", "A_total_censo22"]
print(R1[R1.ano <= 2024][show].to_string(index=False, float_format=lambda v: f"{v:,.2f}"))
for c in ("A_total", "A_total_pool_nv_maio", "A_total_pool_nv_antigo", "A_total_pop_ancorada_c22", "A_idade_total",
          "A_idade_pool_nv_maio", "A_idade_pop_ancorada_c22", "A_munconv", "A_munconv_pool_nv_maio", "A_munconv_pop_ancorada_c22"):
    s = R1[(R1.ano <= 2024)].dropna(subset=[c]); i = s[c].idxmax()
    print(f"  {c}: maximo {s.loc[i, c]:.1f} em {int(s.loc[i, 'ano'])}; anos >= 75: {s[s[c] >= 75].ano.astype(int).tolist()}")
print(f"  2022 com Censo 2022 como denominador: estagio {100 * R1.loc[R1.ano == 2022, 'matA_total'].iloc[0] / c22:.1f} | idade {100 * R1.loc[R1.ano == 2022, 'matA_idade_total'].iloc[0] / c22:.1f}")
# reconciliacao EOL dezembro x Censo maio (municipal + conveniada)
R1["eol_dez_sobre_censo_maio_mesmo"] = R1.mat_eol_dez / R1.matA_munconv
R1["eol_dez_sobre_censo_maio_seguinte"] = R1.mat_eol_dez / R1.matA_munconv.shift(-1)
print(R1[R1.ano.between(2008, 2021)][["ano", "mat_eol_dez", "matA_munconv", "eol_dez_sobre_censo_maio_mesmo", "eol_dez_sobre_censo_maio_seguinte"]].to_string(index=False, float_format=lambda v: f"{v:,.3f}"))
# tentativa 2: denominador interpolado entre os Censos 2010 (564.210, SIDRA 1378; referencia 1/8/2010) e 2022 (31/7/2022),
# linear por ano; 2023-2024 sem Censo (nao extrapolado). E o braco que obriga em dezembro com cada denominador.
c10 = 564210
R1["pop_censos"] = np.where(R1.ano.between(2010, 2022), c10 + (R1.ano - 2010) / 12 * (c22 - c10), np.nan)
for n, col in (("stage", "matA_total"), ("idade", "matA_idade_total"), ("munconv", "matA_munconv")):
    R1[f"A_{n}_censos"] = 100 * R1[col] / R1.pop_censos
print(R1[R1.ano.between(2010, 2022)][["ano", "pop_0a3", "pop_censos", "A_total", "A_stage_censos", "A_idade_censos", "A_munconv_censos"]].to_string(index=False, float_format=lambda v: f"{v:,.1f}"))
for n in ("stage", "idade", "munconv"):
    s = R1.dropna(subset=[f"A_{n}_censos"]); print(f"  A_{n}_censos: anos >= 75: {s[s[f'A_{n}_censos'] >= 75].ano.astype(int).tolist()}; maximo {s[f'A_{n}_censos'].max():.1f}")
print(f"  razao pool NV / Censo: 2010 {R1.loc[R1.ano == 2010, 'pool_nv_maio'].iloc[0] / c10:.3f}; 2022 {R1.loc[R1.ano == 2022, 'pool_nv_maio'].iloc[0] / c22:.3f}")
R1 = R1.merge(B[["ano", "exigB_dez", "exigB_set", "dem_dez"]], on="ano", how="left")
for d in ("pop_0a3", "pop_censos", "pool_nv_maio"):
    R1[f"AsobreB_dez_{d}"] = 0.75 * R1[d] / R1.exigB_dez
    s = R1.dropna(subset=[f"AsobreB_dez_{d}"])
    print(f"  braco que obriga (dez), denominador {d}: B obriga em {s[s[f'AsobreB_dez_{d}'] < 1].ano.astype(int).tolist()}; A/B 2022 = {s.loc[s.ano == 2022, f'AsobreB_dez_{d}'].round(3).tolist()}")
save(R1, "robustez_R1_bracoA.csv")

# ======================= (R2)
print("=" * 30, "(R2) decomposicao da variacao do estoque reconstruido")
sp = pd.read_parquet(ROOT + "03_build/build10/_staging/spine.parquet", columns=["d_sol1", "d_enc1", "d_age47", "d_des1"])
INF = pd.Timestamp(2100, 1, 1)
E = pd.DataFrame({"enc": sp.d_enc1.fillna(INF), "age": sp.d_age47.fillna(INF), "des": sp.d_des1.fillna(INF)})
sp["saida"] = E.min(axis=1); sp["tipo"] = E.idxmin(axis=1)
sp = sp[sp.saida > sp.d_sol1]   # quem nunca esteve na fila (saida <= solicitacao) nao entra
def fim(y, m): return pd.Timestamp(y, m, 1) + pd.offsets.MonthEnd(0) + pd.Timedelta(hours=23, minutes=59, seconds=59)
def stock(t): return int(((sp.d_sol1 <= t) & (sp.saida > t)).sum())
D = []
for y in range(2013, 2019):
    for (a, ma), (b, mb) in (((y - 1, 12), (y, 3)), ((y, 3), (y, 6)), ((y, 6), (y, 9)), ((y, 9), (y, 12))):
        t1, t2 = fim(a, ma), fim(b, mb)
        if t2 > pd.Timestamp(2019, 11, 28): continue
        nov = int(((sp.d_sol1 > t1) & (sp.d_sol1 <= t2)).sum())
        sai = sp[(sp.saida > t1) & (sp.saida <= t2)]
        r = dict(ano=y, trecho=f"{ma:02d}->{mb:02d}", S1=stock(t1), S2=stock(t2), novos=nov,
                 encaminhados=int((sai.tipo == "enc").sum()), aging_out=int((sai.tipo == "age").sum()), desistencias=int((sai.tipo == "des").sum()))
        r["fecha"] = r["S1"] + r["novos"] - r["encaminhados"] - r["aging_out"] - r["desistencias"] - r["S2"]
        D.append(r)
D = pd.DataFrame(D); assert (D.fecha == 0).all(), "identidade nao fecha"
D["var"] = D.S2 - D.S1; D["var_pct"] = 100 * D["var"] / D.S1
D["enc_pct_S1"] = 100 * D.encaminhados / D.S1; D["novos_pct_S1"] = 100 * D.novos / D.S1
D["age_pct_S1"] = 100 * D.aging_out / D.S1; D["des_pct_S1"] = 100 * D.desistencias / D.S1
print(D.to_string(index=False, float_format=lambda v: f"{v:,.1f}"))
sd = D[D.trecho == "09->12"]
print("set->dez 2013-2018, somas: S1", sd.S1.sum(), "novos", sd.novos.sum(), "enc", sd.encaminhados.sum(), "aging", sd.aging_out.sum(), "des", sd.desistencias.sum())
print("set->dez: saidas por tipo, % das saidas:", {k: round(100 * sd[k].sum() / sd[["encaminhados", "aging_out", "desistencias"]].sum().sum(), 1) for k in ("encaminhados", "aging_out", "desistencias")})
for tr in ("12->03", "03->06", "06->09", "09->12"):
    s = D[(D.trecho == tr) & D.ano.between(2013, 2017)]
    print(f"  trecho {tr} (2013-2017): encaminhados medios {s.encaminhados.mean():,.0f} ({s.enc_pct_S1.mean():.1f}% de S1); novos medios {s.novos.mean():,.0f}; aging {s.aging_out.mean():,.0f}; desist {s.desistencias.mean():,.0f}")
save(D, "robustez_R2_decomposicao.csv")
# encaminhamentos de dezembro antes e depois da data de extracao
dt = pd.read_csv(ROOT + "03_build/build19/datas_extracao.csv")
dt = dt[(dt.mes == 12) & dt.data_extracao.notna()].assign(dx=lambda d: pd.to_datetime(d.data_extracao, format="%d/%m/%Y"))
X = []
for y in range(2013, 2019):
    r = dt[dt.ano == y]
    t1, t2 = fim(y, 9), fim(y, 12)
    enc = sp[(sp.saida > t1) & (sp.saida <= t2) & (sp.tipo == "enc")].saida
    encdez = enc[enc.dt.month == 12]
    x = dict(ano=y, enc_set_dez=len(enc), enc_dezembro=len(encdez), pct_enc_set_dez_em_dezembro=100 * len(encdez) / len(enc),
             enc_dez_ate_dia10=int((encdez.dt.day <= 10).sum()), enc_dez_ate_dia20=int((encdez.dt.day <= 20).sum()))
    if len(r):
        dx = r.dx.iloc[0] + pd.Timedelta(hours=23, minutes=59, seconds=59); x["data_extracao"] = r.data_extracao.iloc[0]
        x["enc_dez_ate_extracao"] = int((encdez <= dx).sum()); x["pct_enc_dez_ate_extracao"] = 100 * x["enc_dez_ate_extracao"] / len(encdez)
        x["S_extracao"] = stock(dx); x["S_31dez"] = stock(t2)
    X.append(x)
X = pd.DataFrame(X); print(X.to_string(index=False, float_format=lambda v: f"{v:,.1f}")); save(X, "robustez_R2_extracao.csv")

# ======================= (R3)
print("=" * 30, "(R3) estoque medio anual e parcela atendida media")
S = pd.read_csv(ROOT + "03_build/build19/serie_publicada_completa.csv")
S = S.drop_duplicates(["ano", "mes"], keep="first")
Q = S[S.mes.isin([3, 6, 9, 12])].copy(); Q["B"] = 100 * Q.matric_creche / (Q.matric_creche + Q.dem_total)
A = Q.pivot(index="ano", columns="mes", values="dem_total"); A = A[A.notna().sum(axis=1) == 4]
A["media"] = A[[3, 6, 9, 12]].mean(axis=1); A["dez_sobre_media"] = A[12] / A.media
G = Q.pivot(index="ano", columns="mes", values="B"); G = G[G.notna().sum(axis=1) == 4]; G["media"] = G[[3, 6, 9, 12]].mean(axis=1)
print(A.round(2).to_string()); print(G.round(2).to_string())
for a, b in ((2013, 2017), (2014, 2017), (2013, 2019)):
    ch = {m: round(100 * (A.loc[b, m] - A.loc[a, m]) / A.loc[a, m], 1) for m in (3, 6, 9, 12, "media")}
    ab = {m: int(A.loc[b, m] - A.loc[a, m]) for m in (3, 6, 9, 12, "media")}
    print(f"estoque {a}->{b}: % {ch} | absoluto {ab} | dez/media da variacao % = {ch[12] / ch['media']:.2f}; set/media = {ch[9] / ch['media']:.2f}")
for m in (3, 6, 9, 12, "media"):
    s = G[m]; print(f"parcela atendida >= 75: 1o ano por {m}: {int(s[s >= 75].index.min())}; valores 2015-2017: {s.loc[2015:2017].round(1).tolist()}")
save(A.reset_index().rename(columns=str), "robustez_R3_media_estoque.csv"); save(G.reset_index().rename(columns=str), "robustez_R3_media_atendida.csv")

# ======================= tentativa 3: denominador ancorado nos Censos com forma dos nascidos vivos; leituras da clausula; tabelas
print('=' * 30, '(R1b) leituras da clausula e tabelas')
c10 = 564210
# ---- bloco a colar no script (comeca aqui)
r10 = R1.loc[R1.ano == 2010, "pool_nv_maio"].iloc[0] / c10; r22 = R1.loc[R1.ano == 2022, "pool_nv_maio"].iloc[0] / c22
R1["pop_censos_nv"] = np.where(R1.ano.between(2010, 2022), R1.pool_nv_maio / (r10 + (R1.ano - 2010) / 12 * (r22 - r10)), np.nan)
for n, col in (("stage", "matA_total"), ("idade", "matA_idade_total"), ("munconv", "matA_munconv")):
    R1[f"A_{n}_censos_nv"] = 100 * R1[col] / R1.pop_censos_nv
LEIT = (("SEADE", "pop_0a3", "A_total"), ("Censos linear", "pop_censos", "A_stage_censos"),
        ("Censos + NV", "pop_censos_nv", "A_stage_censos_nv"), ("NV", "pool_nv_maio", "A_total_pool_nv_maio"))
for lab, d, a in LEIT:
    s = R1[R1.ano.between(2007, 2024)].dropna(subset=[d, a]).copy()
    s["Aobriga"] = 0.75 * s[d] > s.exigB_dez
    s["cumpre_so_maior"] = np.where(s.Aobriga, s[a] >= 75, s.dem_dez == 0)
    print(f"  {lab}: A>=75 em {s[s[a] >= 75].ano.astype(int).tolist()} | B obriga (dez) em {s[~s.Aobriga].ano.astype(int).tolist()} | "
          f"cumprida lendo so o braco maior: {s[s.cumpre_so_maior].ano.astype(int).tolist()} | cumprida exigindo fila vazia: {s[s.dem_dez == 0].ano.astype(int).tolist()}")
BS = chr(92); NL = chr(10)
def f1(v): return "--" if pd.isna(v) else f"{v:.1f}"
def k0(v): return "--" if pd.isna(v) else f"{int(round(v / 1000))}"
L = ["% Gerado por 02_audit/build22_robustez.py (FUSAO, 26/10/2026). Nao editar a mao.", BS + "footnotesize", BS + "setlength{" + BS + "tabcolsep}{4pt}", BS + "fitbox{%",
     BS + "begin{tabular}{l rrr rrrr rr c}", BS + "toprule",
     " & " + BS + "multicolumn{3}{c}{Population 0--3 (000)} & " + BS + "multicolumn{4}{c}{Stage enrolment, per cent of population} & " + BS + "multicolumn{2}{c}{Age, per cent} & Binding arm " + BS + BS,
     BS + "cmidrule(lr){2-4}" + BS + "cmidrule(lr){5-8}" + BS + "cmidrule(lr){9-10}",
     "Year & SEADE & Censuses & Births & SEADE & Censuses & Censuses, linear & Births & SEADE & Censuses & (Censuses) " + BS + BS, BS + "midrule"]
for _, r in R1[R1.ano.between(2010, 2024)].iterrows():
    ob = "--" if pd.isna(r.pop_censos_nv) else ("A" if 0.75 * r.pop_censos_nv > r.exigB_dez else "B")
    L.append(f"{int(r.ano)} & {k0(r.pop_0a3)} & {k0(r.pop_censos_nv)} & {k0(r.pool_nv_maio)} & {f1(r.A_total)} & {f1(r.A_stage_censos_nv)} & {f1(r.A_stage_censos)} & "
             f"{f1(r.A_total_pool_nv_maio)} & {f1(r.A_idade_total)} & {f1(r.A_idade_censos_nv)} & {ob} " + BS + BS)
L += [BS + "bottomrule", BS + "end{tabular}}"]
open(ROOT + "04_paper/assets/tables/c/C_armA_rob_body.tex", "w", encoding="utf-8").write(NL.join(L) + NL)
M = ["% Gerado por 02_audit/build22_robustez.py (FUSAO, 26/10/2026). Nao editar a mao.", BS + "footnotesize", BS + "fitbox{%",
     BS + "begin{tabular}{l r r rrr r r}", BS + "toprule",
     " & List on & New & " + BS + "multicolumn{3}{c}{Left the list} & List on & December referrals made " + BS + BS,
     BS + "cmidrule(lr){4-6}",
     "Year & 30 Sep. & requests & Referred & Aged out & Withdrew & 31 Dec. & by extraction date (" + BS + "%) " + BS + BS, BS + "midrule"]
sd = D[D.trecho == "09->12"].merge(X[["ano", "pct_enc_dez_ate_extracao"]], on="ano", how="left")
for _, r in sd.iterrows():
    M.append(f"{int(r.ano)} & {int(r.S1):,} & {int(r.novos):,} & {int(r.encaminhados):,} & {int(r.aging_out):,} & {int(r.desistencias):,} & {int(r.S2):,} & "
             f"{'--' if pd.isna(r.pct_enc_dez_ate_extracao) else f'{r.pct_enc_dez_ate_extracao:.1f}'} " + BS + BS)
M += [BS + "bottomrule", BS + "end{tabular}}"]
M = M[:9] + [l.replace(",", "{,}") for l in M[9:]]
open(ROOT + "04_paper/assets/tables/c/C_decomp_body.tex", "w", encoding="utf-8").write(NL.join(M) + NL); print("[gravado] C_armA_rob_body.tex, C_decomp_body.tex")
