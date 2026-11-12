# NUMEROS_V5: tabela congelada da fusão (`paper_v3.tex`, 26/10/2026)

**Regra.** Nenhum número entra em `paper_v3.tex`, `secV*.tex` ou nos floats de `assets/tables/v3w/` se não estiver nesta tabela, em `NUMEROS_V4.md` ou em `NUMEROS_V3.md`. V3 e V4 continuam válidos sem alteração e não são copiados aqui; esta tabela os indexa por seção (bloco 0) e acrescenta os números novos da fusão (blocos M e N).

**Verificação:** `02_audit/build15_numcheck.py`, apontado para `paper_v3.tex` na fusão (backup `.bak-2026-10-26-fusao`). Ele lê V3 + V4 + V5 + `congelados_v3.csv` e varre o resumo, os `secV*.tex` e os floats de `assets/tables/v3w/`.

**Limite da verificação.** O numcheck confere a presença do número na tabela, não o contexto. Um número novo que coincide com um número antigo passa sem acusar: 97,4 (saídas por encaminhamento) coincide com o limiar 97,4 da regra de completude, e 2,3 (aging out) com a margem de 2,3% do braço A. Por isso o bloco M lista todos os números novos com a origem, inclusive os que o numcheck não acusou.

**Formato.** Convenção pt-BR (vírgula decimal, ponto de milhar), como em V3 e V4.

**Origem dos logs:** B22 = `03_build/build22/robustez.log`, de `02_audit/build22_robustez.py` (3 execuções; os logs das execuções 1 e 2 estão em `robustez_tent1.log` e `robustez_tent2.log`). As tabelas `C_armA_rob_body.tex` e `C_decomp_body.tex` (em `04_paper/assets/tables/c/`) saem da execução 3.

## 0. Índice: de onde vêm os números de cada seção

| Seção de `paper_v3` | Blocos |
|---|---|
| Resumo | V4 C, D, E; V3 A; V5 M1 |
| §1 Introdução | V4 A, C, D, E; V3 A, A3, B, C; V5 M1, M2 |
| §2 Contexto | V3 E; V4 A, B |
| §3 Dados | V3 A, E; V4 C |
| §4 Registro e cobertura | V3 A, A2, A3; V4 F |
| §5 O que mudou | V3 B, C |
| §6 O número publicado | V4 C, E, F, I, L; V5 M2, M3 |
| §7 A meta nunca foi cumprida | V4 B, D, E, J, L; V5 M1 |
| §8 Indicadores | V4 G, J, K, L; V3 B, C |
| §9 Escopo | V3 A, A3, B; V4 F; V5 M1 |
| §10 Conclusão | V4 C, E; V3 A3, B, C; V5 M1 |
| Floats novos (`V3w_armArob`, `V3w_decomp`) | V5 M1, M2 |

## M1. Braço A com outros denominadores (robustez 1)

| Número | O que é | Origem |
|---|---|---|
| 464.826 | Crianças de 0 a 3 anos no Censo 2022, município de SP (106.299 + 107.727 + 121.666 + 129.134) | IBGE/SIDRA, tabela 9514 (`fontes_saidaC/censo2022/sidra9514_sp_idade.json`); B22, linha 2 |
| 531.819 | SEADE 2022, interpolado | B22, linha 3; V4 L |
| 14,4% | SEADE 2022 acima do Censo 2022 (531.819/464.826 − 1) | B22, linha 3 |
| 83,8 | Braço A, etapa, todas as redes, 2022, sobre o Censo 2022 | B22, linha 34 |
| 78,6 | Braço A, leitura literal por idade, 2022, sobre o Censo 2022 | B22, linha 34 |
| 1,228; 1,278 | Razão entre o pool de nascidos vivos e a contagem do Censo, 2010 e 2022 | B22, linha 67 |
| 23%; 28% | Os mesmos valores, como excesso dos nascidos sobre o Censo | arredondamento de 1,228 e 1,278 |
| 564.210 | Censo 2010, 0 a 3 anos | V3 E (já congelado) |
| 1,0% | Maior diferença entre a série ancorada nos Censos e a projeção em 2010–2015 (2010: 564/570) | `C_armA_rob_body.tex`, linhas 2010–2015; V3 E |
| 76,8 (2021) | Braço A, etapa, sobre a série ancorada nos Censos com forma dos nascidos; 1º ano ≥ 75 | `C_armA_rob_body.tex`, linha 2021; B22, linha 163 |
| 79,1 (2019) | Braço A, etapa, interpolação linear entre os Censos; 1º ano ≥ 75 | B22, linha 60 |
| 2021 e 2022; 2019–2022; 2019, 2021, 2022 | Anos com braço A ≥ 75: série ancorada; linear, etapa; linear, idade | B22, linhas 163, 64 e 65 |
| 73,1 | Máximo da leitura municipal + conveniada na interpolação linear (2021); fica abaixo de 75 em todo denominador | B22, linha 66. Na série ancorada a leitura é menor ainda: a população ancorada (`C_armA_rob_body.tex`, coluna Censuses) é maior ou igual à linear (B22, linhas 51–62) em todos os anos de 2010 a 2021, logo a taxa é menor ou igual a 73,1 |
| 69,5 | Máximo do braço A (etapa) sobre os nascidos vivos, 2024 | B22, linha 25 |
| B obriga em 2021 e 2022 | Série ancorada; linear: 2020–2022; SEADE e nascidos: nunca | B22, linhas 161–164 |
| 2019 | Único ano em que a meta é cumprida lendo só o braço maior (interpolação linear) | B22, linha 162 |
| 11% (2020 e 2021) | Matrícula SME de dezembro sobre o Censo municipal + conveniada de maio do mesmo ano: 1,113 | B22, linhas 48–49 |
| 7/12 e 5/12; junho de Y−4 a maio de Y | Pesos do pool de nascidos (parâmetros da definição) | `build22_robustez.py`, cabeçalho |

