# NUMEROS_V3: tabela congelada da janela a partir de jul./2012 (MANHA, 26/10/2026)

Substitui `NUMEROS_V2.md` (que fica como registro). Regra: nenhum número entra no texto sem estar aqui, com a origem. Os valores das tabelas geradas estão também em `03_build/build18/congelados_v3.csv` (93 itens, escritos por `build18_tables.py` e `build18_appx.py`). O `build15_numcheck.py` lê este arquivo e esse CSV.

Decisões da autora aplicadas:
- **D1:** janela a partir de 1º/7/2012 (coortes 2012–2016), com 2013 como robustez.
- **D2:** o artefato está no nível, não na inclinação.
- **D3:** corrigir na direção de um artefato menor.

Abreviações das origens:
- **C14** = `03_build/build14_cobertura/`
- **C15** = `03_build/build15/`
- **C17** = `03_build/build17_fatais/`
- **C18** = `03_build/build18/`
- **TAB** = `04_paper/assets/tables/`
- **V2** = `TAB/v2/`
- **V3** = `TAB/v3/`

## A. Cobertura e completude do registro

**Não mudam** (V2_coverage, como em NUMEROS_V2):

| Número | Valor | Origem |
|---|---|---|
| Entrantes encontrados no registro, 2010 / 2011 / 2012 | 42,1 / 47,9 / 57,2% | V2_coverage |
| Idem, 2013–2018 | de 98,6 a 99,9% | V2_coverage |
| Fevereiro de 2012 contra os outros meses | 41,4% (87.228) contra 98,3% (33.773); mês a mês, de 96,2 a 99,3%; "96 por cento ou mais" | V2_coverage; C14 cob_fevereiro |
| Ausentes datados de fevereiro, 2010–2012 | de 98,9 a 99,8% | C14 |
| Idade mediana na entrada, ausentes contra presentes | 2010: 26 contra 17 meses; 2011: 30 contra 23 | C14 cob_idade |
| Unidades com 20 ou mais entradas em fevereiro | 2012: 1.493, mediana 40%, 1,9% com 90% ou mais; 2013: 97,0% com 90% ou mais | V2_coverage |
| Unidades presentes nos dois anos que subiram 30 pontos ou mais | 92,4% | build14_simultaneidade.py |
| Tipos de centro, fev./2012 → fev./2013 | de 32,0–43,6% para 95,8–98,8% | A_covtype |
| Matriculados antes de 24 meses, fila contra EOL | 2010: 7,4 / 25,1; 2011: 22,8 / 28,3; **2012: 33,2 / 31,9 (diferença 1,3)**; 2013–2016: diferença de 0,5 a 1,0 | V2_coverage; C15 eol_coorte_den96 |
| Solicitantes de 2011 com 1º encaminhamento em dez./2012 | 37,1% | COBERTURA_FILA §5 |
| Solicitantes de 2011: entrada em fev./2013 contra fev./2012 | 32.537 contra 5.371 | COBERTURA_FILA §5 |
| Degrau de registro (linhas de encaminhamento por 1º encaminhamento) | 1,00–1,01 (2010S1–2012S1); 1,24 (2012S2); 2,09 (2013S1) | C15 degrau_semestral |

**Novos** (completude por semestre de solicitação):

| Número | Valor | Origem |
|---|---|---|
| 1as solicitações a partir de 1º/7/2012 | 1.140.848 (de 1.524.560) | C18 janela2012_nums |
| Completude por semestre de solicitação | 2010S1 17,8; 2010S2 24,4; 2011S1 38,9; 2011S2 64,1; **2012S1 92,8; 2012S2 98,0**; de 2012S2 a 2017S2, entre 97,9 e 99,9 | V3_completeness (C17 c2_completude_semestre) |
| Limiares da regra | 96,4 (completude) e 97,4 (encaminhamento registrado) | V3_completeness |
| Sensibilidade à defasagem de referência | 2012S1: 92,6–93,3; 2012S2: 97,9–98,1 | build17_fatais_c2.log |
| Medianas da defasagem entrada − solicitação, 2014–2017 | 314 dias (fevereiro) e 232 (demais meses) | build17_fatais_c2.log (313,6 e 232,2) |
| Completude ponderada por coorte | 2010: 82,8; 2011: 92,0; 2012: 97,9; 2013: 98,4 | V3_completeness, Painel B (C17 c2_coorte_semestres) |
| Coorte 2012: solicitações no 1º semestre de 2012 | 8,2% (de todos os solicitantes) | C17 c2_coorte_semestres |
| Coorte 2012 elegível | 139.440 de 155.292 | TAB A_P2rec |

