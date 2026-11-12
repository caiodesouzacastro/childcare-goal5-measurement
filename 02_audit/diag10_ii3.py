# -*- coding: latin-1 -*-
import os as _os_ne  # pacote de replicacao (R3): raiz unica, variavel NE_ROOT ou a pasta acima de 02_audit
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import csv, collections
AUD = NE_ROOT + r"\02_audit"
DIR = NE_ROOT + r"\01_dados_publicos"

# codigos da Fila
fila = set()
with open(AUD+r"\fila_codesc.csv", encoding="utf-8") as f:
    rd = csv.reader(f)
    next(rd)  # header
    for row in rd:
        if row and row[0].strip():
            fila.add(row[0].strip().lstrip("0"))
print("N codigos distintos na Fila:", len(fila))

def load(path):
    with open(path, encoding="latin-1") as f:
        return list(csv.DictReader(f, delimiter=";"))

# perfil jun2018: CODESC distintos (CRECHE)
rows = load(DIR+r"\perfil_turmas_jun2018.csv")
rows = [ {k.lstrip('﻿'):v for k,v in r.items()} for r in rows ]
perfil_cei = set(r.get("CODESC","").strip().lstrip("0") for r in rows if r.get("MODAL","").strip().upper()=="CRECHE" and r.get("CODESC","").strip())
print("\nperfil jun2018 CRECHE: escolas distintas =", len(perfil_cei))
inter = perfil_cei & fila
print(f"  casam com Fila: {len(inter)} ({100*len(inter)/len(perfil_cei):.1f}% do perfil)")

# parcerias: codigo_escola distintos
P = load(DIR+r"\parcerias_mar2023.csv")
parc = set(r["codigo_escola"].strip().lstrip("0") for r in P if r["codigo_escola"].strip())
print("\nparcerias: escolas conveniadas distintas =", len(parc))
interp = parc & fila
print(f"  casam com Fila: {len(interp)} ({100*len(interp)/len(parc):.1f}% das parcerias)")

# quantas escolas conveniadas com creche do perfil estao em parcerias
print("\nperfil CRECHE que sao conveniadas e casam com parcerias:")
conv = set(r.get("CODESC","").strip().lstrip("0") for r in rows if r.get("MODAL","").strip().upper()=="CRECHE" and r.get("REDE","").strip()=="CON")
print(f"  escolas CRECHE conveniadas (perfil 2018) = {len(conv)}; em parcerias = {len(conv & parc)}")
