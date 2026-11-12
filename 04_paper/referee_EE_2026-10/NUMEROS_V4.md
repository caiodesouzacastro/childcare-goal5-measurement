# NUMEROS_V4: tabela congelada da Saída C (26/10/2026)

**Regra.** Nenhum número entra no manuscrito da Saída C (`paper_C.tex`, `secC*.tex`, `tables_C*.tex`) se não estiver nesta tabela ou em `NUMEROS_V3.md`. Os números reaproveitados de V3 estão listados no bloco H, com a referência de volta.

**Verificação:** `02_audit/build20_numcheck.py`, que lê V4, V3 e `congelados_v3.csv` e varre o resumo de `paper_C.tex` e os `secC*.tex`.

**Formato.** Os números seguem a convenção pt-BR (vírgula decimal, ponto de milhar), que o numcheck converte.

**Origem dos logs:**
- B19 = `03_build/build19/`; B20 = `03_build/build20/`.
- Os logs de B19 vêm de `build19_nucleo.py` (`nucleo.log`), `build19_confere_pdf.py` (`03_build/build19_confere_pdf.log`) e `build19_datas_extracao.py` (`datas_extracao.log`).
- Os logs de B20 vêm de `build20_censo.py` (`censo.log`), `build20_bracos.py` (`bracos.log`, `bracos_ano.csv`) e `build20_tables.py` (`tables.log`).

## A. Textos legais e documentos (fonte: `referee_EE_2026-10/fontes_saidaC/`, ver `README_fontes.md`)

| Número | O que é | Documento |
|---|---|---|
| 16.271; 2015 | Lei do PME, 17/09/2015 | `lei_16271_2015_PME.pdf` |
| 75%; 100%; 3 anos e 11 meses; Meta 5 | Texto da Meta 5 | idem, Anexo, Meta 5 |
| 13 metas; 10 anos | PME: "13 metas"; vigência de 10 anos (art. 1º) | `conferencia_PME_2023_relatorio_final.pdf`, p. 3; lei, art. 1º |
| art. 4 | "censos mais atualizados" | lei, art. 4º |
| 17.437; 2020; 2 anos | Prorrogação dos prazos | lei 16.271 compilada, art. 6º (red. Lei 17.437/2020) |
| 7.972; 12/12/2016; 31/12 | Portaria de monitoramento; "Valor ou situação do indicador em 31/12" | `portaria_SME_7972_2016.pdf`, art. 4º; coleta em jan./fev. (art. 3º) |
| 2023; abr. a set./2023 | Conferência (sessões de 14/04 a 05/09/2023) | relatório, p. 1–2 |
| 2015–2022 | Anos dos indicadores da Meta 5 na Conferência | relatório, p. 41–42 |
| 15.388; 14/04/2026; 1.a; 100%; 60%; 3 anos; 180 dias; arts. 11 e 28 | PNE 2026 | `lei_15388_2026_PNE.pdf` |
| 14.851; 2024 | Levantamento anual da demanda | `lei_14851_2024.pdf` |
| 14.127; 2006; 47.155 | Lei e decreto da publicação trimestral | `lei_14127_2006.pdf`, `decreto_47155_2006.pdf` |
| 24; 2020 | IN SME 24/2020, art. 9º | `IN_SME_24_2020.pdf` |
| 2025–2028; Meta 77; 30 dias | Programa de Metas, indicador da Meta 77 | `SME_acoes_programas_meta77.pdf` |
| 17/12/2020; 540 | Anúncio "zera fila"; 540 crianças por unidade específica | `noticia_PMSP_2020-12-17_fila_zerada.pdf` |
| 566 mil | Total SEADE citado pela SME (2025) | `noticia_SME_2025-08-11_fila_zerada_69pct.pdf` |
| 2011; 3.478; jul./2011 | Notas técnicas de jan./2011 (Mini-grupo II) e out./2011 (Portaria 3.478 de 08/07/2011, demanda preferencial) | `serie_SME/5733.pdf`, `5732.pdf` |
| 2012 | Nota técnica de mar./2012 | `serie_SME/5734.pdf` |
| 47 meses | Idade de saída da lista de creche | V3 (aging out em 47 meses) |
| 3550308 | Código IBGE do município | `build20_censo.py` |