## A2. Prospectividade (novos)

| Número | Valor | Origem |
|---|---|---|
| Entrantes de 2013: mediana solicitação → entrada; pedido depois da entrada; > 30 dias antes | 324 dias; 0,64%; 89,5% | A_prospect (C17 c3_sol_x_eol) |
| Mediana por ano de entrada, 2013–2018 | de 214 a 324 dias | A_prospect |
| Pedido 0 a 7 dias antes da entrada (inclui o mesmo dia), 2013–2018, % dos entrantes no registro | de 2,3 (2016) a 5,5 (2013 e 2018) | A_prospect (= 100 − depois − mais de 7 dias) |
| Solicitantes de 2013–2017: nunca matriculados (fila) | de 7,9 a 10,3% | A_prospect (C17 c3_nunca) |
| Idem, com recusa registrada | de 29,9 a 34,4% | A_prospect (C17 c3_escolas_recusas) |
| Idem, encaminhados a centro que nunca frequentaram | de 27,5 a 30,7% | A_prospect |

## A3. Nível corrigido (novos; V3_level, C18 nivel_*.csv, `build18_nivel.py`)

| Número | Valor | Origem |
|---|---|---|
| Ausentes da coorte (entrantes sem pedido antes da entrada) | 2010: 39.022 (36,7% de N); 2011: 15.825 (12,5%); 2012: 1.761 (1,3%) | V3_level |
| Registro < 12 m, coorte 2010: observado; máximo; corrigido | 11,0; 32,6; 23,2–28,4 | V3_level |
| Registro < 12 m, 2010 → 2016: observado; corrigido; limites; parcela do artefato | 39,1; 22,4–27,6; [17,5; 39,1]; **29–43%** (limites: 0 a 55%) | V3_level |
| Matriculados < 24 m, 2010 → 2016: fila; EOL; parcela | 46,4; 28,1; **39%** | V3_level |
| Encaminhamento 1 ano, coorte 2010: observado; limites; corrigido | 0,563; [0,369; 0,658]; 0,605–0,622 | V3_level |
| Encaminhamento, 2010 → 2016: observado; corrigido; limites (2016 observada); parcela | 0,313; 0,256–0,273; **[0,218; 0,507]**; 13–18% (limites: −62 a +30%) | V3_level |
| Matrícula, 2010 → 2016: observado; corrigido; limites; parcela | 0,279; 0,204–0,228; [0,158; 0,448]; 18–27% | V3_level |
| Janela, 2012 → 2016: encaminhamento; registro < 12 m (observado contra corrigido) | 0,245 contra 0,247; 11,8 contra 12,0 | V3_level |
| Calibração fora da amostra (entrantes cobertos de 2013): imputado contra observado | < 12 m 48,1 / 46,5; encaminhamento 69,3 / 67,0; matrícula 62,7 / 61,8 | V3_level (C18 nivel_calibracao) |
| Razões de ganho (para mostrar a dependência do início) | encaminhamento: janela 2013 / completo = 39%; janela 2012 / completo = 78% | C17 c1_normalizacoes (0,39 e 0,78) |
| Degraus do encaminhamento por coorte | 2012→13 +0,122; 2013→14 +0,008; 14→15 +0,053; 15→16 +0,062 | aritmética V3_service |

## B. Serviço (coortes 2012–2016; anos de solicitação 2013–2017)

