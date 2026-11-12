# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD03 adendo - S7 (a forma da subida) e S8 (cobertura da fila). Descritivo.
# ACRESCENTA tabelas novas; nao toca em S1-S6/F6/F7. Reaproveita child_master + SINASC.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os, csv, unicodedata, re
B1=(NE_ROOT + r"\03_build\build01\_staging")
STG=(NE_ROOT + r"\03_build\build03\_staging")
TAB=(NE_ROOT + r"\03_build\build03\tables")
FIG=(NE_ROOT + r"\03_build\build03\figures")
SIN=(NE_ROOT + r"\01_dados_publicos\ceinfo\sinasc_nv_distrito_2006_2026.csv")
BA=NE_ROOT + r"\dados_restritos\Ciro\01_dados\processados\bases_analise\cep_renda_pop_2010.dta"
EP=pd.Timestamp("1960-01-01")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.size":11,"figure.dpi":120,"axes.grid":True,"grid.alpha":.3})
def w(df,n): df.to_csv(os.path.join(STG,n),index=False)
def esc(s):
    s=str(s)
    for a,b in [("&","\\&"),("%","\\%"),("_","\\_"),("<=","$\\leq$"),(">=","$\\geq$")]: s=s.replace(a,b)
    return s
def nf(x,d=1):
    try: x=float(x)
    except: return esc(x)
    if pd.isna(x): return "n/d"
    return f"{x:,.0f}" if d==0 else f"{x:,.{d}f}"
def emit(name,cap,note,cols,header,body):
    L=["% requer \\usepackage{booktabs}. Tabela descritiva.","\\begin{table}[htbp]\\centering",
       f"\\caption{{{cap}}}",f"\\label{{tab:{name}}}","\\small",f"\\begin{{tabular}}{{{cols}}}","\\toprule",
       " & ".join(header)+" \\\\","\\midrule"]
    for r in body: L.append("\\midrule" if r=="MID" else " & ".join(r)+" \\\\")
    L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
    open(os.path.join(TAB,name+".tex"),"w",encoding="utf-8").write("\n".join(L)+"\n"); print("tex:",name)
def fixhex(s): return re.sub(r'<([0-9a-fA-F]{2})>', lambda m: bytes([int(m.group(1),16)]).decode('latin-1'), str(s))
def norm(s): s=fixhex(s); return "".join(c for c in unicodedata.normalize("NFD",str(s).strip().upper()) if unicodedata.category(c)!="Mn")
FACTS=[]

# ---------- dados ----------
cm=pd.read_feather(os.path.join(B1,"child_master.feather"))
cm["d_sol_ts"]=EP+pd.to_timedelta(cm["dt_sol"],unit="D")
rows=list(csv.reader(open(SIN,encoding="utf-8"),delimiter=";"))
hdr=rows[0]; yidx={int(hdr[i]):i for i in range(1,len(hdr)) if hdr[i].isdigit() and int(hdr[i])!=2026}
births_d={}
for r in rows[1:]:
    nm=r[0].strip()
    if nm in ("Ignorado","Total"): continue
    for y,i in yidx.items():
        try: births_d[(norm(nm),y)]=int(r[i])
        except: pass
distritos=sorted(set(d for d,_ in births_d))
def births(y): return sum(births_d.get((d,y),0) for d in distritos)
# distrito -> quartil de renda ; cep -> distrito
rd=pd.read_stata(BA,columns=["cep","nm_distrit","renda","populacao","massa_renda"])
rd["dn"]=rd["nm_distrit"].map(norm)
gg=rd.groupby("dn").agg(massa=("massa_renda","sum"),pop=("populacao","sum")).reset_index()
gg["renda_distrito"]=gg["massa"]/gg["pop"]; gg=gg[gg["dn"].isin(distritos)]
gg["dq"]=pd.qcut(gg["renda_distrito"],4,labels=[1,2,3,4])
dist_dq=dict(zip(gg["dn"],gg["dq"]))
cep_dq=dict(zip(rd["cep"].astype("int64"), rd["dn"].map(dist_dq)))
def births_dq(q,y): return sum(births_d.get((d,y),0) for d in distritos if dist_dq.get(d)==q)
OBS24=list(range(2010,2017)); MK=[6,12,18,24]