## B. Censo Escolar e SEADE (braço A)

| Número | O que é | Origem |
|---|---|---|
| 170.720; 365.854; 370.706 | Matrícula na etapa creche, todas as redes, 2010, 2018 e 2024 | B20 `censo.log`, linhas 4, 12 e 18 |
| 30,0; 65,8; 72,2 | Taxa (etapa, todas as redes) em 2010, 2018 e 2024 (%) | B20 `bracos.log`, linhas 6, 14 e 20 (29,95; 65,84; 72,20) |
| 73,3 (2022) | Máximo do braço A por etapa, todas as redes | B20 `bracos.log`, linha 25 |
| 38,3 (2010); 67,8 (2024); 68,7 (2022) | Por idade (0–3 em qualquer etapa): 2010, 2024 e máximo | `bracos.log`, linha 27; linha 6 (38,33) |
| 22,5 (2010); 64,0 (2021) | Rede municipal + conveniada | `bracos.log`, linha 26; linha 6 (22,49) |
| 2007–2024 | Nenhum ano com braço A ≥ 75 | `bracos.log`, linha 24 ("None") |
| 569.975; 563.983; 550.172; 504.289 | SEADE 0–3 publicado em 2010, 2015, 2020 e 2025 | `bracos.log`, linha 1 |
| 564.210; 1,0 | Censo 2010 (0–3) e diferença em relação ao SEADE (%) | NUMEROS_V3, bloco E (linha 150) |
| 2022; 2021; 2007 | Rede municipal + conveniada não identificável em 2007 e em 2022–2024 | `censo.log`, linhas 3, 16–18 |

## C. Série publicada

| Número | O que é | Origem |
|---|---|---|
| 89 | Fotos de demanda de creche, jun./2006 a ago./2026 | B19 `serie_publicada_completa.csv` (89 linhas; `build19_confere_pdf.log`, última linha) |
| 36 de 43; 7 | PDFs cujo total bate com os dados abertos | `03_build/build19_confere_pdf.log`, linha 150 |
| 4 trimestres de 2017 | XLS = dados abertos | idem, linha 152 |
| 93.814 + 1.366 + 1.980 = 97.160 | Dez./2012, subcolunas | `SAIDA_C.md` 2.1; PDF `serie_SME/5703.pdf`, linha TOTAL |
| 130.412; 195.561 | Matrícula municipal em dez./2010 e dez./2011 | B19 `nucleo_C_meta.csv` (2010-12, 2011-12); Tabela `C_series_body.tex` |
| 64.436 (2006); 385.100 (2021); 330.106 (2025) | Matrícula municipal de dezembro | B19 `serie_publicada_completa.csv`; `C_series_body.tex` |
| 17; 9; 30/11/2022; 28/12; 09/12/2020 | Edições de dezembro com data impressa; em 31/12; datas | B19 `datas_extracao.log`, linhas 15–17 e 21 |
| 540 (dez./2020): (1)=0, (2)=0, (3)=540 | Componentes da demanda em dez./2020 | B19 `nucleo.log`, linha 186 |
| 2.771 (set./2020); 9.013 (set./2021) | Sem unidade específica há mais de 30 dias | `nucleo.log`, linhas 185 e 189 |
| set./2019; set./2020; 2023 | Datas das quebras na publicação | notas de rodapé dos XLS (`build19_serie_sme.log`); página "Demanda Escolar" |

## D. Os dois braços e a cláusula do maior

