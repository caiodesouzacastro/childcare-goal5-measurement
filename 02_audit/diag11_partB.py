# -*- coding: utf-8 -*-
import os as _os_ne  # pacote de replicacao (R3): raiz unica, variavel NE_ROOT ou a pasta acima de 02_audit
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import csv, os, collections, datetime as dt
DIR = NE_ROOT + r"\01_dados_publicos"
AUD = NE_ROOT + r"\02_audit"

def pdate(s):
    s=(s or "").strip()
    for fmt in ("%d/%m/%Y","%Y-%m-%d","%d/%m/%y"):
        try: return dt.datetime.strptime(s,fmt).date()
        except: pass
    return None
def i(x):
    try: return int(float(str(x).replace(",",".")))
    except: return None

# registro cumulativo mais recente
P=[]
with open(os.path.join(DIR,"parc_parcerias032023.csv"), encoding="latin-1") as f:
    for r in csv.DictReader(f, delimiter=";"):
        P.append(r)
print("N registros (marco_2026):", len(P))
# indexar por escola
byesc=collections.defaultdict(list)
for r in P:
    esc=(r.get("codigo_escola","") or "").strip().lstrip("0")
    r["_esc"]=esc; r["_osc"]=(r.get("codigo_osc_parceria","") or "").strip()
    r["_ini"]=pdate(r.get("data_inicio")); r["_enc"]=pdate(r.get("data_do_encerramento"))
    r["_vag"]=i(r.get("vagas_contratadas")) or 0
    r["_dre"]=(r.get("dre","") or "").strip()
    byesc[esc].append(r)

# ---- B1: classificar encerramentos ----
enc_recs=[r for r in P if r["_enc"] is not None]
print("\n=== B1: encerramentos com data =", len(enc_recs), "===")
cls=collections.Counter()
byyear=collections.defaultdict(lambda:collections.Counter())
for r in enc_recs:
    e=r["_enc"]; esc=r["_esc"]
    cands=[o for o in byesc[esc] if o is not r and o["_ini"] and 0<=(o["_ini"]-e).days<=90]
    if any(o["_osc"]==r["_osc"] for o in cands): c="RENOVACAO"
    elif cands: c="TROCA"
    else: c="FECHAMENTO"
    r["_cls"]=c; cls[c]+=1; byyear[e.year][c]+=1
print("classificacao:", dict(cls))
print("por ano (ano: RENOVACAO/TROCA/FECHAMENTO):")
for y in sorted(byyear):
    if 2013<=y<=2019:
        c=byyear[y]; print(f"  {y}: RENOV={c['RENOVACAO']}  TROCA={c['TROCA']}  FECH={c['FECHAMENTO']}")

# ---- B2: confirmar FECHAMENTO pelo perfil (escola some/creche cai no semestre seguinte) ----
pres=set()  # (codesc, ano, sem) com creche cap>0
with open(os.path.join(AUD,"perfil_panel_creche.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if i(r["cap_vagofer"]) and i(r["cap_vagofer"])>0:
            pres.add((r["codesc"], int(r["ano"]), int(r["sem"])))
def sem_of(d): return (d.year, 1 if d.month<=6 else 2)
def next_sem(a,s): return (a, 2) if s==1 else (a+1, 1)
fech=[r for r in enc_recs if r["_cls"]=="FECHAMENTO"]
conf=0; tot=0; unconf=0
for r in fech:
    a,s=sem_of(r["_enc"]); na,ns=next_sem(a,s)
    if na>2019 or na<2013: continue   # fora da cobertura do perfil
    tot+=1
    here=(r["_esc"],a,s) in pres
    gone=(r["_esc"],na,ns) not in pres
    if gone: conf+=1
    else: unconf+=1; r["_cls"]="FECHAMENTO_NAO_CONF"
print(f"\n=== B2: FECHAMENTOS testaveis no perfil (2013-2019) = {tot} ===")
print(f"  confirmados (escola-creche some no semestre seguinte) = {conf} ({100*conf/max(1,tot):.1f}%)")
print(f"  nao confirmados (reclassificados) = {unconf}")

# ---- B3: fechamentos confirmados por ano e DRE, vagas perdidas ----
fc=[r for r in fech if r["_cls"]=="FECHAMENTO"]
print(f"\n=== B3: FECHAMENTOS CONFIRMADOS = {len(fc)} (variacao utilizavel) ===")
by_y=collections.Counter(); vag_y=collections.Counter()
for r in fc:
    y=r["_enc"].year; by_y[y]+=1; vag_y[y]+=r["_vag"]
print("por ano (N | vagas perdidas):")
for y in sorted(by_y):
    print(f"  {y}: N={by_y[y]}  vagas={vag_y[y]}")
by_dre=collections.Counter(r["_dre"][:35] for r in fc)
print("por DRE (top):", by_dre.most_common(8))

# ---- B4: ABERTURAS (data_inicio sem contrato anterior na mesma escola) ----
print("\n=== B4: ABERTURAS de conveniada ===")
ab_y=collections.Counter(); abv_y=collections.Counter()
for r in P:
    if not r["_ini"]: continue
    esc=r["_esc"]
    prev=[o for o in byesc[esc] if o is not r and o["_ini"] and o["_ini"]<r["_ini"]]
    if not prev:  # primeira parceria dessa escola
        y=r["_ini"].year; ab_y[y]+=1; abv_y[y]+=r["_vag"]
print("por ano (N novas escolas conveniadas | vagas ganhas):")
for y in sorted(ab_y):
    if 2013<=y<=2019: print(f"  {y}: N={ab_y[y]}  vagas={abv_y[y]}")

# salvar eventos de fechamento confirmado e abertura para Stata
with open(os.path.join(AUD,"eventos_conv.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["codesc","tipo","data","vagas","dre"])
    for r in fc:
        w.writerow([r["_esc"],"FECHAMENTO",r["_enc"].isoformat(),r["_vag"],r["_dre"]])
    for r in P:
        if r["_ini"]:
            esc=r["_esc"]; prev=[o for o in byesc[esc] if o is not r and o["_ini"] and o["_ini"]<r["_ini"]]
            if not prev:
                w.writerow([esc,"ABERTURA",r["_ini"].isoformat(),r["_vag"],r["_dre"]])
print("\neventos_conv.csv exportado")
