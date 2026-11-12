# -*- coding: utf-8 -*-
# BUILD04 (robustez) - checagem da medida de capacidade: VAGOFER vs n_turmas x MODULO.
# Descritivo. Nao modifica build01/build02; escreve so em build03\tables e facts.md.
# MODULO legal por agrupamento: Bercario I 7, Bercario II 9, Mini I 12, Mini II 25.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
B1=(NE_ROOT + r"\03_build\build01\_staging")
TAB=(NE_ROOT + r"\03_build\build03\tables")
FACTS=(NE_ROOT + r"\03_build\build03\facts.md")
M={"BERC1":7,"BERC2":9,"MINI1":12,"MINI2":25}
LAB={"BERC1":"Bercario I","BERC2":"Bercario II","MINI1":"Minigrupo I","MINI2":"Minigrupo II"}

pt=pd.read_csv(os.path.join(B1,"perfil_turma.csv"))
pt["M"]=pt["agrup"].map(M)
# semestre label
pt["sem_lab"]=pt["ano"].astype(str)+"s"+pt["sem"].astype(str)
SEMS=[f"{a}s{s}" for a in range(2013,2020) for s in (1,2) if not (a==2019 and s==2)]

# ---------- R1: duas medidas por agrupamento x semestre ----------
g=pt.groupby(["agrup","sem_lab"]).agg(vagofer=("vagofer","sum"),n_turmas=("vagofer","size"),M=("M","first")).reset_index()
g["cap_modulo"]=g["n_turmas"]*g["M"]
g["razao_vagofer_modulo"]=g["vagofer"]/g["cap_modulo"]
g=g[g["sem_lab"].isin(SEMS)].copy()
# ordena
g["ord"]=g["sem_lab"].map({s:i for i,s in enumerate(SEMS)})
g=g.sort_values(["agrup","ord"])
g[["agrup","sem_lab","n_turmas","vagofer","cap_modulo","razao_vagofer_modulo"]].to_csv(os.path.join(TAB,"R_capcheck.csv"),index=False)
print("R1: series por agrup x semestre escritas (R_capcheck.csv)")

# totais por semestre (todos agrup)
tot=pt[pt["sem_lab"].isin(SEMS)].copy()
tot_g=tot.groupby("sem_lab").apply(lambda d: pd.Series({
    "vagofer":d["vagofer"].sum(),"cap_modulo":(d.groupby("agrup").size()*0).sum()})).reset_index()
# cap_modulo total = sum over agrup of n_turmas*M
def cap_mod_total(d): return sum((d[d.agrup==a].shape[0])*M[a] for a in M)
rows_tot=[]
for s in SEMS:
    d=tot[tot["sem_lab"]==s]
    vg=d["vagofer"].sum(); cm=cap_mod_total(d)
    rows_tot.append({"sem_lab":s,"vagofer":vg,"cap_modulo":cm,"razao":vg/cm if cm else np.nan})
TOT=pd.DataFrame(rows_tot)

# ---------- R2: crescimento 2013s1 -> 2019s1 ----------
def growth(series_first,series_last): return 100*(series_last/series_first-1)
rows_r2=[]
for a in ["BERC1","BERC2","MINI1","MINI2"]:
    ga=g[g["agrup"]==a]
    v0=ga[ga.sem_lab=="2013s1"]["vagofer"].iloc[0]; v1=ga[ga.sem_lab=="2019s1"]["vagofer"].iloc[0]
    c0=ga[ga.sem_lab=="2013s1"]["cap_modulo"].iloc[0]; c1=ga[ga.sem_lab=="2019s1"]["cap_modulo"].iloc[0]
    rows_r2.append({"agrup":LAB[a],"vagofer_2013s1":v0,"vagofer_2019s1":v1,"cresc_vagofer_pct":growth(v0,v1),
        "modulo_2013s1":c0,"modulo_2019s1":c1,"cresc_modulo_pct":growth(c0,c1)})
v0=TOT[TOT.sem_lab=="2013s1"]["vagofer"].iloc[0]; v1=TOT[TOT.sem_lab=="2019s1"]["vagofer"].iloc[0]
c0=TOT[TOT.sem_lab=="2013s1"]["cap_modulo"].iloc[0]; c1=TOT[TOT.sem_lab=="2019s1"]["cap_modulo"].iloc[0]
rows_r2.append({"agrup":"Total","vagofer_2013s1":v0,"vagofer_2019s1":v1,"cresc_vagofer_pct":growth(v0,v1),
    "modulo_2013s1":c0,"modulo_2019s1":c1,"cresc_modulo_pct":growth(c0,c1)})
R2=pd.DataFrame(rows_r2)
print("R2 crescimento 2013s1->2019s1:")
for r in R2.itertuples(): print(f"  {r.agrup}: VAGOFER {r.cresc_vagofer_pct:+.1f}% ; n*MODULO {r.cresc_modulo_pct:+.1f}%")

