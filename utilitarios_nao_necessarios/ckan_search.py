import urllib.request, urllib.parse, json, sys, ssl

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
BASE = "https://dados.prefeitura.sp.gov.br/api/3/action/"
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def api(action, **params):
    url = BASE + action
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60, context=ctx) as r:
        return json.load(r)

terms = ["matricula por escola e turma","modulo de atendimento","microdados rede municipal",
         "conveniada vagas","demanda matriculas educacao infantil","construcao equipamentos educacionais",
         "turma","matriculas"]
seen = {}
for t in terms:
    try:
        res = api("package_search", q=t, rows=30)
        for d in res["result"]["results"]:
            seen[d["name"]] = d
    except Exception as e:
        print("ERR term", t, e)

print("=== DATASETS CANDIDATOS (nome | titulo | org | modificado | nres) ===")
for name, d in sorted(seen.items()):
    title = d.get("title","")
    org = (d.get("organization") or {}).get("title","")
    mod = d.get("metadata_modified","")[:10]
    nres = len(d.get("resources",[]))
    # filtrar relevantes
    hay = (name+" "+title+" "+org).lower()
    if any(k in hay for k in ["matric","turma","modulo","módulo","convenia","demanda","construc","constru","vaga","educacao infantil","educação infantil","rede municipal"]):
        print(f"* {name} | {title} | {org} | {mod} | {nres} recursos")
