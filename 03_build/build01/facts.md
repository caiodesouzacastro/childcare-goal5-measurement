# BUILD01 -- facts.md

Fonte de cada numero das tabelas e figuras do BUILD01. Paper descritivo: a redacao deve usar apenas linguagem de associacao/diferenca/variacao/composicao (evitar termos de causalidade).

**Regras cumpridas:** capacidade sempre de VAGOFER/MODULO/CAPREAL/vagas\_contratadas (nunca de matricula); nada em Dropbox\\ (exceto \_audit\\) ou <D>\\ foi modificado; nenhum artefato do pipeline invalidado (rvar, dt\_corte, trat\_ber\*) foi usado.

## Numeros por tabela

- **T1** [build01_child_tables.py]: universo de 1.524.560 solicitacoes. Idade mediana na solicitacao cai de 35 meses (2010) para 11 (2018). % nunca matriculado: 29.2% (2010), minimo 7.9% (2015), 18.3% (2018, censura a direita). Renda mediana do CEP ~R$ 939; n mediano de CEIs <=2km = 32.

- **T2** [build01_perfil.py]: capacidade autorizada total (VAGOFER, DIR+CON) por agrupamento, 2013s1->2019s1: Bercario I 19,733->32,620; Bercario II 47,405->86,402; Mini Grupo I 73,147->104,040; Mini Grupo II 74,276->115,831.

- **T3** [build01_child_tables.py]: idade media de entrada cai de 40.71 meses (2010) para 21.63 (2018); idade media na solicitacao 32.62->17.30; espera media 8.10->4.35. Verificacao da identidade |col5|<=0.042 mes.

- **T3b** [build01_child_tables.py]: entre 2010 e 2018 a idade media de entrada caiu -19.09 meses; 80% dessa queda corresponde a solicitacao mais precoce e 20% a menor espera.

- **T4d** [build01_child_tables.py]: os 203.715 nunca matriculados, vs. matriculados, solicitam mais tarde (idade media 29.2 vs 21.4 meses), tem renda do CEP levemente maior (R$ 1295 vs 1201; dif R$ 94, EP 3.0), menos CEIs proximos (34.3 vs 36.2) e muito menos prioridade (4.0% vs 16.1%).

- **T5a** [build01_child_tables.py]: 12.3% das criancas matriculam-se no CEI mais proximo; 39.0% num CEI alem de ~2km ou sem coordenada.

- **T5c** [build01_child_tables.py]: a modalidade das matriculas passa de Direta 23.9% / Conveniada 51.3% (2010) para Direta 13.9% / Conveniada 69.7% (2018).

- **T6a** [build01_rest.py]: turmas na capacidade (matricula=MODULO) em 2017: Berc.I 89,4%, Berc.II 75,6%, Mini I 62,3%, Mini II 23,3% (Mini II, modulo 25, com 75,5% abaixo da capacidade).

- **T7a** [build01_perfil.py]: CEIs em operacao passam de 1.641 (2013) para 2.406 (2019); a rede direta fica ~400--450 e a conveniada cresce de 1.223 para 2.004.

- **T7b** [build01_rest.py]: aberturas de parcerias somam ~2.070 escolas em 2013--2019 (pico 692 em 2015, 96.397 vagas); fechamentos com vagas crescem de 23 (2015) a 110 (2018, 14.505 vagas) e 84 (2019, 12.158). Saldo de vagas positivo todos os anos.

- **T7c** [build01_rest.py]: a capacidade autorizada de Bercario por solicitacao (mediana entre setores) sobe de ~0,31--0,45 (2013) para ~0,62--0,65 (2018), convergindo entre quartis de renda do setor.

- **T8a** [build01_rest.py]: coortes 2008--2012, % com 1o ano observado 28--33%; on-time ~99,3% e repetencia 2,5--3,3% (levemente maior no quartil de renda mais baixo: 3,33% Q1 vs 2,47% Q4).

- **T8b**: NAO DISPONIVEL -- as notas de proficiencia da PSP (mat/port) nao estao nos arquivos reutilizaveis (so ha indicadores de participacao); os escores so existem no pipeline RDD invalidado, vedado nesta tarefa.

## O que NAO saiu

- **T8b (proficiencia PSP)**: nao disponivel. Os arquivos reutilizaveis de PSP so tem indicadores de participacao; as notas de mat/port so existem no pipeline RDD invalidado, vedado.
- **T5a rank**: 39,5% das matriculas caem em ``fora'' (CEI >2km ou sem coordenada no cadastro geolocalizado de 2.313 CEIs); o rank so e calculado dentro do conjunto geolocalizado.
- **Serie do perfil**: termina em 2019s1 (dez/2019 incompativel); 2018s1 vem do snapshot jun/2018.
- **Anos pre-2010**: 51.106 solicitacoes de 2006--2009 entram so na coluna Total de T1.
- **IPVS**: casado a 99,5% dos CEP via setor censitario; grupos 0--6 (grupo 0 tratado como ausente).
- **Modalidade em T2/T7a**: ``Conveniada''=REDE CON agrupa parceiras e indiretas (o perfil so separa DIR/CON); a separacao em 3 vias (Direta/Indireta/Conveniada) so aparece em T5c.
