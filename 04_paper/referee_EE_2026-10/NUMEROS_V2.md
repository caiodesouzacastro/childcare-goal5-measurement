# NUMEROS_V2: tabela congelada da janela limpa (Fase 2, etapa 1.6, 25/10/2026)

Regra: nenhum número entra no texto sem estar aqui, com a origem. Os valores por tabela gerada estão também em `03_build/build15/congelados_tabelas.csv` (78 itens, escritos pelo `build15_tables.py`).

Abreviações das origens:
- **C14** = `03_build/build14_cobertura/`
- **C15** = `03_build/build15/`
- **TAB** = tabelas do paper em `04_paper/assets/tables/`
- **V2** = `04_paper/assets/tables/v2/`

## A. Cobertura do registro
| Número | Valor | Origem |
|---|---|---|
| Entrantes encontrados no registro, 2010 / 2011 / 2012 | 42,1 / 47,9 / 57,2% | V2_coverage (C14 cob_por_ano) |
| Idem, 2013–2018 | 98,6 / 99,2 / 98,8 / 99,3 / 98,9 / 99,9% | V2_coverage |
| Fevereiro de 2012 contra os outros meses | 41,4% (87.228 entrantes) contra 98,3% (33.773); mês a mês, mar.–dez. de 96,2 a 99,3% | V2_coverage; C14 cob_fevereiro |
| Ausentes que entraram em fevereiro (2010 / 2011 / 2012) | 99,6 / 99,8 / 98,9% | C14 (build14_cobertura.py) |
| Idade mediana na entrada, ausentes contra presentes | 2010: 26 contra 17 meses; 2011: 30 contra 23; 2012: 27 contra 28 | C14 cob_idade |
| Unidades com 20 ou mais entradas em fevereiro: N / mediana / % com 90% ou mais | 2011: 1.328 / 0,47 / 0,8%; 2012: 1.493 / 0,40 / 1,9%; 2013: 1.519 / 1,00 / 97,0%; 2014: 1.550 / 1,00 / 98,8% | V2_coverage |
| Unidades presentes em 2012 e 2013 que subiram 30 pontos ou mais | 92,4% (de 1.339) | build14_simultaneidade.py |
| Tipos de centro, fevereiro de 2012 → 2013 | de 32,0–43,6% para 95,8–98,8% | A_covtype |
| Matriculados antes de 24 meses (% dos nascidos), fila contra EOL | 2010: 7,4 contra 25,1; 2011: 22,8 / 28,3; 2012: 33,2 / 31,9; 2013: 43,4 / 42,9; 2014: 44,1 / 43,2; 2015: 46,6 / 45,6; 2016: 53,8 / 53,2. **De 2013 em diante, diferença de 0,5 a 1,0 ponto.** | V2_coverage (C15 eol_coorte_den96; denominador = 96 distritos, como no paper) |
| Solicitantes de 2011 com 1º encaminhamento em dez./2012 | 37,1% | COBERTURA_FILA §5 |
| Solicitantes de 2011: entrada no EOL em fev./2013 contra fev./2012 | 32.537 contra 5.371 | COBERTURA_FILA §5 |
| 1as solicitações em 2013–2018 | 1.047.288 (de 1.524.560) | C14 v2nums |
| Degrau de registro: linhas de encaminhamento por 1º encaminhamento | 1,00–1,01 (2010S1–2012S1); 1,24 (2012S2); 2,09 (2013S1) | C15 degrau_semestral |
| Coorte de 2013, amostra de duração, que solicitou em jul./2012–dez./2013 | 29,8% (N = 140.811) | build15_degrau_reforma.py |

