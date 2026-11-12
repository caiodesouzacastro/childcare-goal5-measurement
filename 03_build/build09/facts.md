# BUILD09 facts (rastreabilidade dos dois numeros)

- **N1 (entrada em lote)** [build09.py]: entre as 1as solicitacoes (B\_novo, 1,524,560 com timestamp valido), a fracao cujo timestamp ao SEGUNDO e compartilhado por 2+ criancas em qualquer ponto da cidade (sem condicionar em escola/faixa/ano) e 2.7\% no total; por 100+ criancas no mesmo segundo, 0.1\%. A definicao do DIAG10-III2 (celula centro-faixa-ano do encaminhamento, encaminhamentos creche sem prioridade) reproduz 32.4\% (1,906,180 encaminhamentos) --- e a fonte do 32,4\% do paper.

- **N2 (conjunto elegivel)** [build09.py]: no universo do paper (B\_novo, 1,524,560), o numero de CEIs a <=2km do CEP tem mediana 32, p10=13, p90=66 (media 36.0). E uma contagem estatica (geografica), nao condicionada na data de abertura do CEI; a variacao entre anos reflete a geografia dos solicitantes, nao o crescimento da rede.

- **Celulas do painel de capacidade** [build09.py/build01_perfil.py]: o painel cobre 2,734 centros x 13 semestres (2013s1--2019s1) = 86,982 celulas centro x faixa x semestre nao-vazias. O 87.178 do paper e uma contagem antiga (196 celulas a mais, 0.23\%), de um painel que ainda incluia arquivos duplicados/2019s2 depois excluidos; o numero rastreavel e 86,982.