| Número | O que é | Origem |
|---|---|---|
| 0 de 89 | Fotos com demanda zero (braço B nunca cumprido) | B20 `bracos.log`, linha 29 |
| 99,86 (dez./2020; 540) | Máximo do braço B | `bracos.log`, linha 29 (99,856) |
| 98,17 (set./2020) | Máximo do braço B em setembro | `bracos.log`, linha 30 (98,168) |
| 2007–2025 | Anos em que A obriga (dezembro): todos | `bracos.log`, linha 32 |
| 1,05 (2021); 2,83 (2007); 1,26 (2015) | Razão exigência A ÷ exigência B, dezembro | `bracos.log`, linha 33 (1,052 e 2,828); linha 11 (2015: 1,26) |
| 2017 | Único ano em que B obriga medindo em setembro | `bracos.log`, linha 34 |

## E. O indicador da Conferência e o mês da contagem

| Número | O que é | Origem |
|---|---|---|
| 77,62 (2015); 99,99 (2022); 96,31 (2019) | Valores reportados pela Conferência | relatório, p. 41–42; B19 `nucleo.log`, linhas 118–125 |
| 97,28; 99,81; 699; 681 | Calculado em 2019 e 2022; demanda da Conferência × publicada em 2022 | `nucleo.log`, linhas 122 e 125 |
| 6 de 8 | Anos reproduzidos pela fórmula | `nucleo.log`, linha 126 |
| 17 de 19; 2009 e 2010 | Dezembro é o mínimo do ano (2007–2025); exceções | B19 `nucleo_dez_minimo.log` (linha final) |
| 0,80 (2013); 0,23 (2019) | Dezembro ÷ média do ano | `nucleo_dez_minimo.log`, linhas 8 e 14 |
| 54,4; 96.696; 44.092 | Queda de dezembro 2013→2017 e níveis | `nucleo.log`, linha 54 |
| 14,9; 18,1; 15,7 | Queda em mar., jun. e set. 2013→2017 (%) | `nucleo.log`, linhas 51–53 |
| 15 a 18; 54 | Arredondamentos dos anteriores | regra de arredondamento |
| 38,4 (2013); 87,2 (2019); 14,0 (2009); 3,5 p.p./ano | Queda de set. para dez. no mesmo ano; tendência 2007–2019 | `nucleo.log`, linhas 101 e 103 (3,49) |
| 2015; 2018; 2016 | 1º ano ≥ 75% em dez., set. e mar. | `nucleo.log`, linha 246; linha 167 (mar./2016: 75,38) |
| 77,6; 81,4; 87,0 | % atendida em dez. de 2015, 2016 e 2017 | `nucleo.log`, linhas 166, 170 e 174 |
| 63,2; 68,1; 68,7 | % atendida em set. de 2015, 2016 e 2017 | `nucleo.log`, linhas 165, 169 e 173 |
| 79,1 | % atendida em set./2018 | `nucleo.log`, linha 177 |
| 78 a 87; 63 a 69 | Arredondamentos dos dois anteriores | regra de arredondamento |
| 2015, 2016, 2017 | Anos em que o critério depende do mês | `nucleo.log`, linha 242 |

## F. Reconstrução e cobertura

| Número | O que é | Origem |
|---|---|---|
| 0,87–0,96 | Reconstruído ÷ publicado, 2013–2018 | B19 `nucleo.log`, linhas 262–285 |
| 4 a 13 | Complemento de 0,87–0,96 (%) | idem |
| 0,20–0,33 (2010); 0,31–0,35 (mar.–set./2011); 0,85 (dez./2011) | Razões antes de 2012 | `nucleo.log`, linhas 250–257 |
| 16; 19; 17; 53 | Queda do reconstruído 2013→2017 (mar./jun./set./dez.) | `nucleo.log`, linha 289 |
| 39,5 (2013); 66,0 (2017); 75,9 (2018) | Queda set.→dez. do reconstruído | `nucleo.log`, linha 292 |
| 20 a 35 | Arredondamento de 0,20–0,35 | idem |
| 2014–2017 | Coortes de referência da defasagem (imputação da completude) | NUMEROS_V3, bloco A (linha 46) |