## M2. O que produz a queda de dezembro (robustez 2)

| Número | O que é | Origem |
|---|---|---|
| 94.262 | Encaminhamentos médios entre o fim de setembro e o fim de dezembro, 2013–2017 | B22, linha 103 |
| 71,9% | Os mesmos, como percentual da lista reconstruída em 30/9 | B22, linha 103 |
| 10,0 a 40,7% | Encaminhamentos como % da lista no início dos outros trimestres (jun.–set. 10,0; dez.–mar. 40,7) | B22, linhas 100–102 |
| cerca de 32.000 | Novos pedidos por ano entre set. e dez. (32.150 em média) | B22, linha 103 |
| 97,4%; 2,3%; 0,3% | Saídas set.→dez., 2013–2018: encaminhamento, aging out, desistência registrada | B22, linha 99 |
| 99,2% (no mínimo) | Encaminhamentos de dezembro feitos até a data de extração, 2014–2018 (100; 100; 100; 99,2; 99,8) | B22, linhas 107–111 |
| 2% (no máximo) | Diferença entre a lista reconstruída na data de extração e em 31/12 (2017: 42.044/41.243 = +1,9%) | B22, linhas 110–111 |
| Tabela A24 | Todos os valores da tabela `C_decomp_body.tex` | B22, linhas 73–97 (trecho 09->12) e 106–111 |

## M3. Estoque médio anual e o ano de cumprimento (robustez 3)

| Número | O que é | Origem |
|---|---|---|
| 23,9% | Queda da média das 4 contagens trimestrais, 2013→2017 | B22, linha 150 |
| 2016 (março); 2018 (junho e setembro); 2015 (dezembro); 2017 (média) | 1º ano com a parcela atendida ≥ 75% | B22, linhas 153–157 |

## N. Outros da fusão

| Número | O que é | Origem |
|---|---|---|
| 0,95 | Largura da Figura 2 (`width=0.95\textwidth`), parâmetro de diagramação | `tables_main.tex` do manuscrito arquivado |
| 148 | Palavras do resumo (versão final) | `abswc_v3.py` (rascunho) |
| 10.999 | Palavras do corpo, versão final | `wc2.py` (rascunho) |
| 3,47 | Razão das quedas dez./set. do estoque, 2013→2017, com as contagens exatas: (96.696 − 44.092)/96.696 = 0,5440 sobre (156.982 − 132.365)/156.982 = 0,1568. Substitui 3,46 de V4 L, que vinha de valores arredondados (54,4/15,7). **Entrou depois da 3ª execução do numcheck; conferido à mão** | Tabela 1 (`C_series_body.tex`) |
| 3,03 | Agora usado também como "maior/menor variação" do estoque (dez./set. = maior/menor), no lugar de 3,04 de V4 L | V4 J |
| 31,9 → 53,2 | Indicador 1 pelos registros de matrícula (antes o texto dava 33,2 → 53,8, do registro de pedidos). Já em V3 | V3_cohortcov |

**Números que saíram da fusão** (estavam em V3/V4 e não estão no texto novo): a decomposição exata do ganho (−0,014; +0,022; 0,238), a contabilidade da idade de entrada (7,30; 5,65; 77%; 8,84; 69%), o gap de renda (9,4 → 6,8), o aging out em três coortes (5,8; 3,8; 1,7; 15,4; 5,0), a cobertura por quartil de renda (88,1 contra 42,4), o intervalo de 214 a 324 dias da introdução antiga (324 continua na §4), e os números da seção de transferibilidade que não cabem num parágrafo (1.340.527; 1.851.884 → 1.370.410; 26,0%; 61 de 320; 6.510; 3.916; 62,6; 0,49; 61,4; £33; 250.000). Depois da verificação de consistência saíram também: o teste fora da amostra da imputação (48,1 contra 46,5; 69,3 contra 67,0), o encaminhamento 2014→2018 por mês final (0,230; 0,234; 0,231) e 3,04. Continuam congelados em V3/V4 e podem voltar.


## O. V3 FINAL (26/10/2026): série principal = nascidos ajustados aos Censos (`02_audit/build23_denominador.py`, 3 execuções; log `03_build/build23/denominador.log`)

| Número | O que é | Origem |
|---|---|---|
| 30,3 (2010); 67,4 (2018); 73,0 (2019); 74,1 (2020); 76,8 (2021); 83,8 (2022) | Braço A, etapa, série principal | `denominador.log`, bloco (c); `C_arms_v3_body.tex` |
| 70,3 (2021) | Máximo da leitura municipal + conveniada, série principal | idem |
| 78,6 (2022) | Leitura literal por idade, série principal; único ano ≥ 75 | idem |
| 1,03 (2020); 1,83 (2010); 1,25 (2015) | Razão exigência A / exigência B em dezembro, série principal; A obriga em 2010–2020 | idem |
| 0,96 (2021 e 2022) | Idem; B obriga | idem |
| +1,0% (2010); +14,4% (2022) | SEADE contra o Censo | `denominador.log`, bloco (a) |
| 0,3 a 2,4% (2013–2018); 9,9% (2021) | Erro da SEADE contra a série principal | idem |
| 1,228; 1,253; "cerca de um quarto" | Fator nascidos/Censo nas coortes de 2010 e 2016 (reescalonamento das parcelas por coorte) | `denominador.log`, bloco (b) |
| 39% (38,6% reescalado; 39,4% observado) | Parcela da alta 2010→2016 da matrícula antes de 24 meses que é cobertura | idem |
| −0,014; +0,022 | Decomposição exata do ganho (voltou ao texto para o achado E3) | NUMEROS_V3, bloco B; nota de `V3_specs` |

## P. Triagem da REVIEW_V3 (26/10/2026): matriz do veredito (`02_audit/build24_veredito.py`, 1 execução; log `03_build/build24/veredito.log`)

