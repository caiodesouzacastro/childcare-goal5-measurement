import urllib.request, urllib.parse, json, ssl
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BASE = "https://dados.prefeitura.sp.gov.br/api/3/action/"
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
def api(action, **p):
    url = BASE+action+("?"+urllib.parse.urlencode(p) if p else "")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
        return json.load(r)
targets = ["turmas-e-matriculas","perfil-das-turmas-e-unidades-educacionais-em-funcionamento",
           "microdados-matriculas","parcerias-ed-infantil","demanda-e-matriculas",
           "evolutivo-das-vagas-em-creche-e-demanda-por-distrito-2017",
           "organizacoes-credenciadas-para-atendimento-da-educacao-infantil"]
for t in targets:
    try:
        d = api("package_show", id=t)["result"]
    except Exception as e:
        print("ERR", t, e); continue
    print("\n############################################################")
    print("DATASET:", t, "|", d.get("title",""))
    print("  notes:", (d.get("notes","") or "")[:300].replace("\n"," "))
    print("  N recursos:", len(d.get("resources",[])))
    for r in d.get("resources",[]):
        print(f"   - [{r.get('format','')}] {r.get('name','')}  ({r.get('size','?')} bytes)")
        print(f"       url: {r.get('url','')}")
