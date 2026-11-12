# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# BUILD05 - analise de irmaos: aprendizado sobre a fila dentro da familia. S1-S4.
# Descritivo (associacao/diferenca/variacao; sem efeito/impacto/causa).
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import pyhdfe
ROOT=NE_ROOT
OUT=os.path.join(ROOT,r"03_build\build05"); TAB=os.path.join(OUT,"tables"); FIG=os.path.join(OUT,"figures")
os.makedirs(TAB,exist_ok=True); os.makedirs(FIG,exist_ok=True)
LOG=[]; FACTS=[]
def S(x): LOG.append(str(x)); print(x)
def w(df,n): df.to_csv(os.path.join(TAB,n),index=False)
def nf(x,d=1):
    try: x=float(x)
    except: return str(x)
    return f"{x:,.0f}" if d==0 else f"{x:,.{d}f}"
def emit(name,cap,note,cols,header,body):
    L=["% requer booktabs. Descritivo.","\\begin{table}[htbp]\\centering",f"\\caption{{{cap}}}",
       f"\\label{{tab:{name}}}","\\small",f"\\begin{{tabular}}{{{cols}}}","\\toprule",
       " & ".join(header)+" \\\\","\\midrule"]
    for r in body: L.append("\\midrule" if r=="MID" else " & ".join(r)+" \\\\")
    L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
    open(os.path.join(TAB,name+".tex"),"w",encoding="utf-8").write("\n".join(L)+"\n"); print("tex:",name)

def areg(df,y,xvars,fe_cols,cluster=None):
    """OLS absorvendo FE (pyhdfe). SE cluster-robusto se cluster dado, senao HC1."""
    cols=[y]+xvars+fe_cols+([cluster] if cluster else [])
    sub=df.dropna(subset=cols).copy()
    ids=np.column_stack([sub[c].astype("category").cat.codes.values for c in fe_cols])
    alg=pyhdfe.create(ids,drop_singletons=False)
    res=alg.residualize(sub[[y]+xvars].astype(float).values)
    yr=res[:,0]; Xr=res[:,1:]; n,k=Xr.shape
    XtXi=np.linalg.inv(Xr.T@Xr); beta=XtXi@(Xr.T@yr); resid=yr-Xr@beta
    if cluster:
        sc=Xr*resid[:,None]; g=pd.DataFrame(sc); g["cl"]=sub[cluster].values
        gs=g.groupby("cl").sum().values; meat=gs.T@gs; G=len(gs)
        V=XtXi@meat@XtXi*(G/(G-1))
    else:
        V=XtXi*(resid@resid)/(n-k)
    se=np.sqrt(np.diag(V))
    return dict(zip(xvars,beta)),dict(zip(xvars,se)),n

d=pd.read_parquet(os.path.join(OUT,"_panel_criancas.parquet"))
S("# BUILD05 - painel de irmaos. child_master + Fila1018 (cpf_resp_aluno). Descritivo.")

# ==================== S1: PAINEL DE IRMAOS ====================
S("\n## S1 - construir o painel de irmaos")
fam=d[d.cpf_ok].copy()
sz=fam.groupby("cpf").size()
S(f"S1a: {sz.size:,} responsaveis (cpf valido) cobrindo {len(fam):,} criancas ({100*d.cpf_ok.mean():.1f}% do painel).")
dist=sz.value_counts().sort_index()
S("     distribuicao de filhos por responsavel: "+", ".join(f"{k}:{v:,}" for k,v in dist.head(6).items())+
  (f", 7+:{sz[sz>=7].size:,}" if (sz>=7).any() else ""))
n2plus=sz[sz>=2]; S(f"     criancas em familias com 2+ filhos: {int(sz[sz>=2].sum()):,} em {n2plus.size:,} familias.")
w(dist.rename("n_familias").reset_index().rename(columns={"index":"n_filhos"}),"S1a_filhos_por_resp.csv")
FACTS.append(f"**S1a** [build05_irmaos.py]: {sz.size:,} responsaveis (cpf); {n2plus.size:,} familias com 2+ filhos; "
             f"{100*sz[sz==1].size/sz.size:.1f}\\% dos responsaveis tem 1 filho no painel.")