| Número | O que é | Origem |
|---|---|---|
| 1,07 (2021) | Exigência A / exigência B com a matrícula municipal + conveniada do Censo (345.974 + 595) na série principal: 1,065 | `veredito.log`, "contas citadas" |
| 2017–2019 | Anos em que o braço B obriga contando em setembro (série principal, SME, total); também 2021–2022 | `veredito.log`, ('principal', 9, 'SME', 'total') |
| 2021; 2021–2022 | Meta cumprida na série principal com matrícula do Censo; e com a lista sem pedidos por unidade específica | `veredito.log`, ('principal', 12, 'Censo', ...) e ('principal', 12, 'SME', 'sem_unid_especifica') |
| zero em dez./2020–2022 | Lista sem pedidos por unidade específica (dem_1 + dem_2 = 0) | `serie_publicada_completa.csv` |
| 31 de julho; 46 de 48 meses | Data de referência dos Censos; sobreposição entre o pool de jun./Y−4–mai./Y e o de ago./Y−4–jul./Y | definição (IBGE); aritmética |

## Q. INDETERMINAÇÃO (27/10/2026): matriz de combinações (`02_audit/build25_indeterminacia.py`, 3 execuções; log `03_build/build25/indeterminacia.log`; CSV `03_build/build25/combinacoes.csv`)

| Número | O que é | Origem |
|---|---|---|
| 144; 36 | Combinações (fila 2 × data 3 × população 3 × fonte da matrícula em B 2 × rede em A 2 × leitura da cláusula 2); as 36 do Painel A (todas as redes em A, só o braço maior) | `indeterminacia.log`, 1ª linha; `C_indet_body.tex` |
| 123; 21 | Combinações em que a meta nunca é cumprida num ano avaliável; com algum ano cumprido | `indeterminacia.log`, "distribuicao dos padroes" |
| 4 (2019); 8 (2020); 9 (2021) | Primeiro ano cumprido, por número de combinações | idem, "primeiro ano cumprido" |
| 4 | Combinações em que a meta é cumprida num ano e não num ano avaliável posterior | idem, "nao monotonas" |
| 13 de 36 | Combinações do Painel A com algum ano cumprido | `combinacoes.csv` (contagem com pandas, 27/10/2026) |
| 0 de 48 | Combinações com a projeção da SEADE com algum ano cumprido | `indeterminacia.log`, "por pop" |
| 2015–2022; 2018–2022; 2017–2022 | Anos em que o indicador da revisão (parcela atendida ≥ 75%) passa, contado em dezembro, setembro e na média do ano | idem, "indicador da revisao" |
| 8.083 (dez./2019); 71.078 (set./2019) | Fila sem pedido por unidade específica em 2019 (coluna (1)); o build24 omitia 2019 nessa definição | `serie_publicada_completa.csv`; `indeterminacia.log`, "diferenca contra o build24" |
| 79,1; 1,039 | 2019, interpolação linear, fila restrita, dezembro, SME: braço A e razão A/B (A obriga e é cumprido) | idem |
| −20,5; −18,9; −17,5; −53,2; 3,03 | Variação 2014→2017 da contagem do dia (mar., jun., set., dez.) e razão dez./set. | `indeterminacia.log`, "objecao 6" (confere com `C_stab_body`) |
| −20,8; −20,8; −21,5; −25,4; 1,18 | Idem, média das quatro contagens dos 12 meses que terminam no mês; razão dez./set. | idem |
| −2,6% (2019); −1,2% (2020); +2,4% (2021); +11,7% (2022) | Mudança da população principal que levaria o braço A a 75%; em 2020 A continua obrigando (A/B 1,015), em 2021 B obriga (0,980) | `indeterminacia.log`, "objecao 3" |
| 12,2%; 3,3%; 8,3% | Censo 2022, Brasil: taxa de omissão, de inclusão indevida e erro líquido de cobertura (Pesquisa de Pós-Enumeração, divulgada em 22/08/2024) | Agência Brasil, 22/08/2024 (`agenciabrasil2024ppe`); a tabela por idade do IBGE não pôde ser baixada (HTTP 403) |
| zero em dez./2020–2025 (6 de 6); positiva nas outras 30 contagens de set./2019 a ago./2026 | Fila sem pedido por unidade específica: em 2019 e mar./jun. 2020 coluna (1); de set./2020 em diante total − coluna (3) | `serie_publicada_completa.csv` (contagem com pandas, 27/10/2026) |
| 15 de 72 (fila restrita) e 6 de 72 (publicada); 15 de 48 (dez.), 2 de 48 (set.), 4 de 48 (média); 12 de 48 (linear), 9 de 48 (principal); 12 de 72 (Censo) e 9 de 72 (SME); 17 de 72 (todas as redes) e 4 de 72 (municipal); 15 de 72 (só o maior) e 6 de 72 (fila sempre) | Combinações com algum ano cumprido, por escolha | `indeterminacia.log`, "por ..." |
| 16.248 de 28.592 | Set./2021: fila sem pedido por unidade específica em espera até 30 dias (coluna (1)), sobre o total publicado | `serie_publicada_completa.csv` |

## R. FINAL (27/10/2026): pandemia (`02_audit/build26_pandemia.py`, 2 execuções; log `03_build/build26/pandemia.log`, execução 1 em `pandemia_tent1.log`; CSV `03_build/build26/pandemia_anual.csv`)

