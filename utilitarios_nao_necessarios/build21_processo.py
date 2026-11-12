# -*- coding: utf-8 -*-
# FECHAMENTO C (26/10/2026): objecao da revisao (agente 3, item 16). As matriculas em processo (alocadas, aguardando
# confirmacao) ficam fora do numerador e do denominador da razao da Conferencia. Teste: incluir como atendidas ou
# como em espera muda o 1o ano em que a razao passa de 75% (set. e dez.)? Descritivo; nao entra no paper (memo).
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import sys; sys.stdout.reconfigure(encoding="utf-8")
import pandas as pd
S = pd.read_csv((NE_ROOT + r"\03_build\build19\serie_publicada_completa.csv"))
S = S[S.mes.isin([9, 12]) & S.ano.between(2013, 2019)].copy()
S["base"] = 100 * S.matric_creche / (S.matric_creche + S.dem_total)
S["proc_atendido"] = 100 * (S.matric_creche + S.mat_processo_creche) / (S.matric_creche + S.mat_processo_creche + S.dem_total)
S["proc_esperando"] = 100 * S.matric_creche / (S.matric_creche + S.mat_processo_creche + S.dem_total)
print(S[["ano", "mes", "matric_creche", "mat_processo_creche", "dem_total", "base", "proc_atendido", "proc_esperando"]].round(2).to_string(index=False))
for c in ("base", "proc_atendido", "proc_esperando"):
    print(c, {m: int(S[(S.mes == m) & (S[c] >= 75)].ano.min()) for m in (9, 12)})