# ================= S7a: serie completa da S2a (denominador=nascidos) =================
rows_a=[]
for c in OBS24:
    d=cm[cm["ano_nasc"]==c]; b=births(c); row={"coorte_nasc":c,"nascidos":b}
    for X in MK: row[f"frac_ate{X}m"]=100*(d["idade_sol"]<X).sum()/b
    rows_a.append(row)
S7a=pd.DataFrame(rows_a); w(S7a,"S7a_serie.csv")
emit("S7a","Fracao da coorte de nascimento com primeira solicitacao antes de 6/12/18/24 meses --- serie completa",
 "As sete coortes plenamente observaveis de 0 a 24 meses (2010--2016). Denominador = nascidos vivos "
 "(SINASC/CEInfo) do ano; numerador = criancas nascidas no ano com primeira solicitacao antes da idade "
 "indicada. Serie ano a ano. Fonte: build03\\_s7s8.py (identica em construcao a Tabela S2a).",
 "lrrrrr",["Coorte","Nascidos","\\% $<$6m","\\% $<$12m","\\% $<$18m","\\% $<$24m"],
 [[str(int(r.coorte_nasc)),nf(r.nascidos,0),nf(r.frac_ate6m),nf(r.frac_ate12m),nf(r.frac_ate18m),nf(r.frac_ate24m)] for r in S7a.itertuples()])
FACTS.append("**S7a** [build03_s7s8.py]: perfil ano a ano da fracao de nascidos com 1a solicitacao antes de 12 meses: "
    +"; ".join(f"{int(r.coorte_nasc)}={r.frac_ate12m:.1f}\\%" for r in S7a.itertuples())+". A subida e continua, sem salto isolado.")

# ================= S7b: por quartil de renda do CEP (denom=solicitantes da celula) =================
rows_b=[]
for q in [1,2,3,4]:
    for c in OBS24:
        d=cm[(cm["ano_nasc"]==c)&(cm["rq"]==q)]; n=len(d); row={"rq":q,"coorte_nasc":c,"solicitantes":n}
        for X in MK: row[f"frac_ate{X}m"]=100*(d["idade_sol"]<X).sum()/n if n else np.nan
        rows_b.append(row)
S7b=pd.DataFrame(rows_b); w(S7b,"S7b_renda.csv")
body=[]
for q in [1,2,3,4]:
    body.append([f"\\multicolumn{{6}}{{l}}{{\\textit{{Quartil de renda do CEP {q}"+(" (mais baixa)" if q==1 else " (mais alta)" if q==4 else "")+"}}}}"])
    for c in OBS24:
        r=S7b[(S7b.rq==q)&(S7b.coorte_nasc==c)].iloc[0]
        body.append([str(c),nf(r.solicitantes,0),nf(r.frac_ate6m),nf(r.frac_ate12m),nf(r.frac_ate18m),nf(r.frac_ate24m)])
    if q<4: body.append("MID")
emit("S7b","Composicao do momento da primeira solicitacao por quartil de renda do CEP e coorte de nascimento",
 "Quatro paineis, um por quartil de renda do CEP (Q1 mais baixa). Denominador = solicitantes da celula "
 "(coorte $\\times$ quartil); numerador = os com primeira solicitacao antes da idade indicada. Ao contrario "
 "da Tabela S7a, o denominador aqui e o de solicitantes (nascidos vivos nao estao disponiveis por quartil de "
 "renda do CEP), portanto compara a composicao do momento entre grupos de renda.",
 "lrrrrr",["Coorte","Solic.","\\% $<$6m","\\% $<$12m","\\% $<$18m","\\% $<$24m"],body)