| Número no texto | Valor | Fonte |
|---|---|---|
| Combinações com algum ano cumprido / só em 2020–2021 / com 2019 / com 2022 | 21 / 14 / 4 / 4 | log, bloco (d) |
| Limite inferior das entradas (pico do ano − dezembro anterior): 2019, 2020, 2021, 2022 | 55.570; 13.062; 28.052; 8.737 | log, bloco (a) |
| Calibração 2013–2018 (limite inferior / 1os pedidos do registro) | 0,250–0,411 (média 0,327) | log, bloco (a) |
| Nascidos vivos 2020, 2021, 2022 vs 2019 | −7,2%; −13,8%; −16,7% (147.148; 136.722; 132.106 vs 158.596) | log, bloco (a) |
| Matrícula SME dez. 2019→2020 / →2021; fila dez. 2019→2020 | +29.179 / +39.648; −9.130 (9.670 → 540) | log, bloco (c) |
| Set. 2019→2020: fila; matrícula; soma | −68.597 (75.267 → 6.670); +20.490; −11,7% | log, bloco (c) |
| Pool de nascidos (maio) 2019→2020 / →2022 | −2,8% / −11,5% | log, bloco (c) |
| Set. 2019→2022: soma (matrícula + fila) | −10,9% | log, bloco (c) |
| (matrícula + fila de set.) / pool: 2019, 2022 | 0,615; 0,619 | log, bloco (b) |
| Matrícula SME dez. 2021→2022; 2022→2025 | −23.843; −31.151 (361.257 → 330.106) | log, bloco (c) / bloco (b) |
| Censo Escolar 2019→2021: privada não conveniada; municipal + conveniada | −24.183; +15.086 | log, bloco (c) |
| Setembro, população linear, matrícula do Censo: braço A 2020; A/B 2019, 2020, 2021 | 79,1%; 0,904, 1,051, 0,947 | `03_build/build25/combinacoes.csv` (linhas de setembro, `fila=total`); o bloco (d) do log que deveria imprimi-las saiu vazio (falha F-P2) |

## S. Triagem da REVIEW_V4 (27/10/2026): `02_audit/build26_pandemia.py`, 3ª e última execução (blocos (d) e (e) do log `03_build/build26/pandemia.log`; execução 2 em `pandemia_tent2.log`)

| Número no texto | Valor | Fonte |
|---|---|---|
| Combinações cumpridas só em 2020–2021 que podem ser calculadas em 2022 | 0 de 14 | log (e) |
| Combinações calculáveis até 2022 com algum ano cumprido / cumpridas também em 2022 | 5 / 4 | log (e) |
| Combinação-ano cumprida em 2010–2018 | 0 (72 combinações calculáveis nesses anos) | log (e) |
| Limite inferior em janela fixa (junho − dezembro anterior): 2019, 2020, 2021, 2022 | 29.213; 13.062; 8.227; 4.166 | log (e) |
| Calibração da janela fixa, 2013–2018 (sobre 1os pedidos de jan.–jun.) | 0,240–0,422 (texto: "24 a 42 por cento") | log (e) |
| Matrículas em processo, dezembro 2015, 2016, 2017 | 21; 38; 14.016 | log (e); `serie_publicada_completa.csv` |
| Setembro 2020, população linear: A/B com matrícula da SME (fila total; restrita) | 0,991; 0,998 (B continua maior) | log (d) |
| Combinações com algum ano cumprido contadas em dezembro | 15 de 21 | NUMEROS_V5 Q (15 de 48 em dezembro) |
| Censo 2022, crianças até 4 anos: erro | 10,0% (meninas); 10,2% (meninos) | Agência Brasil (2024), mesma matéria de `agenciabrasil2024ppe` |

## T. RETOMADA (27/10/2026, PC <usuario>): Tabela 1 em dois níveis (`02_audit/build25_indeterminacia.py` com `02_audit/build25_tabelas.py`, 1ª execução nesta máquina; log `03_build/build25/indeterminacia_retomada1.log`; `combinacoes.csv` idêntico byte a byte ao da <maquina>)

| Número no texto | Valor | Fonte |
|---|---|---|
| Combinações na Tabela 1 (leituras que o texto sustenta: braço A em todas as redes, só o braço maior, população principal ou linear) | 24 | log, linha "nucleo do corpo"; Tabela 1, linha "Combinations in this table" |
| ... com algum ano cumprido / com nenhum | 13 / 11 | idem ("algum": 13, "nunca": 11) |
| ... com algum ano cumprido antes de 2019 | 0 | idem ("antes_2019": 0) |
| ... conjuntos distintos de anos cumpridos | 8 | idem ("padroes": 8) |
| ... primeiro ano cumprido 2019 / 2020 / 2021 | 4 / 4 / 5 | idem |
| ... cumpridas num ano e não num ano avaliável posterior | 4 (todas na população linear; 3 com a matrícula do Censo, cumpridas em 2020 e não em 2021) | idem; Tabela 1 |
| Todas as 144: nunca / com algum ano / primeiro ano 2019, 2020, 2021 / não monótonas / antes de 2019 / conjuntos distintos | 123 / 21 / 4, 8, 9 / 4 / 0 / 9 | log, linha "todas as 144"; Tabela A13, Painel C |
| Combinações calculáveis em 2010–2018 / combinação-ano cumpridas nesses anos | 72 (todas na lista publicada) / 0 de 648 | `combinacoes.csv` (leitura de conferência, 27/10/2026); bloco S |
| Matrícula municipal de dezembro da SME, 2021 | 385.100 | Tabela 2 (`C_series_body.tex`) |
| Matrícula de todas as redes no Censo, maio de 2021 (não impresso; sustenta "exceeds the census count of enrollment in all networks") | 377.862 | `03_build/build23/denominador_serie.csv`, coluna `matA_total`, 2021 |
| Lista publicada em dezembro de 2021 e de 2022 | 595; 681 | Tabela 2 |
| Referência em um ano: coorte 2013, coorte 2016; ganho a partir da coorte 2012 | 0,753; 0,876; 0,245 | Tabela A25 (`V3_service.tex`), Tabela A23 (`V3_specs.tex`) |
| Lista que daria 99,99 em 2022 (texto: "a few dozen children") | no máximo cerca de 54 crianças | aritmética: 0,00015 × 361.257 / 0,99985 = 54,2 (99,985 arredondado para 99,99; matrícula de dezembro de 2022 na Tabela 2) |
| Registro retroativo (achado pelo `02_audit/infra_numcheck.py`, 1ª execução): (matrícula + lista de setembro) / pool de nascidos, 2019 e 2022 | 0,61; 0,62 | `03_build/build26/pandemia.log`, coluna `soma_set_sobre_pool` (0,614593; 0,618512) |
| Registro retroativo, nota da Tabela A4: centros geolocalizados | 2.313 | `03_build/build01/facts.md` e `build01.log` |
| Registro retroativo, nota da Tabela A5: razão entre as duas medidas de capacidade, mínimo | 0,837 | `03_build/build03/tables/R_capcheck.csv` (0,8373844) |
| Parâmetros de desenho nas notas (não são dados): limiar de 200 entrantes de fevereiro (Tabela A17); 1.000 réplicas de bootstrap e semente 20260726 (Tabela A23) | — | notas das tabelas; `build15_p3boot_clean.py` |
| **Ajuste OQ-109 (27/10/2026):** Tabela 1 só com a lista contada em 31/12 (`build25_indeterminacia.py`, execução 2 nesta máquina; log `03_build/build25/indeterminacia_retomada2.log`; `combinacoes.csv` e `C_indet_full_body.tex` idênticos aos da execução 1). Combinações / com algum ano / nunca | 8 / 7 / 1 (a mais próxima das publicações da SME) | log, linha "nucleo do corpo"; Tabela 1 |
| ... primeiro ano cumprido 2019 / 2021; não monótonas; antes de 2019; conjuntos distintos de anos | 4 / 3; 1 (lista publicada, população linear, matrícula da SME: só 2019); 0; 6 | idem |
| Setembro ou média do ano: cumprimento só com a matrícula do Censo (em todas as 144) | — | Tabela A13 (todas as células com ano nas colunas Sep. e Mean estão nas linhas "School census") |
| Dezembro como menor contagem do ano | 17 de 19 anos (2007–2025) | §5 (`secV6_series.tex`), já no texto; NUMEROS_V3/V4 |

