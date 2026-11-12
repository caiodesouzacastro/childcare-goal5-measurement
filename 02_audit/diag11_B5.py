# -*- coding: utf-8 -*-
import os as _os_ne  # pacote de replicacao (R3): raiz unica, variavel NE_ROOT ou a pasta acima de 02_audit
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import csv, os, collections
AUD = NE_ROOT + r"\02_audit"

# painel escola x agrup x semestre (creche)
rows=[]
with open(os.path.join(AUD,"perfil_panel_creche.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        rows.append(r)
def sidx(a,s): return int(a)*2 + (int(s)-1)  # ordem semestral
# capacidade Bercario (I+II) por escola-semestre (faixa que aperta)
berc = collections.defaultdict(int)   # (codesc, sidx) -> cap
meta = {}
allcap = collections.defaultdict(int) # (codesc, sidx) -> cap total creche
setor_of={}; dist_of={}; rede_of={}
for r in rows:
    si = sidx(r["ano"], r["sem"])
    cap = int(float(r["cap_vagofer"]))
    allcap[(r["codesc"], si)] += cap
    if r["agrup"] in ("BERC1","BERC2"):
        berc[(r["codesc"], si)] += cap
    setor_of[r["codesc"]]=r["setor"]; dist_of[r["codesc"]]=r["distrito"]; rede_of[r["codesc"]]=r["rede"]

# semestres presentes
sems = sorted(set(si for (_,si) in allcap))
print("semestres (idx):", sems, " -> 2013s1..2019s1")
escs = sorted(set(cod for (cod,_) in allcap))
print("N escolas:", len(escs))

# B5: mudancas de capacidade (creche total) entre semestres consecutivos, |delta|>=7 (~1 turma)
print("\n=== B5: eventos de mudanca de VAGOFER (escola, creche total), |delta|>=7 ===")
ev=[]  # (codesc, si_to, delta)
byyear_up=collections.Counter(); byyear_dn=collections.Counter()
mag_up=[]; mag_dn=[]
for cod in escs:
    for k in range(1,len(sems)):
        s0,s1=sems[k-1],sems[k]
        c0=allcap.get((cod,s0),0); c1=allcap.get((cod,s1),0)
        # so consecutivos reais (diferenca de 1 no idx)
        if s1-s0!=1: continue
        d=c1-c0
        if abs(d)>=7:
            ev.append((cod,s1,d))
            yr=s1//2
            if d>0: byyear_up[yr]+=1; mag_up.append(d)
            else: byyear_dn[yr]+=1; mag_dn.append(d)
print("aumentos por ano:", {y:byyear_up[y] for y in sorted(byyear_up)})
print("reducoes por ano:", {y:byyear_dn[y] for y in sorted(byyear_dn)})
import statistics as st
if mag_up: print(f"magnitude aumentos: mediana={st.median(mag_up)} media={sum(mag_up)/len(mag_up):.1f} N={len(mag_up)}")
if mag_dn: print(f"magnitude reducoes: mediana={st.median(mag_dn)} media={sum(mag_dn)/len(mag_dn):.1f} N={len(mag_dn)}")

# exportar painel escola-semestre (cap creche total e bercario) + setor/distrito para Stata
outp=os.path.join(AUD,"esc_sem_cap.csv")
with open(outp,"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["codesc","sidx","cap_creche","cap_berc","setor","distrito","rede"])
    keys=set(list(allcap.keys())+list(berc.keys()))
    for (cod,si) in sorted(keys):
        w.writerow([cod,si,allcap.get((cod,si),0),berc.get((cod,si),0),setor_of.get(cod,""),dist_of.get(cod,""),rede_of.get(cod,"")])
print("esc_sem_cap.csv exportado:", len(set(list(allcap.keys())+list(berc.keys()))),"linhas")
