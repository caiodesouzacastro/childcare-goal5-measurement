> RECONSTRUÇÃO. Este arquivo foi gerado a partir dos logs em 02_audit\ e não
> é o relatório original, que não foi preservado em .md. Os números vêm dos
> logs; a estrutura e as regras de decisão foram reconstruídas e podem estar
> incompletas. Fonte primária: os arquivos .log listados ao final.

# DIAG04 — reconstrução a partir dos logs (02_audit\)

Nota factual: em todos os `.do` a global `$aud` aponta para `...\Neighborhood Effects\02_audit`, mas o cabeçalho gravado dentro dos `.log` mostra o caminho `...\Neighborhood Effects\_audit\...` (sem o `02`). Os arquivos `.do`/`.log` estão fisicamente em `02_audit\`.

## Arquivos lidos

| Arquivo .do | Linhas | Arquivo .log | Linhas | O que o .do faz (pelos comandos) |
|---|---|---|---|---|
| diag04_A.do | 112 | diag04_A.log | 403 | Lê `Fila1018.dta`; monta lista de códigos de escola distintos (encaminhamento + matrícula) → `fila_codesc.dta`. Lê `escolassite.dta`; faz parse de datas (`date(...,"DMY")` para `dt_criacao`, `dt_ini_func`, `dt_ini_conv`, `dt_autoriza`) e de coordenadas (`latitude`/`longitude` → `lat`/`lon`); cria flag `cei` via `inlist(tipoesc, ...)` → `escolas_parsed.dta`. Blocos A2 (distribuição de datas por ano), A3 (`tab tipoesc`), A5 (sanidade de coords), A4 (contagens de CEI 2008-2016 com coord e casamento com Fila via `merge m:1 codesc`). |
| diag04_A2fix.do | 56 | diag04_A2fix.log | 192 | Reabre `escolas_parsed.dta`; diagnostica `tipoesc` (comprimento fixo 12, `levelsof`); **reconstrói** flag `cei` via `strpos` (CEI/CR.P/CEMEI/CCI); refaz A3 e A4 (contagens de CEI por raio de data e casamento com Fila). Termina com erro `r(111)` ao tabular `yr_dt_criacao_d` (variável inexistente). |
| diag04_B.do | 90 | diag04_B.log | 300 | Lê `Fila1018.dta` (subset de colunas); converte `dt_solicitacao`/`dt_matricula`; cria `serie_aluno` por `cd_serie_ensino_matricula`; mantém linhas com matrícula e reduz à 1ª matrícula por criança → `child_firstmat.dta`. Blocos B1 (`idade_entrada`), B2 (por ano letivo e por série), B3 (`espera_dias`), B4 (universo potencial cep/nasc/sol) → `universo_B4.dta`. |
| diag04_C1.do | 57 | diag04_C1.log | 173 | Lê `universo_B4.dta`; `joinby cep` com `cep_cei_pairs.dta`; conta aberturas na janela solicitação..matrícula por raio (2km/1km/500m) e placebo pós-12m (1km); `collapse` por criança → `child_counts_raw.dta` → `child_counts.dta`. Distribuições e médias de `n_aberturas`. |
| diag04_C2.do | 56 | diag04_C2.log | 379 | Lê `child_counts.dta`; cria `regiao` (setor CEP) e `regyear`; regressões C2 (`idade_entrada ~ n_ab_1km`), C3 (`espera_dias ~ n_ab_1km`) e C5 placebo (`idade_entrada ~ n_post_1km`), cada uma OLS com `i.ano_solic i.mes_nasc` e com `areg absorb(regyear)`; programa `showfs` reporta coef/se/t/N/r2 e F. |
| diag04_C6.do | 29 | diag04_C6.log | 83 | Event-study cru: `cep_cei_pairs.dta` filtrado `dist_km<=1`, `joinby` com universo; tempo relativo `relm=(ceiopen-dt_sol)/30.44`; mantém abertura mais próxima no tempo por criança; `table` de `idade_entrada` por bin de 3 meses (-24..+24). |
| diag04_Cprep.do | 67 | diag04_Cprep.log | 179 | Constrói `cei_openings.dta` (CEI com coord e `dt_criacao_d`, `ceiopen=dt_criacao_d`); expande CEIs para grade 3×3 células (`cei_grid.dta`); junta com `cepcentroide.dta` por célula; calcula haversine `dist_km`; filtra `<=2km` → `cep_cei_pairs.dta`; distribuição de CEIs por CEP. |
| diag04_D.do | 73 | diag04_D.log | 225 | D1: `describe` dos arquivos PSP (2017/2018/2019 e Microdados_PSP_2018_2ano). D2/D3: monta universo de `cd_aluno_sme`; por ano de PSP conta crianças com proficiência e casa com universo B4; consolida `psp_any` e distribuição `npsp`. |
| diag04_E.do | 77 | diag04_E.log | 79 | D1 (compl.): lista variáveis de proficiência/série nos PSP. E1: tenta tamanho de turma via `matriculas1018.dta` — interrompido por erro `r(2000)` (nenhuma observação com `serie_aluno` não-missing). E2 (não alcançado neste log). |
| diag04_Eredo.do | 72 | diag04_Eredo.log | 246 | E1 refeito: tamanho de turma via matrículas do próprio `Fila1018.dta` (séries 1-6, dedup criança×escola×ano×série, `contract`). E2: CEIs-em-Fila × `censo2018.dta` por `codinep`; lista de variáveis de infraestrutura em `censo2018`. |

## Estatísticas e tabelas encontradas (transcritas)

### A — diag04_A.log

**Fila / fila_codesc**
- `N linhas Fila = 3298064`
- `keep cd_esc_encaminhamento` → `drop if missing`: (417,675 observations deleted)
- `keep cd_esc_matricula` → `drop if missing`: (1,169,483 observations deleted)
- Após `append` + `duplicates drop`: (5,005,225 observations deleted)
- `N códigos distintos (enc+mat) em Fila = 3745`

**Parse de escolassite**
- `N= 4753`
- Parse datas — missing gerados: `dt_criacao` 970; `dt_ini_func` 2,654; `dt_ini_conv` 3,183; `dt_autoriza` 1,705.
- Parse coordenadas — por variável (latitude, longitude): 24/25 missing e 4,728 real changes.

**A2 — datas de criação/inauguração**

`dt_criacao_d`: N não-missing = 3783.

| Variable | Obs | Mean | Std. dev. | Min | Max |
|---|---|---|---|---|---|
| dt_criacao_d | 3,783 | 16486.81 | 5445.015 | -1461 | 21549 |

min = 01jan1956   max = 31dec2018

| yr_dt_criacao_d | Freq. | Percent | Cum. |
|---|---|---|---|
| 2005 | 5 | 0.19 | 0.19 |
| 2006 | 24 | 0.94 | 1.13 |
| 2007 | 92 | 3.59 | 4.72 |
| 2008 | 236 | 9.20 | 13.91 |
| 2009 | 143 | 5.57 | 19.49 |
| 2010 | 206 | 8.03 | 27.51 |
| 2011 | 182 | 7.09 | 34.61 |
| 2012 | 217 | 8.46 | 43.06 |
| 2013 | 101 | 3.94 | 47.00 |
| 2014 | 208 | 8.11 | 55.11 |
| 2015 | 358 | 13.95 | 69.06 |
| 2016 | 219 | 8.53 | 77.59 |
| 2017 | 255 | 9.94 | 87.53 |
| 2018 | 320 | 12.47 | 100.00 |
| Total | 2,566 | 100.00 | |

`dt_ini_func_d`: N não-missing = 2099.

| Variable | Obs | Mean | Std. dev. | Min | Max |
|---|---|---|---|---|---|
| dt_ini_func_d | 2,099 | 11799.77 | 6438.409 | -9131 | 21607 |

min = 01jan1935   max = 27feb2019

| yr_dt_ini_func_d | Freq. | Percent | Cum. |
|---|---|---|---|
| 2005 | 16 | 2.47 | 2.47 |
| 2006 | 40 | 6.16 | 8.63 |
| 2007 | 62 | 9.55 | 18.18 |
| 2008 | 101 | 15.56 | 33.74 |
| 2009 | 73 | 11.25 | 44.99 |
| 2010 | 57 | 8.78 | 53.78 |
| 2011 | 64 | 9.86 | 63.64 |
| 2012 | 55 | 8.47 | 72.11 |
| 2013 | 52 | 8.01 | 80.12 |
| 2014 | 79 | 12.17 | 92.30 |
| 2015 | 34 | 5.24 | 97.53 |
| 2016 | 7 | 1.08 | 98.61 |
| 2017 | 6 | 0.92 | 99.54 |
| 2018 | 3 | 0.46 | 100.00 |
| Total | 649 | 100.00 | |

`dt_ini_conv_d`: N não-missing = 1570.

| Variable | Obs | Mean | Std. dev. | Min | Max |
|---|---|---|---|---|---|
| dt_ini_conv_d | 1,570 | 18702.61 | 1385.949 | 9388 | 21462 |

min = 14sep1985   max = 05oct2018

| yr_dt_ini_conv_d | Freq. | Percent | Cum. |
|---|---|---|---|
| 2005 | 25 | 1.72 | 1.72 |
| 2006 | 34 | 2.34 | 4.07 |
| 2007 | 157 | 10.83 | 14.90 |
| 2008 | 80 | 5.52 | 20.41 |
| 2009 | 89 | 6.14 | 26.55 |
| 2010 | 192 | 13.24 | 39.79 |
| 2011 | 135 | 9.31 | 49.10 |
| 2012 | 211 | 14.55 | 63.66 |
| 2013 | 162 | 11.17 | 74.83 |
| 2014 | 219 | 15.10 | 89.93 |
| 2015 | 28 | 1.93 | 91.86 |
| 2016 | 8 | 0.55 | 92.41 |
| 2017 | 96 | 6.62 | 99.03 |
| 2018 | 14 | 0.97 | 100.00 |
| Total | 1,450 | 100.00 | |

**A3 — tipo de unidade** (`tab tipoesc, miss`)

| tipoesc | Freq. | Percent | Cum. |
|---|---|---|---|
| CCI/CIPS | 3 | 0.06 | 0.06 |
| CEI DIRET | 317 | 6.67 | 6.73 |
| CEI INDIR | 376 | 7.91 | 14.64 |
| CEMEI | 14 | 0.29 | 14.94 |
| CEU CEI | 45 | 0.95 | 15.88 |
| CEU EMEF | 46 | 0.97 | 16.85 |
| CEU EMEI | 47 | 0.99 | 17.84 |
| CIEJA | 16 | 0.34 | 18.18 |
| CMCT | 2 | 0.04 | 18.22 |
| CR.P.CONV | 1,629 | 34.27 | 52.49 |
| EMEBS | 6 | 0.13 | 52.62 |
| EMEF | 501 | 10.54 | 63.16 |
| EMEFM | 8 | 0.17 | 63.33 |
| EMEI | 508 | 10.69 | 74.02 |
| ESC.PART. | 892 | 18.77 | 92.78 |
| MOVA | 343 | 7.22 | 100.00 |
| Total | 4,753 | 100.00 | |

`tab tipoesc cei, miss`: todos os `cei==0` (coluna única `0`, iguais aos totais acima). `count if cei==1` → **0**. (A flag `inlist` de A não capturou nenhum registro — ver A2fix.)

**A5 — sanidade das coordenadas** (`sum lat lon, detail`)

lat:

| | valor |
|---|---|
| 1% | -23.78399 |
| 5% | -23.72994 |
| 10% | -23.68653 |
| 25% | -23.62662 |
| 50% | -23.56573 |
| 75% | -23.50708 |
| 90% | -23.46793 |
| 95% | -23.45066 |
| 99% | -23.41209 |
| Obs | 4,728 |
| Mean | -23.57284 |
| Std. dev. | .0851686 |
| Variance | .0072537 |
| Skewness | -.4940845 |
| Kurtosis | 2.91724 |
| Smallest | -23.90708 / -23.88053 / -23.87412 / -23.87048 |
| Largest | -23.40161 / -23.40122 / -23.40084 / -23.39961 |

lon:

| | valor |
|---|---|
| 1% | -46.7942 |
| 5% | -46.77729 |
| 10% | -46.75841 |
| 25% | -46.71187 |
| 50% | -46.63467 |
| 75% | -46.48688 |
| 90% | -46.41514 |
| 95% | -46.39806 |
| 99% | -46.37978 |
| Obs | 4,728 |
| Mean | -46.60452 |
| Std. dev. | .1259758 |
| Variance | .0158699 |
| Skewness | .2829226 |
| Kurtosis | 1.75313 |
| Smallest | -46.80745 / -46.80573 / -46.80446 / -46.80168 |
| Largest | -46.36724 / -46.3672 / -46.36685 / -46.36622 |

- `count if !missing(lat,lon)` → 4,727
- `count if !missing(lat,lon) & fora_sp==1` → 0
- `count if !missing(lat,lon) & fora_sp==0` → 4,727

**A4 — merge com Fila** (`merge m:1 codesc using fila_codesc.dta`)

| Result | Number of obs |
|---|---|
| Not matched | 1,814 |
| — from master (mfila==1) | 1,411 |
| — from using (mfila==2) | 403 |
| Matched (mfila==3) | 3,342 |

`drop if mfila==2` → (403 observations deleted). Contagens (com flag `cei` de A, que é sempre 0):
- CEI 2008-2016 + coord + Fila (dt_criacao) → 0
- idem dt_ini_func → 0
- CEI 2008-2016 + coord (sem Fila) → 0
- CEI que casam com Fila (qualquer data) → 0

### A2fix — diag04_A2fix.log

- `N= 4753`
- `tab L` (comprimento de `tipoesc`): valor 12 = 4,753 (100%). `levelsof` mostra os 16 valores com padding a 12 caracteres (ex.: `[CEI DIRET   ]`).

**Flag CEI reconstruída** (`strpos`): `tab tipoesc cei, miss`

| tipoesc | cei=0 | cei=1 | Total |
|---|---|---|---|
| CCI/CIPS | 0 | 3 | 3 |
| CEI DIRET | 0 | 317 | 317 |
| CEI INDIR | 0 | 376 | 376 |
| CEMEI | 0 | 14 | 14 |
| CEU CEI | 0 | 45 | 45 |
| CEU EMEF | 46 | 0 | 46 |
| CEU EMEI | 47 | 0 | 47 |
| CIEJA | 16 | 0 | 16 |
| CMCT | 2 | 0 | 2 |
| CR.P.CONV | 0 | 1,629 | 1,629 |
| EMEBS | 6 | 0 | 6 |
| EMEF | 501 | 0 | 501 |
| EMEFM | 8 | 0 | 8 |
| EMEI | 508 | 0 | 508 |
| ESC.PART. | 892 | 0 | 892 |
| MOVA | 343 | 0 | 343 |
| Total | 2,369 | 2,384 | 4,753 |

- `count if cei==1` → **2,384**

`tab tipoesc if cei==1`:

| tipoesc | Freq. | Percent | Cum. |
|---|---|---|---|
| CCI/CIPS | 3 | 0.13 | 0.13 |
| CEI DIRET | 317 | 13.30 | 13.42 |
| CEI INDIR | 376 | 15.77 | 29.19 |
| CEMEI | 14 | 0.59 | 29.78 |
| CEU CEI | 45 | 1.89 | 31.67 |
| CR.P.CONV | 1,629 | 68.33 | 100.00 |
| Total | 2,384 | 100.00 | |

**A4 refeito** — mesmo merge de A (Not matched 1,814; from master 1,411; from using 403; Matched 3,342). Após `drop if mfila==2` (403 deleted):
- CEI total → 2,384
- CEI com coord → 2,383
- CEI com coord & casa Fila → 2,378
- **A4 dt_criacao 2008-2016 + coord + Fila (NÚMERO CRÍTICO) → 1,037**
- idem dt_ini_func → 351
- idem dt_ini_conv → 938
- CEI dt_criacao 2008-2016 + coord (sem Fila) → 1,038

Última linha: `tab yr_dt_criacao_d ...` → **erro** `variable yr_dt_criacao_d not found`, `r(111)`, `end of do-file`.

### B — diag04_B.log

- `N linhas Fila = 3298064`
- `gen dt_mat` → 1,169,483 missing gerados.
- `serie_aluno` — real changes por regra: 1→302,910; 2→510,979; 3→437,416; 4→288,825; 5→381,158; 6→172,367; 7→3,452; 8→11,330; 9→10,440; 10→8,897.
- `keep if !missing(dt_mat)` → 1,169,483 deleted. `N linhas com matricula = 2128581`.
- 1ª matrícula por criança: 807,692 deleted. `N criancas distintas com matricula = 1320889`.

**B1 — idade_entrada**
- `count if !missing(idade_entrada)` → 1,320,889
- `_pctile`: p5=6  p10=8  p25=15  p50=27  p75=43  p90=57  p95=63

`sum idade_entrada, detail`:

| | valor |
|---|---|
| 1% | 3 |
| 5% | 6 |
| 10% | 8 |
| 25% | 15 |
| 50% | 27 |
| 75% | 43 |
| 90% | 57 |
| 95% | 63 |
| 99% | 70 |
| Obs | 1,320,889 |
| Mean | 29.85326 |
| Std. dev. | 18.09049 |
| Variance | 327.2658 |
| Skewness | .4958118 |
| Kurtosis | 2.221532 |
| Smallest | -9 / -2 / -1 / 0 |
| Largest | 107 / 122 / 125 / 140 |

**B2 — por ano letivo** (count / p10 / p50 / p90 / mean / sd de idade_entrada)

| an_letivo_matricula | N | p10 | p50 | p90 | Mean | SD |
|---|---|---|---|---|---|---|
| 2010 | 54,455 | 13 | 43 | 67 | 40.08622 | 20.27617 |
| 2011 | 49,627 | 15 | 37 | 65 | 40.22145 | 18.75365 |
| 2012 | 86,032 | 17 | 43 | 64 | 41.54596 | 17.27846 |
| 2013 | 180,808 | 11 | 34 | 59 | 34.47996 | 17.42256 |
| 2014 | 163,228 | 10 | 30 | 57 | 31.62309 | 17.29529 |
| 2015 | 168,304 | 9 | 25 | 54 | 28.53185 | 16.75792 |
| 2016 | 163,867 | 7 | 24 | 57 | 28.75134 | 18.38315 |
| 2017 | 159,399 | 7 | 23 | 54 | 26.58658 | 17.65056 |
| 2018 | 196,309 | 7 | 22 | 48 | 24.7938 | 15.67193 |
| Total | 1,222,029 | 9 | 28 | 58 | 30.90583 | 18.15522 |

**B2 — por série** (count / p10 / p50 / p90 / mean de idade_entrada)

| serie_aluno | N | p10 | p50 | p90 | Mean |
|---|---|---|---|---|---|
| 1 | 240,092 | 4 | 8 | 13 | 8.312968 |
| 2 | 361,267 | 12 | 17 | 24 | 17.77016 |
| 3 | 276,941 | 23 | 30 | 37 | 30.13296 |
| 4 | 168,900 | 35 | 42 | 49 | 41.78218 |
| 5 | 154,988 | 48 | 54 | 60 | 53.76113 |
| 6 | 84,444 | 58 | 65 | 71 | 64.51551 |
| 7 | 3,450 | 28 | 34 | 40 | 33.8742 |
| 8 | 11,311 | 39 | 45 | 51 | 45.14225 |
| 9 | 10,430 | 51 | 57 | 62 | 56.83586 |
| 10 | 8,891 | 63 | 68 | 73 | 67.96952 |
| Total | 1,320,714 | 8 | 27 | 57 | 29.84944 |

**B3 — espera_dias**
- `count if !missing(espera_dias)` → 1,320,889

`sum espera_dias, detail`:

| | valor |
|---|---|
| 1% | 1 |
| 5% | 2 |
| 10% | 4 |
| 25% | 18 |
| 50% | 119 |
| 75% | 293 |
| 90% | 457 |
| 95% | 586 |
| 99% | 821 |
| Obs | 1,320,889 |
| Mean | 182.8217 |
| Std. dev. | 198.3955 |
| Variance | 39360.79 |
| Skewness | 1.487345 |
| Kurtosis | 5.723277 |
| Smallest | 0 / 0 / 0 / 0 |
| Largest | 1938 / 1954 / 2032 / 2271 |

**B3 — por ano de matrícula** (count / p10 / p50 / p90 / mean de espera_dias)

| an_letivo_matricula | N | p10 | p50 | p90 | Mean |
|---|---|---|---|---|---|
| 2010 | 54,455 | 3 | 68 | 429 | 156.534 |
| 2011 | 49,627 | 2 | 55 | 476 | 161.1129 |
| 2012 | 86,032 | 2 | 23 | 415 | 128.9179 |
| 2013 | 180,808 | 3 | 112 | 518 | 196.986 |
| 2014 | 163,228 | 3 | 141 | 525 | 205.9069 |
| 2015 | 168,304 | 3 | 147 | 502 | 205.7584 |
| 2016 | 163,867 | 6 | 122 | 450 | 187.4343 |
| 2017 | 159,399 | 6 | 122 | 410 | 173.4715 |
| 2018 | 196,309 | 4 | 122 | 402 | 171.3518 |
| Total | 1,222,029 | 3 | 113 | 467 | 182.8684 |

**B4 — universo potencial**
- `count if univ==1` → 1,320,845

`tab ano_solic if univ==1 & inrange(ano_solic,2008,2018)`:

| ano_solic | Freq. | Percent | Cum. |
|---|---|---|---|
| 2008 | 3,960 | 0.30 | 0.30 |
| 2009 | 25,559 | 1.94 | 2.24 |
| 2010 | 54,981 | 4.17 | 6.40 |
| 2011 | 88,021 | 6.67 | 13.07 |
| 2012 | 160,053 | 12.13 | 25.20 |
| 2013 | 173,535 | 13.15 | 38.35 |
| 2014 | 160,819 | 12.19 | 50.53 |
| 2015 | 170,690 | 12.93 | 63.47 |
| 2016 | 165,247 | 12.52 | 75.99 |
| 2017 | 155,189 | 11.76 | 87.75 |
| 2018 | 161,735 | 12.25 | 100.00 |
| Total | 1,319,789 | 100.00 | |

- `keep if univ==1` → (44 observations deleted). `N universo salvo = 1320845`.

### Cprep — diag04_Cprep.log

- `keep if cei==1 & !missing(lat,lon) & !missing(dt_criacao_d)` → 2,837 deleted. `N CEI com coord e data de criacao = 1916`.

`tab yr if inrange(yr,2005,2018)` (ano de abertura = dt_criacao):

| yr | Freq. | Percent | Cum. |
|---|---|---|---|
| 2005 | 1 | 0.07 | 0.07 |
| 2006 | 10 | 0.66 | 0.73 |
| 2007 | 60 | 3.98 | 4.71 |
| 2008 | 128 | 8.50 | 13.21 |
| 2009 | 84 | 5.58 | 18.79 |
| 2010 | 89 | 5.91 | 24.70 |
| 2011 | 56 | 3.72 | 28.42 |
| 2012 | 135 | 8.96 | 37.38 |
| 2013 | 35 | 2.32 | 39.71 |
| 2014 | 134 | 8.90 | 48.61 |
| 2015 | 249 | 16.53 | 65.14 |
| 2016 | 128 | 8.50 | 73.64 |
| 2017 | 155 | 10.29 | 83.93 |
| 2018 | 242 | 16.07 | 100.00 |
| Total | 1,506 | 100.00 | |

**Grade / join**
- `expand 9` → 15,328 observations created.
- `N CEP = 46258`
- `N pares (mesma celula/vizinhas) = 3070352`
- `keep if dist_km <= 2` → 1,966,555 deleted. `N pares com dist<=2km = 1103797`.

**Distribuição de CEIs (<=2km) por CEP** — `by cep: keep if _n==1` → 1,059,239 deleted. `sum n, detail`:

| | valor |
|---|---|
| 1% | 1 |
| 5% | 3 |
| 10% | 5 |
| 25% | 11 |
| 50% | 22 |
| 75% | 35 |
| 90% | 49 |
| 95% | 60 |
| 99% | 78 |
| Obs | 44,558 |
| Mean | 24.77214 |
| Std. dev. | 17.67312 |
| Variance | 312.3393 |
| Skewness | 1.000289 |
| Kurtosis | 3.876826 |
| Smallest | 1 / 1 / 1 / 1 |
| Largest | 98 / 98 / 98 / 98 |

- `N CEP com >=1 CEI <=2km = 44558`

### C1 — diag04_C1.log

- `N universo = 1320845`
- `joinby cep using cep_cei_pairs.dta, unmatched(master)` → `N linhas apos joinby = 40776370`
- `gen inwin` / `gen post12` → 18,151 missing gerados cada.
- Merge de volta ao universo: Matched 1,320,845; Not matched 0. `replace ... = 0 if missing`: 0 real changes (todos os 4).
- `compress` converteu n_ab_* de double para byte.

`tab c500` (n_ab_500, top-coded em 3):

| c500 | Freq. | Percent | Cum. |
|---|---|---|---|
| 0 | 1,211,580 | 91.73 | 91.73 |
| 1 | 92,529 | 7.01 | 98.73 |
| 2 | 13,616 | 1.03 | 99.76 |
| 3 | 3,120 | 0.24 | 100.00 |
| Total | 1,320,845 | 100.00 | |

`tab c1` (n_ab_1km, top-coded em 3):

| c1 | Freq. | Percent | Cum. |
|---|---|---|---|
| 0 | 1,025,945 | 77.67 | 77.67 |
| 1 | 189,402 | 14.34 | 92.01 |
| 2 | 62,642 | 4.74 | 96.76 |
| 3 | 42,856 | 3.24 | 100.00 |
| Total | 1,320,845 | 100.00 | |

`tab c2` (n_ab_2km, top-coded em 3):

| c2 | Freq. | Percent | Cum. |
|---|---|---|---|
| 0 | 766,229 | 58.01 | 58.01 |
| 1 | 208,604 | 15.79 | 73.80 |
| 2 | 122,900 | 9.30 | 83.11 |
| 3 | 223,112 | 16.89 | 100.00 |
| Total | 1,320,845 | 100.00 | |

`sum n_ab_500 n_ab_1km n_ab_2km n_post_1km`:

| Variable | Obs | Mean | Std. dev. | Min | Max |
|---|---|---|---|---|---|
| n_ab_500 | 1,320,845 | .09839 | .357226 | 0 | 7 |
| n_ab_1km | 1,320,845 | .3599188 | .8376132 | 0 | 15 |
| n_ab_2km | 1,320,845 | 1.209049 | 2.162598 | 0 | 39 |
| n_post_1km | 1,320,845 | .6233775 | 1.030774 | 0 | 11 |

% com >=1 abertura:
- n_ab_500>=1 : 109265 (8.27%)
- n_ab_1km>=1 : 294900 (22.33%)
- n_ab_2km>=1 : 554616 (41.99%)

### C2 — diag04_C2.log

- `N = 1320845`
- `codebook regiao`: Obs 1320845, Unique 661, Mean 510.4061, Min 0, Max 9999.
- `codebook regyear`: Obs 1320845, Unique 5528, Mean 3067.345, Min 1, Max 5528.

**C2 (1) — reg idade_entrada n_ab_1km i.ano_solic i.mes_nasc**

Number of obs = 1,320,845; F(24, 1320820) = 4669.82; R-squared = 0.0782; Adj R² = 0.0782; Root MSE = 17.369.

| variável | Coef. | Std. err. | t | P>\|t\| |
|---|---|---|---|---|
| n_ab_1km | -1.849721 | .0182211 | -101.52 | 0.000 |
| ano 2007 | -5.248858 | 1.247193 | -4.21 | 0.000 |
| ano 2008 | -13.48853 | 1.120116 | -12.04 | 0.000 |
| ano 2009 | -20.73622 | 1.091068 | -19.01 | 0.000 |
| ano 2010 | -18.25201 | 1.088204 | -16.77 | 0.000 |
| ano 2011 | -22.14412 | 1.087234 | -20.37 | 0.000 |
| ano 2012 | -23.85487 | 1.086539 | -21.95 | 0.000 |
| ano 2013 | -25.47718 | 1.086493 | -23.45 | 0.000 |
| ano 2014 | -28.18034 | 1.086493 | -25.94 | 0.000 |
| ano 2015 | -29.8365 | 1.086421 | -27.46 | 0.000 |
| ano 2016 | -31.70981 | 1.086505 | -29.19 | 0.000 |
| ano 2017 | -32.56737 | 1.086516 | -29.97 | 0.000 |
| ano 2018 | -35.3379 | 1.08652 | -32.52 | 0.000 |
| _cons | 58.65183 | 1.087104 | 53.95 | 0.000 |

(coef. mensais mes_nasc 2–12, do log: 2 -.1736041; 3 -.2229822; 4 .8781182; 5 .5621149; 6 .3547182; 7 .3525961; 8 .2240168; 9 .1607981; 10 .1650779; 11 .0825335; 12 -.1859642.)

showfs: coef=-1.8497211 se=.01822111 t=-101.5153 N=1320845 r2=.07821618. F(1,1320820)=10305.36; F(instrumento)=10305.356 p=0.

**C2 (2) — areg idade_entrada n_ab_1km i.mes_nasc, absorb(regyear)**

Number of obs = 1,320,845; No. categories regyear = 5,528; F(12, 1315305) = 1817.96; R² = 0.1265; Adj R² = 0.1229; Root MSE = 16.9425.

| variável | Coef. | Std. err. | t | P>\|t\| |
|---|---|---|---|---|
| n_ab_1km | -3.010524 | .020611 | -146.06 | 0.000 |
| _cons | 30.78033 | .0521707 | 589.99 | 0.000 |

F test of absorbed indicators: F(5527, 1315305) = 31.744, Prob>F = 0.000.
showfs: coef=-3.0105237 se=.02061097 t=-146.06414 N=1320845 r2=.12654328. F(instrumento)=21334.732 p=0.

**C3 (1) — reg espera_dias n_ab_1km i.ano_solic i.mes_nasc**

Number of obs = 1,320,845; F(24, 1320820) = 14100.32; R² = 0.2040; Adj R² = 0.2039; Root MSE = 177.

| variável | Coef. | Std. err. | t | P>\|t\| |
|---|---|---|---|---|
| n_ab_1km | 81.93464 | .18569 | 441.24 | 0.000 |
| ano 2007 | -332.453 | 12.71006 | -26.16 | 0.000 |
| ano 2008 | -685.9966 | 11.41503 | -60.10 | 0.000 |
| ano 2009 | -952.1854 | 11.119 | -85.64 | 0.000 |
| ano 2010 | -1038.862 | 11.08981 | -93.68 | 0.000 |
| ano 2011 | -954.7125 | 11.07993 | -86.17 | 0.000 |
| ano 2012 | -1052.857 | 11.07285 | -95.08 | 0.000 |
| ano 2013 | -1060.786 | 11.07238 | -95.80 | 0.000 |
| ano 2014 | -1081.408 | 11.07237 | -97.67 | 0.000 |
| ano 2015 | -1111.981 | 11.07164 | -100.44 | 0.000 |
| ano 2016 | -1086.488 | 11.0725 | -98.12 | 0.000 |
| ano 2017 | -1114.066 | 11.07261 | -100.61 | 0.000 |
| ano 2018 | -1152.963 | 11.07265 | -104.13 | 0.000 |
| _cons | 1238.896 | 11.0786 | 111.83 | 0.000 |

showfs: coef=81.934639 se=.18569 t=441.24422 N=1320845 r2=.20395496. F(instrumento)=194696.47 p=0.

**C3 (2) — areg espera_dias n_ab_1km i.mes_nasc, absorb(regyear)**

Number of obs = 1,320,845; categorias = 5,528; F(12, 1315305) = 20650.58; R² = 0.3691; Adj R² = 0.3665; Root MSE = 157.9046.

| variável | Coef. | Std. err. | t | P>\|t\| |
|---|---|---|---|---|
| n_ab_1km | 95.39061 | .1920944 | 496.58 | 0.000 |
| _cons | 156.3305 | .4862312 | 321.51 | 0.000 |

F test of absorbed indicators: F(5527, 1315305) = 95.999, Prob>F = 0.000.
showfs: coef=95.390614 se=.19209444 t=496.58187 N=1320845 r2=.36910795. F(instrumento)=246593.55 p=0.

**C5 placebo (1) — reg idade_entrada n_post_1km i.ano_solic i.mes_nasc**

Number of obs = 1,320,845; F(24, 1320820) = 4226.72; R² = 0.0713; Adj R² = 0.0713; Root MSE = 17.433.

| variável | Coef. | Std. err. | t | P>\|t\| |
|---|---|---|---|---|
| n_post_1km | .3097143 | .0149994 | 20.65 | 0.000 |
| _cons | 56.31922 | 1.090958 | 51.62 | 0.000 |

showfs: coef=.30971434 se=.01499945 t=20.648382 N=1320845 r2=.07132397. F(instrumento)=426.3557 p=1.045e-94.

**C5 placebo (2) — areg idade_entrada n_post_1km i.mes_nasc, absorb(regyear)**

Number of obs = 1,320,845; categorias = 5,528; F(12, 1315305) = 70.00; R² = 0.1126; Adj R² = 0.1089; Root MSE = 17.0770.

| variável | Coef. | Std. err. | t | P>\|t\| |
|---|---|---|---|---|
| n_post_1km | .3456777 | .0180524 | 19.15 | 0.000 |
| _cons | 29.42676 | .0532118 | 553.01 | 0.000 |

F test of absorbed indicators: F(5527, 1315305) = 30.081, Prob>F = 0.000.
showfs: coef=.34567768 se=.01805239 t=19.148578 N=1320845 r2=.11262287. F(instrumento)=366.66804 p=1.021e-81.

### C6 — diag04_C6.log

- `keep if dist_km<=1` (em cep_cei_pairs) → 796,129 deleted.
- `joinby cepk` → `N linhas (crianca x CEI <=1km) = 11932867`
- abertura mais próxima no tempo por criança → 10,667,768 deleted. `N criancas com >=1 CEI <=1km = 1265099`.

`table bin if inrange(relm,-24,24)` (count / mean idade_entrada):

| bin | N | Mean idade_entrada |
|---|---|---|
| -24 | 16,310 | 29.87658 |
| -21 | 21,104 | 30.74882 |
| -18 | 25,470 | 30.47774 |
| -15 | 35,521 | 30.04597 |
| -12 | 47,048 | 28.73871 |
| -9 | 67,806 | 28.38461 |
| -6 | 104,249 | 28.75796 |
| -3 | 167,976 | 28.01311 |
| 0 | 150,409 | 27.80322 |
| 3 | 98,664 | 28.73502 |
| 6 | 74,351 | 29.69709 |
| 9 | 58,004 | 30.82865 |
| 12 | 41,192 | 30.49141 |
| 15 | 34,472 | 31.54827 |
| 18 | 27,776 | 32.933 |
| 21 | 24,214 | 33.79458 |
| Total | 994,566 | 29.20847 |

(O log não mostra a linha `bin = 24`; ver seção final.)

### D — diag04_D.log

**D1** — `describe` dos 4 arquivos PSP não retornou saída no log (linhas apenas com os cabeçalhos `==== <arquivo> ====`; os `cap describe` não imprimiram conteúdo).

**D2 — universo**
- `duplicates drop`: (0 observations are duplicates). `N universo (cd_aluno distintos) = 1320845`.

Por ano de PSP:

| PSP | N linhas | Excluídas (sem prof) | N crianças distintas c/ proficiência | N casadas com universo B4 |
|---|---|---|---|---|
| 2017 | 227,005 | 16,782 | 210,223 | 42,459 |
| 2018 | 394,040 | 25,538 | 368,502 | 114,999 |
| 2019 | 378,957 | 28,160 | 350,797 | 144,703 |

(Cada merge com universo: Not matched 0, Matched = N casadas.)

**D3 — universo × PSP (algum ano)**
- merge 2017: Not matched 1,278,386 (master); Matched 42,459.
- merge 2018: Not matched 1,205,846 (master); Matched 114,999.
- merge 2019: Not matched 1,176,142 (master); Matched 144,703.
- `count if psp_any==1` → **162,808** (rotulado "N do paper").
- Por ano no universo: PSP 2017 → 42459; PSP 2018 → 114999; PSP 2019 → 144703.
- `count if psp2018==1` → 114,999.

`tab npsp`:

| npsp | Freq. | Percent | Cum. |
|---|---|---|---|
| 0 | 1,158,037 | 87.67 | 87.67 |
| 1 | 56,840 | 4.30 | 91.98 |
| 2 | 72,583 | 5.50 | 97.47 |
| 3 | 33,385 | 2.53 | 100.00 |
| Total | 1,320,845 | 100.00 | |

### E — diag04_E.log

**D1 (compl.) — variáveis (abreviadas por `ds`)**
- psp_2017: `proficienc~p  proficienc~t  proficienc~e  cd_serie  desc_serie  cd_aluno_sme`
- psp_2018: `proficienc~p  prof~p_arred  proficienc~t  prof~t_arred  proficienc~e  prof~e_arred  cd_serie  desc_serie  cd_aluno_sme`
- psp_2019: `proficienc~p  prof~p_arred  proficienc~e  proficienc~t  prof~t_arred  prof~e_arred  cd_serie  desc_serie  cd_aluno_sme`
- Microdados_PSP_2018_2ano (`ds`, lista completa abreviada): id, ano_letivo, cd_unidade~o, tipo_escola, dre, nome_distr~o, cd_turma, cd_turno, cd_serie, desc_serie, modalidade, modalidade~o, cd_ciclo_e~o, desc_ciclo~o, cd_aluno_sme, cd_inep_al~o, possui_nee, desc_tp_p~pt, desc_tp_p~at, desc_tp_pr~e, prova_lpt, prova_mat, prova_cie, caderno_mat, caderno_lpt, caderno_cie, in_presenc~p, in_presenc~t, in_presenc~e, in_presenc~d, vetor_corr~p, vetor_corr~t, vetor_corr~e, vetor_mat, vetor_lp, vetor_cie, acertos_al~p, acertos_al~t, acertos_al~e, per_aluno_lp, per_aluno_~t, per_aluno_~e, proficienc~p, proficienc~t, proficienc~e, prof~p_arred, prof~t_arred, prof~e_arred, nota_red, nivel_lp, nivel_mat, nivel_cie, nivel_red, desc_nivel~p, desc_nivel~t, desc_nivel~e, desc_nivel~d, nome_turma, cd_turno (conforme grade impressa no log).

**E1 — matriculas1018.dta**
- `N linhas = 86122`

`tab serie_aluno, miss`:

| serie_aluno | Freq. | Percent | Cum. |
|---|---|---|---|
| 1 | 9 | 0.01 | 0.01 |
| 2 | 9 | 0.01 | 0.02 |
| 3 | 9 | 0.01 | 0.03 |
| 4 | 9 | 0.01 | 0.04 |
| 5 | 9 | 0.01 | 0.05 |
| 6 | 9 | 0.01 | 0.06 |
| 7 | 4 | 0.00 | 0.07 |
| 8 | 7 | 0.01 | 0.08 |
| 9 | 5 | 0.01 | 0.08 |
| 10 | 6 | 0.01 | 0.09 |
| . | 86,046 | 99.91 | 100.00 |
| Total | 86,122 | 100.00 | |

- `keep if !missing(...serie_aluno)` → (86,122 observations deleted).
- `contract` → **`no observations` / `r(2000)` / `end of do-file`** (log interrompido; blocos E2 e infra não executados neste log).

### Eredo — diag04_Eredo.log

**E1 — tamanho de turma via matrículas do Fila**
- `gen dt_mat` → 1,169,483 missing gerados.
- `keep if !missing(dt_mat) & ...` → 1,169,483 deleted.
- `serie_aluno` real changes: 1→302,910; 2→510,979; 3→437,416; 4→288,825; 5→381,158; 6→172,367.
- `keep if !missing(serie_aluno)` → 34,926 deleted.
- `duplicates drop cd_aluno_sme cd_esc_matricula an_letivo_matricula serie_aluno, force` → 311,163 deleted.
- `contract` → `N celulas escola-ano-serie = 70590`.

`sum turma, detail` (todas séries 1-6):

| | valor |
|---|---|
| 1% | 1 |
| 5% | 2 |
| 10% | 3 |
| 25% | 8 |
| 50% | 17 |
| 75% | 32 |
| 90% | 54 |
| 95% | 73 |
| 99% | 144 |
| Obs | 70,590 |
| Mean | 25.25134 |
| Std. dev. | 29.70475 |
| Variance | 882.3719 |
| Skewness | 4.392758 |
| Kurtosis | 39.07728 |
| Smallest | 1 / 1 / 1 / 1 |
| Largest | 551 / 574 / 591 / 595 |

`sum turma if serie_aluno==1`:

| | valor |
|---|---|
| 1% | 1 | 5% | 2 | 10% | 3 | 25% | 9 | 50% | 17 | 75% | 27 | 90% | 42 | 95% | 54 | 99% | 91 |
| Obs | 12,099 | Mean | 21.21853 | Std. dev. | 19.17647 | Variance | 367.7372 | Skewness | 3.054902 | Kurtosis | 21.48699 |
| Largest | 202 / 225 / 229 / 296 |

`sum turma if serie_aluno==2`:

| | valor |
|---|---|
| Percentis | 1%=1, 5%=2, 10%=4, 25%=9, 50%=20, 75%=34, 90%=52, 95%=65, 99%=105 |
| Obs | 16,805 | Mean | 24.88307 | Std. dev. | 22.22292 | Variance | 493.8582 | Skewness | 2.299904 | Kurtosis | 13.71665 |
| Largest | 209 / 224 / 314 / 322 |

`sum turma if serie_aluno==3`:

| | valor |
|---|---|
| Percentis | 1%=1, 5%=2, 10%=3, 25%=7, 50%=15, 75%=29, 90%=49, 95%=63, 99%=103 |
| Obs | 16,535 | Mean | 21.74702 | Std. dev. | 22.04327 | Variance | 485.9059 | Skewness | 2.793284 | Kurtosis | 18.37578 |
| Largest | 267 / 289 / 297 / 349 |

**E2 — censo2018 casa com CEIs de Fila?**
- `keep if cei==1` → 2,369 deleted.
- `merge m:1 codesc using fila_codesc.dta, keep(match)` → Not matched 0, Matched 2,379. `N CEI que casam com Fila = 2379`.
- `count if tem_codinep==1` → 2,379.
- `codinep distintos em censo2018 = 286014` (após `duplicates drop`, 0 duplicatas; `drop if missing`, 0 deletadas).
- `merge m:1 codinep using cs`: Not matched 177 (from master, mc==1); Matched 2,202 (mc==3).
- `count if mc==3` → 2,202.
- `count if tem_codinep==1` → 2,379.
- `count if mc==3 & tem_codinep==1` → 2,202.

**Variáveis de infraestrutura em censo2018** (`ds`, abreviadas): `qt_salas_e~s  qt_salas_u~s  qt_equip_tv  qt_equip_v~e  qt_equip_dvd  qt_equip_p~a  qt_equip_c~a  qt_equip_r~r  qt_equip_i~a  qt_equip_i~t  qt_equip_som  qt_equip_m~a  qt_equip_fax  qt_equip_f~o  qt_computa~r  qt_comp_ad~o  qt_comp_al~o  qt_funcion~s  in_bercario  in_agua_re~a  in_esgoto~ca  in_energia~a  in_banheir~i  in_parque_~l  in_cozinha  in_refeito~o  tp_depende~a  in_conveni~p`.

## O que o log NÃO permite recuperar

- **Flag CEI em diag04_A**: em A a flag `cei` (via `inlist`) resultou 0 em tudo (`count if cei==1` = 0) porque `tipoesc` tem comprimento fixo 12 com padding de espaços (constatado em A2fix). Todas as contagens A4 do log A saem 0; os números "reais" só aparecem em A2fix. O log A não explicita a causa — ela só é dedutível de A2fix.
- **diag04_A2fix**: termina em erro `r(111)` (variável `yr_dt_criacao_d` não existe em `escolas_parsed.dta`); a distribuição por ano dos CEIs que casam com Fila **não foi produzida**.
- **diag04_E**: interrompido em `contract` com `r(2000)` (nenhuma obs com `serie_aluno` em `matriculas1018.dta` — o arquivo tem 86.046/86.122 com `serie_aluno` missing). Os blocos E2 e a listagem de infraestrutura **não rodaram** neste log; foram refeitos em Eredo.
- **diag04_D — D1**: os `cap describe` dos 4 arquivos PSP não imprimiram nada no log (só os títulos `==== ... ====`). Estrutura/variáveis dos PSP só aparecem parcialmente em diag04_E (via `ds`).
- **Nomes de variáveis abreviados** pelo Stata (`ds` e `levelsof`): p.ex. `proficienc~p`, `qt_salas_e~s`, `in_esgoto~ca`, `desc_nivel~e`. Os nomes completos não constam dos logs.
- **diag04_C6**: a tabela `table bin` mostra bins de -24 a 21 mais Total; o bin `24` não aparece na saída transcrita (não impresso ou fora do range efetivo). O comportamento exato não é recuperável do log.
- **Coordenadas / lat-lon**: `sum lat lon` reporta 4,728 obs, mas `count if !missing(lat,lon)` = 4,727 (1 caso com apenas uma coordenada não-missing). O log não detalha esse caso.
- **Datas de decisão / thresholds**: os `.do` aplicam regras fixas (janelas 2008-2016, raios 0.5/1/2 km, bin de 3 meses, `dt_criacao` como data de abertura), mas o log não registra justificativa dessas escolhas — apenas a execução.
- **Arquivos-fonte externos** (`Fila1018.dta`, `escolassite.dta`, `cepcentroide.dta`, `psp_*.dta`, `Microdados_PSP_2018_2ano.dta`, `matriculas1018.dta`, `censo2018.dta`) não estão nos logs; apenas contagens/resultados derivados deles.
- **Discrepância de caminho**: os `.log` gravam o diretório como `...\Neighborhood Effects\_audit\` enquanto os `.do` definem `$aud = ...\02_audit`. A origem da diferença não é recuperável do log.

---

### Fonte primária (arquivos .log)

- `02_audit\diag04_A.log` (403 linhas) — `.do`: `diag04_A.do` (112)
- `02_audit\diag04_A2fix.log` (192) — `.do`: `diag04_A2fix.do` (56)
- `02_audit\diag04_B.log` (300) — `.do`: `diag04_B.do` (90)
- `02_audit\diag04_C1.log` (173) — `.do`: `diag04_C1.do` (57)
- `02_audit\diag04_C2.log` (379) — `.do`: `diag04_C2.do` (56)
- `02_audit\diag04_C6.log` (83) — `.do`: `diag04_C6.do` (29)
- `02_audit\diag04_Cprep.log` (179) — `.do`: `diag04_Cprep.do` (67)
- `02_audit\diag04_D.log` (225) — `.do`: `diag04_D.do` (73)
- `02_audit\diag04_E.log` (79) — `.do`: `diag04_E.do` (77)
- `02_audit\diag04_Eredo.log` (246) — `.do`: `diag04_Eredo.do` (72)