## U. NOTAS (27/10/2026): séries de população e contagem do continente (`02_audit/build27_populacao.py`, rodada `notas-2026-10-27`, execução 1; log `03_build/build27/populacao.log`; CSV `03_build/build27/populacao_series.csv` e `combinacoes_pop6.csv`)

Checagem do script: as três séries da A13 (principal, linear, SEADE) reproduzem `03_build/build25/combinacoes.csv` nas 1.872 linhas.

| Número | O que é | Origem |
|---|---|---|
| 0 | Artigos ou estratégias da Lei 16.271/2015 que tratam da fonte de população | `lei_texto.py` (scratchpad), texto completo do HTML do catálogo; art. 4º = "censos mais atualizados da educação básica e superior" |
| 2 (1.7 d; 5.7) | Menções à SEADE na lei: só como fonte do IPVS | idem |
| 12; 7; 5 | Tabela 1 com a SEADE como terceira série (31/12, todas as redes, só o braço maior): combinações; com algum ano; nunca | `populacao.log`, bloco (2) |
| 4 de 4 | Combinações SEADE dessa fatia sem nenhum ano cumprido | idem |
| 73,3 (2022) | Máximo do braço A (etapa, todas as redes) na SEADE, 2010–2022 | bloco (1b) |
| −2,3% (2022); −6,6% (2019); −7,7% (2020); −6,9% (2021) | Mudança da população SEADE que levaria o braço A a 75% | bloco (1e) |
| 1,102 (2022); 1,052 (2021); 1,100 (2020) | A/B em dezembro na SEADE; A é o maior em 2010–2022 | bloco (1d) |
| 498,2 mil (2010); −11,7% | SEADE reescalada ao Censo 2022, 2010; distância para o Censo 2010 | blocos (1a), (1f); linha "SEADE_ancorada contra o Censo 2010" |
| 75,3 (2018) | Braço A (etapa, todas as redes) na SEADE reescalada ao Censo 2022 | bloco (1b) |
| 2018–2021; 2018–2019 | Anos cumpridos na SEADE reescalada, lista publicada, 31/12: matrícula do Censo; matrícula da SME | bloco (2) |
| 12 de 48 | Combinações com algum ano na SEADE reescalada (estrutura da A13) | bloco (3) |
| 69,0 (2022); 0 de 48 | Censo 2010 fixo (564.210): máximo do braço A; combinações com algum ano | blocos (1b), (3) |
| 65,6 (2022); 0 de 48 | Nascidos sem ajuste: máximo do braço A; combinações com algum ano | idem |
| +22,8% (2010) a +27,8% (2022) | Nascidos sem ajuste sobre a série principal | bloco (1f) |
| 20; 11; 9; 2018 em 2 | Tabela 1 com as cinco séries de população (sem os nascidos): combinações; com algum ano; nunca; primeiro ano 2018 | bloco (2) |
| 504.289; 566.000; 1,122 | SEADE 2025 na série do projeto; "566 mil crianças (dados do SEADE)" na notícia da SME de 11/08/2025; razão | linha "SEADE 2025" do log; `fontes_saidaC/noticia_SME_2025-08-11_fila_zerada_69pct.pdf` |
| 2.010 | Palavras das exibições do corpo no continente, com as legendas e notas redigidas com IA | `03_build/contagem_jpart_notas2_continente_antes.log` (`contagem_jpart.py`, execução 2 da rodada `notas-2026-10-27`) |
| 617 | Idem, com legendas e notas vazias (tabelas, figuras, rótulos, títulos de painel) | `03_build/contagem_jpart_notas3_continente_vazio.log` (execução 3) |
| 1.393 | Legendas e notas das seis exibições do corpo (2.010 − 617) | diferença entre os dois logs |
| 47 | Palavras do corpo do continente (títulos das 10 seções e o título "Tables and figures") | execução 3 |
| 107 (5 obras); 219 (9 obras); 1.539 (59 obras, v3) | Palavras das referências | execuções 3, 2 e 1 |
| 16.035 | Controle positivo: v3 arquivada medida de novo, idêntica parte por parte ao controle anterior | `03_build/contagem_jpart_notas1_controle_v3.log` (execução 1) |

