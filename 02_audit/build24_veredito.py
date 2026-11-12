# -*- coding: utf-8 -*-
# V3 FINAL, triagem da REVIEW_V3 (26/10/2026): matriz do veredito da Meta 5 por escolha nao fixada pela lei. Descritivo.
# Conferencia das contas dos pareceristas 2, 3, 4 e 6 (fonte da matricula do braco B; mes da contagem; definicao de demanda).
# Dimensoes: populacao (principal = nascidos ajustados aos Censos; SEADE; linear entre Censos); mes (dez; set);
#   fonte da matricula no braco B (SME, mesma publicacao; Censo municipal + conveniada de maio, 2008-2021);
#   definicao de demanda (total publicado; sem os pedidos por unidade especifica, publicado de set./2019 em diante);
#   leitura da clausula (so o braco maior conta; fila vazia exigida sempre).
# Braco A: etapa, todas as redes (Censo Escolar de maio). Saida: 03_build/build24/veredito.log (via tee), veredito.csv
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys, os, itertools; sys.stdout.reconfigure(encoding="utf-8")
import numpy as np, pandas as pd
ROOT = (NE_ROOT + "/"); OUT = ROOT + "03_build/build24/"; os.makedirs(OUT, exist_ok=True)
D = pd.read_csv(ROOT + "03_build/build23/denominador_serie.csv")
S = pd.read_csv(ROOT + "03_build/build19/serie_publicada_completa.csv").drop_duplicates(["ano", "mes"])
c10, c22 = 564210, 464826
D["pop_linear"] = np.where(D.ano.between(2010, 2022), c10 + (D.ano - 2010) / 12 * (c22 - c10), np.nan)
POP = {"principal": "pop_main", "SEADE": "pop_0a3", "linear": "pop_linear"}
rows = []
for y in range(2010, 2023):
    d = D[D.ano == y].iloc[0]
    for mes in (12, 9):
        s = S[(S.ano == y) & (S.mes == mes)]
        if not len(s): continue
        s = s.iloc[0]
        for dem_def in ("total", "sem_unid_especifica"):
            if dem_def == "total": dem = s.dem_total
            else:
                if pd.isna(s.dem_3): continue
                dem = s.dem_total - s.dem_3
            for fonte in ("SME", "Censo"):
                mat = s.matric_creche if fonte == "SME" else d.matA_munconv
                if pd.isna(mat): continue
                for pl, pc in POP.items():
                    pop = d[pc]
                    if pd.isna(pop): continue
                    A = 100 * d.matA_total / pop; reqA = 0.75 * pop; reqB = mat + dem
                    a_obriga = reqA > reqB
                    so_maior = (A >= 75) if a_obriga else (dem == 0)
                    fila_sempre = (dem == 0) and (A >= 75 or not a_obriga)
                    rows.append(dict(ano=y, mes=mes, demanda=dem_def, fonte_B=fonte, pop=pl, A=round(A, 1), AB=round(reqA / reqB, 3),
                                     obriga="A" if a_obriga else "B", dem=int(dem), cumpre_so_maior=so_maior, cumpre_fila_sempre=fila_sempre))
R = pd.DataFrame(rows); R.to_csv(OUT + "veredito.csv", index=False); assert len(pd.read_csv(OUT + "veredito.csv")) == len(R)
print("[gravado e relido] veredito.csv", len(R), "linhas")
print("=== anos cumpridos (leitura 'so o braco maior') por combinacao")
for k, g in R.groupby(["pop", "mes", "fonte_B", "demanda"]):
    print(k, "| cumprida em:", g[g.cumpre_so_maior].ano.tolist(), "| B obriga em:", g[g.obriga == "B"].ano.tolist())
print("=== leitura 'fila vazia sempre': anos cumpridos em qualquer combinacao:", sorted(R[R.cumpre_fila_sempre].ano.unique().tolist()))
print("=== contas citadas pelos pareceristas")
for y, mes, f, p in ((2021, 12, "Censo", "principal"), (2017, 9, "SME", "principal"), (2019, 9, "SME", "principal"), (2020, 12, "SME", "principal")):
    print(y, mes, f, p, R[(R.ano == y) & (R.mes == mes) & (R.fonte_B == f) & (R["pop"] == p) & (R.demanda == "total")][["A", "AB", "obriga", "cumpre_so_maior"]].to_dict("records"))
print("principal, dez, SME, sem unidade especifica:", R[(R["pop"] == "principal") & (R.mes == 12) & (R.fonte_B == "SME") & (R.demanda == "sem_unid_especifica")][["ano", "dem", "A", "AB", "obriga", "cumpre_so_maior"]].to_dict("records"))