## B. Serviço (coortes 2013–2016; anos de solicitação 2013–2017)
| Número | Valor | Origem |
|---|---|---|
| Encaminhamento em 1 ano, por coorte | 0,753 / 0,761 / 0,814 / 0,876 | V2_service (TAB E1_cohort) |
| Matrícula em 1 ano, por coorte | 0,644 / 0,639 / 0,686 / 0,747 | V2_service (TAB P2_endpoint) |
| Ganhos 2013 → 2016 | encaminhamento +0,123; matrícula +0,103 | V2_naive |
| ref180; ref730; age365 | 0,417 → 0,522; 0,945 → 0,993; 0,023 → 0,000 | V2_service |
| Tempo médio restrito (RMST) sem encaminhamento | 203 → 181 dias; sem matrícula: 230 → 220 | V2_service |
| Mediana até o encaminhamento | 223 → 171 dias | V2_service |
| Lacuna entre encaminhamento e matrícula em 1 ano | 0,109 (2013); 0,129 (2016) | aritmética V2_service |
| Por ano de solicitação 2013 → 2017 | encaminhamento 0,646 → 0,903 (+0,257); matrícula 0,551 → 0,764; mediana 278 → 187 dias | V2_service |
| Por semestre: 1º sem. 2013 / 1º sem. 2016 / 1º sem. 2018 | 0,707 / 0,800 / 0,974 | V2_service Painel C |
| Antes e depois da reforma, 1º semestre | +0,093 (2013S1 → 2016S1); +0,174 (2016S1 → 2018S1); 2016S1 → 2017S1: +0,116 | aritmética C15 reforma_semestral |
| 2º semestre | 0,568 (2013S2); 0,760 (2015S2); 0,724 (2016S2); 0,887 (2017S2) | V2_service |
| Parte de cada coorte que solicitou a partir de jul./2016 | 2013: 8,2%; 2014: 20,0%; 2015: 40,0%; 2016: 85,8% | build15_degrau_reforma.py |
| Especificações: base / desistência / tardios / 1º semestre / sem jul./2012–dez./2013 / a partir de 2014 / matrícula | +0,123 / +0,122 / +0,178 / +0,091 / +0,083 / +0,115 / +0,103 | V2_specs |
| Padronizado (células principais), IC de 95% | +0,132 [+0,128; +0,134]; bruto +0,123 [+0,120; +0,126] | V2_specs (C15 p3boot_2013_2016.log) |
| Padronizado, células grossa / fina | +0,132 / +0,124 | V2_specs |
| Com ambiente de oferta | +0,116; grossa +0,127; fina +0,115 | V2_specs |
| Decomposição exata | composição −0,009; ambiente +0,016; residual +0,116 | C15 p3_2013_2016.log |
| Aging out, todos os solicitantes | 11,5% (2013) → 5,0% (2014); 2013: 8,0 pontos de tardios + 3,5 de elegíveis; 2014: 3,4 + 1,6 | TAB N1_agingout |
| Aging out, elegíveis | 3,8 → 1,7% | TAB N1_agingout |
| Gradiente de renda Q4 − Q1 | 9,3 → 6,8 p.p. (Q1 0,722 → 0,855; Q4 0,815 → 0,923) | TAB A_E2 |
| Nunca matriculados, solicitações 2013–2017 | 9,1% (80.534 de 881.957); por ano: 9,6% (2014) → 8,6% (2016); 18,3% em 2018 (seguimento curto) | A_T4dv2; TAB A_T1 |
| Nunca contra matriculados | idade 26,0 contra 19,6 meses; prioridade 4,7 contra 19,2%; renda R$ 1.367 contra 1.207 | A_T4dv2 |
| Matrícula após encaminhamento (C4, solicitações 2013+) | célula 0–5 meses e 0–30 dias: N 22.935, 94,3%, idade mediana 4 meses; faixa entre células 84,6–94,6%; re-encaminhamento após recusa 58,1–87,2% | A_C4v2 |

## C. Timing de inscrição (coortes 2013–2016)
| Número | Valor | Origem |
|---|---|---|
| Registrados antes de 6 / 12 / 24 meses (% dos nascidos) | 26,1 → 33,4; 41,5 → 50,1 (série 41,5 / 44,1 / 48,6 / 50,1); 62,3 → 70,9 | V2_timing |
| Mediana do nascimento à 1ª solicitação | 17 → 12 meses | C14 v2nums |
| Antes de 12 meses entre os registrados antes de 24 | 0,666 / 0,664 / 0,701 / 0,707 (+0,041) | V2_timing |
| Com pesos distritais de 2010 / 2016 | 0,666 → 0,708; 0,666 → 0,707 | V2_timing |
| Distritos | sobe em 85 de 96; mediana +0,042; de −0,060 a +0,171 | V2_timing (C14 janela_distritos) |
| Restrito à faixa corrente, antes de 12 meses | 41,5 → 49,0 | C14 v2nums |
| Concordância com a regra de 31/03; faixa futura; 0–5 meses pedindo Berçário I | 89,4%; 1,7%; 100% (solicitações 2013+) | C15 tres_faixa |
| Mediana mensal da idade na 1ª solicitação | 43 (jan./2013) → 13 (dez./2018) | C14 v2nums |
| Registrados até 47 meses | 81,5 (2013) → 83,7% (2014) | TAB A_P5cov |
| Razão (antes de 12 meses) / na fila | 0,468 → 0,653 | TAB A_S8ac |
| Na fila por quartil de renda distrital, coorte de 2016 | 88,1 (Q1) contra 42,4% (Q4) | TAB A_S8b |
| Série análoga a Soares (todos os solicitantes, por ano da 1ª solicitação) | 35,64 → 16,78 meses (−18,9); 24,35 → 16,78 (−7,6), cerca de 40% | build14_soares_analog.py |
| Decomposição por ano de solicitação, matriculados | 2013–2016: −7,30 meses, 77%; 2013–2017: −8,84, 69% | A_decompyear |