## V. AUTOR-01 (27/10/2026): Tabela 1 com três séries de população e contagem do continente (`02_audit/build25_indeterminacia.py` com `02_audit/build25_tabelas.py` editado, rodada `autor-01`, execução 1; log `03_build/build25/indeterminacia_autor01.log`. `contagem_jpart.py` corrigido, rodada `autor-01`, execução 1; log `03_build/contagem_jpart_autor-01_exec1.log`)

Checagens: `combinacoes.csv` idêntico byte a byte ao anterior (`.bak-2026-10-27-autor01`); `C_indet_full_body.tex` (A13) idêntico byte a byte; `C_indet_body.tex` igual ao pré-teste (`t1_preteste.py`, scratchpad), com CRLF como antes; o log é igual ao `indeterminacia_retomada2.log`, exceto as linhas do corpo e do núcleo.

| Número | O que é | Origem |
|---|---|---|
| 12; 7; 5 | Tabela 1 (31/12, todas as redes, só o braço maior; principal, linear, SEADE): combinações; com algum ano; nunca | `indeterminacia_autor01.log`, linha "nucleo do corpo" |
| 2019 em 4; 2021 em 3 | Primeiro ano cumprido, Tabela 1 | idem |
| 0 | Combinações da Tabela 1 com ano cumprido antes de 2019 | idem |
| 1; 6 | Tabela 1: não monótonas; conjuntos distintos de anos | idem |
| 3; 1 / 4; 0 / 0; 4 | Com algum ano; nunca, por série: principal / linear / SEADE | `t1_tres_series.py` (scratchpad) |
| 0; 0; 0 | Combinações da A13 (48 por série) com ano cumprido antes de 2019: principal, linear, SEADE | idem |
| 498.176; 564.210; −11,70% | SEADE reescalada ao Censo 2022 em 2010; Censo 2010; distância (motivo da exclusão, decisão do autor) | `03_build/build27/populacao_series.csv`, coluna `pop` |
| 0,874 | Fator da reescala (464.826 / 531.819) | idem |
| 16.035 | Controle (v3 arquivada), igual parte por parte aos valores congelados | `contagem_jpart_autor-01_exec1.log` |
| 771 | Continente antes da Tabela 1 nova (cópia do PDF), igual à execução 3 da rodada `notas-2026-10-27` | idem |
| 785; 631 | Continente atual: total JPART; exibições do corpo sem legenda e nota | idem |
| 14 | Palavras das 4 linhas novas da Tabela 1 (631 − 617) | idem |
| 8.240 | Prosa pela conta medida: 12.000 − 150 − 631 − 1.393 − 1.539 − 47 | conta sobre os números acima e o bloco U |
| 24; 0; 0; 3; 10 | `paper_v4.pdf`: páginas; erros; referências indefinidas; overfull (os mesmos 4,25 pt); underfull (todos em `appendix_V3_designs.tex`) | `04_paper/paper_v4.log` |

## W. TEXTO (28/10/2026, <maquina>, rodada `texto-secoes234-2026-10-28`): número da §3 registrado por decisão do autor

| Número | O que é | Origem |
|---|---|---|
| 3.298.064 | Linhas dos arquivos de pedidos 2010–2018: soma dos nove `FGV_Microdados_Demanda_Infantil_2010..2018.csv` = observações do `Fila1018.dta` no Stata (§3, L10: "3,298,064 records") | `Dropbox/Compartilhado/Microdados_Creches_SME/LEIAME.md`, linha 40 (seção "Validacao das contagens de linha"); lida em 28/10/2026. Já citado em `notas/03_dados.md`, c, como fora dos registros NUMEROS (OQ-165) |

## X. TEXTO, §6 (28/10/2026, <maquina>, rodada `secao6-labels-2026-10-28`): números da §6 que estavam só no NUMEROS_V3

Números de `04_paper/secV4_coverage.tex` (linhas do arquivo instalado, com o cabeçalho de 5 linhas), antes registrados só em `NUMEROS_V3.md` (bloco "Não mudam", linhas 25–33; bloco "Novos", linhas 43–44; A2, linha 55; A3, linha 69). Valores conferidos nas exibições geradas e nos CSV e logs abaixo; nenhum diverge do V3.