# S1b: familias com exatamente 2 filhos
two=sz[sz==2].index
t=fam[fam.cpf.isin(two)].sort_values(["cpf","nasc_idx","d_sol1"])
t["ord"]=t.groupby("cpf").cumcount()+1
p1=t[t.ord==1].set_index("cpf"); p2=t[t.ord==2].set_index("cpf")
pair=pd.DataFrame({"cpf":p1.index})
for col in ["ano_nasc","mes_nasc","nasc_idx","idade_sol","espera_enc","referido","nunca","ever_mat",
            "renda","distrito","d_sol1","d_enc1","esc_enc1","esc_mat1","tipo_prioridade_encaminhamento"]:
    pair[col+"_1"]=p1[col].values; pair[col+"_2"]=p2[col].values
pair["espac"]=pair.nasc_idx_2-pair.nasc_idx_1
S(f"S1b: {len(pair):,} familias com exatamente 2 filhos. espacamento entre nascimentos (meses):")
br=pd.cut(pair.espac,[-1,0,11,23,35,47,10**4],labels=["0(gemeos)","1-11","12-23","24-35","36-47","48+"])
sb=br.value_counts().sort_index()
for k,v in sb.items(): S(f"     {k}: {v:,} ({100*v/len(pair):.1f}%)")
S(f"     espacamento mediano (excl.\\ gemeos): {pair[pair.espac>0].espac.median():.0f} meses")
w(sb.rename("n_pares").reset_index().rename(columns={"index":"faixa_espac"}),"S1b_espacamento.csv")

# S1c: ambos plenamente observaveis 0-24 (nascidos 2010-2016), espacamento>=1
pc=pair[(pair.ano_nasc_1.between(2010,2016))&(pair.ano_nasc_2.between(2010,2016))&(pair.espac>0)].copy()
S(f"S1c: pares com AMBOS nascidos 2010-2016 e espacamento>=1m: {len(pc):,} pares.")
FACTS.append(f"**S1c** [build05_irmaos.py]: {len(pc):,} pares de irmaos com ambos os filhos nascidos 2010-2016 "
             f"(plenamente observaveis 0-24m) e espacamento >=1 mes.")
w(pc.drop(columns=["d_sol1_1","d_sol1_2","d_enc1_1","d_enc1_2"]),"S1c_pares.csv")

# ==================== S2: ESTATISTICA CENTRAL ====================
S("\n## S2 - a estatistica central (idade na 1a solicitacao)")
pc["dif"]=pc.idade_sol_2-pc.idade_sol_1   # filho2 - filho1 (negativo = mais novo inscrito mais cedo)
S(f"S2a: idade na 1a solicitacao -- filho1 (mais velho): media {pc.idade_sol_1.mean():.1f}, mediana {pc.idade_sol_1.median():.0f} meses; "
  f"filho2 (mais novo): media {pc.idade_sol_2.mean():.1f}, mediana {pc.idade_sol_2.median():.0f}.")
S(f"     diferenca (filho2 - filho1): media {pc.dif.mean():.2f}, mediana {pc.dif.median():.0f} meses.")
S(f"S2b: fracao de pares com filho2 inscrito MAIS CEDO (em idade) que filho1: {100*(pc.dif<0).mean():.1f}%.")
FACTS.append(f"**S2ab** [build05_irmaos.py]: o filho mais novo e inscrito, em media, {abs(pc.dif.mean()):.1f} meses "
             f"{'mais cedo' if pc.dif.mean()<0 else 'mais tarde'} que o mais velho (idade na 1a solicitacao); "
             f"em {100*(pc.dif<0).mean():.0f}\\% dos pares o filho mais novo e inscrito mais cedo.")
# S2c por faixa de espacamento
brc=pd.cut(pc.espac,[0,23,35,47,10**4],labels=["12-23","24-35","36-47","48+"])  # nota: <12 raro
g2c=pc.groupby(brc).agg(n=("dif","size"),dif_med=("dif","mean"),dif_medn=("dif","median"),
    frac_antecipa=("dif",lambda s:100*(s<0).mean())).reset_index()