| Número | Valor | Origem |
|---|---|---|
| Encaminhamento em 1 ano, por coorte | 0,631 / 0,753 / 0,761 / 0,814 / 0,876 (+0,245) | V3_service (TAB E1_cohort) |
| Matrícula em 1 ano, por coorte | 0,523 / 0,644 / 0,639 / 0,686 / 0,747 (+0,224) | V3_service (TAB P2_endpoint) |
| Lacuna encaminhamento − matrícula | 0,108 (2012); 0,129 (2016) | aritmética V3_service |
| ref180; ref730; age365 | 0,314 → 0,522 (31,4 → 52,2%); 0,902 → 0,993 (90,2 → 99,3%); 0,036 → 0,000 | V3_service |
| RMST sem encaminhamento; sem matrícula | 237 → 181 dias (56 dias = 8 semanas); 260 → 220 | V3_service |
| Mediana até o encaminhamento; com censura | 287 → 171; 283 e 171 | V3_service; TAB A_E1d |
| Por ano de solicitação 2013 → 2017 (não muda) | encaminhamento 0,646 → 0,903; matrícula 0,551 → 0,764 | V3_service |
| Por semestre | 2012S2 0,562; 2013S1 0,707; 2016S1 0,800; 2016S2 0,724; 2017S2 0,887; 2018S1 0,974; 2016S1→2017S1 +0,116; +0,093 e +0,174 | V3_service Painel C |
| Parte de cada coorte que solicitou a partir de jul./2016 | 2012: 0,5%; 2016: 85,8% | C18 janela2012_nums; build15_degrau_reforma.py |
| Composição fixa em 2012 (células principais) | 0,631 → 0,891; +0,259 [0,256; 0,262]; bruto [0,242; 0,249] | V3_specs (C18 p3boot_2012_2016.log) |
| Células grossa / fina | +0,257 / +0,250 | V3_specs |
| Com ambiente de oferta | 0,631 → 0,869; +0,238; grossa +0,249; fina +0,238 | V3_specs |
| Decomposição exata | composição −0,014; ambiente +0,022; residual +0,238 | C18 p3_2012_2016.log |
| Especificações (base 2012) | base +0,245; desistência +0,244; tardios +0,305; 1º semestre +0,217; sem jul./2012–dez./2013 +0,146; coorte 2012 só de jul./2012 +0,269 (0,607); matrícula +0,224; faixa 0,15–0,31 | V3_specs |
| Robustez: início em 2013 / 2014 | +0,123 / +0,115; matrícula 2013 +0,103; registro < 12 m 2013 +8,6 p.p. | V3_specs; C17 c2_inicio_janela |
| Coorte 2012: solicitou depois do limite (por dia; meses inteiros) | 10,2%; 9,4% | C18 janela2012_nums; TAB A_P2rec |
| Coorte 2012 elegível em jul./2012–dez./2013 | 53,6% | C18 janela2012_nums |
| Aging out, elegíveis | 5,8 (2012) → 3,8 (2013) → 1,7% (2014) | TAB A_full_N1ag |
| Aging out, todos | 15,4 → 5,0% (2012 → 2014); 10,2 pontos de tardios em 2012 | TAB A_full_N1ag |
| Gradiente de renda Q4 − Q1 | 9,4 (2012) → 6,8 p.p. (2016) | TAB A_E2 |
| Nunca matriculados, solicitações 2013–2017 (não muda) | 9,1%; 9,6 (2014), 8,6 (2016), 18,3 (2018); idade 26,0 contra 19,6; prioridade 4,7 contra 19,2 | A_T4dv2; A_T1 |
| C4 (não muda) | 84,6–94,6%; 94,3%, 4 meses | A_C4v2 |
| Faixa de N por coorte | entre 128 mil e 147 mil (128.143 a 146.665; 2012: 139.440) | V3_service |

## C. Timing de inscrição (coortes 2012–2016)

| Número | Valor | Origem |
|---|---|---|
| Registrados antes de 6 / 12 / 24 meses (% dos nascidos) | 23,5 → 33,4; 38,3 → 50,1 (série 38,3 / 41,5 / 44,1 / 48,6 / 50,1); 59,4 → 70,9 | V3_timing |
| Mediana do nascimento à 1ª solicitação | 18 (2012) → 12 meses | C18 janela2012_nums |
| Antes de 12 meses entre os registrados antes de 24 | 0,644 / 0,666 / 0,664 / 0,701 / 0,707 (+0,063) | V3_timing |
| Com pesos distritais de 2010 / 2016 | 0,643 → 0,708; 0,643 → 0,707 | V3_timing |
| Distritos, 2012–2016 | sobe em 93 de 96 (cai em 3); mediana +0,060; de −0,023 a +0,252 | V3_timing (C18 janela2012_nums) |
| Restrito à faixa corrente, antes de 12 meses | 38,3 → 49,0 | C18 janela2012_nums |
| Concordância com a regra de 31/03; faixa futura (solicitações de 2013 em diante, não muda) | 89,4%; 1,7% | C15 tres_faixa |
| Mediana mensal da idade (não muda) | 43 (jan./2013) → 13 (dez./2018) | C14 v2nums |
| Registrados até 47 meses | 79,4 (2012), 81,5 (2013), 83,7% (2014) | TAB A_P5cov |
| Na fila alguma vez, coorte de 2012 | 88,4% | TAB A_S8ac |
| Série análoga a Soares | 35,64 → 16,78 meses (−18,9); de 2012S2 (26,22) a 2018: −9,4, cerca de metade | C18 janela2012_nums; build14_soares_analog.py |
| Decomposição por ano de solicitação (não muda) | 2013–2016: −7,30 meses, 77% (solicitação −5,65; espera −1,65); 2013–2017: −8,84, 69% | A_decompyear |