## G. Indicadores de fluxo (janelas móveis de 12 meses, pedidos desde jul./2012)

| Número | O que é | Origem |
|---|---|---|
| −8,3; −5,4; −8,2; −6,2 | Novos pedidos 2014→2017 (%), janela terminando em mar./jun./set./dez. | B19 `nucleo.log`, linha 320 |
| 5 a 8 | Arredondamento | idem |
| −5,2; −4,6; −4,1; −3,8 | Idade mediana 2014→2017 (meses) | `nucleo.log`, linha 322 |
| 4 a 5 | Arredondamento | idem |
| +0,130; +0,146; +0,172; +0,191 | Encaminhamento em 365 dias 2014→2017 | `nucleo.log`, linha 324 |
| 0,13 a 0,19 | Arredondamento | idem |
| +0,230; +0,234; +0,231 | Idem, 2014→2018 (mar./jun./set.) | `nucleo.log`, linha 325 |
| −20,5; −18,9; −17,5; −53,2 | Estoque 2014→2017 por mês (%) | B20 `C_stab_body.tex` (`build20_tables.py`; dados de `nucleo.log`, linhas 12 e 15 da tabela A) |
| um terço (2017) | Dez. ÷ set. de 2017: 44.092 ÷ 132.365 = 0,333 | `nucleo.log`, linha 15 da tabela A |
| 3 vezes | Queda de dez. ÷ queda de set., 2014→2017: 53,2 ÷ 17,5 = 3,0 | `C_stab_body.tex` |
| 12 meses; 365 dias | Definição da janela e do indicador | `build19_nucleo.py`, parte E |

## H. Reaproveitados de NUMEROS_V3 (sem recálculo)

- **Calendário:** 50,5 / 15,8 / 5,0 (bloco E; `A_calendar`).
- **Grid:** 18 centros (bloco E).
- **Rede:** 2.384 / 1.629 / 376 unidades; 1.641 → 2.406 centros; 400–450 diretos (bloco E).
- **Faixas etárias:** 0–13 meses, 1:7; 35–46 meses, 1:25 (bloco E).
- **Completude por semestre:** 17,8 / 24,4 / 38,9 / 64,1 / 92,8 / 98,0; de 97,9 a 99,9; regra 96,4; 2 p.p.; 2014–2016 (bloco A).
- **Coortes:** registro antes de 12 m 38,3 → 50,1; antes de 6 m 23,5 → 33,4; encaminhamento em 1 ano 0,631 → 0,876; RMST 237 → 181; matriculados antes de 24 m 33,2 → 53,8; fila × EOL 33,2 / 31,9 (blocos A, C, D; `V3_cohortcov`).
- **Pesquisa de 2015:** 43,2 / 37,3 (bloco E; `ibge2017cuidados`).
- **Matrícula de creche por idade, 2010:** 38,3 (bloco E). É o mesmo número da linha "38,3 (2010)" do bloco B.

## Regra de arredondamento

Um valor do texto que é o arredondamento de um valor congelado conta como congelado. Exemplos: 54,4 → 54; 0,130 → 0,13; 99,856 → 99,86; 3,49 → 3,5.

## I. Acrescentados depois da verificação da etapa 2 (`fontes_saidaC/verificacao_etapa2.md`)

| Número | O que é | Documento |
|---|---|---|
| 3.478; 08/07/2011; jul./2011 | Portaria SME 3.478, art. 14, §9º ("considerado, exclusivamente, para vaga disponível na escola indicada") | `fontes_saidaC/portaria_SME_3478_2011.html` |
| 5.033; 10/10/2011; out./2011 | Portaria SME 5.033: revoga a 3.478 (art. 40) e repete a regra | `portaria_SME_5033_2011.html` |
| 31/12/2015; 75.194; 77,62 | Linha de Base (dez./2016): "A data de referência adotada foi 31/12/2015"; valores da Meta 5 | `PME_SP_Linha_de_Base_dez2016_sinesp.pdf`, linhas 196, 326 e 330 do texto extraído |
| 701; 03/09/2026; set./2026 | Portaria MEC 701 (GT PNE), "elaboração dos indicadores e das projeções" | `portaria_MEC_701_2026_mecnormas.html` |
| 31 de março | Data de contagem dos registros de habitação social na Inglaterra | `MHCLG_social_housing_lettings_tenants_2024-25.pdf` |
| 2026 (out.) | Não localizamos a publicação dos indicadores do Inep até 26/10/2026 | `verificacao_etapa2.md`, item 3 |

