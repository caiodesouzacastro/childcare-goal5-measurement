# -*- coding: utf-8 -*-
import os as _os_ne  # pacote de replicacao (R3): raiz unica, variavel NE_ROOT ou a pasta acima de 02_audit
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import csv, os, collections, datetime as dt, statistics as st
DIR = NE_ROOT + r"\01_dados_publicos"
def pdate(s):
    s=(s or "").strip()
    for f in ("%d/%m/%Y","%Y-%m-%d","%d/%m/%y"):
        try: return dt.datetime.strptime(s,f).date()
        except: pass
    return None
def i(x):
    try: return float(str(x).replace(",","."))
    except: return None
P=[]
with open(os.path.join(DIR,"parc_parcerias032023.csv"), encoding="latin-1") as f:
    for r in csv.DictReader(f, delimiter=";"): P.append(r)
for r in P:
    r["_ini"]=pdate(r.get("data_inicio")); r["_enc"]=pdate(r.get("data_do_encerramento"))
    r["_vag"]=i(r.get("vagas_contratadas")) or 0
    r["_val"]=i(r.get("valor_mensal")) or 0
    r["_enced"]= r["_enc"] is not None
    r["_percap"]= (r["_val"]/r["_vag"]) if r["_vag"]>0 else None
    r["_dur"]= ((r["_enc"] - r["_ini"]).days/365 if (r["_enc"] and r["_ini"]) else None)

print("### E2: encerramento vs tamanho/valor/idade do contrato ###")
enc=[r for r in P if r["_enced"]]
noenc=[r for r in P if not r["_enced"]]
def mean(xs): xs=[x for x in xs if x is not None]; return sum(xs)/len(xs) if xs else float('nan')
print(f"  vagas_contratadas: encerrados media={mean([r['_vag'] for r in enc]):.0f}  ativos media={mean([r['_vag'] for r in noenc]):.0f}")
print(f"  repasse per capita (R$/vaga): encerrados={mean([r['_percap'] for r in enc]):.1f}  ativos={mean([r['_percap'] for r in noenc]):.1f}")
print(f"  duracao ate encerramento (anos, so encerrados): media={mean([r['_dur'] for r in enc]):.2f}")
# correlacao bruta: repasse per capita baixo -> mais encerra?
allp=[r for r in P if r["_percap"] is not None]
allp.sort(key=lambda r:r["_percap"])
q=len(allp)//4
for k in range(4):
    seg=allp[k*q:(k+1)*q] if k<3 else allp[3*q:]
    rate=sum(1 for r in seg if r["_enced"])/len(seg)
    print(f"    quartil repasse/vaga Q{k+1} (media R${mean([r['_percap'] for r in seg]):.0f}): taxa de encerramento={rate:.3f}")
