# BUILD07 -- facts.md (intencao: faixa corrente vs futura; fluxo: aceitacao e contabilidade da fila)

Descritivo. Reaproveita child\_master + Fila1018 + evolucaodemanda.csv. Nao modifica build01-06.

## Numeros

- **A2** [build07.py]: das 1as solicitacoes, 63\% sao para a faixa CORRENTE (a que a idade implica), 1\% para faixa FUTURA (mais velha que a idade), 21\% para faixa mais nova, e 15\% para nivel acima da creche.

- **A3** [build07.py]: a fracao das 1as solicitacoes para a faixa CORRENTE sobe de 27.9\% (2010) para 77.4\% (2018); por coorte, 47.1\% (2010) -> 85.7\% (2016).

- **A4** [build07.py]: entre as solicitacoes muito precoces (0--5 meses), 100\% pedem Bercario I (faixa corrente) e 0\% pedem faixa futura; quase toda solicitacao precoce e para vaga imediata, nao reserva.

- **A5** [build07.py]: restringindo a solicitacoes para a faixa corrente, a subida da fracao da coorte com 1a solicitacao antes de 12 meses persiste: 11.0\% (2010) -> 49.0\% (2016), vs 11.0\% -> 50.1\% sem restricao.

- **B3** [build07.py]: entre encaminhados, os que se inscreveram muito cedo (0--5m) tem gap mediano encaminhamento->matricula de 7 dias e 6\% nunca matriculam, vs gap 5 e 11\% para os de 24m+.

- **C2** [build07.py]: com o DEM\_CRECHE lido corretamente (separador de milhar; ver DIAG16), o estoque construido (microdados, com censura por idade) e o oficial tem correlacao 0.48 e razao mediana 0.76 (constr/oficial); ambas as series sao sazonais (pico set., vale dez.).

