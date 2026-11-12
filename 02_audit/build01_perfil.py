# -*- coding: utf-8 -*-
# BUILD01 - painel de turmas do perfil (creche) e tabelas T2, T6b, T6c, T7a.
# Capacidade = VAGOFER / CAPREAL (autorizada). MATRIC so aparece como denominador
# descritivo (razao matricula/VAGOFER, T6b), nunca para DEFINIR capacidade.
# Caminhos portateis (28/10/2026, <maquina>; sentido inverso do patch de 27/10): raiz do projeto por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import csv, os, re, collections, statistics as st

SRC = (NE_ROOT + r"\01_dados_publicos")
STG = (NE_ROOT + r"\03_build\build01\_staging")
os.makedirs(STG, exist_ok=True)

# um arquivo por semestre (2013s1..2019s1); 2018s1 vem de perfil_turmas_jun2018;
# 2019s2 excluido (estrutura incompativel); duplicatas perfil_turmas_jun2013/2015 ignoradas.
FILES = [
    ("2013","1","perfil_2013s1_turmasjun2013.csv"),
    ("2013","2","perfil_2013s2_r30turmasparadre20131231.csv"),
    ("2014","1","perfil_2014s1_turmasjun2014.csv"),
    ("2014","2","perfil_2014s2_r30turmasparadre20141231.csv"),
    ("2015","1","perfil_2015s1_turmasjun2015.csv"),
    ("2015","2","perfil_2015s2_r30turmasparadre20151231.csv"),
    ("2016","1","perfil_2016s1_turmasjun2016.csv"),
    ("2016","2","perfil_2016s2_turmasmatriculas20161231.csv"),
    ("2017","1","perfil_2017s1_turmasjun2017.csv"),
    ("2017","2","perfil_2017s2_turmasdez2017.csv"),
    ("2018","1","perfil_turmas_jun2018.csv"),
    ("2018","2","perfil_2018s2_turmasdez2018.csv"),
    ("2019","1","perfil_2019s1_turmas062019.csv"),
]

def sidx(a, s): return int(a)*2 + (int(s)-1)

def norm_agr(desc):
    d = (desc or "").upper()
    if "BERC" in d or "BER�" in d or "BER\xc7" in d:
        return "BERC2" if re.search(r"\bII\b", d) else "BERC1"
    if "MINI" in d:
        return "MINI2" if re.search(r"\bII\b", d) else "MINI1"
    return None

def num(x):
    try: return float(str(x).replace(",", "."))
    except: return None

AGR_ORDER = ["BERC1","BERC2","MINI1","MINI2"]
AGR_LAB = {"BERC1":"Bercario I","BERC2":"Bercario II","MINI1":"Mini Grupo I","MINI2":"Mini Grupo II"}
REDE_LAB = {"DIR":"Direta","CON":"Conveniada"}

rows = []   # dicts per turma-creche
for ano, sem, fn in FILES:
    path = os.path.join(SRC, fn)
    with open(path, encoding="latin-1") as f:
        rd = csv.DictReader(f, delimiter=";")
        # normalizar nomes de coluna (tirar BOM/espacos)
        for r in rd:
            r = { (k or "").strip().lstrip("﻿").upper(): v for k, v in r.items() }
            if (r.get("MODAL","") or "").strip().upper() != "CRECHE":
                continue
            agr = norm_agr(r.get("DESCSERIE",""))
            if agr is None:
                continue
            vg = num(r.get("VAGOFER"))
            mt = num(r.get("MATRIC"))
            cr = num(r.get("CAPREAL"))
            rede = (r.get("REDE","") or "").strip().upper()
            # normaliza CODESC (zero-padding inconsistente na fonte: '090026' == '90026')
            _cod=(r.get("CODESC","") or "").strip()
            _cod=str(int(_cod)) if _cod.isdigit() else _cod
            rows.append(dict(
                codesc=_cod,
                ano=int(ano), sem=int(sem), sidx=sidx(ano,sem),
                rede=rede if rede in ("DIR","CON") else "OUT",
                tipoesc=(r.get("TIPOESC","") or "").strip(),
                distrito=(r.get("DISTRITO","") or "").strip(),
                setor=(r.get("SETOR","") or "").strip(),
                agrup=agr,
                vagofer=vg if vg is not None else 0.0,
                matric=mt if mt is not None else 0.0,
                capreal=cr if cr is not None else 0.0,
            ))

