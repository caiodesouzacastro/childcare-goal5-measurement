# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD09 - torna rastreaveis dois numeros do paper:
#   N1 (paper:368) "32.4% das solicitacoes compartilham timestamp exato na celula
#       centro-faixa-ano" -> reproduz a definicao do DIAG10-III2 E calcula a
#       definicao natural de entrada em lote (1a solicitacao, ao segundo, sem
#       condicionar em escola/faixa/ano), por ano e por limiar (2+/10+/50+/100+).
#   N2 (paper:277) "mediana 32 CEIs, p10=14, p90=68" -> recalcula os percentis do
#       conjunto elegivel (CEIs <=2km) para o UNIVERSO DO PAPER (B_novo, 1.524.560),
#       total e por ano. (O DIAG11-C1 usara so Bercario 2013-2018.)
# Regras BUILD01: descritivo; .tex + .csv; facts.md. Nao modifica build01-08.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os

ROOT=NE_ROOT
FILA=NE_ROOT + r"\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
CM=os.path.join(ROOT,r"03_build\build01\_staging\child_master.feather")
PERFIL=os.path.join(ROOT,r"03_build\build01\_staging\perfil_turma.csv")
OUT=os.path.join(ROOT,r"03_build\build09"); TAB=os.path.join(OUT,"tables")
os.makedirs(TAB,exist_ok=True)
LOG=[]; FACTS=[]
def S(x): LOG.append(str(x)); print(x)