## J. Braço A: decisão do autor de 26/10 (noite), e §6 e §8 ampliadas

| Número | O que é | Origem |
|---|---|---|
| 345.974 → 53.417 | Matrícula municipal + conveniada no Censo, 2021 → 2022 (quebra das colunas) | B20 `censo.log`, linhas 15–16 |
| 2008–2021 | Anos com a leitura municipal + conveniada | `censo.log`; `bracos.log`, linha 26 |
| 2011 | Ano a partir do qual a leitura por idade fica abaixo da leitura por etapa | `bracos.log`, linhas 6–20 (2010: 38,33 > 29,95; 2011: 37,60 < 43,25) |
| Indicador 1B | Inep, PNE 2014: "Percentual da população de 0 a 3 anos que frequenta a escola ou creche" | `fontes_saidaC/Inep_PNE2014_5ciclo_relatorio.pdf` (texto, linhas 870–880) |
| 3,03; 0,75; 0,93; 1,11 | Razão variação dez./variação set., 2014→2017: estoque, novos pedidos, idade mediana, encaminhamento em 365 dias | B20 `tables.log` ("estabilidade", 3,035 / 0,753 / 0,927 / 1,11) |
| 12, 24, 36 meses; 180 e 365 dias; 6, 12, 24 meses | Parâmetros das definições dos indicadores | definição (`secC6_indicators.tex`) |
| 3 meses; mensal; prorrogável por igual período | GT PNE (Portaria MEC 701, arts. 4º e 7º) | `fontes_saidaC/portaria_MEC_701_2026_mecnormas.html` |
| 18 meses | 1ª publicação do monitoramento do PNE (art. 30) | `lei_15388_2026_PNE.pdf` |
| 60% | Meta 1.a, condição populacional | idem |

## K. Transferibilidade (`fontes_saidaC/transfer/TRANSFER.md`; conferido por mim nos arquivos salvos)