w(g2c,"S2c_por_espacamento.csv")
S("S2c: diferenca de idade de inscricao por faixa de espacamento (filho2-filho1):")
for _,r in g2c.iterrows(): S(f"     {r.iloc[0]}: n={int(r.n):,}  dif_media={r.dif_med:.2f}  mediana={r.dif_medn:.0f}  %antecipa={r.frac_antecipa:.1f}")
# S2d regressao FE de familia (formato longo)
lg=pd.concat([
    pd.DataFrame({"cpf":pc.cpf,"idade_sol":pc.idade_sol_1,"ordem":1,"ano_nasc":pc.ano_nasc_1,"distrito":pc.distrito_1}),
    pd.DataFrame({"cpf":pc.cpf,"idade_sol":pc.idade_sol_2,"ordem":2,"ano_nasc":pc.ano_nasc_2,"distrito":pc.distrito_2})])
lg["dano"]=lg.distrito.astype(str)+"_"+lg.ano_nasc.astype(str)
b1,s1,n1=areg(lg,"idade_sol",["ordem","ano_nasc"],["cpf"],cluster="cpf")
S(f"S2d(i) FE familia: idade_sol ~ ordem + ano_nasc | familia. "
  f"ordem={b1['ordem']:.3f} (EP {s1['ordem']:.3f}); ano_nasc={b1['ano_nasc']:.3f} (EP {s1['ano_nasc']:.3f}); N={n1:,}")
b2,s2,n2=areg(lg,"idade_sol",["ordem"],["cpf","dano"],cluster="cpf")
S(f"S2d(ii) FE familia + distrito x ano_nasc: ordem={b2['ordem']:.3f} (EP {s2['ordem']:.3f}); N={n2:,}")
FACTS.append(f"**S2d** [build05_irmaos.py]: com efeito fixo de familia, o filho mais novo (ordem 2) e inscrito "
             f"{abs(b1['ordem']):.2f} meses {'mais cedo' if b1['ordem']<0 else 'mais tarde'} que o mais velho "
             f"(EP {s1['ordem']:.2f}); acrescentando FE distrito x ano de nascimento, {abs(b2['ordem']):.2f} (EP {s2['ordem']:.2f}).")

# ==================== S3: TESTE DE APRENDIZADO ====================
S("\n## S3 - o teste de aprendizado (espera do filho 1)")
pr=pc[pc.referido_1==1].copy()   # filho1 referido (espera_enc observavel)
pr["q1"]=pd.qcut(pr.espera_enc_1,4,labels=["Q1 (curta)","Q2","Q3","Q4 (longa)"])
S(f"S3a: {len(pr):,} pares com filho1 referido. espera_enc do filho1 (dias) por quartil: "
  +", ".join(f"{q}:{pr[pr.q1==q].espera_enc_1.median():.0f}" for q in pr.q1.cat.categories))
g3=pr.groupby("q1").agg(n=("dif","size"),espera1_med=("espera_enc_1","median"),
    dif_med=("dif","mean"),dif_medn=("dif","median"),frac_antecipa=("dif",lambda s:100*(s<0).mean())).reset_index()
w(g3,"S3b_por_quartil_espera.csv")
S("S3b: diferenca de idade de inscricao (filho2-filho1) por quartil de espera do filho1:")
for _,r in g3.iterrows(): S(f"     {r.q1}: n={int(r.n):,}  espera1_med={r.espera1_med:.0f}d  dif_media={r.dif_med:.2f}  mediana={r.dif_medn:.0f}  %antecipa={r.frac_antecipa:.1f}")
S(f"     Q4-Q1 na diferenca media: {g3.iloc[-1].dif_med-g3.iloc[0].dif_med:.2f} meses")
# S3c regressao
pr["dano2"]=pr.distrito_2.astype(str)+"_"+pr.ano_nasc_2.astype(str)
b3,s3,n3=areg(pr,"dif",["espera_enc_1","ano_nasc_2"],["distrito_2"])
S(f"S3c: dif ~ espera_filho1(dias) + ano_nasc_filho2 | FE(distrito). "
  f"espera1={b3['espera_enc_1']*100:.3f} meses/100d (EP {s3['espera_enc_1']*100:.3f}); N={n3:,}")