| Número | O que é | Origem | Exibição |
|---|---|---|---|
| 42,1 / 47,9 / 57,2 | Entrantes em creche (EOL) com pedido no registro, 2010 / 2011 / 2012, % (§6 L10) | `03_build/build14_cobertura/cob_por_ano.csv`, linhas 4–6 (coluna `no_paper`); `assets/tables/v2/V2_coverage.tex`, linhas 13–15 | T4 (`tab:coverage`), Painel A; F2 |
| 98,6 a 99,9 | Idem, 2013–2018 (mínimo 2013, máximo 2018), % (§6 L10) | `cob_por_ano.csv`, linhas 7–12; `V2_coverage.tex`, linhas 16–21 | T4, Painel A; F2 |
| 41,4 de 87.228 | Entrantes de fevereiro de 2012 com pedido no registro: % e N (§6 L10) | `03_build/build14_cobertura/cob_fevereiro.csv`, linha 7 (2012, `fev` True); `V2_coverage.tex`, linha 15 (coluna February) | T4, Painel A (só o %) |
| 98,3 de 33.773 | Entrantes de 2012 nos outros meses com pedido no registro: % e N (§6 L10) | `cob_fevereiro.csv`, linha 6 (2012, `fev` False); `V2_coverage.tex`, linha 15 (coluna Other months) | T4, Painel A (só o %) |
| 32,0 a 43,6 → 95,8 a 98,8 | Cobertura de fevereiro por tipo de centro, 2012 → 2013, % (mínimo CEU EMEI; máximo CR.P.CONV em 2012, CEI DIRET em 2013) (§6 L10) | `03_build/build14_cobertura/simultaneidade.log`, linhas 4–9; `cob_fev_tipo.csv`; `assets/tables/appx/A_covtype.tex`, linhas 11–16 | A17 (`tab:covtype`) |
| 92,4 | Unidades com 20 ou mais entradas em fevereiro de 2012 e de 2013 (1.339) cuja cobertura subiu 30 pontos ou mais, % (§6 L10) | `03_build/build14_cobertura/simultaneidade.log`, linha 13 (`02_audit/build14_simultaneidade.py`, sha256 863335a01c6a460e, rodado em 28/10/2026). **Lacuna de procedência até 28/10:** a única origem era a saída de tela do script, sem log arquivado; resolvida nesta rodada com o log, valor igual (92,4) | nenhuma (só no texto) |
| 1.493; 1,9; 97,0 | Unidades com 20 ou mais entradas em fevereiro: 1.493 em 2012, das quais 1,9% com cobertura de 90% ou mais; 97,0% com 90% ou mais em 2013. **Estão nas notas e NÃO aparecem no texto da §6** | `simultaneidade.log`, linhas 11–12; `V2_coverage.tex`, linhas 15–16 (colunas Centers e Centers ≥90%) | T4, Painel A |
| 2 p.p. | Regra da janela: o semestre é completo se completude e encaminhamento registrado ficam a até 2 pontos das médias de 2014S1–2016S2 (§6 L12) | `assets/tables/v3/V3_completeness.tex`, linha 45 (nota, "within 2 points of their 2014S1--2016S2 means") | A28 (`tab:completeness`) |
| 96,4 | Limiar da coluna **Completeness (%)** da A28: média de 2014S1–2016S2 = 98,42 (97,9; 97,9; 98,6; 98,6; 98,7; 98,8), menos 2 (§6 L12) | `V3_completeness.tex`, linhas 20–25 (coluna 4) e 45 | A28, Painel A |
| 97,4 | Limiar da coluna **Referral recorded (%)** da A28, não da completude: média de 2014S1–2016S2 = 99,43 (99,2; 99,1; 99,5; 99,6; 99,6; 99,6), menos 2. A §6 L12 atribui os dois limiares à completude (OQ-173) | `V3_completeness.tex`, linhas 20–25 (coluna 5) e 45 | A28, Painel A |
| 92,8 e 98,0 | Completude por semestre do 1º pedido: 2012S1 e 2012S2, % (§6 L12) | `V3_completeness.tex`, linhas 16–17 (C17 `c2_completude_semestre`) | A28, Painel A |
| 97,9 a 99,9 | Completude de 2012S2 a 2017S2: mínimo (2014S1 e 2014S2) e máximo (2017S2), % (§6 L12) | `V3_completeness.tex`, linhas 17–27 | A28, Painel A |
| 324 / 89,5 / 0,64 | Entrantes de 2013: mediana de dias do pedido à entrada; % com pedido mais de 30 dias antes; % com pedido depois da entrada (§6 L12) | `assets/tables/appx/A_prospect.tex`, linha 13 (C17 `c3_sol_x_eol`) | A18 (`tab:prospect`) |
| 7,4 contra 25,1 | Coorte de 2010 matriculada antes de 24 meses, % dos nascidos: registro de pedidos contra registros de matrícula (EOL) (§6 L16) | `V2_coverage.tex`, linha 30 (C15 `eol_coorte_den96`) | T4, Painel B |
| 33,2 contra 31,9 | Idem, coorte de 2012 (§6 L16) | `V2_coverage.tex`, linha 32 | T4, Painel B |
| 0,5 a 1,0 | Idem, diferença em pontos nas coortes de 2013–2016 (+0,5; +0,9; +1,0; +0,6) (§6 L16) | `V2_coverage.tex`, linhas 33–36 | T4, Painel B |
| 39 | Parcela da alta 2010 → 2016 da matrícula antes de 24 meses, no registro de pedidos, que é cobertura, % (§6 L16; já no bloco O, linha 99: 38,6 reescalado, 39,4 observado) | `assets/tables/v3/V3_level.tex`, linha 40 | A20 (`tab:level`) |
| 20 a 33 | Lista reconstruída do registro ÷ lista publicada, fim de trimestre de 2010 (0,33; 0,25; 0,20; 0,31), % (§6 L8; já no NUMEROS_V4, linha 104) | `03_build/build19/nucleo.log`, linhas 250–253; `assets/tables/c/C_recon_body.tex`, linha 8 | A15 (`tab:recon`) |

## Y. TEXTO, §1, §8, §9 e §10 (29/10/2026, CaioNote, rodada `acabamento-2026-10-29`): números das seções novas sem registro próprio

Números de `04_paper/secV9_scope.tex` e `04_paper/secV8_indicators.tex` (linhas do arquivo instalado, com o cabeçalho de 5 linhas) apontados na conferência da rodada `instala-final-2026-10-29` (item 11).

