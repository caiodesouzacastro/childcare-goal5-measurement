> RECONSTRUÇÃO. Este arquivo foi gerado a partir dos logs em 02_audit\ e não
> é o relatório original, que não foi preservado em .md. Os números vêm dos
> logs; a estrutura e as regras de decisão foram reconstruídas e podem estar
> incompletas. Fonte primária: os arquivos .log listados ao final.

# DIAG02 — Reconstrução a partir dos logs de auditoria

## Arquivos lidos

Todos em `<NE_ROOT>\02_audit\`.

| Arquivo | Linhas | O que o .do faz (só pelos comandos) |
|---|---|---|
| `diag02_scanA.do` | 39 | Varre 7 diretórios em `<NE_ROOT>\dados_restritos\Dados - SME/...` (`Atual (25.06)` e subpastas `ceps`, `escolas`, `matriculas`, `Microdados_..._FGV`; `01.07` e `01.07/matriculas`) buscando, em cada `.dta`, nomes ou rótulos de variáveis que contenham as palavras-chave `corte vaga capac limite class posic ordem rank fila prior chamada convoc sorteio data_lim`. Abre cada arquivo com `use "...`" in 1` e imprime `MATCH | arquivo | var | tipo | rótulo`. |
| `diag02_scanA.log` | 1311 | Saída do scan acima. |
| `diag02_descB.do` | 24 | Faz `use` + `describe, fullnames` em 8 arquivos fixos (`corteescolaunique`, `escolassite`, `escolasPSP2`, `censo2018`, `fila1018`, `matriculas1018`, `filamatriculasite`, `fila_preferencia`), reportando N obs e N vars de cada. |
| `diag02_descB.log` | 638 | Saída do describe acima. |
| `diag02_ABD.do` | 119 | Blocos **A2** (estatísticas de `dt_corte`/`dt_corte_escola` em `corteescolaunique.dta`; `tab tipo_prioridade_encaminhamento` em `fila1018.dta`), **A3** (`duplicates report` e `tab serie_aluno × ano` em `corteescolaunique.dta`), **B2/B3/B4/B5/B6** (tabulações e contagens em `b1_2011_audit.dta`: `exp_tratamento`, matrícula, `esc_trat`, `trat2011ber`, `encaminhado`, idade em meses) e **D** (compara `prof_mat` para `rvar==0` vs tratados vs controles; `rdrobust` de `prof_mat` sobre `rvar` excluindo `rvar==0`). |
| `diag02_ABD.log` | 545 | Saída dos blocos A2/A3/B/D acima. |
| `diag02_partC.do` | 145 | Constrói universo de encaminhados "2011 Ber I" a partir de `Fila1018.dta` (filtros: `tipo_prioridade_encaminhamento==.`, série 1 [cod 1/2/3], `an_letivo_encaminhamento==2011`, `dt_encaminhamento<=31dec2010`), calcula estatísticas por escola (`school_stats_2011ber.dta`), monta corte leave-one-out (LOO) via `reshape`/`merge` (`loo_long.dta`), define `rvar_loo` para a escola mais próxima (`loo_child.dta`) e roda blocos **C1**–**C6** (percentis de nº de encaminhados, corte_LOO, `rvar_loo`, primeiro estágio por faixas, `rdrobust`, `rddensity`). |
| `diag02_partC.log` | 450 | Saída dos blocos C acima. |

Observação de cabeçalho: em todos os `.log` o caminho registrado por `log using` aparece como `...\Neighborhood Effects\_audit\...` (com `_audit`), enquanto o global `$aud` nos `.do` aponta para `02_audit`. Datas de abertura/fechamento: scanA 22 Jul 2026 10:24:16–10:24:22; descB 10:25:43–10:25:49; ABD 10:30:00–10:30:01; partC 10:33:33–10:33:46.

---

## Estatísticas e tabelas encontradas (transcritas)

### `diag02_scanA.log` — varredura de variáveis por palavra-chave

Palavras-chave: `corte vaga capac limite class posic ordem rank fila prior chamada convoc sorteio data_lim`.

**Erro de abertura registrado:** `ERRO ao abrir <NE_ROOT>\dados_restritos\Dados - SME/Atual (25.06)/escolas/escolaspsp3.dta : rc=610`.

Fecho: `=== FIM SCAN A ===`.

**MATCH em `corteescolaunique.dta`:**

| Arquivo | Variável | Tipo | Rótulo |
|---|---|---|---|
| corteescolaunique.dta | dt_corte_escola | float | (mean) dt_corte_escola |
| corteescolaunique.dta | dt_corte | float | (mean) dt_corte |

**MATCH `tipo_prioridade_encaminhamento` (byte, sem rótulo)** nos arquivos (via palavra-chave `prior`):
cpf.dta; cpf_fila_101; cpf_fila_101_old; cpf_fila_102; cpf_fila_102_old; cpf_fila_11; cpf_fila_11_old; cpf_fila_12; cpf_fila_12_old; cpf_fila_13; cpf_fila_13_old; cpf_fila_14; cpf_fila_14_old; fila1018; fila1018ber; fila1018ber12; fila1018ber12_psp; fila1018ber_psp; fila1018min1; fila1018min1_psp; fila1018min2; fila1018min2_psp; trat2010ber; trat2010ber2; trat2010bernodup; trat2010ber_psp; trat2011ber; trat2011ber2; trat2011bernodup; trat2011ber_psp; trat2011min1; trat2011min2; trat2012ber; trat2012ber2; trat2012ber_psp; trat2012min1; trat2012min2; trat2013ber; trat2013ber2; trat2013min1; trat2013min1_psp; trat2013min2; trat2014ber; trat2014ber2; trat2014min1; trat2014min1_psp; trat2014min2; trat2014min2_psp; trat2015ber; trat2015ber2; trat2016ber; trat2017ber; trat2018ber. No diretório `01.07`/`01.07/matriculas`: fila1018 (2×) e matriculas1018.

**MATCH de variáveis CNAE (via palavra-chave `class`)** — presentes em cpf_fila_11, cpf_fila_11_old, cpf_fila_12, cpf_fila_12_old, cpf_fila_13, cpf_fila_13_old, cpf_fila_14, cpf_fila_14_old:

| Variável | Tipo | Rótulo |
|---|---|---|
| cnae95classe | long | CNAE 95 Classe |
| cnae20classe | long | CNAE 2.0 Classe |
| cnae20subclasse | long | CNAE 2.0 Subclasse |

**MATCH do bloco `dt_corte_escola1` … `dt_corte_escola31`** (31 variáveis, cada uma `float`, rótulos `1 dt_corte_escola` … `31 dt_corte_escola`) nos arquivos:
trat2010ber; trat2010ber2; trat2010bernodup; trat2010ber_psp; trat2011ber; trat2011ber2; trat2011ber2_psp; trat2011bernodup; trat2011ber_psp; trat2011min1; trat2011min2; trat2012ber; trat2012ber2; trat2012ber2_psp; trat2012ber_psp; trat2012min1; trat2012min2; trat2013ber; trat2013ber2; trat2013ber2_psp; trat2013min1; trat2013min1_psp; trat2013min2; trat2014ber; trat2014ber2; trat2014min1; trat2014min1_psp; trat2014min2; trat2014min2_psp; trat2015ber; trat2015ber2; trat2016ber; trat2017ber; trat2018ber; trat_min1_2011; trat_min1_2012; trat_min1_2013; trat_min1_2014.

(Os `*_psp`/`*_psp2` que só contêm o bloco `dt_corte_escola1-31` — sem `tipo_prioridade_encaminhamento` — incluem trat2011ber2_psp, trat2012ber2_psp, trat2013ber2_psp.)

---

### `diag02_descB.log` — dimensões e estrutura dos 8 arquivos

| Arquivo | N obs | N vars | Data do .dta |
|---|---|---|---|
| corteescolaunique.dta | 50.058 | 5 | 14 Aug 2020 |
| escolas/escolassite.dta | 4.753 | 34 | 30 Jun 2020 |
| escolas/escolasPSP2.dta | 554 | 34 | 1 Jul 2020 |
| escolas/censo2018.dta | 286.014 | 166 | 1 Jul 2020 |
| matriculas/fila1018.dta | 86.046 | 32 | 5 Jul 2020 |
| matriculas/matriculas1018.dta | 86.122 | 34 | 5 Jul 2020 |
| matriculas/filamatriculasite.dta | 12 | 21 | 30 Jun 2020 |
| Microdados_..._FGV/fila_preferencia.dta | 563.105 | 7 | 21 Sep 2020 |

Variáveis de `corteescolaunique.dta` (do `describe`): `an_letivo_encaminhamento` (int), `cd_esc_encaminhamento` (long), `serie_aluno` (float), `dt_corte_escola` (float %td, "(mean) dt_corte_escola"), `dt_corte` (float %td, "(mean) dt_corte"). Sorted by: `an_letivo_encaminhamento serie_aluno cd_esc_encaminhamento`.

`fila1018.dta` (32 vars) e `matriculas1018.dta` (34 vars) contêm o conjunto de campos de solicitação/encaminhamento/matrícula/desistência/recusa (`dt_*`, `an_letivo_*`, `cd_esc_*`, `cd_serie_ensino_*`), além de `tipo_prioridade_encaminhamento`, `cd_sexo_aluno`, `tp_raca_cor`, `mes_nasc`, `ano_nasc`, `cd_pais_mec`, `cep_aluno`, `cpf_resp_aluno`; `matriculas1018.dta` acrescenta `serie_aluno` e `total` ("(sum) total"). `fila_preferencia.dta` (7 vars): `cd_aluno_sme`, `cd_unidade_educacao`, `dt_inicio`, `dt_fim`, `tp_preferencia`, `data_inicio` (%td), `data_fim` (%td). (Estruturas completas de `censo2018`, `escolassite`, `escolasPSP2`, `filamatriculasite` constam do log; não reproduzidas aqui campo a campo.)

Fecho: `=== FIM DESC B ===`.

---

### `diag02_ABD.log`

#### A2 — `corteescolaunique.dta` (N=50.058)

`dt_corte`: N não-missing = 50.058. `sum, detail`:

| | valor |
|---|---|
| 1% / 5% / 10% / 25% | 18262 / 18627 / 19358 / 19723 |
| 50% | 20453 |
| 75% / 90% / 95% / 99% | 21184 / 21549 / 21549 / 21549 |
| Menores | 18262; 18262; 18262; 18262 |
| Maiores | 21549; 21549; 21549; 21549 |
| Obs | 50.058 |
| Mean | 20351.68 |
| Std. dev. | 902.346 |
| Variance | 814228.3 |
| Skewness | -.441595 |
| Kurtosis | 2.308209 |

Como data: `min=31dec2009 max=31dec2018`.

`dt_corte_escola`: N não-missing = 50.058. `sum, detail`:

| | valor |
|---|---|
| 1% / 5% / 10% / 25% | 17990 / 18498 / 18983 / 19647 |
| 50% | 20417 |
| 75% / 90% / 95% / 99% | 21108 / 21486 / 21523 / 21530 |
| Menores | 16834; 16881; 16883; 16891 |
| Maiores | 21531; 21531; 21531; 21531 |
| Obs | 50.058 |
| Mean | 20266.91 |
| Std. dev. | 931.2978 |
| Variance | 867315.7 |
| Skewness | -.5232576 |
| Kurtosis | 2.51973 |

Como data: `min=02feb2006 max=13dec2018`.

**`fila1018.dta` (N=86.046)** — `tab tipo_prioridade_encaminhamento, miss`:

| valor | Freq. | Percent | Cum. |
|---|---|---|---|
| 1 | 1.707 | 1.98 | 1.98 |
| 3 | 4 | 0.00 | 1.99 |
| 6 | 3 | 0.00 | 1.99 |
| . | 84.332 | 98.01 | 100.00 |
| **Total** | **86.046** | 100.00 | |

#### A3 — `corteescolaunique.dta`: 1 linha por escola-ano-série?

`duplicates report an_letivo_encaminhamento serie_aluno cd_esc_encaminhamento`: Copies 1 → Observations 50058, Surplus 0.

`tab serie_aluno an_letivo_encaminhamento`:

| serie_aluno | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 320 | 169 | 196 | 974 | 968 | 1.061 | 1.145 | 1.221 | 1.280 | 1.439 | 8.773 |
| 2 | 396 | 243 | 357 | 1.337 | 1.320 | 1.472 | 1.684 | 1.692 | 1.943 | 2.119 | 12.563 |
| 3 | 0 | 272 | 463 | 1.338 | 1.236 | 1.297 | 1.357 | 1.654 | 1.923 | 1.991 | 11.531 |
| 4 | 0 | 66 | 468 | 1.277 | 1.043 | 1.035 | 1.224 | 1.325 | 1.586 | 1.467 | 9.491 |
| 5 | 0 | 218 | 298 | 530 | 481 | 408 | 544 | 545 | 545 | 321 | 3.890 |
| 6 | 0 | 144 | 253 | 474 | 314 | 285 | 445 | 362 | 259 | 202 | 2.738 |
| 7 | 176 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 176 |
| 8 | 317 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 317 |
| 9 | 278 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 278 |
| 10 | 267 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 267 |
| **Total** | 1.754 | 1.112 | 2.035 | 5.930 | 5.362 | 5.558 | 6.399 | 6.799 | 7.536 | 7.539 | **50.024** |

#### B — `b1_2011_audit.dta` (N=991)

- `gen double dt_mat = date(dt_matricula, "DMY hms")` → 28 missing gerados.

**B2 — `tab exp_tratamento, miss`:**

| exp_tratamento | Freq. | Percent | Cum. |
|---|---|---|---|
| 0 | 2 | 0.20 | 0.20 |
| 1 | 6 | 0.61 | 0.81 |
| 2 | 5 | 0.50 | 1.31 |
| 3 | 33 | 3.33 | 4.64 |
| 4 | 48 | 4.84 | 9.49 |
| 5 | 56 | 5.65 | 15.14 |
| 6 | 59 | 5.95 | 21.09 |
| 7 | 72 | 7.27 | 28.36 |
| 8 | 91 | 9.18 | 37.54 |
| 9 | 111 | 11.20 | 48.74 |
| 10 | 154 | 15.54 | 64.28 |
| 11 | 205 | 20.69 | 84.96 |
| 12 | 66 | 6.66 | 91.62 |
| 13 | 80 | 8.07 | 99.70 |
| . | 3 | 0.30 | 100.00 |
| **Total** | **991** | 100.00 | |

**B3 — `exp_tratamento × mat_nm` (dt_matricula não-missing):** totais por linha idênticos a B2; coluna `mat_nm==1` (não-missing): Total `0`=28, `1`=963 (Total 991). Distribuição por linha (mat_nm=0 | mat_nm=1): 0→(1|1); 1→(4|2); 2→(1|4); 3→(3|30); 4→(1|47); 5→(4|52); 6→(1|58); 7→(0|72); 8→(2|89); 9→(1|110); 10→(4|150); 11→(0|205); 12→(2|64); 13→(2|78); .→(2|1).

**`exp_tratamento × an_letivo_matricula`** (colunas 2010/2011/2012/2013/.):

| exp | 2010 | 2011 | 2012 | 2013 | . | Total |
|---|---|---|---|---|---|---|
| 0 | 0 | 0 | 1 | 0 | 1 | 2 |
| 1 | 0 | 2 | 0 | 0 | 4 | 6 |
| 2 | 0 | 3 | 1 | 0 | 1 | 5 |
| 3 | 0 | 30 | 0 | 0 | 3 | 33 |
| 4 | 0 | 46 | 0 | 1 | 1 | 48 |
| 5 | 0 | 52 | 0 | 0 | 4 | 56 |
| 6 | 0 | 58 | 0 | 0 | 1 | 59 |
| 7 | 0 | 72 | 0 | 0 | 0 | 72 |
| 8 | 0 | 89 | 0 | 0 | 2 | 91 |
| 9 | 0 | 110 | 0 | 0 | 1 | 111 |
| 10 | 0 | 150 | 0 | 0 | 4 | 154 |
| 11 | 1 | 204 | 0 | 0 | 0 | 205 |
| 12 | 0 | 64 | 0 | 0 | 2 | 66 |
| 13 | 13 | 65 | 0 | 0 | 2 | 80 |
| . | 0 | 1 | 0 | 0 | 2 | 3 |
| **Total** | 14 | 946 | 2 | 1 | 28 | **991** |

**`exp_tratamento × esc_trat_nm`** (esc_trat não-missing): coluna `0`/`1` por linha: 0→(2|0); 1→(6|0); 2→(5|0); 3→(32|1); 4→(45|3); 5→(52|4); 6→(53|6); 7→(67|5); 8→(84|7); 9→(98|13); 10→(133|21); 11→(176|29); 12→(56|10); 13→(10|70); .→(3|0). Total 822 | 169.

**`exp_tratamento × trat2011ber`** (colunas 0/1/.): 0→(2|0|0); 1→(6|0|0); 2→(5|0|0); 3→(32|1|0); 4→(45|3|0); 5→(52|4|0); 6→(53|6|0); 7→(67|5|0); 8→(84|7|0); 9→(98|13|0); 10→(133|21|0); 11→(176|29|0); 12→(55|10|1); 13→(10|70|0); .→(3|0|0). Total 821 | 169 | 1.

**`exp_tratamento × encaminhado`** (colunas 0/1): 0→(2|0); 1→(0|6); 2→(1|4); 3→(0|33); 4→(0|48); 5→(0|56); 6→(0|59); 7→(0|72); 8→(0|91); 9→(0|111); 10→(0|154); 11→(1|204); 12→(0|66); 13→(15|65); .→(0|3). Total 19 | 972.

**B4 — `encaminhado × esc_trat_nm`:** 0→(7|12)=19; 1→(815|157)=972; Total (822|169)=991.
**`encaminhado × mat_nm`:** 0→(3|16)=19; 1→(25|947)=972; Total (28|963)=991.

**B5 —** `count if mat_nm==1` → 963; `count if anmat_nm==1` → 963.

`tab an_letivo_matricula, miss`: 2010→14 (1.41%); 2011→946 (95.46%); 2012→2 (0.20%); 2013→1 (0.10%); .→28 (2.83%); Total 991.

`tab ano_mat, miss` (ano de dt_matricula): 2010→16 (1.61%); 2011→939 (94.75%); 2012→8 (0.81%); .→28 (2.83%); Total 991.

`sum idade_mat_meses, detail`:

| | valor |
|---|---|
| 1% / 5% / 10% / 25% | 2 / 4 / 5 / 7 |
| 50% | 9 |
| 75% / 90% / 95% / 99% | 11 / 14 / 15 / 18 |
| Menores | 1; 1; 2; 2 |
| Maiores | 22; 23; 25; 25 |
| Obs | 963 |
| Mean | 9.202492 |
| Std. dev. | 3.645621 |
| Variance | 13.29056 |
| Skewness | .5013445 |
| Kurtosis | 3.600493 |

**B6 —** `count if anmat_nm==1` → 963; `count if esc_mat_nm==1` → 963; `count if mat_nm==1` → 963; `count if anmat_nm==0` → 28; `count if esc_mat_nm==0` → 28.

#### D — artefato `rvar==0` (`scalar h = 54.549695`)

`sum prof_mat`:

| Grupo (condição) | Obs | Mean | Std. dev. | Min | Max |
|---|---|---|---|---|---|
| (i) rvar==0 | 18 | .5145634 | 1.297812 | -1.571827 | 2.901977 |
| (ii) tratados 0<rvar<=h | 66 | .0443849 | 1.139783 | -2.500895 | 2.934986 |
| (iii) controles -h<=rvar<0 | 100 | -.0960281 | .9901042 | -2.012608 | 2.915176 |

**D2 —** `rdrobust prof_mat rvar if rvar!=0, c(0) kernel(triangular) bwselect(mserd) vce(cluster escola_rdd)`:
- Aviso: "Mass points detected in the running variable." Sharp RD, local polynomial.
- Cutoff c = 0. Number of obs = 655. BW type = mserd. Kernel = Triangular. VCE = Cluster.
- Left / Right — Number of obs: 529 / 126; Eff. N of obs: 141 / 72; Order est. (p): 1/1; Order bias (q): 2/2; BW est. (h): 68.996 / 68.996; BW bias (b): 107.783 / 107.783; rho (h/b): 0.640 / 0.640; Unique obs: 267 / 82; N of clusters: 77 / 53.
- **RD Effect:** Point Estimate = .28069; z-stat = 0.8687; P>|z| = 0.385; IC 95% = [-.393273, 1.01937].
- Linha `di`: `tau_cl=.28068975 se_rb=.36037408 p_rb=.38502531 h=68.996204 Nl=141 Nr=72`.

Fecho: `=== FIM diag02_ABD ===`.

---

### `diag02_partC.log`

Filtros declarados: `tipo_prioridade_encaminhamento==.`; `serie_aluno==1` (cod 1/2/3); `an_letivo_encaminhamento==2011`; `dt_encaminhamento<=31dec2010`.

**Construção do universo (a partir de `Fila1018.dta`):**
- `N total Fila1018 = 3.298.064`.
- `replace serie_aluno = 1 if inlist(cd_serie_ensino_encaminhamento,1,2,3)` → 416.377 real changes.
- `gen dt_enc = date(...)` → 417.675 missing.
- `keep if tipo_prioridade_encaminhamento==.` → 353.123 deletadas.
- `keep if serie_aluno==1` → 2.574.958 deletadas.
- `keep if an_letivo_encaminhamento==2011` → 364.573 deletadas.
- `keep if !missing(dt_enc) & dt_enc<=mdy(12,31,2010)` → 4.987 deletadas.
- `keep if !missing(cd_esc_encaminhamento) & !missing(dt_sol)` → 0 deletadas.
- **`N linhas no universo = 423`.**
- `codebook cd_aluno_sme, compact`: Obs 423, Unique 423, Mean 4108274, Min [REDACTED: individual identifier], Max [REDACTED: individual identifier].
- Após `collapse`/`by cd_esc_encaminhamento`: `s_max2` → 92 missing; `keep if _n==1` → 254 deletadas. `save school_stats_2011ber.dta` (169 escolas).

**C1 — nº de encaminhados por escola** (`school_stats_2011ber.dta`, N=169 escolas):

`sum nchild, detail`:

| | valor |
|---|---|
| 1% / 5% / 10% / 25% | 1 / 1 / 1 / 1 |
| 50% | 1 |
| 75% / 90% / 95% / 99% | 3 / 5 / 8 / 19 |
| Menores | 1; 1; 1; 1 |
| Maiores | 13; 18; 19; 33 |
| Obs | 169 |
| Mean | 2.502959 |
| Std. dev. | 3.523939 |
| Variance | 12.41815 |
| Skewness | 5.362272 |
| Kurtosis | 39.71724 |

`tabstat nchild`: N=169, Min=1, p25=1, p50=1, p75=3, Max=33, Mean=2.502959, SD=3.523939.
`count`: nchild>=2 → 77; nchild>=5 → 17; nchild>=10 → 5.

**C2 — pares criança-escola com corte_LOO** (`b1_2011_audit.dta`):
- `reshape long` sobre 31 escolas: 991 obs (97 vars) → 30.721 obs (38 vars); j = 1..31.
- `merge m:1 cd_esc_encaminhamento using school_stats_2011ber.dta`: Not matched 27.826 (todos master, mrg==1); Matched 2.895 (mrg==3).
- `replace corte_loo = s_max1 if mrg==3 & s_alu1 != cd_aluno_sme` → 2.877 changes; `replace corte_loo = s_max2 if mrg==3 & s_alu1 == cd_aluno_sme` → 7 changes.
- `count if !missing(cd_esc_encaminhamento)` → 30.690.
- `count if mrg==3` → 2.895.
- `count if !missing(corte_loo)` → 2.884.
- Validação `difcorte = dt_corte_escola - s_max1` (`sum, detail`): Obs 2.895; todos percentis, Menores/Maiores, Mean, Std.dev., Variance = 0; Skewness/Kurtosis = `.`.

**C3 — `rvar_loo` fixando escola mais próxima (k==1)** (`loo_long.dta`):
- `keep if k==1` → 29.730 deletadas.
- `gen rvar_loo = corte_loo - dt_sol` → 900 missing.
- `count if !missing(rvar_loo)` → **91**.

`sum rvar_loo, detail`:

| | valor |
|---|---|
| 1% / 5% / 10% / 25% | -612 / -346 / -289 / -195 |
| 50% | -100 |
| 75% / 90% / 95% / 99% | -19 / 30 / 118 / 189 |
| Menores | -612; -441; -438; -378 |
| Maiores | 126; 189; 189; 189 |
| Obs | 91 |
| Mean | -115.8462 |
| Std. dev. | 139.8659 |
| Variance | 19562.46 |
| Skewness | -.4989114 |
| Kurtosis | 4.154566 |

`tab rvar_loo_int if inrange(...,-10,10), miss`: -7→3 (60%); -2→1 (20%); 5→1 (20%); Total 5.
`count if rvar_loo_int==0 & !missing(rvar_loo)` → **0**.
`gen dt_mat` → 28 missing.

**C4 — primeiro estágio bruto por faixas de `rvar_loo`** (`loo_child.dta`):
`replace faixa` — real changes: faixa1 [-60,-31]→5; faixa2 [-30,-11]→8; faixa3 [-10,-1]→4; faixa4 [0,10]→1; faixa5 [11,30]→3; faixa6 [31,60]→2.

`table faixa, stat(count esc_trat_nm) stat(mean esc_trat_nm)`:

| faixa | N (count) | Mean esc_trat_nm |
|---|---|---|
| [-60,-31] | 5 | 0 |
| [-30,-11] | 8 | .375 |
| [-10,-1] | 4 | .25 |
| [0,10] | 1 | 1 |
| [11,30] | 3 | 1 |
| [31,60] | 2 | 1 |
| Total | 23 | .4347826 |

`table faixa, stat(count mat_nm) stat(mean mat_nm)`:

| faixa | N (count) | Mean mat_nm |
|---|---|---|
| [-60,-31] | 5 | 1 |
| [-30,-11] | 8 | 1 |
| [-10,-1] | 4 | .75 |
| [0,10] | 1 | 1 |
| [11,30] | 3 | 1 |
| [31,60] | 2 | .5 |
| Total | 23 | .9130435 |

**C5 — `rdrobust` primeiro estágio com `rvar_loo`:**
- DEP `esc_trat_nm`: `tau_cl=.65355704 se_rb=.17391455 p_rb=.00035102 h=180.21706 Nl=53 Nr=10`.
- DEP `mat_nm`: `tau_cl=.33335321 se_rb=.28276078 p_rb=.13219111 h=74.219481 Nl=20 Nr=6`.

**C6 — `rddensity rvar_loo, c(0)`:** `T=.35084036 p=.72570811`.

Fecho: `=== FIM diag02_partC ===`.

---

## O que o log NÃO permite recuperar

- **Definições/derivação de variáveis a montante:** `b1_2011_audit.dta` já traz `exp_tratamento`, `esc_trat`, `trat2011ber`, `encaminhado`, `rvar`, `prof_mat` (padronizado), `escola_rdd`, `cd_esc_encaminhamento1-31`, `dt_corte_escola1-31`. Os logs não mostram como essas variáveis foram construídas nem o `.do` de build ("build audit") citado em comentário no `diag02_ABD.do`.
- **`scalar h = 54.549695`** em D é fixado manualmente; o log não mostra de onde veio esse bandwidth.
- **Referência a `dataencaminhamentopico_0607_2.do`** (comentário do `diag02_partC.do`) — o `.do` original replicado não está nos logs; a única diferença declarada ("EXCETO exclusão de escola específica") não é detalhada.
- **`describe` completo não reproduzido aqui campo a campo** para `censo2018.dta` (166 vars), `escolassite.dta`, `escolasPSP2.dta` e `filamatriculasite.dta`; os campos constam de `diag02_descB.log` mas não foram todos transcritos nesta reconstrução.
- **`diag02_scanA.log`:** por causa da repetição do bloco `dt_corte_escola1-31`, esta reconstrução lista os arquivos afetados sem repetir as 31 linhas por arquivo. O erro `escolaspsp3.dta rc=610` (arquivo não abre) aparece registrado, mas o log não diz a causa (rc=610 = "file … not Stata format / version incompatível", não explicitado no log).
- **Discrepância de caminho:** o cabeçalho dos `.log` grava `\_audit\` enquanto os `.do` usam `$aud = ...\02_audit`; o log não esclarece se são o mesmo diretório (possível renomeação/junction) — não é possível confirmar pelos arquivos.
- **Números não presentes:** o log não traz saída de regressão completa para C5/C1/C6 além das linhas `di` com escalares e-class; intervalos de confiança e tabelas RD detalhadas de C5/C6 não foram impressos (só os `e()` selecionados).
- **Nenhum log está truncado ou vazio;** todos abrem e fecham normalmente (com `=== FIM ... ===`).

---

## Fonte primária (arquivos .log)

- `02_audit\diag02_scanA.log`
- `02_audit\diag02_descB.log`
- `02_audit\diag02_ABD.log`
- `02_audit\diag02_partC.log`
