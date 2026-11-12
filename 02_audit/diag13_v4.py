# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
import os as _os_ne  # pacote de replicacao (R3): raiz unica, variavel NE_ROOT ou a pasta acima de 02_audit
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
# DIAG13 V4 - o elo crianca-turma existe? e qual o N do segundo estagio?
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd, numpy as np, os
AUD=NE_ROOT + r"\02_audit"
STG=NE_ROOT + r"\03_build\build01\_staging"
FILA=NE_ROOT + r"\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
M={"BERC1":7,"BERC2":9,"MINI1":12,"MINI2":25}
SERIE={1:"BERC1",2:"BERC1",3:"BERC1",4:"BERC2",5:"BERC2",6:"BERC2",11:"MINI1",27:"MINI1",28:"MINI2",29:"MINI2"}

# ---------- V4a: a fila registra a turma? ----------
cols=pd.read_stata(FILA,chunksize=1); first=next(cols)
mat_vars=[c for c in first.columns if "matricula" in c or "mat" in c]
print("### V4a: variaveis de matricula na fila ###")
print("  ",[c for c in first.columns if "esc_mat" in c or "serie_ensino_matricula" in c or c=="dt_matricula"])
print("  Existe identificador de TURMA? ", any("turma" in c.lower() for c in first.columns))
print("  -> A fila registra ESCOLA (cd_esc_matricula) e SERIE (cd_serie_ensino_matricula),")
print("     mas NAO a turma. Tamanho de turma so pode ser atribuido no nivel escola x agrup x semestre.")

# ---------- painel e janela [kM-3,kM+3] ----------
pt=pd.read_csv(os.path.join(STG,"perfil_turma.csv"))
g=pt.groupby(["codesc","agrup","sidx"]).agg(N=("matric","sum")).reset_index()
g=g[g["N"]>0].copy(); g["M"]=g["agrup"].map(M)
def near(row):
    m=row["M"]; N=row["N"]
    for k in range(1,9):
        if abs(N-k*m)<=3: return True
    return False
g["janela"]=g.apply(near,axis=1)
win=set(zip(g.loc[g["janela"],"codesc"].astype(int),g.loc[g["janela"],"agrup"],g.loc[g["janela"],"sidx"]))
print(f"\n  unidades escola x agrup x sem em [kM-3,kM+3]: {len(win)} de {len(g)}")

# ---------- V4b: criancas com PSP ligaveis a uma unidade na janela ----------
psp=[]
for f in ["psp2018_2ano.dta","psp2019_2ano.dta"]:
    d=pd.read_stata(os.path.join(AUD,f),columns=["cd_aluno_sme"]); psp.append(d)
psp=pd.concat(psp).drop_duplicates("cd_aluno_sme")
pspset=set(psp["cd_aluno_sme"].astype(int))
print(f"\n### V4b: criancas com PSP (2o ano 2018/2019): {len(pspset)} ###")

# matricula em creche dessas criancas (Fila1018)
def dp(s): return pd.to_datetime(s,format="%d/%m/%Y %H:%M:%S",errors="coerce")
rows=[]
for ch in pd.read_stata(FILA,columns=["cd_aluno_sme","dt_matricula","cd_esc_matricula","cd_serie_ensino_matricula"],chunksize=400000):
    ch=ch[ch["cd_aluno_sme"].isin(pspset)]
    ch=ch.dropna(subset=["dt_matricula","cd_esc_matricula"])
    if len(ch): rows.append(ch)
F=pd.concat(rows,ignore_index=True)
F["dmat"]=dp(F["dt_matricula"])
F=F.dropna(subset=["dmat"])
F["agrup"]=F["cd_serie_ensino_matricula"].map(SERIE)
F=F.dropna(subset=["agrup"])
F["sidx"]=F["dmat"].dt.year*2+(F["dmat"].dt.month>6).astype(int)
F["codesc"]=F["cd_esc_matricula"].astype(int)
# 1a matricula em creche por crianca
F=F.sort_values(["cd_aluno_sme","dmat"]).groupby("cd_aluno_sme",as_index=False).first()
print(f"  criancas PSP com matricula de creche (escola x agrup x sem): {len(F)}")
F["na_janela"]=[ (c,a,s) in win for c,a,s in zip(F["codesc"],F["agrup"],F["sidx"]) ]
n2=F["na_janela"].sum()
print(f"  destas, em unidade [kM-3,kM+3] (N do 2o estagio): {int(n2)}")
print(f"  por agrupamento:")
for a in ["BERC1","BERC2","MINI1","MINI2"]:
    print(f"    {a}: {int(F[(F['agrup']==a)&(F['na_janela'])].shape[0])}")
print("\nOK diag13_v4")