## D. Estoque publicado e calendário
| Número | Valor | Origem |
|---|---|---|
| Estoque de dezembro, 2013 → 2017 | 96.696 → 44.092 (−54%) | TAB T11T12 (aritmética) |
| Estoque de setembro, 2013 → 2017 | 156.982 → 132.365 (−16%) | TAB T11T12 |
| Setembro − dezembro; dezembro/setembro | 2013: 60.286 e 62%; 2017: 88.273 e 33% | TAB T11T12 (aritmética) |
| Matrícula de dezembro, 2013 → 2017 | 214.460 → 296.260 | TAB T11T12 |
| Estoque de dezembro / matrícula | 2013: 45%; 2017: 15% | aritmética |
| Calendário 2013–2017: dezembro | 5,0% das solicitações; 50,5% dos encaminhamentos; 35,5% das matrículas; jan.–fev.: 15,8% dos encaminhamentos | A_calendar |
| Reconstrução contra a série publicada, 2013–2017 | 6 a 13% abaixo (máximo 12,5%) | TAB A_P5queue (aritmética: 8,6; 12,5; 11,7; 7,6; 6,4) |

## E. Contexto institucional (não depende da Fila1018; mantido)
Seção 2 atual:
- Meta 5 (75% / 100%);
- Censo Escolar e SEADE (30,0 → 65,8%; 22,5 → 55,8%), com a nota 1;
- TPE (23,5 e 31,8%; 18,6 e 62,4%) e IBGE (74,5%);
- 2.384 / 1.629 / 376 unidades;
- faixas etárias e razões; 89,4% e 0,4% (Berçário I, 2017);
- grade com mediana de 18 centros (de 12 a 29), 32 no total; 12,3% no centro mais próximo (extrato completo);
- portarias 6.770, 6.811 e 4.993;
- capacidade (58%, 65/82, 42/56, 58,3/57,9, 97–100%, 0,929/0,959);
- centros (1.641 → 2.406; 1.223 → 2.004; 400–450; 692); 23,9 → 13,9%; −6,3%; 0,307 → 0,514; 86/14; 0,31–0,45 → 0,62–0,65;
- matrícula publicada (64.436 → 296.260; 28 e 8% ao ano);
- 3,3 milhões de linhas; 98,1% com CPF; 2,7% e 0,6% de carimbos compartilhados;
- painel de capacidade: 2.734 centros, 13 semestres, 86.982 células;
- IBGE 2017: 43,2 e 37,3%.

## F. Cortados (não podem aparecer no texto)
- Todos os números ingênuos de 2010–2012 fora da tabela V2_naive e da introdução.
- Irmãos: −7,20; 78; 67; +3,21; 20,4; −0,88; 37,8; 10,5.
- C6: 0,009 (0,010).
- Pares adjacentes e bases fixas: 139, 91, 52, 130, 101, 132, 76, 19, 81, 93, 55, 34.
- Quem nunca entra: 27,4; 5,2; 115; 112.
- Base de 2011: 0,530 → 0,876.
- Estoque: +19% em setembro; −15% na média; 25.999; −69%; "6 a 17%".
- Composição "contra o ganho" (−0,074).
- Ingênuos do serviço: 218, 304, 346, 296, 36,2, 84,2, 0,095.
- Ingênuos do timing: 4,2, 33,7, 36 meses, 61,1, 0,149, 0,326, 0,325, 0,321, 0,407, 0,244.

## G. Acrescentados durante a escrita (Fase 2), com origem
| Número | Valor | Origem |
|---|---|---|
| Mediana com aging out tratado como censura | 221 (2013) e 171 (2016) dias | TAB A_E1d |
| Na fila alguma vez, coorte de 2013 | 88,6% | TAB A_S8ac |
| Decomposição 2013–2016 | solicitação −5,65 meses; espera −1,65 | A_decompyear |
| Matriculados antes de 36 meses | 60,7 (2013) → 68,6% (2015) | V2_cohortcov |
| Solicitantes da coorte de 2013 | 153.033 (140.811 elegíveis) | TAB A_P2rec |
| Razão corrigida / ingênua | encaminhamento 39%; matrícula 37%; padronizado 34%; registro antes de 12 meses 22%; por ano de solicitação 65% | aritmética V2_naive |
| Contexto, §2 | 170.720 → 365.854; 128.212 → 309.947; 3550308; 555.696; 569.975; 564.210; 38,3 e 62,9%; 44% (SME); 52,9% (2015); portarias 6.770, 6.811, 4.993; cerca de 2.400 centros | §2.1 e nota 1 (build13_coverage/facts.md; build14 SEADE), já presentes na versão pós-EE |
| Soares (2021) | 2,48 → 1,01 anos | citação externa |
| Faixas de N por coorte | entre 128 mil e 147 mil elegíveis (128.143 a 146.665) | V2_service |

Regra de arredondamento: um valor do texto que é o arredondamento de um valor congelado (0,563 → 0,56; 50,1 → 50; a faixa +0,083 a +0,178 → "0,08 a 0,18") conta como congelado.

| Ganho ingênuo acumulado antes da janela (coortes 2010 → 2013) | 0,190 (= 0,753 − 0,563) | aritmética V2_service / janela_cif.csv (Figura 2) |
| Primeiras solicitações de 2006–2009 no total de 1.524.560 (Etapa 6, 26/10) | 51.106 | TAB A_T1 (nota) |
