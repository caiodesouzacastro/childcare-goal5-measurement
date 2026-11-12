# BUILD03 -- facts.md (correcao de truncamento por coorte de nascimento; contexto demografico)

Descritivo (associacao/diferenca/variacao/composicao). Reaproveita child\_master (BUILD01), child\_dtenc (BUILD02) e SINASC/CEInfo. Escrito so em 03\_build\\build03 e 02\_audit; build01/build02 e <D>\\ intocados.

## Numeros por secao

- **S1** [build03_cohort.py]: coortes plenamente observaveis do nascimento aos 24 meses = 2010--2016 (7 coortes); ate 36 meses = 2010--2015 (6 coortes). Coortes 2008--2009 sao truncadas a esquerda; 2017--2018 a direita.

- **S2a (central)** [build03_cohort.py]: a fracao de nascidos com primeira solicitacao antes dos 24 meses sobe de 33.7\% (coorte 2010) para 70.9\% (2016); antes dos 12 meses, de 11.0\% para 50.1\%; antes dos 6 meses, 4.2\% para 33.4\%. Denominador = nascidos vivos (SINASC).

- **S2c** [build03_cohort.py]: entre quem solicitou antes dos 24 meses (truncamento identico), a idade media na solicitacao cai de 14.0 meses (2010) para 8.0 (2016); mediana 15 para 6.

- **S2d** [build03_cohort.py]: a mediana KM do tempo do nascimento a primeira solicitacao cai de 36 meses (coorte 2010) para 12 (2016); $S(24)$ de 0.663 a 0.291.

- **S3** [build03_cohort.py]: nas coortes de nascimento 2010--2014 (entrada $\leq$48m), a idade media de entrada varia -9.37 meses, repartida em 93\% solicitacao e 7\% espera.

- **S4** [build03_cohort.py]: a espera mediana KM ao encaminhamento por coorte de nascimento nao cai de forma monotona (2010=267d no Q1); em toda coorte o quartil de renda mais alto espera menos que o mais baixo.

- **S6a** [build03_demog.py]: nascidos vivos no municipio tem pico de 176,268 em 2011 e 165,230 em 2018 --- variacao pico$\to$2018 de -6.3\%. 96 distritos (excluidas as linhas Ignorado e Total; 2026 parcial descartado).

- **S6b** [build03_demog.py]: a queda de nascidos vivos do pico ate 2018 e semelhante entre distritos pobres e ricos --- Q1 (mais pobre) -6.2\% vs.\ Q4 (mais rico) -6.0\% (Q3 = -10,0\%, o maior).

- **S6c** [build03_demog.py]: a razao capacidade autorizada / pool 0--3 no municipio sobe de 0.307 (2013) para 0.514 (2019).

- **S6d** [build03_demog.py]: o ganho de cobertura 2013$\to$2019 (0.207) reparte-se em 86\% crescimento da capacidade e 14\% contracao do pool 0--3.

## S5 -- as tres versoes lado a lado (repartição da queda da idade de entrada)

| Quantidade | BUILD01 | BUILD02 | BUILD03 |
|---|---|---|---|
| Unidade / janela | ano de solicitacao 2010--2018 | ano de solicitacao 2010--2016 (730d completo) | coorte de nascimento 2010--2014 (entrada $\leq$48m) |
| Queda/variacao da idade de entrada (meses) | -19.09 | -15.11 | -9.37 |
| Fracao da solicitacao | 80\% | 99\% | 93\% |
| Fracao da espera | 20\% | 1\% | 7\% |

**Quantas coortes sustentam o numero final e qual o intervalo:** o numero do BUILD03 vem de **5 coortes de nascimento (2010--2014)**, as plenamente observaveis para a entrada ate 48 meses. As estatisticas centrais de solicitacao (S2) usam **7 coortes (2010--2016)**, plenas de 0 a 24 meses. A magnitude da ``queda'' difere entre as tres builds porque a unidade e a janela diferem (ano de solicitacao vs.\ coorte de nascimento); a quantidade comparavel e a **repartição**: a solicitacao mais precoce responde por 80\% (BUILD01), 99\% (BUILD02) e 93\% (BUILD03), e a espera por 20\%, 1\% e 7\%. As tres concordam qualitativamente: a variacao da idade de entrada e dominada pela solicitacao mais precoce, nao pela espera; o BUILD03, por coorte de nascimento e com truncamento controlado nas duas pontas, situa a parcela da espera em ~7\%.

## O que nao saiu

- Coortes de nascimento 2008--2009 (truncadas a esquerda) e 2017--2018 (a direita) ficam fora das estatisticas limpas (S2--S4); aparecem so na Tabela S1a de janelas.
- ``Fracao da coorte'' usa nascidos vivos (SINASC) como denominador e solicitantes (fila) como numerador; as duas fontes nao sao ligadas no nivel da crianca, entao a fracao supoe que os solicitantes de uma coorte nasceram no municipio naquele ano (aproximacao).
- S6c/S6d usam capacidade do perfil (VAGOFER, semestre 1) e pool de nascidos; a capacidade por distrito depende do casamento perfil--distrito (96/96) e do semestre 1 de cada ano.


## S7-S8 (adendo): a forma da subida e a cobertura da fila

Pergunta: a subida da inscricao precoce (S2a) e aprendizado difuso, mudanca de canal administrativo, ou aumento de cobertura da propria fila? As tabelas abaixo separam as leituras (descritivo, sem interpretacao causal).