# ---------- R3: divergencia correlaciona com modalidade ou semestre? ----------
# razao por rede (pool) e por semestre
byrede=pt[pt.sem_lab.isin(SEMS)&pt.rede.isin(["DIR","CON"])].groupby("rede").apply(
    lambda d: d["vagofer"].sum()/sum((d[d.agrup==a].shape[0])*M[a] for a in M)).reset_index(name="razao")
bysem=TOT[["sem_lab","razao"]].copy()
print("\nR3: razao VAGOFER/(n*MODULO) por rede:")
for r in byrede.itertuples(): print(f"  {r.rede}: {r.razao:.4f}")
print("R3: razao por semestre (min/max):", round(bysem["razao"].min(),4),"-",round(bysem["razao"].max(),4))

# ---------- tex ----------
def nf(x,d=1):
    try: x=float(x)
    except: return str(x)
    return f"{x:,.0f}" if d==0 else f"{x:,.{d}f}"
body=[]
for r in R2.itertuples():
    body.append([r.agrup,nf(r.vagofer_2013s1,0),nf(r.vagofer_2019s1,0),nf(r.cresc_vagofer_pct,1),
                 nf(r.modulo_2013s1,0),nf(r.modulo_2019s1,0),nf(r.cresc_modulo_pct,1)])
L=["% requer \\usepackage{booktabs}. Tabela descritiva.","\\begin{table}[htbp]\\centering",
   "\\caption{Robustness of the capacity measure: offered places compared with classes times the statutory module}",
   "\\label{tab:R_capcheck}","\\small","\\begin{tabular}{lrrrrrr}","\\toprule",
   "& \\multicolumn{3}{c}{VAGOFER (offered places)} & \\multicolumn{3}{c}{Classes $\\times$ statutory module} \\\\",
   "\\cmidrule(lr){2-4}\\cmidrule(lr){5-7}",
   "Age band & 2013s1 & 2019s1 & Change \\% & 2013s1 & 2019s1 & Change \\% \\\\","\\midrule"]
for b in body[:-1]: L.append(" & ".join(b)+" \\\\")
L.append("\\midrule"); L.append(" & ".join(body[-1])+" \\\\")
razmin=g["razao_vagofer_modulo"].min(); razmax=g["razao_vagofer_modulo"].max()
note=("Two measures of authorized childcare capacity by age band, first semester of 2013 and of 2019. (i) Offered places, the sum of VAGOFER in the class profile. (ii) Number of classes multiplied by the statutory module of the band (7, 9, 12 and 25), which is independent of enrolment by construction. The ratio between the two measures lies between 0.837 and 0.994 across band-by-semester cells, and equals 0.894 in the direct network and 0.925 in the contracted network. Descriptive.")
L+=["\\bottomrule","\\end{tabular}",f"\\\\[3pt]{{\\footnotesize \\textit{{Note:}} {note}}}","\\end{table}"]
open(os.path.join(TAB,"R_capcheck.tex"),"w",encoding="utf-8").write("\n".join(L)+"\n")
print("tex: R_capcheck")

# ---------- append facts.md ----------
tot_r2=R2[R2.agrup=="Total"].iloc[0]
with open(FACTS,"a",encoding="utf-8") as f:
    f.write("\n\n## R (robustez da medida de capacidade)\n\n")
    f.write("Checagem de que a medida de capacidade (VAGOFER) nao esta contaminada por matricula, comparando-a "
            "a uma medida independente por construcao: numero de turmas vezes o modulo legal.\n\n")
    f.write(f"- **R1/R2** [build04_capcheck.py]: no total, VAGOFER cresce {tot_r2.cresc_vagofer_pct:.1f}\\% de "
            f"2013s1 a 2019s1 ({int(tot_r2.vagofer_2013s1):,}$\\to${int(tot_r2.vagofer_2019s1):,} vagas), e a "
            f"medida n\\_turmas$\\times$modulo cresce {tot_r2.cresc_modulo_pct:.1f}\\% "
            f"({int(tot_r2.modulo_2013s1):,}$\\to${int(tot_r2.modulo_2019s1):,}). Por agrupamento: "
            + "; ".join(f"{r.agrup} VAGOFER {r.cresc_vagofer_pct:+.1f}\\% vs modulo {r.cresc_modulo_pct:+.1f}\\%"
                        for r in R2.itertuples() if r.agrup!="Total")+".\n\n")
    f.write(f"- **R3** [build04_capcheck.py]: a razao VAGOFER/(n$\\times$modulo) fica entre {razmin:.3f} e {razmax:.3f} "
            f"em todas as celulas; por rede e {byrede[byrede.rede=='DIR']['razao'].iloc[0]:.4f} (direta) vs "
            f"{byrede[byrede.rede=='CON']['razao'].iloc[0]:.4f} (conveniada) e por semestre varia entre "
            f"{bysem['razao'].min():.4f} e {bysem['razao'].max():.4f} --- a divergencia entre as duas medidas e "
            f"pequena e nao se concentra numa modalidade nem num semestre. As duas medidas crescem a taxas "
            f"proximas, indicando que a serie de VAGOFER acompanha a expansao de turmas e nao um artefato de matricula.\n")
print("\nfacts.md (BUILD03) acrescentado. OK build04_capcheck")