| Número | O que é | Origem |
|---|---|---|
| 31 de março; 1º de abril; 2017–18 | Data de referência dos registros de habitação social (Inglaterra) | `transfer/england_housing/LAHS_Guidance_2024-25.txt`; nota 3 da Live Table 600 |
| 1.340.527 (31/03/2025) | Domicílios nos registros, Inglaterra | `table600_england_series.csv` |
| 1.851.884 (2012); 1.370.410 (2014); 26,0% | Queda após o Localism Act (2011) | `table600_england_series.csv` (calculado: 1 − 1.370.410/1.851.884 = 0,260) |
| 61 de 320 (2014) | Conselhos com registro reduzido à metade ou menos em um ano | `table600_la_breaks_summary.csv` (n_drop50 = 61; n_LAs = 320) |
| 15.12; 6.510 (2025) | Noruega, crianças na lista de espera, data de referência e total | `transfer/norway/ssb_13632_metadata_v2.json` (refperiod "15.12."); `ssb_13632_hele_landet.csv` |
| 2018; 2019; 15:2209 | Resposta escrita ao Storting (06/09/2019) | `norway/stortinget_spm15-2209_2018-2019.html` |
| 3.916; 2007–2008; 2009 | Innst. O. nr. 69 (2007–2008); direito à vaga desde 2009 | `norway/innst_O_69_2007-2008_kap2.html`; `barnehageloven_lovdata.txt` (§ 16) |
| 92%; 18 semanas | Padrão constitucional do NHS | `transfer/nhs_rtt/Mar26-RTT-statistical-press-notice.txt` |
| 65%; mar./2026; 65,3; 2025/26 | Meta intermediária e resultado | `nhs_rtt/nhs-england-annual-report-and-accounts-2025-2026.txt` |
| 62,6 (fev./2026); 2,7 p.p.; maior alta mensal desde abr./2016 fora de 2020–2021; 0,49 p.p. média; 61,4 média e 62,6 máximo dos 11 meses anteriores; 65,0–65,8 (abr.–ago./2026) | Série mensal reconstruída | `02_audit/build21_rtt.py` → `03_build/build21/rtt.log`, linhas 2–5 |
| 8 anos (fiscais 2017–2024); 3; 2025 e 2026 | Março nunca é o melhor mês; pior em 3; melhor nos 2 anos com meta | `nhs_rtt/rtt_march_vs_other_months.csv` |
| metade do ganho do ano | 2,7 ÷ 5,5 (variação anual de março/2026) | `rtt_march_vs_other_months.csv` (coluna March_yoy_change = 5,5) |
| £33; 250.000; 14,3%; 14.460.885; abr.–nov./2025 | Validação: pagamento, remoções adicionais, remoções não reportadas | `nhs_rtt/WPQ_107367_answer.txt`, `WPQ_75251_answer.txt`, `WPQ_111345_answer.txt` |
| 9 boletins; set./2017–ago./2026 | Fonte da série mensal | `TRANSFER.md`; `build_rtt_series.py` |

## L. Triagem da revisão (26/10/2026); números derivados de valores já congelados

| Número | O que é | Origem / cálculo |
|---|---|---|
| 2,3% | Erro da projeção que faria a taxa de 2022 chegar a 75%: 1 − (389.561/0,75)/531.819 = 2,33% | B20 `censo.log`, linha 16; `bracos.log`, linha 18 (pop. 531.819) |
| 77,1% (2021) | (385.100 + 377.862 − 345.974)/540.995 = 77,08%: matrícula municipal da SME em dez. + Censo de outras redes | `nucleo_C_meta.csv` (2021-12); `censo.log`, linha 15; `bracos.log`, linha 17 |
| 385.100; 345.974 | Matrícula municipal SME (dez./2021) e Censo municipal + conveniada (maio/2021) | idem |
| 13.200 (cerca de) | Fila necessária para reproduzir 96,31 em 2019: 345.452 × (1/0,9631 − 1) = 13.236 | `nucleo.log`, linha 122; matrícula de dez./2019 em `serie_sme_xls.csv` |
| 9.670; 681; 699; 99,81 | 2019 e 2022, publicados e da Conferência | blocos C e E |
| 14.016 (dez./2017) | Matrículas em processo de creche | `03_build/build19_serie_sme.log`, linha 5 |
| 3,46 | Razão das quedas dez./set., estoque 2013→2017: 54,4/15,7 | `nucleo.log`, linhas 53–54 |
| 1,54; 1,37; 1,47; 3,04 | Maior/menor variação entre os 4 meses, 2014→2017: novos pedidos 8,3/5,4; idade 5,2/3,8; encaminhamento 0,191/0,130; estoque 53,2/17,5 | `C_stab_body.tex` |
| 8,2% | Pedidos da coorte 2012 anteriores a jul./2012 | NUMEROS_V3, bloco A (linha 48) |
| 5% (2021) | Folga da exigência A sobre B em dez./2021 (razão 1,05) | `bracos.log`, linha 33 |
| 566.000 | Total SEADE citado pela SME (2025); mesmo número que "566 mil" (bloco A) | `noticia_SME_2025-08-11_fila_zerada_69pct.pdf` |
| 2,0 / 97,4 / 96,4 | Regra de completude: 2 p.p. abaixo da média de 2014–2016; limiares | NUMEROS_V3, bloco A (linha 44) |
