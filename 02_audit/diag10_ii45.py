# -*- coding: latin-1 -*-
import os as _os_ne  # pacote de replicacao (R3): raiz unica, variavel NE_ROOT ou a pasta acima de 02_audit
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import csv, collections, io
DIR = NE_ROOT + r"\01_dados_publicos"
def load(path):
    with open(path, encoding="latin-1") as f:
        return list(csv.DictReader(f, delimiter=";"))

print("################## II4 — perfil-das-turmas: capacidade (VAGOFER) por escola-agrupamento ##################")
for y in [2013,2015,2018]:
    rows = load(DIR+f"\\perfil_turmas_jun{y}.csv")
    # normalizar chaves (BOM no primeiro campo)
    rows = [ {k.lstrip('﻿'):v for k,v in r.items()} for r in rows ]
    cols = list(rows[0].keys())
    creche = [r for r in rows if r.get("MODAL","").strip().upper()=="CRECHE"]
    capcol = "VAGOFER"
    def isint(x):
        try: return int(float(str(x).replace(",",".")))
        except: return None
    vag = [isint(r.get(capcol)) for r in creche]
    nonnull = [v for v in vag if v is not None and v>0]
    rede = collections.Counter(r.get("REDE","").strip() for r in creche)
    hasmod = "MODULO" in cols
    print(f"\n--- jun{y}: N turmas CRECHE={len(creche)}  REDE={dict(rede)}  temMODULO={hasmod} ---")
    print(f"    VAGOFER preenchido (>0): {len(nonnull)}/{len(creche)}  media={sum(nonnull)/max(1,len(nonnull)):.1f}")
    # capacidade autorizada por (escola x serie) = soma VAGOFER
    cap = collections.Counter()
    for r in creche:
        v = isint(r.get(capcol))
        if v: cap[(r.get("CODESC","").strip(), r.get("DESCSERIE","").strip())] += v
    print(f"    N celulas escola x serie com capacidade = {len(cap)}")
    # nº de escolas distintas com creche
    escs = set(r.get("CODESC","").strip() for r in creche)
    print(f"    N escolas distintas com CRECHE = {len(escs)}")

print("\n\n################## II5 — parcerias (conveniadas): vagas contratadas e rescisoes ##################")
P = load(DIR+r"\parcerias_mar2023.csv")
print("N linhas =", len(P))
sit = collections.Counter(r["situacao"].strip() for r in P)
print("situacao:", sit.most_common())
def i(x):
    try: return int(float(str(x).replace(",",".")))
    except: return None
vc = [i(r["vagas_contratadas"]) for r in P]
vc = [x for x in vc if x is not None]
vb = [i(r["vagas_bercario_contratadas"]) for r in P]
vb = [x for x in vb if x is not None]
print(f"vagas_contratadas: N={len(vc)} soma={sum(vc)} media={sum(vc)/len(vc):.0f} min={min(vc)} max={max(vc)}")
print(f"vagas_bercario: N={len(vb)} soma={sum(vb)}")
# escolas distintas conveniadas
escs = set(r["codigo_escola"].strip() for r in P if r["codigo_escola"].strip())
osc = set(r["codigo_osc_parceria"].strip() for r in P if r["codigo_osc_parceria"].strip())
print(f"escolas conveniadas distintas={len(escs)}  OSC distintas={len(osc)}")
# encerramentos (rescisoes) com data
enc = [r for r in P if r["situacao"].strip()=="Encerrado"]
encdate = [r for r in enc if r["data_do_encerramento"].strip()]
print(f"parcerias Encerradas={len(enc)}  com data de encerramento={len(encdate)}")
# distribuicao do ano de encerramento
def yr(d):
    d=d.strip()
    if len(d)>=10 and d[2]=="/": return d[6:10]
    return None
anos_enc = collections.Counter(yr(r["data_do_encerramento"]) for r in encdate)
print("ano de encerramento:", sorted((k,v) for k,v in anos_enc.items() if k))
anos_ini = collections.Counter(yr(r["data_inicio"]) for r in P)
print("ano de inicio (todas):", sorted((k,v) for k,v in anos_ini.items() if k and k>="2010"))