- **S7a** [build03_s7s8.py]: perfil ano a ano da fracao de nascidos com 1a solicitacao antes de 12 meses: 2010=11.0\%; 2011=27.4\%; 2012=38.3\%; 2013=41.5\%; 2014=44.1\%; 2015=48.6\%; 2016=50.1\%. A subida e continua, sem salto isolado.

- **S7b** [build03_s7s8.py]: entre os solicitantes, a fracao com 1a solicitacao antes de 12 meses na coorte 2010 e 16.3\% (Q1) vs 12.5\% (Q4); a composicao precoce ja e maior no quartil de renda mais alto nas coortes iniciais.

- **S7c** [build03_s7s8.py]: a idade mediana na solicitacao (serie mensal, 108 pontos) cai de 46 meses (jan/2010) para 13 (dez/2018); a queda e gradual, sem degrau isolado em uma data unica; ha sazonalidade (oscilacoes dezembro--janeiro, p.ex.\ salto de 24 meses em jan/2013) e uma aceleracao ao longo de 2014--2015 (jan: 35 meses em 2014 -> 19 em 2015), mas nao um degrau abrupto atribuivel a uma unica data (ver F8).

- **S7d** [build03_s7s8.py]: **nao existe** variavel que registre o canal/forma da solicitacao (online, portal, presencial, posto, etc.) na microdados da fila (Fila1018) nem nos dicionarios disponiveis; ``CANAL''/``POSTO'' so aparecem no perfil das turmas (campos de escola). S7e fica sem tabela.

- **S8a** [build03_s7s8.py]: a fracao da coorte que aparece na fila em algum momento vai de 73.7\% (2010) a 76.7\% (2016) --- denominador = nascidos vivos; ``em algum momento'' e truncado a direita para as coortes recentes.

- **S8b** [build03_s7s8.py]: a fracao na fila por quartil de renda do distrito (2016) e Q1=88.1\%, Q4=42.4\% (ponte CEP--distrito casada em 98\% dos CEP).

- **S8c** [build03_s7s8.py]: a razao (antes de 12m)/(na fila) sobe de 0.149 (2010) para 0.653 (2016) --- o momento mais precoce persiste mesmo liquido de cobertura da fila.

### O que nao saiu (adendo)

- **S7e**: sem tabela --- nao existe variavel de canal (S7d), entao nao ha como tabular o canal por ano.
- **S7b**: usa denominador de solicitantes (nascidos vivos nao estao disponiveis por quartil de renda do CEP).
- **S8a/S8c**: ``em algum momento'' e truncado a direita para as coortes recentes (solicitacoes apos a idade maxima observavel nao aparecem).


## S7-S8 (adendo): a forma da subida e a cobertura da fila

Pergunta: a subida da inscricao precoce (S2a) e aprendizado difuso, mudanca de canal administrativo, ou aumento de cobertura da propria fila? As tabelas abaixo separam as leituras (descritivo, sem interpretacao causal).

- **S7a** [build03_s7s8.py]: perfil ano a ano da fracao de nascidos com 1a solicitacao antes de 12 meses: 2010=11.0\%; 2011=27.4\%; 2012=38.3\%; 2013=41.5\%; 2014=44.1\%; 2015=48.6\%; 2016=50.1\%. A subida e continua, sem salto isolado.

- **S7b** [build03_s7s8.py]: entre os solicitantes, a fracao com 1a solicitacao antes de 12 meses na coorte 2010 e 16.3\% (Q1) vs 12.5\% (Q4); a composicao precoce ja e maior no quartil de renda mais alto nas coortes iniciais.

- **S7c** [build03_s7s8.py]: a idade mediana na solicitacao (serie mensal, 108 pontos) cai de 46 meses (jan/2010) para 13 (dez/2018); a queda e gradual, sem degrau isolado em uma data unica; ha sazonalidade (oscilacoes dezembro--janeiro, p.ex.\ salto de 24 meses em jan/2013) e uma aceleracao ao longo de 2014--2015 (jan: 35 meses em 2014 -> 19 em 2015), mas nao um degrau abrupto atribuivel a uma unica data (ver F8).

- **S7d** [build03_s7s8.py]: **nao existe** variavel que registre o canal/forma da solicitacao (online, portal, presencial, posto, etc.) na microdados da fila (Fila1018) nem nos dicionarios disponiveis; ``CANAL''/``POSTO'' so aparecem no perfil das turmas (campos de escola). S7e fica sem tabela.

- **S8a** [build03_s7s8.py]: a fracao da coorte que aparece na fila em algum momento vai de 73.7\% (2010) a 76.7\% (2016) --- denominador = nascidos vivos; ``em algum momento'' e truncado a direita para as coortes recentes.

- **S8b** [build03_s7s8.py]: a fracao na fila por quartil de renda do distrito (2016) e Q1=88.1\%, Q4=42.4\% (ponte CEP--distrito casada em 98\% dos CEP).

- **S8c** [build03_s7s8.py]: a razao (antes de 12m)/(na fila) sobe de 0.149 (2010) para 0.653 (2016) --- o momento mais precoce persiste mesmo liquido de cobertura da fila.

### O que nao saiu (adendo)

- **S7e**: sem tabela --- nao existe variavel de canal (S7d), entao nao ha como tabular o canal por ano.
- **S7b**: usa denominador de solicitantes (nascidos vivos nao estao disponiveis por quartil de renda do CEP).
- **S8a/S8c**: ``em algum momento'' e truncado a direita para as coortes recentes (solicitacoes apos a idade maxima observavel nao aparecem).