# CONFOUND: idade_sol_1 e espera_enc_1 sao negativamente correlacionados (quem inscreve
# cedo espera mais); como dif = idade_sol_2 - idade_sol_1, o gradiente de S3b/S3c e mecanico.
rho=pr.idade_sol_1.corr(pr.espera_enc_1)
b3c,s3c,n3c=areg(pr,"idade_sol_2",["espera_enc_1","idade_sol_1","ano_nasc_2"],["distrito_2"])
S(f"S3c(confound): corr(idade_sol_1, espera_enc_1)={rho:.3f}. Controlando a idade de inscricao do "
  f"proprio 1o filho, o coeficiente da espera do 1o sobre a idade de inscricao do 2o cai de "
  f"{b3['espera_enc_1']*100:.2f} para {b3c['espera_enc_1']*100:.3f} meses/100d (EP {s3c['espera_enc_1']*100:.3f}) -- ~0.")
pd.DataFrame([{"modelo":"dif~espera1 (S3c bruto)","coef_100d":b3['espera_enc_1']*100,"ep":s3['espera_enc_1']*100,"N":n3},
    {"modelo":"idade_sol_2~espera1+idade_sol_1 (limpo)","coef_100d":b3c['espera_enc_1']*100,"ep":s3c['espera_enc_1']*100,"N":n3c}]).to_csv(os.path.join(TAB,"S3c_confound.csv"),index=False)
FACTS.append(f"**S3bc** [build05_irmaos.py]: no bruto, mais espera do 1o filho associa-se a inscricao mais precoce "
             f"do 2o ({abs(b3['espera_enc_1']*100):.2f} meses/100d). Porem idade de inscricao e espera do 1o sao "
             f"negativamente correlacionadas (r={rho:.2f}: quem inscreve cedo espera mais); como a diferenca inclui a "
             f"idade do 1o, o gradiente e mecanico: controlando a idade de inscricao do proprio 1o filho, o "
             f"coeficiente cai a {abs(b3c['espera_enc_1']*100):.2f} meses/100d (~0). Nao ha gradiente de aprendizado liquido.")
# S3d nunca atendido vs atendido rapido
never=pc[pc.nunca_1==1]
fast=pr[pr.q1=="Q1 (curta)"]
S(f"S3d: antecipacao media (dif filho2-filho1): filho1 NUNCA matriculado={never.dif.mean():.2f} (n={len(never):,}) "
  f"vs filho1 atendido rapido (Q1 espera)={fast.dif.mean():.2f} (n={len(fast):,}); diferenca={never.dif.mean()-fast.dif.mean():.2f} meses.")
FACTS.append(f"**S3d** [build05_irmaos.py]: familias cujo 1o filho nunca foi matriculado antecipam o 2o em "
             f"{abs(never.dif.mean()):.1f} meses, vs {abs(fast.dif.mean()):.1f} nas de 1o filho atendido rapido "
             f"(diferenca {never.dif.mean()-fast.dif.mean():.1f}).")

# ==================== S4: PLACEBOS E AMEACAS ====================
S("\n## S4 - placebos e ameacas")
# S4a placebo: filho1 ainda na fila quando filho2 inscrito (enc do filho1 apos sol do filho2)
pr["enc1_apos_sol2"]=(pr.d_enc1_1>pr.d_sol1_2)
plb=pr[pr.enc1_apos_sol2].copy()
if len(plb)>50:
    b4,s4,n4=areg(plb,"dif",["espera_enc_1","ano_nasc_2"],["distrito_2"])
    S(f"S4a PLACEBO ({len(plb):,} pares onde a espera do filho1 se realiza APOS a inscricao do filho2): "
      f"espera1={b4['espera_enc_1']*100:.3f} meses/100d (EP {s4['espera_enc_1']*100:.3f}); N={n4:,}. "
      f"(nao-observavel pela familia no ato -> nao deveria prever)")
else:
    S(f"S4a PLACEBO: apenas {len(plb):,} pares -- amostra insuficiente.")
# S4b filho2 inscrito antes de filho1 ser encaminhado
pc["sol2_antes_enc1"]=(pc.d_sol1_2<pc.d_enc1_1)|(pc.referido_1==0)
S(f"S4b: {100*pc.sol2_antes_enc1.mean():.1f}% dos pares tem o filho2 inscrito ANTES de o filho1 ser encaminhado "
  f"(familia ainda nao observou a espera completa).")