print("turmas creche (todas):", len(rows))
# painel turma-level exportado
with open(os.path.join(STG,"perfil_turma.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f, fieldnames=["codesc","ano","sem","sidx","rede","tipoesc","distrito","setor","agrup","vagofer","matric","capreal"])
    w.writeheader(); w.writerows(rows)

sems = sorted(set(r["sidx"] for r in rows))
sem_lab = {}
for r in rows: sem_lab[r["sidx"]] = f"{r['ano']}s{r['sem']}"
SEMS = [(s, sem_lab[s]) for s in sems]
print("semestres:", [l for _,l in SEMS])

# ---------- T2: capacidade autorizada (soma VAGOFER) por agrup x rede x semestre ----------
# painel A: capacidade; painel B: n escolas; painel C: n turmas
capA = collections.defaultdict(float)  # (agrup,rede,sidx)->vagofer
nturmas = collections.defaultdict(int)
escset = collections.defaultdict(set)
for r in rows:
    if r["rede"] not in ("DIR","CON"): continue
    key=(r["agrup"], r["rede"], r["sidx"])
    capA[key]+=r["vagofer"]
    nturmas[key]+=1
    escset[key].add(r["codesc"])

def write_panel(fname, datadict, isset=False):
    with open(os.path.join(STG,fname),"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f)
        w.writerow(["agrup","rede"]+[l for _,l in SEMS])
        for agr in AGR_ORDER:
            for rede in ("DIR","CON"):
                row=[AGR_LAB[agr], REDE_LAB[rede]]
                for s,_ in SEMS:
                    v=datadict.get((agr,rede,s))
                    if isset: row.append(len(v) if v else 0)
                    else: row.append(round(v) if v is not None else 0)
                w.writerow(row)
write_panel("T2a_capacidade.csv", capA)
write_panel("T2b_nescolas.csv", escset, isset=True)
write_panel("T2c_nturmas.csv", nturmas)
print("T2 escrita")

# ---------- T6b: razao matricula/VAGOFER por agrup x semestre ----------
vg_sum=collections.defaultdict(float); mt_sum=collections.defaultdict(float)
for r in rows:
    k=(r["agrup"], r["sidx"])
    vg_sum[k]+=r["vagofer"]; mt_sum[k]+=r["matric"]
with open(os.path.join(STG,"T6b_ratio.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["agrup"]+[l for _,l in SEMS])
    for agr in AGR_ORDER:
        row=[AGR_LAB[agr]]
        for s,_ in SEMS:
            vg=vg_sum.get((agr,s),0); mt=mt_sum.get((agr,s),0)
            row.append(round(mt/vg,3) if vg>0 else "")
        w.writerow(row)
print("T6b escrita")

# ---------- T6c: n medio de turmas por escola-agrupamento, por rede e ano (s1) ----------
# usa apenas semestre 1 de cada ano p/ comparabilidade anual
yr_turmas=collections.defaultdict(lambda: collections.defaultdict(int))  # (ano,rede,agrup)->{codesc:count}
for r in rows:
    if r["sem"]!=1 or r["rede"] not in ("DIR","CON"): continue
    yr_turmas[(r["ano"],r["rede"],r["agrup"])][r["codesc"]]+=1
years=sorted(set(r["ano"] for r in rows if r["sem"]==1))
with open(os.path.join(STG,"T6c_turmas_por_escola.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["rede","agrup"]+[str(y) for y in years])
    for rede in ("DIR","CON"):
        for agr in AGR_ORDER:
            row=[REDE_LAB[rede], AGR_LAB[agr]]
            for y in years:
                d=yr_turmas.get((y,rede,agr),{})
                row.append(round(sum(d.values())/len(d),2) if d else "")
            w.writerow(row)
print("T6c escrita")

# ---------- T7a: n de CEIs em operacao (>=1 turma creche) por rede e ano (s1) ----------
yr_esc=collections.defaultdict(set)  # (ano,rede)->{codesc}
yr_esc_tot=collections.defaultdict(set)
for r in rows:
    if r["sem"]!=1: continue
    if r["rede"] in ("DIR","CON"):
        yr_esc[(r["ano"],r["rede"])].add(r["codesc"])
    yr_esc_tot[r["ano"]].add(r["codesc"])
with open(os.path.join(STG,"T7a_ceis_operacao.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["modalidade"]+[str(y) for y in years])
    for rede in ("DIR","CON"):
        w.writerow([REDE_LAB[rede]]+[len(yr_esc.get((y,rede),set())) for y in years])
    w.writerow(["Total"]+[len(yr_esc_tot.get(y,set())) for y in years])
print("T7a escrita")
print("OK build01_perfil")