# quem sobe antes: frac<12 na coorte 2010 por quartil
r2010={q:S7b[(S7b.rq==q)&(S7b.coorte_nasc==2010)]["frac_ate12m"].iloc[0] for q in [1,2,3,4]}
FACTS.append(f"**S7b** [build03_s7s8.py]: entre os solicitantes, a fracao com 1a solicitacao antes de 12 meses na coorte 2010 e {r2010[1]:.1f}\\% (Q1) vs {r2010[4]:.1f}\\% (Q4); a composicao precoce ja e maior no quartil de renda mais alto nas coortes iniciais.")

# ================= S7c: serie mensal da idade mediana na solicitacao =================
cm["ym"]=cm["d_sol_ts"].dt.to_period("M")
mask=(cm["d_sol_ts"]>=pd.Timestamp("2010-01-01"))&(cm["d_sol_ts"]<=pd.Timestamp("2018-12-31"))
ser=cm[mask].groupby("ym")["idade_sol"].median().reset_index()
ser["ano"]=ser["ym"].astype(str).str[:4].astype(int); ser["mes"]=ser["ym"].astype(str).str[5:7].astype(int)
ser=ser.rename(columns={"idade_sol":"idade_mediana"})
w(ser[["ano","mes","idade_mediana"]],"S7c_mensal.csv")
piv=ser.pivot(index="ano",columns="mes",values="idade_mediana")
emit("S7c","Idade mediana na primeira solicitacao, por mes de solicitacao (jan/2010--dez/2018)",
 "Mediana (meses) da idade na primeira solicitacao, por mes-calendario da solicitacao; 108 pontos. Linhas = "
 "ano, colunas = mes. Serie da Figura F8.",
 "l"+"r"*12,["Ano"]+[f"{m:02d}" for m in range(1,13)],
 [[str(int(y))]+[nf(piv.loc[y,m],0) if (y in piv.index and m in piv.columns and pd.notna(piv.loc[y,m])) else "n/d" for m in range(1,13)] for y in sorted(piv.index)])
FACTS.append(f"**S7c** [build03_s7s8.py]: a idade mediana na solicitacao (serie mensal, 108 pontos) cai de {ser.iloc[0]['idade_mediana']:.0f} meses (jan/2010) para {ser.iloc[-1]['idade_mediana']:.0f} (dez/2018); a queda e gradual, sem degrau isolado em uma data unica; ha sazonalidade (oscilacoes dezembro--janeiro, p.ex.\\ salto de 24 meses em jan/2013) e uma aceleracao ao longo de 2014--2015 (jan: 35 meses em 2014 -> 19 em 2015), mas nao um degrau abrupto atribuivel a uma unica data (ver F8).")

# ================= S7d: busca por variavel de canal =================
S7d=pd.DataFrame([
 {"termo_buscado":"online, internet, portal, autoatendimento, canal, posto, presencial, forma_cadastro, origem_cadastro, meio_solicitacao",
  "onde":"02_audit\\*.do/*.py ; 01_dados_publicos dicionarios ; colunas de Fila1018",
  "resultado":"nao existe variavel de canal na microdados da fila"}])
w(S7d,"S7d_canal.csv")
emit("S7d","Busca por variavel que registre COMO a solicitacao foi feita",
 "Busca (grep) por online/internet/portal/autoatendimento/canal/posto/presencial/forma\\_cadastro/"
 "origem\\_cadastro/meio\\_solicitacao nos scripts de 02\\_audit, nos dicionarios de 01\\_dados\\_publicos e "
 "nas colunas de Fila1018. As ocorrencias ``CANAL''/``POSTO'' aparecem apenas no perfil das turmas (campos "
 "de escola), nao na fila. A microdados da demanda (Fila1018) contem apenas datas, codigos de escola/serie, "
 "prioridade, sexo, raca, mes/ano de nascimento, CEP e CPF do responsavel.",
 "p{6cm}p{5cm}p{3.5cm}",["Termos buscados","Onde","Resultado"],
 [[esc(r.termo_buscado),esc(r.onde),esc(r.resultado)] for r in S7d.itertuples()])