obs=pr[pr.d_sol1_2>=pr.d_enc1_1].copy()   # filho1 ja encaminhado antes da inscricao do filho2
obs["q1o"]=pd.qcut(obs.espera_enc_1,4,labels=["Q1","Q2","Q3","Q4"])
g4=obs.groupby("q1o").agg(n=("dif","size"),espera1_med=("espera_enc_1","median"),dif_med=("dif","mean")).reset_index()
w(g4,"S4b_espera_observada.csv")
S("S4b (refeito, so pares com filho1 JA encaminhado antes da inscricao do filho2):")
for _,r in g4.iterrows(): S(f"     {r.q1o}: n={int(r.n):,}  espera1_med={r.espera1_med:.0f}d  dif_media={r.dif_med:.2f}")
S(f"     Q4-Q1: {g4.iloc[-1].dif_med-g4.iloc[0].dif_med:.2f} meses")
b5,s5,n5=areg(obs,"dif",["espera_enc_1","ano_nasc_2"],["distrito_2"])
S(f"     regressao (espera observada): espera1={b5['espera_enc_1']*100:.3f} meses/100d (EP {s5['espera_enc_1']*100:.3f}); N={n5:,}")
FACTS.append(f"**S4ab** [build05_irmaos.py]: o PLACEBO (espera do 1o filho realizada APOS a inscricao do 2o, "
             f"logo nao-observavel pela familia no ato) preve tao forte quanto a espera observada: "
             f"{b4['espera_enc_1']*100:.2f} meses/100d (placebo) vs {b5['espera_enc_1']*100:.2f} (observada). "
             f"Como o placebo nao morre, a associacao nao vem de a familia observar a espera -- consistente com o "
             f"confound mecanico de S3, nao com aprendizado.")
# S4c prioridade de irmao: mesma escola
pc["mesma_esc_enc"]=(pc.esc_enc1_2.notna())&(pc.esc_enc1_1.notna())&(pc.esc_enc1_2==pc.esc_enc1_1)
pc["mesma_esc_mat"]=(pc.esc_mat1_2.notna())&(pc.esc_mat1_1.notna())&(pc.esc_mat1_2==pc.esc_mat1_1)
S(f"S4c: filho2 encaminhado para a MESMA escola do filho1 em {100*pc.mesma_esc_enc.mean():.1f}% dos pares; "
  f"matriculado na mesma escola em {100*pc.mesma_esc_mat.mean():.1f}%.")
FACTS.append(f"**S4c** [build05_irmaos.py]: {100*pc.mesma_esc_mat.mean():.0f}\\% dos pares tem os dois filhos "
             f"matriculados na mesma escola -- possivel prioridade de irmao (ver grep no relatorio).")
# S4d composicao 2+ vs 1
one=sz[sz==1].index
d1=d[d.cpf_ok&d.cpf.isin(one)]; d2=d[d.cpf_ok&d.cpf.isin(sz[sz>=2].index)]
S("S4d: composicao familias 1 filho vs 2+ filhos (media):")
S(f"     renda CEP: 1={d1.renda.mean():.0f} vs 2+={d2.renda.mean():.0f}")
S(f"     % com prioridade: 1={100*d1.tipo_prioridade_encaminhamento.notna().mean():.1f} vs 2+={100*d2.tipo_prioridade_encaminhamento.notna().mean():.1f}")
S(f"     idade 1a solic (m): 1={d1.idade_sol.mean():.1f} vs 2+={d2.idade_sol.mean():.1f}")
S(f"     % nunca matriculado: 1={100*d1.nunca.mean():.1f} vs 2+={100*d2.nunca.mean():.1f}")
comp=pd.DataFrame({"grupo":["1 filho","2+ filhos"],
    "renda":[d1.renda.mean(),d2.renda.mean()],
    "pct_prioridade":[100*d1.tipo_prioridade_encaminhamento.notna().mean(),100*d2.tipo_prioridade_encaminhamento.notna().mean()],
    "idade_sol":[d1.idade_sol.mean(),d2.idade_sol.mean()],
    "pct_nunca":[100*d1.nunca.mean(),100*d2.nunca.mean()]})
