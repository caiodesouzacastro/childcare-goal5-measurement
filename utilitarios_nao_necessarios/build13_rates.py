# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# EXT-1: cobertura de creche, municipio de Sao Paulo. Numerador: build13_coverage.py (Censo Escolar INEP).
# Denominadores: Censo Demografico 2010 (SIDRA tabela 1378, idades simples 0-3, salvo em sidra_1378_sp_2010_0a4.json)
# e pool SINASC (nascidos vivos residentes no municipio em Y-3..Y; mesma definicao do pool da Figura A3).
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
NE_SME = _os_ne.environ.get("NE_DADOS_SME", _os_ne.path.normpath(_os_ne.path.join(NE_ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")))
import sys, json, pandas as pd; sys.stdout.reconfigure(encoding="utf-8")
B=(NE_ROOT + "/03_build/build13_coverage/")
m=pd.read_csv(B+"creche_mat_sp.csv")
m["grupo"]=m.rede.map(lambda r:"mun_conv" if r in("municipal_direta","privada_conveniada_municipal") else "outra")
tot=m.groupby("ano")[["QT_MAT_INF_CRE","QT_MAT_BAS_0_3"]].sum()
mc=m[m.grupo=="mun_conv"].groupby("ano")[["QT_MAT_INF_CRE","QT_MAT_BAS_0_3"]].sum()
sid=json.load(open(B+"sidra_1378_sp_2010_0a4.json",encoding="utf-8-sig"))
cen=sum(int(r["V"]) for r in sid[1:] if r["D4N"] in("Menos de 1 ano","1 ano","2 anos","3 anos"))
s=pd.read_csv((NE_SME + "/originais/sme_dados_abertos/sinasc_nv_distrito_2006_2026.csv"),sep=";",encoding="latin-1")
T=s[s.iloc[:,0].str.contains("Total")].iloc[0]
pool={y:int(sum(T[str(k)] for k in range(y-3,y+1))) for y in range(2010,2019)}
rows=[]
for y in range(2010,2019):
    r={"ano":y,"pool_sinasc":pool[y],"censo2010_0a3":cen if y==2010 else None}
    for nm,src in(("total",tot),("mun_conv",mc)):
        for v,lab in(("QT_MAT_INF_CRE","etapa"),("QT_MAT_BAS_0_3","idade")):
            n=int(src.loc[y,v]); r[f"mat_{lab}_{nm}"]=n; r[f"cob_{lab}_{nm}_sinasc"]=round(n/pool[y],4)
            if y==2010: r[f"cob_{lab}_{nm}_censo"]=round(n/cen,4)
    rows.append(r)
o=pd.DataFrame(rows); o.to_csv(B+"cobertura_sp.csv",index=False)
# --- Denominador SEADE (adotado em 25/10, 4a rodada). Projecao "populacao em idade escolar" (0-3 so em 2010/2015/2020);
# 2018 = interpolacao linear 2015-2020 (opcao a). Verificacao (b): estimativa anual 0-4 de 2018 x razao 0-3/0-4 do Censo 2010.
R=B+"seade_raw/"
pj=pd.read_csv(R+"pop_idade_escolar-2000a2050_esp.csv",sep=";",encoding="latin-1",dtype=str); pj.columns=[c.strip() for c in pj.columns]
pj=pj[pj.cod_ibge=="3550308"].set_index("ano")["00_03anos"].str.replace(".","",regex=False).astype(int)
es=pd.read_csv(R+"estimativa_pop_idade_sexo_esp.csv",sep=";",encoding="latin-1",dtype=str)
e04=lambda y:int(es[(es.cod_ibge=="3550308")&(es.ano==str(y))&(es.idade=="00 a 04")].populacao.astype(int).sum())
c04=sum(int(r["V"]) for r in sid[1:] if r["D4N"]=="0 a 4 anos")
den={"seade2010":pj["2010"],"seade2015":pj["2015"],"seade2018a":pj["2015"]+0.6*(pj["2020"]-pj["2015"]),"seade2018b":e04(2018)*cen/c04}
print("SEADE:",{k:round(v) for k,v in den.items()},"| SEADE2010/Censo-1 = %.4f"%(pj["2010"]/cen-1))
srows=[]
for nm,y,d in (("2010",2010,den["seade2010"]),("2015",2015,den["seade2015"]),("2018a",2018,den["seade2018a"]),("2018b",2018,den["seade2018b"])):
    r={"ano":nm,"denominador":round(d)}
    for grp,src in(("total",tot),("mun_conv",mc)):
        for v,lab in(("QT_MAT_INF_CRE","etapa"),("QT_MAT_BAS_0_3","idade")): r[f"cob_{lab}_{grp}"]=round(src.loc[y,v]/d,4)
    srows.append(r)
so=pd.DataFrame(srows); so.to_csv(B+"cobertura_sp_seade.csv",index=False); print(so.to_string())
pd.set_option("display.width",250); print(o.T.to_string())
print("censo 2010 0-3:",cen,"| pool SINASC 2010:",pool[2010],"| razao pool/censo:",round(pool[2010]/cen,4))