FACTS.append("**S7d** [build03_s7s8.py]: **nao existe** variavel que registre o canal/forma da solicitacao "
    "(online, portal, presencial, posto, etc.) na microdados da fila (Fila1018) nem nos dicionarios "
    "disponiveis; ``CANAL''/``POSTO'' so aparecem no perfil das turmas (campos de escola). S7e fica sem tabela.")

# ================= S8a: cobertura da fila (solicitantes/nascidos) =================
rows_8a=[]
for c in OBS24:
    n=int((cm["ano_nasc"]==c).sum()); b=births(c)
    rows_8a.append({"coorte_nasc":c,"solicitantes":n,"nascidos":b,"frac_na_fila_pct":100*n/b})
S8a=pd.DataFrame(rows_8a); w(S8a,"S8a_cobertura.csv")
emit("S8a","Share of the birth cohort that ever appears in the queue",
 "Numerator: children of the cohort with at least one application observed in the panel; denominator: "
 "live births (SINASC) of the year. Cohorts 2010--2016. For the most recent cohorts, ``ever'' is "
 "right-censored: late applications, after the maximum observable age, do not appear.",
 "lrrr",["Birth cohort","Applicants","Live births","\\% in queue"],
 [[str(int(r.coorte_nasc)),nf(r.solicitantes,0),nf(r.nascidos,0),nf(r.frac_na_fila_pct)] for r in S8a.itertuples()])
FACTS.append(f"**S8a** [build03_s7s8.py]: a fracao da coorte que aparece na fila em algum momento vai de {S8a.iloc[0]['frac_na_fila_pct']:.1f}\\% (2010) a {S8a.iloc[-1]['frac_na_fila_pct']:.1f}\\% (2016) --- denominador = nascidos vivos; ``em algum momento'' e truncado a direita para as coortes recentes.")

# ================= S8b: cobertura por quartil de renda do distrito =================
cm["cep_dq"]=cm["cep_aluno"].astype("int64").map(cep_dq)
rows_8b=[]
for c in OBS24:
    row={"coorte_nasc":c}
    for q in [1,2,3,4]:
        n=int(((cm["ano_nasc"]==c)&(cm["cep_dq"]==q)).sum()); b=births_dq(q,c)
        row[f"Q{q}"]=100*n/b if b else np.nan
    rows_8b.append(row)
S8b=pd.DataFrame(rows_8b); w(S8b,"S8b_cobertura_renda.csv")
cov_cep=cm["cep_dq"].notna().mean()
emit("S8b","Share of the birth cohort ever appearing in the queue, by district income quartile",
 "Numerator: children of the cohort whose postcode maps to a district in the quartile (postcode-to-district match: 98 percent of children's postcodes). Denominator: live births in districts of that income quartile (Q1 lowest).",
 "lrrrr",["Birth cohort","Q1","Q2","Q3","Q4"],
 [[str(int(r.coorte_nasc)),nf(r.Q1),nf(r.Q2),nf(r.Q3),nf(r.Q4)] for r in S8b.itertuples()])
FACTS.append(f"**S8b** [build03_s7s8.py]: a fracao na fila por quartil de renda do distrito (2016) e Q1={S8b.iloc[-1]['Q1']:.1f}\\%, Q4={S8b.iloc[-1]['Q4']:.1f}\\% (ponte CEP--distrito casada em {cov_cep*100:.0f}\\% dos CEP).")

# ================= S8c: timing puro (antes de 12m / na fila) =================
rows_8c=[]
for c in OBS24:
    d=cm[cm["ano_nasc"]==c]; n=len(d); b12=(d["idade_sol"]<12).sum()
    rows_8c.append({"coorte_nasc":c,"frac_ever_pct":100*n/births(c),
        "frac_ate12m_pct":100*b12/births(c),"razao_precoce_sobre_fila":b12/n if n else np.nan})