## D. Estoque publicado e calendário (não muda)

| Número | Valor | Origem |
|---|---|---|
| Estoque de dezembro, 2013 → 2017 | 96.696 → 44.092 (−54%) | TAB T11T12 |
| Estoque de setembro, 2013 → 2017 | 156.982 → 132.365 (−16%) | TAB T11T12 |
| Setembro − dezembro; dezembro/setembro | 2013: 60.286 e 62%; 2017: 88.273 e 33% | TAB T11T12 |
| Matrícula de dezembro | 214.460 → 296.260 | TAB T11T12 |
| Estoque de dezembro / matrícula | 45% → 15% | aritmética |
| Calendário 2013–2017 | dezembro: 5,0% das solicitações, 50,5% dos encaminhamentos; jan.–fev.: 15,8% | A_calendar |
| Reconstrução contra a série publicada | 6 a 13% abaixo | TAB A_P5queue |
| Coorte 2016 na fila por quartil de renda distrital | 88,1 contra 42,4% | TAB A_S8b |
| Matriculados antes de 36 meses | 52,5 (2012) → 68,6% (2015) | V3_cohortcov |

## E. Contexto institucional (não depende da Fila1018; idêntico ao bloco E e às linhas de contexto do bloco G do NUMEROS_V2)

Seção 2 e §3.1:
- Meta 5 (75% / 100%);
- Censo Escolar e SEADE (30,0 → 65,8%; 22,5 → 55,8%);
- TPE (23,5 e 31,8%; 18,6 e 62,4%) e IBGE (74,5%);
- 2.384 / 1.629 / 376 unidades; cerca de 2.400 centros;
- 89,4% e 0,4% (Berçário I, 2017);
- grade com mediana de 18 centros (de 12 a 29), 32 no total; 12,3%;
- portarias SME 6,770, 6,811 e 4,993 (escritas com vírgula aqui porque o numcheck lê o ponto como separador de milhar; no texto: 6.770, 6.811, 4.993);
- capacidade (58%, 65/82, 42/56, 58,3/57,9, 97–100%, 0,929/0,959);
- centros (1.641 → 2.406; 1.223 → 2.004; 400–450; 692); 23,9 → 13,9%; −6,3%; 0,307 → 0,514; 86/14; 0,31–0,45 → 0,62–0,65;
- matrícula publicada (64.436 → 296.260; 28 e 8% ao ano);
- 170.720 → 365.854; 128.212 → 309.947; 3550308; 555.696; 569.975; 564.210; 38,3 e 62,9%; 44%; 52,9%;
- 3,3 milhões de linhas; 98,1% com CPF; 2,7% e 0,6% de carimbos compartilhados; 51.106 (2006–2009);
- painel de capacidade: 2.734 centros, 13 semestres, 86.982 células;
- IBGE 2017: 43,2 e 37,3%;
- Soares (2021): 2,48 → 1,01 anos.

## F. Saem do texto (não podem aparecer)

- "between a fifth and two fifths"; as razões 37, 34, 22 e 65%.
- 0,190.
- 0,75 → 0,88 e 42 → 50 como ganho corrigido; "0.12 and 9 percentage points" como ganho principal (0,123 fica só como robustez de início em 2013).
- "0.08 to 0.18" (faixa antiga); 0,083; 0,091; 0,178; 0,122 como desistência (agora 0,244); 0,132; 0,128; 0,134; 0,116 como residual (agora 0,238).
- Mediana 17 meses como início da janela; 41,5 → 49,0; 0,666 → 0,708; 85 de 96; +0,042; +0,041; −0,060; +0,171.
- 140.811 de 153.033; 29,8% da coorte 2013; 8,2% da coorte 2013 depois de jul./2016; 8,0% tardios em 2013; 7,3%.
- Os limites e a imputação antigos: 0,412; 0,680; 0,635; 27,0; 29,6; 0,196; 0,464; "15 a 18 p.p."; "39% a 46%".
- Os itens da seção F do NUMEROS_V2 continuam valendo (irmãos, C6, pares adjacentes, quem nunca entra, estoque antigo, ingênuos de serviço e timing), exceto os que voltaram como números da coorte 2012 (por exemplo, 0,630 não; 0,631 sim).

Regra de arredondamento: um valor do texto que é o arredondamento de um valor congelado (0,631 → 0,63; 17,8 → 18; 0,146 → 0,15; 0,305 → 0,31; 0,218 → 0,22; 0,507 → 0,51) conta como congelado.