w(comp,"S4d_composicao.csv")

# ==================== F9 ====================
fig,ax=plt.subplots(figsize=(7,4.3))
lab=[str(q) for q in g3.q1]; ax.bar(lab,g3.dif_med,color=["#9ecae1","#6baed6","#3182bd","#08519c"])
ax.axhline(0,color="k",lw=.8); ax.set_ylabel("Sibling age-at-application difference\n(child 2 - child 1, months)")
ax.set_xlabel("Wait of the first child (application to referral), quartile")
ax.set_title("Younger sibling registered earlier where the first child waited longer")
for i,v in enumerate(g3.dif_med): ax.text(i,v,f"{v:.1f}",ha="center",va="top" if v<0 else "bottom")
fig.tight_layout(); fig.savefig(os.path.join(FIG,"F9_irmaos_espera.pdf")); plt.close(fig)
g3[["q1","espera1_med","dif_med","frac_antecipa"]].to_csv(os.path.join(FIG,"F9_data.csv"),index=False)
print("fig F9")

# ==================== tabelas .tex ====================
emit("S1c_pares","Sibling pairs, both children fully observable (born 2010--2016)",
 "One row per family with exactly two children, both born 2010--2016 and spaced at least one month apart. Siblings linked by the guardian's taxpayer id (cpf\\_resp\\_aluno). Source: build05\\_irmaos.py.",
 "lr",["Item","N"],[["Guardians (valid CPF)",nf(sz.size,0)],["Families with 2+ children",nf(n2plus.size,0)],
    ["Families with exactly 2",nf(len(pair),0)],["Pairs, both born 2010--2016, spacing $\\geq$1m",nf(len(pc),0)]])
emit("S2c_por_espacamento","Difference in age at first application between siblings, by birth spacing",
 "Age at first application in months; difference is younger minus older sibling (negative = younger registered earlier). Pairs with both children born 2010--2016. Source: build05\\_irmaos.py.",
 "lrrrr",["Spacing (months)","N pairs","Mean diff","Median diff","\\% younger earlier"],
 [[str(r.iloc[0]),nf(r.n,0),nf(r.dif_med,2),nf(r.dif_medn,0),nf(r.frac_antecipa,1)] for _,r in g2c.iterrows()])
emit("S3b_por_quartil_espera","Sibling difference in age at application, by the first child's wait",
 "Pairs where the first child was referred. Quartiles of the first child's wait (application to first referral, days). Difference is younger minus older sibling (months); negative means the younger was registered earlier. Source: build05\\_irmaos.py.",
 "lrrrr",["First child wait","N pairs","Median wait (d)","Mean diff","\\% younger earlier"],
 [[str(r.q1),nf(r.n,0),nf(r.espera1_med,0),nf(r.dif_med,2),nf(r.frac_antecipa,1)] for _,r in g3.iterrows()])
emit("S4d_composicao","Composition: one-child versus multi-child families",
 "Means across children, by number of children of the guardian in the panel. Postcode income in R\\$; priority and never-enrolled in percent; age at application in months. Source: build05\\_irmaos.py.",
 "lrrrr",["Group","Postcode income","\\% priority","Age at application","\\% never enrolled"],
 [[r.grupo,nf(r.renda,0),nf(r.pct_prioridade,1),nf(r.idade_sol,1),nf(r.pct_nunca,1)] for _,r in comp.iterrows()])

# ==================== facts.md + log ====================
with open(os.path.join(OUT,"facts.md"),"w",encoding="utf-8") as f:
    f.write("# BUILD05 -- facts.md (analise de irmaos: aprendizado sobre a fila)\n\n")
    f.write("Descritivo (associacao/diferenca/variacao). Irmaos ligados por cpf\\_resp\\_aluno (Fila1018); "
            "variaveis de child\\_master. Nao modifica build01/02/03/04.\n\n## Numeros\n\n")
    for s in FACTS: f.write("- "+s+"\n\n")
with open(os.path.join(OUT,"build05.log"),"w",encoding="utf-8") as f: f.write("\n".join(LOG))
print("\nfacts.md + build05.log + tabelas + F9 OK")