| Número | O que é | Origem | Exibição |
|---|---|---|---|
| 12 | Desenhos de identificação candidatos (§8 L8: "Twelve candidate identification designs"): as 12 linhas da Tabela B1, numeradas de 1 a 12 | `04_paper/appendix_V3_designs.tex`, linhas 28–39 | B1 (`tab:designs`) |
| 504.289 → aproximadamente 504.000 | SEADE, 0–3 anos, 2025, na série do projeto; a §9 (L46: "approximately 504,000") usa o valor arredondado. O NUMEROS_V4, linha 48, registra 504.289 como o valor publicado pela SEADE para 2025 | NUMEROS_V5, linha 211 (linha "SEADE 2025" do log); NUMEROS_V4, linha 48 (`bracos.log`, linha 1) | — |
| 14/04/2026; 15/04/2026; 180 dias | Lei 15.388/2026 (PNE): data da lei, 14/04/2026; publicação no DOU, 15/04/2026. O art. 28 conta os 180 dias "da data de publicação desta Lei"; a §9 (L8: "180 days from the law's publication on April 15, 2026") usa 15/04, corretamente | `fontes_saidaC/lei_15388_2026_PNE.pdf` (art. 28; nota "publicado no DOU de 15.4.2026"); `fontes_saidaC/README_fontes.md`, linha 16; NUMEROS_V4, linha 26 | — |
| 214.561 → 338.893; 1,5795; +57,95% → 58% | Vagas autorizadas de creche (Painel A da Tabela A6: as 8 células de faixa × modalidade), 1º semestre de 2013 contra 1º semestre de 2019: razão 1,5795, isto é +57,95%, arredondado para 58% na §2 L14 ("Authorized places for children under four rose by 58\% from the first semester of 2013 to the first semester of 2019"). Acrescentado na rodada `fecha-trava-2026-10-30`, a pedido do autor | `04_paper/assets/tables/appx/A_T2.tex` (A6), linhas 13–20, colunas 2013S1 e 2019S1: soma das 8 células (a A6 não tem linha de total). Os dois totais impressos estão na Tabela A5, `04_paper/assets/tables/appx/A_Rcap.tex`, linha 18 ("Total & 214,561 & 338,893 & 57.9"), e em `03_build/build03/tables/R_capcheck.tex`, linha 17; `verificacao_final.py`, `V2.vag_2013` e `V2.vag_2019` CONFERE (`03_build/verificacao_final/run_2026-10-29_secao7-labels.log`, linhas 77–78) | A6 (`tab:T2a_capacidade`), Painel A; A5 (`tab:R_capcheck`) |

## Z. CORREÇÕES DE 11/11/2026 (<maquina>, rodada `instala-texto-2026-11-11`): linhas 58 e 277, por escolha do autor (folha `FOLHA_texto_2026-11-11.md`, itens B5.3 e B7)

Entrada nova; as linhas 58 e 277 ficam como estavam (registro append-only). Exibições citadas por nome de arquivo, por causa da renumeração do Apêndice A ainda pendente (`renumeracao.md`, entrada de 11/11/2026).

| Número | O que é | Origem | Exibição |
|---|---|---|---|
| 71,2% (substitui o 71,9% da linha 58) | Encaminhamentos médios entre o fim de setembro e o fim de dezembro, 2013–2017 (94.262,4), divididos pelo estoque médio reconstruído em 30/9 nos mesmos anos (132.466,2): **razão das médias**, 71,16%. É o número da §5 (`secV6_series.tex` L14: "equivalent to 71.2\% of the reconstructed September stock"). O 71,9% do log é a **média das cinco razões anuais** (59,3; 62,5; 75,7; 72,6; 89,5), que o texto deixou de usar | `03_build/build22/robustez.log`, linha 103 (94.262, e 71,9% como média das razões, `02_audit/build22_robustez.py` L101 e L109); estoque de 30/9 e encaminhados de 2013–2017 em `04_paper/assets/tables/c/C_decomp_body.tex`, linhas 10–14 (colunas "List on 30 Sep." e "Referred"; médias 132.466,2 e 94.262,4), incluído no `V3w_decomp.tex` | `V3w_decomp` (`tab:decomp`) |
| 11 desenhos em 12 linhas (substitui o 12 da linha 277) | Desenhos de identificação candidatos (§8 L8: "Eleven candidate identification designs failed"). A Tabela B1 tem 12 linhas, numeradas de 1 a 12; as linhas 9 ("Class-formation rule") e 10 ("Class-formation validity") são duas etapas do mesmo desenho, conforme a nota do autor na própria tabela ("Each row corresponds to one design, except rows 9 and 10, which are two stages of the same design.") | `04_paper/appendix_V3_designs.tex`, linhas 28–39 (as 12 linhas) e 43 (a nota) | B1 (`tab:designs`) |

## AA. MÉDIAS ANUAIS DA §5 (11/11/2026, <maquina>, rodada `renumera-2026-11-11`): os dois números do item [17] da rodada `instala-texto-2026-11-11` (folha, item B6.8)

São derivações dos valores impressos em `V3w_series` (`tab:series`) e não saem de log próprio. Como a tabela tem as quatro contagens trimestrais de 2013 e de 2017, o leitor reconstrói as duas médias a partir dela.

| Número | O que é | Origem | Exibição |
|---|---|---|---|
| 121.087 | Média das quatro contagens trimestrais de 2013 da lista publicada (§5, `secV6_series.tex` L10: "from 121,087 to 92,158"): 103.309 + 127.361 + 156.982 + 96.696 = 484.348; média 121.087,0 | `04_paper/assets/tables/c/C_series_body.tex` L14 (mar., jun., set. e dez. de 2013), incluído no `V3w_series`; os mesmos valores em `03_build/build19/serie_publicada_completa.csv` (`dem_total`, ano 2013, meses 3, 6, 9 e 12) | `V3w_series` (`tab:series`) |
| 92.158 | Idem, 2017: 87.906 + 104.268 + 132.365 + 44.092 = 368.631; média 92.157,75, arredondada para 92.158 | `C_series_body.tex` L18 (idem, 2017); `serie_publicada_completa.csv` (`dem_total`, ano 2017, meses 3, 6, 9 e 12) | `V3w_series` (`tab:series`) |
| 23,9% | Queda da média anual de 2013 a 2017: 1 − 92.157,75 / 121.087,0 = 23,89% (mesma frase da §5) | as duas linhas acima | `V3w_series` (`tab:series`) |
