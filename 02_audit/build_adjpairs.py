# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# ADJPAIRS (revisao pos-EE, item 5): decomposicao por TODOS os pares adjacentes de coorte.
# Descritivo. Replica exatamente S3 (build03_cohort.py, condicional a entrada <=48m) e P55
# (build_p55.py, base: resolucao = 1o evento, retirada = resolucao), trocando apenas o par
# 2010->2014 por cada par adjacente e por cada base fixa. NAO escreve em 03_build nem em 04_paper.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
ROOT=NE_ROOT
B1=os.path.join(ROOT,r"03_build\build01\_staging"); B2=os.path.join(ROOT,r"03_build\build02\_staging")
B10=os.path.join(ROOT,r"03_build\build10\_staging")
OUT=os.path.join(ROOT,r"04_paper\referee_EE_2026-10\_revision\adjpairs"); os.makedirs(OUT,exist_ok=True)
EP=pd.Timestamp("1960-01-01"); MO=30.4375; COH=list(range(2010,2015))

# ---------- S3: entrantes (identico a build03_cohort.py) ----------
cm=pd.read_feather(os.path.join(B1,"child_master.feather"))
m=cm[(cm["ever_mat"]==1)&(cm["ano_nasc"].isin(COH))&(cm["idade_ent"]<=48)]
S3=m.groupby("ano_nasc").agg(N=("idade_sol","size"),app=("idade_sol","mean"),
    wait=("espera_m","mean"),entry=("idade_ent","mean")).reset_index()
S3["resid"]=S3.app+S3.wait-S3.entry

# ---------- P55: todos os solicitantes (identico a build_p55.py, base) ----------
sp=pd.read_parquet(os.path.join(B10,"spine.parquet"),
    columns=["ano_nasc","d_sol1","d_enc1","d_mat1","d_des1","d_age47","d_birth"])
sp=sp[sp.d_sol1.notna()&sp.d_birth.notna()].copy(); sp["d_sol"]=sp.d_sol1
big=pd.Timestamp("2100-01-01")
c={"ref":sp.d_enc1.where(sp.d_enc1>=sp.d_sol),"mat":sp.d_mat1.where(sp.d_mat1>=sp.d_sol),
   "age":sp.d_age47.where(sp.d_age47>=sp.d_sol,sp.d_sol),"des":sp.d_des1.where(sp.d_des1>=sp.d_sol)}
D=pd.DataFrame({k:v.fillna(big) for k,v in c.items()})
rd=D.min(axis=1); ok=rd<big
o=sp.loc[ok,["ano_nasc","d_sol","d_birth"]].copy(); o["rdate"]=rd[ok]
o["app"]=(o.d_sol-o.d_birth).dt.days/MO; o["res"]=(o.rdate-o.d_birth).dt.days/MO
o["ival"]=(o.rdate-o.d_sol).dt.days/MO
P55=o[o.ano_nasc.isin(COH)].groupby("ano_nasc").agg(N=("app","size"),app=("app","mean"),
    ival=("ival","mean"),res=("res","mean")).reset_index()

def pairs(lv,tot,parts,label):
    rows=[]
    idx=lv.set_index("ano_nasc")
    combos=[(a,a+1) for a in COH[:-1]]+[(a,2014) for a in COH[:-2]]+[(2010,b) for b in COH[2:-1]]
    seen=set()
    for a,b in combos:
        if (a,b) in seen: continue
        seen.add((a,b))
        A,B=idx.loc[a],idx.loc[b]; dt=B[tot]-A[tot]
        r={"sample":label,"pair":f"{a}-{b}","type":"adjacent" if b==a+1 else "fixed",
           "d_total":dt}
        for p in parts:
            r[f"d_{p}"]=B[p]-A[p]; r[f"share_{p}"]=100*(B[p]-A[p])/dt if abs(dt)>1e-9 else np.nan
        rows.append(r)
    return pd.DataFrame(rows)

R=pd.concat([pairs(S3,"entry",["app","wait"],"entrants (S3, entry<=48m)"),
             pairs(P55,"res",["app","ival"],"all applicants (P55, resolution)")])
S3.to_csv(os.path.join(OUT,"levels_S3.csv"),index=False)
P55.to_csv(os.path.join(OUT,"levels_P55.csv"),index=False)
R.to_csv(os.path.join(OUT,"adjpairs.csv"),index=False)
pd.set_option("display.width",200)
print("LEVELS S3 (entrants)\n",S3.round(3).to_string(index=False))
print("\nLEVELS P55 (all applicants)\n",P55.round(3).to_string(index=False))
print("\nPAIRS\n",R.round(2).to_string(index=False))