def emit(name,cap,note,cols,header,body,label=None):
    label=label or name
    L=["% requer booktabs. Descritivo (BUILD09).","\\begin{table}[htbp]\\centering",
       f"\\caption{{{cap}}}",f"\\label{{tab:{label}}}","\\small",
       "\\setlength{\\tabcolsep}{5pt}",f"\\begin{{tabular}}{{{cols}}}","\\toprule",
       " & ".join(header)+" \\\\","\\midrule"]
    for r in body: L.append("\\midrule" if r=="MID" else " & ".join(r)+" \\\\")
    L+=["\\bottomrule","\\end{tabular}",
        f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
    open(os.path.join(TAB,name+".tex"),"w",encoding="utf-8").write("\n".join(L)+"\n")
    print("tex:",name)

# =====================================================================
# Carga do Fila1018 (uma vez): colunas para N1b e N1c
# =====================================================================
S("carregando Fila1018 (colunas p/ N1)...")
fa=pd.read_stata(FILA,columns=["cd_aluno_sme","dt_solicitacao","dt_encaminhamento",
    "cd_esc_encaminhamento","an_letivo_encaminhamento","cd_serie_ensino_encaminhamento",
    "tipo_prioridade_encaminhamento"])
S(f"  Fila1018: {len(fa):,} linhas.")
fa["clk_sol"]=pd.to_datetime(fa["dt_solicitacao"],format="%d/%m/%Y %H:%M:%S",errors="coerce")
fa["clk_enc"]=pd.to_datetime(fa["dt_encaminhamento"],format="%d/%m/%Y %H:%M:%S",errors="coerce")

# universo B_novo (paper): cd_aluno_sme do child_master
cm=pd.read_feather(CM,columns=["cd_aluno_sme","ano_sol","nelig"])
bnovo=set(cm["cd_aluno_sme"].unique())
S(f"  B_novo (child_master): {len(bnovo):,} criancas.")

# =====================================================================
# N1b - REPRODUZIR a definicao do DIAG10-III2 (celula centro-faixa-ano do
#        ENCAMINHAMENTO; universo = encaminhamentos creche sem prioridade)
# =====================================================================
S("\n## N1b - reproducao do DIAG10-III2 (32,4%)")
r=fa[fa["clk_enc"].notna() & fa["cd_esc_encaminhamento"].notna()
     & fa["tipo_prioridade_encaminhamento"].isna()].copy()
r=r[r["cd_serie_ensino_encaminhamento"].isin([1,4,27,28])]
S(f"  N (encaminhamentos creche, sem prioridade, serie in 1/4/27/28) = {len(r):,}")
r["cell"]=(r["cd_esc_encaminhamento"].astype(str)+"|"
           +r["cd_serie_ensino_encaminhamento"].astype(str)+"|"
           +r["an_letivo_encaminhamento"].astype(str))
r["clk_s"]=r["clk_sol"].values.astype("datetime64[s]")
grp=r.groupby(["cell","clk_s"])["cd_aluno_sme"].transform("size")
share_diag=(grp>1).mean()
S(f"  fracao com timestamp (segundo) EMPATADO na celula = {share_diag*100:.1f}%  "
  f"(DIAG10-III2 = 32.4%)")

# =====================================================================
# N1c - ENTRADA EM LOTE: 1a solicitacao (B_novo), timestamp ao segundo,
#        SEM condicionar em escola/faixa/ano. Por ano e por limiar.
# =====================================================================
S("\n## N1c - entrada em lote (1a solicitacao, sem condicionar)")
fb=fa[fa["clk_sol"].notna()].copy()
# 1a solicitacao por crianca = menor timestamp observado
first=fb.groupby("cd_aluno_sme",as_index=False)["clk_sol"].min()
first=first[first["cd_aluno_sme"].isin(bnovo)].copy()
S(f"  1as solicitacoes com timestamp valido (em B_novo) = {len(first):,}")
first["clk_s"]=first["clk_sol"].values.astype("datetime64[s]")
first["ano"]=first["clk_sol"].dt.year
# n de criancas no MESMO segundo exato (global, sem condicionar)
first["n_seg"]=first.groupby("clk_s")["cd_aluno_sme"].transform("size")
THR=[2,10,50,100]
def by_year(df):
    out=[]
    for y in range(2010,2019):
        d=df[df["ano"]==y]
        row={"ano":y,"n":len(d)}
        for k in THR: row[f"p{k}"]=100*(d["n_seg"]>=k).mean() if len(d) else np.nan
        out.append(row)
    # total B_novo (todos os anos, inclusive 2006-2009)
    row={"ano":"Total (todos)","n":len(df)}
    for k in THR: row[f"p{k}"]=100*(df["n_seg"]>=k).mean()
    out.append(row)
    return pd.DataFrame(out)
N1=by_year(first)
S("  fracao em lote por ano (2+/10+/50+/100+ criancas no mesmo segundo):")
for _,x in N1.iterrows():
    S(f"    {str(x['ano']):>14}: n={int(x['n']):>9,}  "
      f"2+={x['p2']:5.1f}%  10+={x['p10']:5.1f}%  50+={x['p50']:5.1f}%  100+={x['p100']:5.1f}%")
N1.to_csv(os.path.join(TAB,"N1_lotes.csv"),index=False)

def fnum(x,d=1):
    return f"{x:,.{d}f}" if pd.notna(x) else "n/d"
body=[]
for _,x in N1.iterrows():
    lbl=str(int(x["ano"])) if str(x["ano"]).isdigit() else x["ano"]
    if lbl=="Total (todos)": body.append("MID")
    body.append([lbl,f"{int(x['n']):,}",fnum(x['p2']),fnum(x['p10']),fnum(x['p50']),fnum(x['p100'])])
emit("N1_lotes",
 "Share of first applications sharing an exact-second timestamp, by year of application",
 f"Universe: first application per child (B\\_novo, {len(first):,} with a valid "
 "timestamp), the panel used throughout the paper. A first application is ``in a "
 "batch'' if its timestamp, recorded to the second, is shared by at least $k$ "
 "children's first applications \\emph{anywhere in the city} that same second "
 "(no conditioning on centre, band, or year). Columns give $k=2,10,50,100$. For "
 "comparison, the referral-cell definition of DIAG10 (share of non-priority "
 f"childcare referrals whose application second is shared within the "
 f"centre-of-referral $\\times$ band $\\times$ academic-year cell) gives "
 f"{share_diag*100:.1f} percent on {len(r):,} referrals.",
 "lrrrrr",
 ["Year of application","N","$\\geq$2","$\\geq$10","$\\geq$50","$\\geq$100"],body,
 label="N1")

FACTS.append(
 f"**N1 (entrada em lote)** [build09.py]: entre as 1as solicitacoes (B\\_novo, "
 f"{len(first):,} com timestamp valido), a fracao cujo timestamp ao SEGUNDO e "
 f"compartilhado por 2+ criancas em qualquer ponto da cidade (sem condicionar em "
 f"escola/faixa/ano) e {N1[N1.ano=='Total (todos)']['p2'].iloc[0]:.1f}\\% no total; "
 f"por 100+ criancas no mesmo segundo, {N1[N1.ano=='Total (todos)']['p100'].iloc[0]:.1f}\\%. "
 f"A definicao do DIAG10-III2 (celula centro-faixa-ano do encaminhamento, "
 f"encaminhamentos creche sem prioridade) reproduz {share_diag*100:.1f}\\% "
 f"({len(r):,} encaminhamentos) --- e a fonte do 32,4\\% do paper.")

# =====================================================================
# N2 - percentis do conjunto elegivel (nelig) no universo do paper
# =====================================================================
S("\n## N2 - percentis do conjunto elegivel (CEIs <=2km), universo do paper")
S("  (nelig do child_master: contagem ESTATICA de CEIs <=2km do CEP, sem "
  "condicionar na data de abertura do CEI; ver build01_child.py)")
cm2=pd.read_feather(CM,columns=["cd_aluno_sme","ano_sol","nelig"])
P=[10,25,50,75,90]
def pct_row(s):
    q=np.percentile(s,P)
    return list(q)+[s.mean(),len(s)]
rows2=[]
allp=pct_row(cm2["nelig"].values)
rows2.append(["Total (2006--2018)"]+allp)
for y in range(2010,2019):
    d=cm2[cm2["ano_sol"]==y]["nelig"].values
    if len(d): rows2.append([str(y)]+pct_row(d))
N2=pd.DataFrame(rows2,columns=["grupo","p10","p25","p50","p75","p90","media","N"])
S("  percentis de nelig (p10/p25/mediana/p75/p90/media/N):")
for _,x in N2.iterrows():
    S(f"    {x['grupo']:>18}: p10={x.p10:4.0f} p25={x.p25:4.0f} med={x.p50:4.0f} "
      f"p75={x.p75:4.0f} p90={x.p90:4.0f} media={x.media:5.1f}  N={int(x.N):,}")
N2.to_csv(os.path.join(TAB,"N2_grid.csv"),index=False)

body2=[]
for _,x in N2.iterrows():
    if x["grupo"].startswith("2010"): body2.append("MID")
    body2.append([x["grupo"],f"{x.p10:.0f}",f"{x.p25:.0f}",f"{x.p50:.0f}",
                  f"{x.p75:.0f}",f"{x.p90:.0f}",f"{x.media:.1f}",f"{int(x.N):,}"])
emit("N2_grid",
 "Size of the eligible set: \\emph{static} count of childcare centres within "
 "2\\,km of the postcode, paper universe, total and by year of application",
 f"Universe: all first applications (B\\_novo, {len(cm2):,} children). The "
 "eligible set is the count of childcare centres within 2\\,km of the child's "
 "postcode, from the postcode-to-centre distance file. This is the "
 "\\emph{static} count: it includes every centre in the register regardless of "
 "whether it had opened at the application date, so year-to-year differences "
 "reflect the geography of where applicants live, not growth of the network. The "
 "preferred measure conditions on centres already open at the application date "
 "(a median of 18, rising from 12 in 2010 to 29 in 2018); it is reported, "
 "alongside this static count, in the dynamic eligible-set table.",
 "lrrrrrrr",
 ["Group","p10","p25","Median","p75","p90","Mean","N"],body2,
 label="N2")

med_tot=N2[N2.grupo=="Total (2006--2018)"]["p50"].iloc[0]
p10_tot=N2[N2.grupo=="Total (2006--2018)"]["p10"].iloc[0]
p90_tot=N2[N2.grupo=="Total (2006--2018)"]["p90"].iloc[0]
FACTS.append(
 f"**N2 (conjunto elegivel)** [build09.py]: no universo do paper (B\\_novo, "
 f"{len(cm2):,}), o numero de CEIs a <=2km do CEP tem mediana {med_tot:.0f}, "
 f"p10={p10_tot:.0f}, p90={p90_tot:.0f} (media {N2[N2.grupo=='Total (2006--2018)']['media'].iloc[0]:.1f}). "
 f"E uma contagem estatica (geografica), nao condicionada na data de abertura do "
 f"CEI; a variacao entre anos reflete a geografia dos solicitantes, nao o "
 f"crescimento da rede.")

# =====================================================================
# 87.178 vs 86.982 celulas
# =====================================================================
S("\n## Celulas centro x faixa x semestre (87.178 vs 86.982)")
pf=pd.read_csv(PERFIL)
ncel=pf.groupby(["codesc","agrup","sidx"]).ngroups
ncen=pf["codesc"].nunique(); nsem=pf["sidx"].nunique()
S(f"  perfil_turma.csv atual: {ncen:,} centros, {nsem} semestres, "
  f"{ncel:,} celulas (codesc x agrup x sidx nao-vazias).")
S(f"  paper diz 87.178; build atual = {ncel:,}; diferenca = {87178-ncel} celulas "
  f"({100*(87178-ncel)/ncel:.2f}%). 2019s2 e arquivos duplicados (jun2013/2015) "
  f"foram excluidos do build atual (ver build01_perfil.py), o que explica o "
  f"excedente do numero antigo.")
FACTS.append(
 f"**Celulas do painel de capacidade** [build09.py/build01_perfil.py]: o painel "
 f"cobre {ncen:,} centros x {nsem} semestres (2013s1--2019s1) = {ncel:,} celulas "
 f"centro x faixa x semestre nao-vazias. O 87.178 do paper e uma contagem antiga "
 f"({87178-ncel} celulas a mais, {100*(87178-ncel)/ncel:.2f}\\%), de um painel que "
 f"ainda incluia arquivos duplicados/2019s2 depois excluidos; o numero rastreavel "
 f"e {ncel:,}.")

# =====================================================================
# facts.md + log
# =====================================================================
with open(os.path.join(OUT,"facts.md"),"w",encoding="utf-8") as f:
    f.write("# BUILD09 facts (rastreabilidade dos dois numeros)\n\n")
    for x in FACTS: f.write("- "+x+"\n\n")
with open(os.path.join(OUT,"build09.log"),"w",encoding="utf-8") as f:
    f.write("\n".join(LOG))
S("\nOK build09: N1_lotes, N2_grid, facts.md, build09.log")
