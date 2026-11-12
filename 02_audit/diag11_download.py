# -*- coding: utf-8 -*-
import os as _os_ne  # pacote de replicacao (R3): raiz unica, variavel NE_ROOT ou a pasta acima de 02_audit
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import urllib.request, urllib.parse, json, ssl, os, re
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BASE = "https://dados.prefeitura.sp.gov.br/api/3/action/"
DEST = NE_ROOT + r"\01_dados_publicos"
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
def api(action, **p):
    url = BASE+action+("?"+urllib.parse.urlencode(p) if p else "")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60, context=ctx) as r: return json.load(r)
def dl(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest)>1000:
        return "JA EXISTE "+os.path.basename(dest)+f" ({os.path.getsize(dest)})"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=180, context=ctx) as r, open(dest,"wb") as f:
            f.write(r.read())
        return "OK "+os.path.basename(dest)+f" ({os.path.getsize(dest)})"
    except Exception as e:
        return "FALHA "+os.path.basename(dest)+" :: "+str(e)

# ---- PERFIL 2013-2019 ----
d = api("package_show", id="perfil-das-turmas-e-unidades-educacionais-em-funcionamento")["result"]
print("### PERFIL: baixando semestres 2013-2019 ###")
for r in d["resources"]:
    if (r.get("format","") or "").upper()!="CSV": continue
    u = r.get("url",""); base = u.split("/")[-1].lower()
    if "dicion" in base: continue
    # detectar ano
    m = re.search(r"(20)(1[3-9])", base)
    if not m: continue
    yr = int(m.group(1)+m.group(2))
    if yr<2013 or yr>2019: continue
    # semestre: jun/06/dez/12/1231
    sem = "1" if re.search(r"jun|062|0630|junho|jun18|_06|jun2", base) else ("2" if re.search(r"dez|122|1231|dezembro|dez2", base) else "?")
    label = f"perfil_{yr}s{sem}_{base}"
    label = re.sub(r"[^a-z0-9_.]","",label)[:60]
    print("  ", dl(u, os.path.join(DEST, label)))

# ---- PARCERIAS: todos os CSV ----
d = api("package_show", id="parcerias-ed-infantil")["result"]
print("\n### PARCERIAS: baixando todos os snapshots CSV ###")
for r in d["resources"]:
    if (r.get("format","") or "").upper()!="CSV": continue
    u = r.get("url",""); base = u.split("/")[-1].lower()
    if "dicion" in base: continue
    label = "parc_"+re.sub(r"[^a-z0-9_.]","", base)[:50]
    print("  ", dl(u, os.path.join(DEST, label)))
print("\nFIM download")
