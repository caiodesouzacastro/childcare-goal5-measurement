# -*- coding: utf-8 -*-
import os as _os_ne  # pacote de replicacao (R3): raiz unica, variavel NE_ROOT ou a pasta acima de 02_audit
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import csv, glob, os, collections, re
DIR = NE_ROOT + r"\01_dados_publicos"
AUD = NE_ROOT + r"\02_audit"

allfiles = []
for f in sorted(glob.glob(os.path.join(DIR,"perfil_20*s*_*.csv"))):
    m=re.match(r"perfil_(\d{4})s(\d)_",os.path.basename(f))
    if m: allfiles.append((f,m.group(1),m.group(2)))
allfiles.append((os.path.join(DIR,"perfil_turmas_jun2018.csv"),"2018","1"))

def isint(x):
    try: return int(float(str(x).replace(",",".")))
    except: return None
def norm_agr(desc):
    d=desc.upper()
    if "BERC" in d or d.startswith("BI") or d.startswith("BII"):
        return "BERC2" if re.search(r"\bII\b|BII", d) else "BERC1"
    if "MINI" in d or "GRUPO" in d:
        return "MINI2" if re.search(r"\bII\b", d) else "MINI1"
    return "OUTRO"

capser = collections.defaultdict(int)
rows_out=[]; escset=set(); cellset=set(); per_file={}
for path,ano,sem in allfiles:
    n=0
    with open(path, encoding="latin-1") as fh:
        rd = csv.DictReader(fh, delimiter=";")
        hdr = [h.lstrip('﻿') for h in rd.fieldnames]
        modalcol = "MODAL" if "MODAL" in hdr else None
        for r in rd:
            r = {k.lstrip('﻿'):v for k,v in r.items()}
            if (r.get("MODAL","") or "").strip().upper()!="CRECHE": continue
            ag = norm_agr((r.get("DESCSERIE","") or "").strip())
            if ag=="OUTRO": continue
            vag = isint(r.get("VAGOFER")) or 0
            cod = (r.get("CODESC","") or "").strip().lstrip("0")
            rede=(r.get("REDE","") or "").strip(); dist=(r.get("DISTRITO","") or "").strip(); setor=(r.get("SETOR","") or "").strip()
            n+=1
            capser[(int(ano),int(sem),ag)]+=vag
            escset.add(cod); cellset.add((cod,ag,ano,sem))
            rows_out.append([cod,ag,ano,sem,rede,dist,setor,vag])
    per_file[(ano,sem)]=per_file.get((ano,sem),0)+n

print("=== turmas CRECHE por semestre (diagnostico por arquivo) ===")
for k in sorted(per_file): print(f"  {k[0]}s{k[1]}: {per_file[k]}")
print(f"\nN escolas distintas = {len(escset)}")
print(f"N semestres = {len(per_file)}")
print(f"N celulas escola x agrup x semestre = {len(cellset)}")

# exportar painel escola x agrup x semestre
agg=collections.defaultdict(int); meta={}
for cod,ag,ano,sem,rede,dist,setor,vag in rows_out:
    agg[(cod,ag,ano,sem)]+=vag; meta[(cod,ag,ano,sem)]=(rede,dist,setor)
outp=os.path.join(AUD,"perfil_panel_creche.csv")
with open(outp,"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["codesc","agrup","ano","sem","rede","distrito","setor","cap_vagofer"])
    for (cod,ag,ano,sem),cap in agg.items():
        rede,dist,setor=meta[(cod,ag,ano,sem)]; w.writerow([cod,ag,ano,sem,rede,dist,setor,cap])
print(f"painel exportado: {len(agg)} linhas -> perfil_panel_creche.csv")

print("\n=== A3: capacidade autorizada (soma VAGOFER) por agrupamento x semestre ===")
agr=["BERC1","BERC2","MINI1","MINI2"]
print("ano-sem | "+" | ".join(agr))
for (a,s) in sorted(set((a,s) for (a,s,d) in capser)):
    print(f"  {a}s{s} | "+" | ".join(f"{capser.get((a,s,g),0):>7d}" for g in agr))
