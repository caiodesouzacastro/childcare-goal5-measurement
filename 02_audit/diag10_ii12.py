# -*- coding: latin-1 -*-
import os as _os_ne  # pacote de replicacao (R3): raiz unica, variavel NE_ROOT ou a pasta acima de 02_audit
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import csv, collections
P = NE_ROOT + r"\01_dados_publicos\turmas_modulo_2016_2017.csv"
rows=[]
with open(P, encoding="latin-1") as f:
    rd = csv.DictReader(f, delimiter=";")
    cols = rd.fieldnames
    for r in rd:
        rows.append(r)
print("N linhas:", len(rows))
print("colunas:", cols)
# tipos de escola e modalidade
tipos = collections.Counter(r["TIPO ESCOLA"].strip() for r in rows)
print("\nTIPO ESCOLA (top):", tipos.most_common(20))
mods = collections.Counter(r["MODALIDADE"].strip() for r in rows)
print("MODALIDADE:", mods.most_common())
datas = collections.Counter(r["DATA BASE"].strip() for r in rows)
print("DATA BASE:", datas.most_common())

# CEI / CRECHE
def isint(x):
    try: return int(x)
    except: return None
cei = [r for r in rows if r["MODALIDADE"].strip()=="CRECHE" and "CEI" in r["TIPO ESCOLA"] or ("CR.P" in r["TIPO ESCOLA"])]
cei = [r for r in rows if r["MODALIDADE"].strip()=="CRECHE"]
print("\nN turmas CRECHE:", len(cei))
series = collections.Counter(r["SERIE"].strip() for r in cei)
print("SERIE (creche):", series.most_common())

print("\n### II1: MODULO (capacidade) modal por SERIE (creche) ###")
for s in ["BERCARIO I","BERCARIO II","MINI GRUPO I","MINI GRUPO II"]:
    sub=[isint(r["MODULO"]) for r in cei if r["SERIE"].strip()==s]
    sub=[x for x in sub if x is not None]
    if sub:
        c=collections.Counter(sub)
        print(f"  {s}: N={len(sub)}  MODULO modal={c.most_common(3)}  media={sum(sub)/len(sub):.2f}")

print("\n### II2: folga (MODULO - MATRICULA) por SERIE ###")
for s in ["BERCARIO I","BERCARIO II","MINI GRUPO I","MINI GRUPO II"]:
    sub=[(isint(r["MODULO"]),isint(r["MATRICULA"])) for r in cei if r["SERIE"].strip()==s]
    sub=[(m,mt) for m,mt in sub if m is not None and mt is not None]
    if not sub: continue
    folga=[m-mt for m,mt in sub]
    n=len(folga)
    exact=sum(1 for f in folga if f==0)
    above=sum(1 for f in folga if f<0)   # matricula > modulo (acima da capacidade)
    below=sum(1 for f in folga if f>0)
    print(f"  {s}: N={n}  folga media={sum(folga)/n:.2f}  EXATO(folga=0)={exact} ({100*exact/n:.1f}%)  ACIMA(mat>mod)={above} ({100*above/n:.1f}%)  ABAIXO={below} ({100*below/n:.1f}%)")