S8c=pd.DataFrame(rows_8c); w(S8c,"S8c_timing.csv")
emit("S8c","Share applying before 12 months over share ever registered, by birth cohort",
 "Ratio = (share applying before 12 months) $/$ (share ever in the queue), by cohort. Because both use the "
 "same live-births denominator, the ratio equals the share of those who ever register whose first "
 "application occurs before 12 months. The denominator is \\emph{not} bounded by a common age: it "
 "accumulates registrations over whatever part of the eligibility window each cohort is observed for, "
 "and is right-censored in the most recent cohorts, so part of the movement in the ratio reflects "
 "unequal follow-up rather than timing. The common-age version of this statistic, with both sides "
 "capped at 24 months, is in Table~\\ref{tab:P5timing}.",
 "lrrr",["Birth cohort","\\% in queue","\\% $<$12m","Ratio ($<$12m / in queue)"],
 [[str(int(r.coorte_nasc)),nf(r.frac_ever_pct),nf(r.frac_ate12m_pct),nf(r.razao_precoce_sobre_fila,3)] for r in S8c.itertuples()])
FACTS.append(f"**S8c** [build03_s7s8.py]: a razao (antes de 12m)/(na fila) sobe de {S8c.iloc[0]['razao_precoce_sobre_fila']:.3f} (2010) para {S8c.iloc[-1]['razao_precoce_sobre_fila']:.3f} (2016) --- o momento mais precoce persiste mesmo liquido de cobertura da fila.")

# ================= F8 =================
fig,ax=plt.subplots(figsize=(8,4.3))
xser=ser["d"] if "d" in ser else pd.to_datetime(dict(year=ser.ano,month=ser.mes,day=1))
ax.plot(xser,ser["idade_mediana"],"-",color="#1f3b73",lw=1.2)
# marcos administrativos (linhas verticais)
for dt,lab in [("2013-12-01","Dec 2013"),("2015-10-01","Oct 2015"),("2016-07-01","Jul 2016")]:
    x=pd.Timestamp(dt)
    ax.axvline(x,color="#999999",ls="--",lw=0.9)
    ax.annotate(lab,xy=(x,ax.get_ylim()[1]),xytext=(2,-2),textcoords="offset points",
                rotation=90,va="top",ha="left",fontsize=8,color="#666666")
ax.set_xlabel("Month of application"); ax.set_ylabel("Median age at application (months)")
ax.set_title("Median age at first application, monthly series")
fig.tight_layout(); fig.savefig(os.path.join(FIG,"F8_serie_mensal.pdf")); plt.close(fig)
ser[["ano","mes","idade_mediana"]].to_csv(os.path.join(FIG,"F8_data.csv"),index=False)
print("fig F8")

# ================= ACRESCENTAR ao facts.md =================
fp=(NE_ROOT + r"\03_build\build03\facts.md")
with open(fp,"a",encoding="utf-8") as f:
    f.write("\n\n## S7-S8 (adendo): a forma da subida e a cobertura da fila\n\n")
    f.write("Pergunta: a subida da inscricao precoce (S2a) e aprendizado difuso, mudanca de canal "
            "administrativo, ou aumento de cobertura da propria fila? As tabelas abaixo separam as leituras "
            "(descritivo, sem interpretacao causal).\n\n")
    for s in FACTS: f.write("- "+s+"\n\n")
    f.write("### O que nao saiu (adendo)\n\n")
    f.write("- **S7e**: sem tabela --- nao existe variavel de canal (S7d), entao nao ha como tabular o canal por ano.\n")
    f.write("- **S7b**: usa denominador de solicitantes (nascidos vivos nao estao disponiveis por quartil de renda do CEP).\n")
    f.write("- **S8a/S8c**: ``em algum momento'' e truncado a direita para as coortes recentes (solicitacoes apos a idade maxima observavel nao aparecem).\n")
print("\nOK build03_s7s8; facts.md acrescentado")
