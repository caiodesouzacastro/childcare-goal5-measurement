# DIAG06 — Reconstrução a partir dos logs

> RECONSTRUÇÃO. Este arquivo foi gerado a partir dos logs em 02_audit\ e não
> é o relatório original, que não foi preservado em .md. Os números vêm dos
> logs; a estrutura e as regras de decisão foram reconstruídas e podem estar
> incompletas. Fonte primária: os arquivos .log listados ao final.

---

## Arquivos lidos

Todos em `<NE_ROOT>\02_audit\`. (Observação: o cabeçalho de cada .log grava o caminho `...\Neighborhood Effects\_audit\...`, enquanto o `global aud` nos .do aponta para `...\02_audit`. Transcrito como aparece.)

| Par | .do (linhas) | .log (linhas) | O que o .do faz (a partir dos comandos) |
|---|---|---|---|
| diag06_explore | 41 | 284 | Abre `Fila1018.dta` (1 obs) e lista variáveis (`ds`); depois carrega `cd_serie_ensino_matricula cd_serie_ensino_encaminhamento cd_sexo_aluno tp_raca_cor cpf_resp_aluno` da Fila e faz `tab` (miss) de série de matrícula, sexo, raça; conta `cpf_resp_aluno` não-missing e distintos. Abre `cpf_fila_14.dta` (1 obs) e faz `ds` + `describe, fullnames`. |
| diag06_A12 | 51 | 138 | Usa `B_novo.dta`. **A1**: `tab mes_nasc, miss` e qui-quadrado GOF vs uniforme calculado em loop. **A2**: `merge` com `cep_renda_pop_2010.dta` (renda), cria quartil `rq` via `xtile`, imprime % de nascidos em março/abril por quartil de renda e `tab mes_nasc rq, col nofreq`. |
| diag06_chkmat | 13 | 32 | Abre `matriculas_2018.dta` (1 obs); `di c(k)`; `ds`; tenta `ds *serie* *aluno* *ano* *nasc* *nivel* *etapa* cd_*`. |
| diag06_serie | 15 | 517 | Usa `cd_serie desc_serie cd_etapa_ensino desc_etapa_ensino` de `matriculas_2018.dta`; `tab desc_serie`, `tab desc_etapa_ensino`, `tab cd_serie`. |
| diag06_matri | 46 | 206 | Empilha `matriculas_2010..2018` mantendo séries fundamentais (110,111,112,115–120) e EI (241,242,267,268,270,274); salva `matri_traj.dta`. **A3**: primeira aparição no 1º ano (cd_serie==110) por criança; `tab mes_nasc_aluno an_letivo`; por coorte 2008–2012 `tab an_letivo`; coorte 2011 `tab mes_nasc_aluno an_letivo`. |
| diag06_C | 56 | 308 | Usa `child_expo.dta`; gera `idade_entrada`, `espera_dias`, `mat12`, `anomat`, `mesmat`; merge renda. **C1**: `table anomat` (2010–2018) e `table ym` mensal 2012–2014. **C2**: `table ano_sol`. **C3**: mediana idade por anomat × quartil de renda e × quartil de `estoque_1km`. **C2b/C5**: da Fila, encaminhamentos por ano e `tipo_prioridade_encaminhamento`. |
| diag06_AE | 83 | 258 | Usa `matri_traj.dta`. **A4**: primeira aparição por (criança,série); `tab mes_nasc_aluno an_letivo` para Berçário I (241, coorte 2015) e Infantil I (270, coorte 2011). **A5**: anos de EI por criança; `table mes_nasc_aluno` (coortes 2011 e 2010). **E1/E2/E3**: `tab sit_al_reprov`; collapse por criança (tem1ano, tem3ano, ever_reprov, on-time); salva `traj_child.dta`; contagens por coorte 2008–2012. |
| diag06_B | 104 | 324 | **B1**: `describe` de `cpf_fila_101/102/11/12/13/14`. **B2**: idade do linkado em `cpf_fila_14`, cpf não-missing, cobertura por ano. **B3**: empilha (cd_aluno,cpf) de todos cpf_fila, dedup, casa com `B_novo`, filhos por CPF adulto. **B5**: irmãos via `cpf_resp_aluno` da Fila casado com `child_expo.dta`; distribuição de filhos por responsável, diff de idade de entrada entre irmãos. |
| diag06_A6 | 40 | 176 | Constrói sexo/raça do `Fila1018` (collapse por aluno) e distância ao CEI mais próximo por CEP; casa com `B_novo`, renda e distância; mantém nascidos em março/abril; `tab mes_nasc` e `ttest` de `fem branco renda dist_nearest_cei` por `abril`. |
| diag06_D | 95 | 240 | Da Fila, 1º encaminhamento por criança → `d_assign.dta` (cep, ym_sol, escola atribuída, tipoesc, codinep). **D1**: rank de distância da escola atribuída entre CEIs ≤2km (via `joinby cep_cei_pairs_novo`). **D2**: células CEP×mes_sol com ≥2 crianças, variação de escola. **D4**: SD within-célula de modalidade/infra (merge `censo2018.dta`). |
| diag06_D2 | 80 | 224 | Refaz D1/D2/D4 com abordagem alternativa: rank dentro do CEP via `cep_cei_pairs_novo.dta` (merge m:1 cep esc_atrib); D2 células ≥2 crianças e distribuição de nº escolas; D4 SD within-célula de modalidade/in_bercario/qt_salas. |

---

## Estatísticas e tabelas encontradas (transcritas)

### diag06_explore.log

Variáveis da Fila (`ds` da `Fila1018.dta`, 1 obs — nomes abreviados como no log): `ano cd_aluno_sme dt_solicit~o cd_esc_sol~o an_letivo~ao cd_serie_~ao dt_encamin~o an_letivo~to cd_esc_enc~o cd_serie_~to dt_matricula an_letivo~la cd_esc_mat~a cd_serie_~la dt_desiste~a cd_esc_des~a cd_serie_~ia an_letivo~ia cd_tipo_m~ia an_letivo~sa dt_recusa cd_serie_~sa cd_tipo_m~sa tipo_prior~o cd_sexo_al~o tp_raca_cor mes_nasc ano_nasc cd_pais_mec cep_aluno cpf_resp_a~o`.

**tab cd_serie_ensino_matricula, miss**

| cd_serie_ensino_matricula | Freq. | Percent | Cum. |
|---|---|---|---|
| 1 | 302,909 | 9.18 | 9.18 |
| 3 | 1 | 0.00 | 9.18 |
| 4 | 510,976 | 15.49 | 24.68 |
| 6 | 3 | 0.00 | 24.68 |
| 8 | 3,452 | 0.10 | 24.78 |
| 12 | 1 | 0.00 | 24.78 |
| 14 | 11,329 | 0.34 | 25.13 |
| 15 | 3 | 0.00 | 25.13 |
| 16 | 10,437 | 0.32 | 25.44 |
| 18 | 8,897 | 0.27 | 25.71 |
| 23 | 381,156 | 11.56 | 37.27 |
| 24 | 2 | 0.00 | 37.27 |
| 25 | 172,367 | 5.23 | 42.50 |
| 27 | 437,416 | 13.26 | 55.76 |
| 28 | 288,825 | 8.76 | 64.52 |
| 297 | 747 | 0.02 | 64.54 |
| . | 1,169,543 | 35.46 | 100.00 |
| **Total** | **3,298,064** | 100.00 | |

**tab cd_sexo_aluno, miss**

| cd_sexo_aluno | Freq. | Percent | Cum. |
|---|---|---|---|
| F | 1,611,610 | 48.87 | 48.87 |
| M | 1,686,454 | 51.13 | 100.00 |
| **Total** | **3,298,064** | 100.00 | |

**tab tp_raca_cor, miss**

| tp_raca_cor | Freq. | Percent | Cum. |
|---|---|---|---|
| 1 | 1,049,248 | 31.81 | 31.81 |
| 2 | 91,117 | 2.76 | 34.58 |
| 3 | 829,109 | 25.14 | 59.72 |
| 4 | 11,561 | 0.35 | 60.07 |
| 5 | 6,881 | 0.21 | 60.28 |
| 6 | 1,127,996 | 34.20 | 94.48 |
| 7 | 182,152 | 5.52 | 100.00 |
| **Total** | **3,298,064** | 100.00 | |

- `count if !missing(cpf_resp_aluno) & cpf_resp_aluno>0` = **3,262,077**
- CPF resp distintos = **1,175,700** (após dropar 35,987 missing e 2,086,377 duplicados)

`cpf_fila_14.dta`: **94 variáveis**, 1 obs, data de 1 Jul 2020. `describe, fullnames` lista variáveis da RAIS (município, cnae, vínculo, remuneração, `cpf`, `datadenascimento`, `idade`, `pis`, `nometrabalhador`, etc.) mais as variáveis da Fila anexadas (`cd_aluno_sme`, `dt_solicitacao`, `dt_encaminhamento`, `cd_esc_*`, `cd_serie_ensino_*`, `tipo_prioridade_encaminhamento`, `cd_sexo_aluno`, `tp_raca_cor`, `mes_nasc`, `ano_nasc`, `cep_aluno`, `dup`, `_merge`).

### diag06_A12.log

- `di "N B_novo = " _N` → **N B_novo = 1524560**

**A1 — tab mes_nasc, miss**

| mes_nasc | Freq. | Percent | Cum. |
|---|---|---|---|
| 1 | 125,465 | 8.23 | 8.23 |
| 2 | 121,913 | 8.00 | 16.23 |
| 3 | 138,065 | 9.06 | 25.28 |
| 4 | 134,479 | 8.82 | 34.10 |
| 5 | 138,617 | 9.09 | 43.20 |
| 6 | 129,558 | 8.50 | 51.69 |
| 7 | 130,368 | 8.55 | 60.24 |
| 8 | 126,385 | 8.29 | 68.53 |
| 9 | 125,112 | 8.21 | 76.74 |
| 10 | 119,647 | 7.85 | 84.59 |
| 11 | 113,597 | 7.45 | 92.04 |
| 12 | 121,354 | 7.96 | 100.00 |
| **Total** | **1,524,560** | 100.00 | |

- N (mes 1-12) = 1524560 ; esperado/mes = **127046.6666666667**
- Qui-quadrado(11 df) vs uniforme = **4950.5109**
- p-valor = **0**

**A2 — merge com cep_renda_pop_2010 (renda)**: Not matched 25,004 (todos from master); Matched 1,499,556.

% nascidos em março (3) e abril (4) por quartil de renda:

| Quartil | N | março | abril | razão mar/abr |
|---|---|---|---|---|
| Q1 | 374,987 | 9.03% | 8.84% | 1.022 |
| Q2 | 374,857 | 9.11% | 8.83% | 1.032 |
| Q3 | 374,883 | 9.05% | 8.83% | 1.026 |
| Q4 | 374,829 | 9.02% | 8.79% | 1.027 |

**tab mes_nasc rq, col nofreq** (% coluna; "4 quantiles of renda"):

| mes_nasc | Q1 | Q2 | Q3 | Q4 | Total |
|---|---|---|---|---|---|
| 1 | 8.23 | 8.26 | 8.25 | 8.19 | 8.23 |
| 2 | 7.97 | 8.00 | 7.99 | 8.01 | 7.99 |
| 3 | 9.03 | 9.11 | 9.05 | 9.02 | 9.05 |
| 4 | 8.84 | 8.83 | 8.83 | 8.79 | 8.82 |
| 5 | 9.07 | 9.13 | 9.11 | 9.07 | 9.09 |
| 6 | 8.48 | 8.51 | 8.51 | 8.49 | 8.50 |
| 7 | 8.55 | 8.51 | 8.53 | 8.60 | 8.55 |
| 8 | 8.29 | 8.27 | 8.28 | 8.32 | 8.29 |
| 9 | 8.18 | 8.16 | 8.24 | 8.25 | 8.21 |
| 10 | 7.89 | 7.85 | 7.82 | 7.86 | 7.85 |
| 11 | 7.47 | 7.45 | 7.47 | 7.41 | 7.45 |
| 12 | 8.00 | 7.92 | 7.92 | 7.99 | 7.96 |
| Total | 100.00 | 100.00 | 100.00 | 100.00 | 100.00 |

### diag06_chkmat.log

- `matriculas_2018.dta`: N vars = **95** (`c(k)`).
- `ds` lista variáveis (nomes abreviados): inclui `an_letivo cd_serie desc_serie cd_etapa_e~o desc_etapa~o cd_aluno_sme ano_nasc_a~o mes_nasc_a~o cd_sexo cd_raca_cor` entre outras.
- `ds *serie* *aluno* *ano* *nasc* *nivel* *etapa* cd_*` → erro: **variable *nivel* not found — r(111)**. O do-file encerra com `r(111)` (o `log close` não é executado).

### diag06_serie.log

- `di "N linhas = " _N` → **N linhas = 1756527**

**tab desc_serie** (seleção; transcrição integral no log):

| DESC_SERIE | Freq. | Percent | Cum. |
|---|---|---|---|
| 1A.C.NORMAL | 92 | 0.01 | 0.01 |
| 1A.SER.E.M. | 689 | 0.04 | 0.04 |
| 2A.C.NORMAL | 38 | 0.00 | 0.05 |
| 2A.SER.E.M. | 1,344 | 0.08 | 0.12 |
| 3A.C.NORMAL | 31 | 0.00 | 0.12 |
| 3A.SER E.M | 1,201 | 0.07 | 0.19 |
| 4A.C.NORMAL | 25 | 0.00 | 0.19 |
| ATCOMP | 233,662 | 13.30 | 13.50 |
| BERCARIO I | 49,234 | 2.80 | 16.30 |
| BERCARIO II | 106,033 | 6.04 | 22.34 |
| C.I 1.ANO F9 | 55,287 | 3.15 | 25.48 |
| C.I 2.ANO F9 | 54,281 | 3.09 | 28.57 |
| C.I 3.ANO F9 | 58,866 | 3.35 | 31.93 |
| C.II 4.ANO F9 | 56,428 | 3.21 | 35.14 |
| C.II 5.ANO F9 | 56,446 | 3.21 | 38.35 |
| C.II 6.ANO F9 | 62,098 | 3.54 | 41.89 |
| C.III 7.ANO F9 | 60,960 | 3.47 | 45.36 |
| C.III 8.ANO F9 | 59,260 | 3.37 | 48.73 |
| C.III 9.ANO F9 | 50,478 | 2.87 | 51.60 |
| CMCT | 3,230 | 0.18 | 51.79 |
| CONVEE | 3,296 | 0.19 | 51.98 |
| EDFIS | 12,073 | 0.69 | 52.66 |
| EE PRE | 14 | 0.00 | 52.66 |
| EEC.I Biling | 91 | 0.01 | 52.67 |
| EJA ALF I | 1,159 | 0.07 | 52.74 |
| EJA ALF II | 2,024 | 0.12 | 52.85 |
| EJA BASICA I | 3,587 | 0.20 | 53.06 |
| EJA BASICA II | 5,412 | 0.31 | 53.36 |
| EJA COMPL I | 10,481 | 0.60 | 53.96 |
| EJA COMPL II | 13,560 | 0.77 | 54.73 |
| EJA FINAL I | 20,591 | 1.17 | 55.90 |
| EJA FINAL II | 27,699 | 1.58 | 57.48 |
| EJA MI | 910 | 0.05 | 57.53 |
| EJA MII | 1,152 | 0.07 | 57.60 |
| EJA MIII | 3,595 | 0.20 | 57.80 |
| EJA MIV | 5,964 | 0.34 | 58.14 |
| EJAQUAL | 594 | 0.03 | 58.18 |
| INFANTIL I | 158,852 | 9.04 | 67.22 |
| INFANTIL II | 136,221 | 7.76 | 74.98 |
| MI - ED PROF | 1,616 | 0.09 | 75.07 |
| MI CIEJA | 2,319 | 0.13 | 75.20 |
| MII - ED PROF | 1,409 | 0.08 | 75.28 |
| MII CIEJA | 3,301 | 0.19 | 75.47 |
| MIII - ED PROF | 1,111 | 0.06 | 75.53 |
| MIII CIEJA | 6,551 | 0.37 | 75.90 |
| MINI GRUPO I | 137,973 | 7.85 | 83.76 |
| MINI GRUPO II | 144,528 | 8.23 | 91.99 |
| MIV - ED PROF | 22 | 0.00 | 91.99 |
| MIV CIEJA | 9,549 | 0.54 | 92.53 |
| MOVA | 14,884 | 0.85 | 93.38 |
| OIE | 2,237 | 0.13 | 93.51 |
| OSL | 2,982 | 0.17 | 93.68 |
| RECCIE | 206 | 0.01 | 93.69 |
| RECHISGEO | 216 | 0.01 | 93.70 |
| RECING | 276 | 0.02 | 93.72 |
| RECMAT | 35,827 | 2.04 | 95.76 |
| RECPOR | 63,340 | 3.61 | 99.36 |
| SAAI DA | 626 | 0.04 | 99.40 |
| SAAI DF | 247 | 0.01 | 99.41 |
| SAAI DI | 10,230 | 0.58 | 99.99 |
| SAAI DV | 119 | 0.01 | 100.00 |
| **Total** | **1,756,527** | 100.00 | |

**tab desc_etapa_ensino**

| DESC_ETAPA_ENSINO | Freq. | Percent | Cum. |
|---|---|---|---|
| EDUCACAO INFANTIL | 732,855 | 53.40 | 53.40 |
| EJA CIEJA | 21,720 | 1.58 | 54.98 |
| EJA ESCOLAS EDUCACAO ESPECIAL | 46 | 0.00 | 54.98 |
| EJA ESCOLAS ENSINO FUNDAMENTAL | 96,088 | 7.00 | 61.98 |
| ENSINO FUNDAMENTAL 9 ANOS | 829 | 0.06 | 62.04 |
| ENSINO FUNDAMENTAL DE 9 ANOS | 513,366 | 37.40 | 99.45 |
| ENSINO MEDIO | 3,234 | 0.24 | 99.68 |
| ENSINO MEDIO NORMAL/MAGISTERIO | 186 | 0.01 | 99.70 |
| TECNICO MEDIO | 4,158 | 0.30 | 100.00 |
| **Total** | **1,372,482** | 100.00 | |

**tab cd_serie**: tabela completa com muitos códigos (1,756,527 total). Códigos de interesse do pipeline (fundamental e EI):

| cd_serie | Freq. | Percent |
|---|---|---|
| 110 | 55,245 | 3.15 |
| 111 | 54,248 | 3.09 |
| 112 | 58,800 | 3.35 |
| 115 | 62,005 | 3.53 |
| 116 | 56,376 | 3.21 |
| 117 | 56,389 | 3.21 |
| 118 | 60,858 | 3.46 |
| 119 | 59,134 | 3.37 |
| 120 | 50,311 | 2.86 |
| 241 | 49,162 | 2.80 |
| 242 | 105,915 | 6.03 |
| 267 | 137,834 | 7.85 |
| 268 | 141,919 | 8.08 |
| 270 | 145,806 | 8.30 |
| 274 | 128,590 | 7.32 |

(A tabela completa no log lista dezenas de outros códigos — 198, 269, 271, 273, 275–291, 351–1020, 20001–20345 — cada um com freq/percent/cum; ver `diag06_serie.log` linhas 105–511.)

### diag06_matri.log

Construção de `matri_traj.dta` — observações deletadas por ano (mantendo apenas séries alvo):

| Ano | Obs deletadas |
|---|---|
| 2010 | 1,616,837 |
| 2011 | 1,159,860 |
| 2012 | 1,310,565 |
| 2013 | 1,258,273 |
| 2014 | 459,630 |
| 2015 | 533,260 |
| 2016 | 550,976 |
| 2017 | 581,612 |
| 2018 | 533,935 |

- N linhas trajetoria = **7613706**; `compress` → (0 bytes saved).

**A3** — após `keep if cd_serie==110` (7,046,620 deletadas) e primeira aparição por criança (49,629 deletadas):
- N crianças distintas com 1º ano observado = **517457**

**tab mes_nasc_aluno an_letivo** (freq; entrada no 1º ano):

| mes | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | Total |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6,254 | 4,758 | 4,639 | 5,052 | 4,744 | 4,913 | 5,031 | 5,078 | 4,322 | 44,791 |
| 2 | 4,381 | 4,927 | 4,452 | 4,821 | 4,836 | 4,860 | 4,876 | 4,947 | 4,323 | 42,423 |
| 3 | 5,317 | 6,181 | 5,466 | 5,414 | 5,400 | 5,514 | 5,573 | 5,582 | 4,883 | 49,330 |
| 4 | 5,254 | 4,870 | 4,888 | 4,982 | 4,736 | 4,777 | 4,776 | 4,612 | 4,198 | 43,093 |
| 5 | 5,228 | 4,945 | 5,211 | 5,188 | 5,011 | 5,002 | 4,691 | 4,735 | 4,313 | 44,324 |
| 6 | 5,172 | 4,840 | 4,795 | 4,787 | 4,709 | 4,654 | 4,524 | 4,610 | 4,011 | 42,102 |
| 7 | 5,045 | 4,814 | 4,903 | 4,971 | 4,911 | 4,885 | 4,767 | 4,846 | 4,289 | 43,431 |
| 8 | 4,938 | 4,884 | 4,832 | 4,789 | 4,721 | 4,865 | 4,927 | 4,523 | 4,176 | 42,655 |
| 9 | 5,067 | 4,820 | 4,825 | 5,025 | 4,645 | 4,841 | 5,156 | 4,697 | 3,929 | 43,005 |
| 10 | 4,916 | 4,669 | 4,687 | 4,780 | 4,598 | 4,649 | 4,841 | 4,548 | 3,832 | 41,520 |
| 11 | 4,644 | 4,549 | 4,534 | 4,411 | 4,350 | 4,272 | 4,459 | 4,372 | 3,687 | 39,278 |
| 12 | 4,896 | 4,558 | 4,534 | 4,732 | 4,641 | 4,824 | 4,609 | 4,702 | 4,009 | 41,505 |
| **Total** | 61,112 | 58,815 | 57,766 | 58,952 | 57,302 | 58,056 | 58,230 | 57,252 | 49,972 | **517,457** |

Por coorte de nascimento (`tab an_letivo`):

- **coorte 2008** (Total 57,432): 2010=2 (0.00%); 2012=1; 2013=2; 2014=14,721 (25.63%); 2015=42,279 (73.62%); 2016=344 (0.60%); 2017=59 (0.10%); 2018=24 (0.04%).
- **coorte 2009** (Total 57,944): 2013=1; 2014=5 (0.01%); 2015=15,209 (26.25%); 2016=42,366 (73.12%); 2017=310 (0.53%); 2018=53 (0.09%).
- **coorte 2010** (Total 57,015): 2010=2; 2013=1; 2016=15,373 (26.96%); 2017=41,318 (72.47%); 2018=321 (0.56%).
- **coorte 2011** (Total 51,634): 2016=1; 2017=15,524 (30.07%); 2018=36,109 (69.93%).
- **coorte 2012** (Total 13,413): 2018=13,413 (100.00%).

**Coorte 2011 — tab mes_nasc_aluno an_letivo**:

| mes | 2016 | 2017 | 2018 | Total |
|---|---|---|---|---|
| 1 | 0 | 5,028 | 60 | 5,088 |
| 2 | 1 | 4,882 | 52 | 4,935 |
| 3 | 0 | 5,499 | 74 | 5,573 |
| 4 | 0 | 41 | 4,123 | 4,164 |
| 5 | 0 | 40 | 4,236 | 4,276 |
| 6 | 0 | 29 | 3,936 | 3,965 |
| 7 | 0 | 3 | 4,231 | 4,234 |
| 8 | 0 | 0 | 4,142 | 4,142 |
| 9 | 0 | 1 | 3,874 | 3,875 |
| 10 | 0 | 0 | 3,784 | 3,784 |
| 11 | 0 | 0 | 3,647 | 3,647 |
| 12 | 0 | 1 | 3,950 | 3,951 |
| **Total** | 1 | 15,524 | 36,109 | 51,634 |

### diag06_C.log

Preparo (de `child_expo.dta`): `idade_entrada` → 203,715 missing; `replace ... if !inrange(0,72)` → 5,966 changes to missing; `espera_dias` → 203,715 missing; `anomat`/`mesmat` → 203,715 missing. Merge renda: Not matched 25,004 (master); Matched 1,499,556.

**C1 — table anomat (2010–2018)**: idade de entrada (meses)

| anomat | N (não-missing) | Mean | p50 |
|---|---|---|---|
| 2010 | 53,094 | 39.28352 | 42 |
| 2011 | 49,322 | 39.72219 | 37 |
| 2012 | 162,853 | 34.69192 | 34 |
| 2013 | 165,025 | 33.53439 | 32 |
| 2014 | 170,572 | 29.84398 | 27 |
| 2015 | 156,759 | 27.81142 | 24 |
| 2016 | 187,744 | 27.57619 | 23 |
| 2017 | 105,034 | 30.92276 | 28 |
| 2018 | 211,106 | 23.26718 | 20 |
| **Total** | 1,261,509 | 30.13524 | 27 |

**C1 mensal — table ym (2012–2014)**: p50 idade / N (`ym` em formato %tm, valores numéricos internos 624–659):

| ym | p50 | N |
|---|---|---|
| 624 | 51 | 9,184 |
| 625 | 42 | 15,568 |
| 626 | 41 | 13,761 |
| 627 | 40 | 8,432 |
| 628 | 42 | 7,386 |
| 629 | 42 | 5,929 |
| 630 | 42 | 5,560 |
| 631 | 45 | 6,987 |
| 632 | 40 | 3,539 |
| 633 | 39 | 4,807 |
| 634 | 37 | 3,476 |
| 635 | 26 | 78,224 |
| 636 | 45 | 20,708 |
| 637 | 37 | 24,096 |
| 638 | 40 | 15,057 |
| 639 | 39 | 10,026 |
| 640 | 40 | 8,545 |
| 641 | 39 | 4,329 |
| 642 | 41 | 3,847 |
| 643 | 42 | 5,380 |
| 644 | 42 | 3,889 |
| 645 | 41 | 2,773 |
| 646 | 41 | 2,245 |
| 647 | 22 | 64,130 |
| 648 | 37 | 26,896 |
| 649 | 33 | 22,147 |
| 650 | 36 | 12,740 |
| 651 | 36 | 7,541 |
| 652 | 35 | 6,119 |
| 653 | 35 | 3,460 |
| 654 | 39 | 4,783 |
| 655 | 38 | 4,392 |
| 656 | 36 | 4,606 |
| 657 | 36 | 3,594 |
| 658 | 34 | 2,631 |
| 659 | 18 | 71,663 |

**C2 — table ano_sol (2010–2018)**: N, p50 espera_dias, mean mat12

| ano_sol | N (cd_aluno_sme) | p50 espera_dias | Mean mat12 |
|---|---|---|---|
| 2010 | 81,004 | 93 | .5222458 |
| 2011 | 124,240 | 384 | .37632 |
| 2012 | 220,922 | 217 | .6134156 |
| 2013 | 191,149 | 243 | .6155355 |
| 2014 | 174,676 | 251 | .6303385 |
| 2015 | 179,869 | 206 | .713497 |
| 2016 | 172,341 | 199 | .6974313 |
| 2017 | 163,922 | 192 | .7989227 |
| 2018 | 165,331 | 113 | .8074045 |
| **Total** | 1,473,454 | 201 | .6551416 |

**C3 — mediana idade por anomat × quartil de RENDA**:

| anomat | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| 2010 | 41 | 42 | 42 | 43 |
| 2011 | 36 | 37 | 37 | 38 |
| 2012 | 34 | 34 | 34 | 33 |
| 2013 | 32 | 32 | 32 | 32 |
| 2014 | 27 | 27 | 27 | 26 |
| 2015 | 23 | 25 | 24 | 23 |
| 2016 | 24 | 24 | 23 | 23 |
| 2017 | 28 | 28 | 29 | 29 |
| 2018 | 19 | 20 | 20 | 20 |

**C3 — mediana idade por anomat × quartil de ESTOQUE_1km**:

| anomat | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| 2010 | 44 | 41 | 35 | 28 |
| 2011 | 38 | 38 | 36 | 32 |
| 2012 | 36 | 34 | 33 | 29 |
| 2013 | 34 | 33 | 32 | 27 |
| 2014 | 30 | 28 | 26 | 21 |
| 2015 | 27 | 26 | 23 | 19 |
| 2016 | 27 | 25 | 23 | 20 |
| 2017 | 32 | 30 | 29 | 25 |
| 2018 | 23 | 22 | 20 | 18 |

**C2b/C5 — encaminhamentos por ano** (`dt_enc` → 417,675 missing na conversão de data).

**tab an_letivo_encaminhamento (2010–2018)**:

| ano | Freq. | Percent | Cum. |
|---|---|---|---|
| 2010 | 62,546 | 2.27 | 2.27 |
| 2011 | 56,733 | 2.05 | 4.32 |
| 2012 | 110,205 | 3.99 | 8.31 |
| 2013 | 341,031 | 12.35 | 20.66 |
| 2014 | 342,376 | 12.40 | 33.06 |
| 2015 | 366,932 | 13.29 | 46.35 |
| 2016 | 465,536 | 16.86 | 63.21 |
| 2017 | 418,809 | 15.17 | 78.37 |
| 2018 | 597,188 | 21.63 | 100.00 |
| **Total** | 2,761,356 | 100.00 | |

**table an_letivo_encaminhamento — count dt_enc / mean prior**:

| ano | N (dt_enc) | Mean prior |
|---|---|---|
| 2010 | 62,546 | .0233268 |
| 2011 | 56,733 | .0494421 |
| 2012 | 110,205 | .0564584 |
| 2013 | 341,031 | .0524087 |
| 2014 | 342,376 | .1141494 |
| 2015 | 366,932 | .1259143 |
| 2016 | 465,536 | .1546755 |
| 2017 | 418,809 | .1421101 |
| 2018 | 597,188 | .0926074 |
| **Total** | 2,761,356 | .1088128 |

**tab an_letivo_encaminhamento tipo_prioridade_encaminhamento, row** (freq / % linha; só encaminhados com prioridade não-missing):

| ano | 1 | 3 | 4 | 5 | 6 | Total |
|---|---|---|---|---|---|---|
| 2010 | 1,459 (100.00) | 0 | 0 | 0 | 0 | 1,459 |
| 2011 | 2,805 (100.00) | 0 | 0 | 0 | 0 | 2,805 |
| 2012 | 6,180 (99.32) | 40 (0.64) | 2 (0.03) | 0 | 0 | 6,222 |
| 2013 | 17,238 (96.45) | 573 (3.21) | 62 (0.35) | 0 | 0 | 17,873 |
| 2014 | 20,616 (52.75) | 708 (1.81) | 18 (0.05) | 17,740 (45.39) | 0 | 39,082 |
| 2015 | 22,590 (48.89) | 751 (1.63) | 9 (0.02) | 17,874 (38.69) | 4,978 (10.77) | 46,202 |
| 2016 | 22,808 (31.67) | 454 (0.63) | 0 | 3,482 (4.84) | 45,263 (62.86) | 72,007 |
| 2017 | 29,044 (48.80) | 477 (0.80) | 0 | 14,376 (24.15) | 15,620 (26.24) | 59,517 |
| 2018 | 16,614 (30.04) | 320 (0.58) | 0 | 19,347 (34.98) | 19,023 (34.40) | 55,304 |
| **Total** | 139,354 (46.38) | 3,323 (1.11) | 91 (0.03) | 72,819 (24.23) | 84,884 (28.25) | 300,471 |

### diag06_AE.log

**A4 — Berçário I (241), coorte 2015** (após primeira aparição por criança×série; 730,853 obs deletadas). `tab mes_nasc_aluno an_letivo if cd_serie==241 & ano_nasc_aluno==2015`:

| mes | 2015 | 2016 | 2017 | Total |
|---|---|---|---|---|
| 1 | 620 | 2 | 0 | 622 |
| 2 | 381 | 0 | 0 | 381 |
| 3 | 255 | 1 | 0 | 256 |
| 4 | 173 | 5,432 | 1 | 5,606 |
| 5 | 102 | 5,207 | 2 | 5,311 |
| 6 | 41 | 4,465 | 0 | 4,506 |
| 7 | 17 | 4,007 | 0 | 4,024 |
| 8 | 7 | 3,369 | 0 | 3,376 |
| 9 | 3 | 2,796 | 2 | 2,801 |
| 10 | 1 | 2,070 | 0 | 2,071 |
| 11 | 0 | 1,620 | 0 | 1,620 |
| 12 | 0 | 1,214 | 1 | 1,215 |
| **Total** | 1,600 | 30,183 | 6 | 31,789 |

**A4 — Infantil I (270), coorte 2011**. `tab mes_nasc_aluno an_letivo if cd_serie==270 & ano_nasc_aluno==2011`:

| mes | 2012 | 2014 | 2015 | 2016 | 2017 | Total |
|---|---|---|---|---|---|---|
| 1 | 0 | 1 | 8,528 | 61 | 0 | 8,590 |
| 2 | 0 | 0 | 8,130 | 41 | 0 | 8,171 |
| 3 | 0 | 0 | 9,370 | 74 | 0 | 9,444 |
| 4 | 0 | 0 | 13 | 9,058 | 4 | 9,075 |
| 5 | 1 | 1 | 8 | 9,529 | 1 | 9,540 |
| 6 | 0 | 0 | 4 | 8,884 | 4 | 8,892 |
| 7 | 0 | 0 | 8 | 9,029 | 4 | 9,041 |
| 8 | 0 | 0 | 7 | 8,881 | 2 | 8,890 |
| 9 | 0 | 0 | 3 | 8,221 | 7 | 8,231 |
| 10 | 0 | 0 | 2 | 7,988 | 6 | 7,996 |
| 11 | 0 | 0 | 6 | 7,809 | 1 | 7,816 |
| 12 | 0 | 0 | 2 | 8,542 | 5 | 8,549 |
| **Total** | 1 | 2 | 26,081 | 78,117 | 34 | 104,235 |

**A5 — anos de EI por mês de nascimento** (após: keep is_ei → 3,104,458 deletadas; dedup criança×ano → 439,430 deletadas; dedup criança → 2,462,753 deletadas).

Coorte 2011 — `table mes_nasc_aluno` (count / mean / p50 de `n_ei_anos`):

| mes | N | Mean | p50 |
|---|---|---|---|
| 1 | 11,849 | 3.066925 | 3 |
| 2 | 11,345 | 3.014191 | 3 |
| 3 | 12,987 | 2.984446 | 3 |
| 4 | 12,199 | 3.584064 | 4 |
| 5 | 12,785 | 3.52937 | 4 |
| 6 | 11,926 | 3.473671 | 4 |
| 7 | 12,048 | 3.403718 | 4 |
| 8 | 11,740 | 3.390204 | 3 |
| 9 | 10,894 | 3.287589 | 3 |
| 10 | 10,599 | 3.263232 | 3 |
| 11 | 10,408 | 3.222713 | 3 |
| 12 | 11,217 | 3.161897 | 3 |
| **Total** | 139,997 | 3.284263 | 3 |

Coorte 2010 — `table mes_nasc_aluno` (mean / p50):

| mes | Mean | p50 |
|---|---|---|
| 1 | 3.015287 | 3 |
| 2 | 3.008825 | 3 |
| 3 | 2.935936 | 3 |
| 4 | 3.466385 | 4 |
| 5 | 3.470163 | 4 |
| 6 | 3.404957 | 4 |
| 7 | 3.340498 | 3 |
| 8 | 3.316074 | 3 |
| 9 | 3.242185 | 3 |
| 10 | 3.159779 | 3 |
| 11 | 3.124284 | 3 |
| 12 | 3.100517 | 3 |
| **Total** | 3.218065 | 3 |

**E1/E2/E3** — `tab sit_al_reprov, miss`:

| sit_al_reprov | Freq. | Percent | Cum. |
|---|---|---|---|
| 0 | 7,519,556 | 98.76 | 98.76 |
| 1 | 94,150 | 1.24 | 100.00 |
| **Total** | 7,613,706 | 100.00 | |

Collapse por criança (`ano110` → 7,046,620 missing; `ontime` → 1,603,222 missing). `save traj_child.dta`.

**E1 — por coorte, N com 1º e 3º ano**:

| coorte | N traj | 1º ano | 3º ano |
|---|---|---|---|
| 2008 | 144,554 | 57,431 | 51,665 |
| 2009 | 143,713 | 57,942 | 50,648 |
| 2010 | 141,281 | 57,018 | 13,690 |
| 2011 | 143,260 | 51,634 | 2 |
| 2012 | 144,321 | 13,413 | 1 |

**E2 — on-time (1º ano) e taxa reprov, por coorte**:

| coorte | on-time (N) | taxa reprov |
|---|---|---|
| 2008 | 0.988 (57,431) | 0.027 |
| 2009 | 0.987 (57,942) | 0.023 |
| 2010 | 0.989 (57,018) | 0.010 |
| 2011 | 0.994 (51,634) | 0.002 |
| 2012 | 0.991 (13,413) | 0.001 |

**E3 — N disponível por desfecho (coortes 2008–2012)**:
- com 1º ano fundamental: **237,438**
- com 3º ano fundamental: **116,006**
- com on-time calculável: **237,438**
- (linha impressa: "(comparar com ~27 mil / ~115 mil da PSP)")

### diag06_B.log

**B1 — `describe` de cpf_fila_*.dta**:

| arquivo | N | k |
|---|---|---|
| cpf_fila_101 | 256,765 | 91 |
| cpf_fila_102 | 346,485 | 91 |
| cpf_fila_11 | 677,823 | 93 |
| cpf_fila_12 | 706,676 | 93 |
| cpf_fila_13 | 731,684 | 93 |
| cpf_fila_14 | 744,703 | 94 |

**B2 — cpf_fila_14**: N linhas = **744703**.

`sum idade, detail` (Idade do linkado):

| | valor |
|---|---|
| 1% / Smallest | 17 / 14 |
| 5% | 19 |
| 10% | 21 |
| 25% | 24 |
| 50% | 29 |
| 75% / Largest | 34 / 92 |
| 90% | 38 / 92 |
| 95% | 41 / 95 |
| 99% | 48 / 99 |
| Obs | 744,703 |
| Mean | 29.19538 |
| Std. dev. | 6.908295 |
| Variance | 47.72454 |
| Skewness | .6610712 |
| Kurtosis | 3.670861 |

- `count if !missing(cpf) & cpf>0` = **744,703**

`tab ano` (cobertura):

| Ano | Freq. | Percent | Cum. |
|---|---|---|---|
| 2010 | 30,746 | 4.13 | 4.13 |
| 2011 | 41,496 | 5.57 | 9.70 |
| 2012 | 82,666 | 11.10 | 20.80 |
| 2013 | 84,233 | 11.31 | 32.11 |
| 2014 | 76,453 | 10.27 | 42.38 |
| 2015 | 75,403 | 10.13 | 52.50 |
| 2016 | 100,604 | 13.51 | 66.01 |
| 2017 | 88,950 | 11.94 | 77.96 |
| 2018 | 164,152 | 22.04 | 100.00 |
| **Total** | 744,703 | 100.00 | |

**B3** — após empilhar todos cpf_fila e `duplicates drop` (2,682,711 deletadas):
- N pares (aluno,cpf) distintos = **781425**
- crianças distintas com RAIS = **781425** (0 duplicados após keep cd_aluno_sme + dedup)

Merge com B_novo (`merge m:1 cd_aluno_sme`): Not matched 743,179 (from master 22 = _merge==1; from using 743,157 = _merge==2); Matched 781,403 (_merge==3).

`keep if !missing(cpf) & cpf>0` → 0 deletadas. `sum nfilhos, detail` (filhos por CPF adulto):

| | valor |
|---|---|
| 1% / Smallest | 1 / 1 |
| 25% | 2 |
| 50% | 4 |
| 75% / Largest | 6 / 72 |
| 90% | 7 / 87 |
| 95% | 9 / 118 |
| 99% | 12 / 349 |
| Obs | 781,425 |
| Mean | 4.433101 |
| Std. dev. | 2.601207 |
| Variance | 6.766279 |
| Skewness | 4.380766 |
| Kurtosis | 409.9451 |

- N adultos distintos = **781425**

**B5 — irmãos via cpf_resp_aluno**: `keep if !missing & >0` → 35,987 deletadas. Merge com `child_expo.dta` (keep match): Not matched 0; Matched **1,495,127**.
- `idade_entrada` → 190,025 missing; `replace ... if !inrange(0,72)` → 5,678 changes to missing.

`tab fc` (nº filhos em B_novo por responsável, top-coded em 5):

| fc | Freq. | Percent | Cum. |
|---|---|---|---|
| 1 | 918,674 | 78.14 | 78.14 |
| 2 | 208,740 | 17.76 | 95.90 |
| 3 | 38,751 | 3.30 | 99.19 |
| 4 | 7,268 | 0.62 | 99.81 |
| 5 | 2,225 | 0.19 | 100.00 |
| **Total** | 1,175,658 | 100.00 | |

- N responsáveis distintos = **1175658**
- crianças de B_novo com ≥1 irmão em B_novo (`count if nfilhos_bnovo>=2`) = **576,453**

Famílias com exatamente 2 filhos (idade válida): `keep if nfilhos_bnovo==2 & !missing(idade_entrada)` → 1,129,053 deletadas; `keep if n2==2` → 38,286 deletadas; dedup → 163,894 restantes.
- N famílias 2-filhos com ambos idade válida = **163894**

`sum diff, detail` (diff idade de entrada entre irmãos, meses):

| | valor |
|---|---|
| 1% / Smallest | 0 / 0 |
| 5% | 0 |
| 10% | 1 / 0 |
| 25% | 5 / 0 |
| 50% | 13 |
| 75% / Largest | 24 / 69 |
| 90% | 37 / 69 |
| 95% | 44 / 69 |
| 99% | 56 / 70 |
| Obs | 163,894 |
| Mean | 16.45443 |
| Std. dev. | 13.75743 |
| Variance | 189.267 |
| Skewness | .9531924 |
| Kurtosis | 3.352073 |

- pares de irmãos com diff idade entrada ≥6 meses (`count if diff>=6`) = **121671**

### diag06_A6.log

Construção: `bysort cep (dist_km): keep if _n==1` → 1,281,883 obs deletadas (dist ao CEI mais próximo). Merges com B_novo: sr → Matched 1,524,560 (Not matched 0); renda → Not matched 25,004 (master), Matched 1,499,556; dn (distância) → Not matched 21,827 (master), Matched 1,502,733. `keep if inlist(mes_nasc,3,4)` → 1,252,016 deletadas.

`tab mes_nasc`:

| mes_nasc | Freq. | Percent | Cum. |
|---|---|---|---|
| 3 | 138,065 | 50.66 | 50.66 |
| 4 | 134,479 | 49.34 | 100.00 |
| **Total** | 272,544 | 100.00 | |

**ttest por `abril` (0=março, 1=abril), variância igual:**

**fem**: Grupo 0: N 138,065, Mean .4883135, SD .4998652; Grupo 1: N 134,479, Mean .4879498, SD .4998566; Combined N 272,544, Mean .488134. diff = .0003637 (SE .0019151), IC95% [-.0033899, .0041173]. t = 0.1899; df = 272,542. Pr(|T|>|t|) = 0.8494.

**branco**: Grupo 0: N 138,065, Mean .3206823, SD .4667405; Grupo 1: N 134,479, Mean .3206077, SD .4667119; Combined Mean .3206455. diff = .0000746 (SE .0017882), IC95% [-.0034302, .0035794]. t = 0.0417; df = 272,542. Pr(|T|>|t|) = 0.9667.

**renda**: Grupo 0: N 135,772, Mean 1211.866, SD 1176.068; Grupo 1: N 132,241, Mean 1211.874, SD 1148.625; Combined N 268,013, Mean 1211.87. diff = -.0082855 (SE 4.491829), IC95% [-8.812148, 8.795577]. t = -0.0018; df = 268,011. Pr(|T|>|t|) = 0.9985.

**dist_nearest_cei**: Grupo 0: N 136,005, Mean .2896969, SD .2078027; Grupo 1: N 132,570, Mean .2893849, SD .2082581; Combined N 268,575, Mean .2895429. diff = .000312 (SE .0008029), IC95% [-.0012616, .0018856]. t = 0.3886; df = 268,573. Pr(|T|>|t|) = 0.6976.

### diag06_D.log

Base 1º encaminhamento: `dt_enc` → 417,675 missing; `keep if !missing(dt_enc)...` → 417,680 deletadas; primeira aparição por criança → 1,422,957 deletadas. Merge `escolas_parsed.dta` (tipoesc, codinep): Not matched 70,924 (master); Matched 1,386,503. `save d_assign.dta`.
- N crianças com encaminhamento = **1457427**

**D1 — rank de distância** (via `joinby cep`): dist_assigned → 18,292,235 missing; rank_assigned → 18,292,235 missing; `replace rank+1` → 34,251,976 changes; dedup → 51,086,784 deletadas.
- crianças com escola atribuída entre CEIs≤2km (`has_assigned==1`) = **894,843**
- crianças com atribuída NÃO nos pares (`has_assigned==0`) = **562,584**

`tab rc` (rank, top-coded em 6):

| rc | Freq. | Percent | Cum. |
|---|---|---|---|
| 1 | 83,342 | 9.31 | 9.31 |
| 2 | 131,941 | 14.74 | 24.06 |
| 3 | 90,673 | 10.13 | 34.19 |
| 4 | 70,529 | 7.88 | 42.07 |
| 5 | 57,985 | 6.48 | 48.55 |
| 6 | 460,373 | 51.45 | 100.00 |
| **Total** | 894,843 | 100.00 | |

**D2 — células CEP×mes_sol com ≥2 crianças**: `keep if ncel>=2` → 634,869 deletadas; dedup célula → 538,543 deletadas.
- N células (≥2 crianças) = **284015**
- células com ≥2 escolas distintas (`variou==1`) = **247,410**
- `sum variou`: Obs 284,015, Mean **.871116**, SD .3350721, Min 0, Max 1.

**D4 — SD within-célula da qualidade** (merge `censo2018.dta`: Not matched 95,083 master; Matched 1,362,344; `keep if ncel>=2` → 634,869 deletadas):
- SD within-célula de modal: média = **2.2782103** (34,243 missing gerados)
- SD within-célula de in_bercario: média = **.26370971** (50,669 missing)
- SD within-célula de qt_salas_existentes: média = **2.4207166** (50,669 missing)
- `sum var_modal`: Obs 284,015, Mean **.5985353**, SD .4901955, Min 0, Max 1.

### diag06_D2.log

- N crianças com encaminhamento = **1457427**

**D1 (abordagem alternativa)** — merge `m:1 cep esc_atrib` com ranks: Not matched 562,584 (from master, mr==1); Matched 894,843 (mr==3).
- `count if mr==3` = **894,843**
- `count if mr==1` = **562,584**

`tab rc` (rank_in_cep, top-coded em 6):

| rc | Freq. | Percent | Cum. |
|---|---|---|---|
| 1 | 162,322 | 18.14 | 18.14 |
| 2 | 103,877 | 11.61 | 29.75 |
| 3 | 78,570 | 8.78 | 38.53 |
| 4 | 62,646 | 7.00 | 45.53 |
| 5 | 53,747 | 6.01 | 51.54 |
| 6 | 433,681 | 48.46 | 100.00 |
| **Total** | 894,843 | 100.00 | |

- % rank==1 entre as com rank definido: rank==1 = 162322 / 894843 = **0.1814**

**D2 — células ≥2 crianças** (`keep if ncel>=2` → 634,869 deletadas; dedup → 538,543 deletadas):
- N células (≥2 crianças) = **284015**
- células com ≥2 escolas distintas = **247410**
- % células com variação de escola = **0.8711**

`tab nc` (nº escolas por célula, top-coded em 5):

| nc | Freq. | Percent | Cum. |
|---|---|---|---|
| 1 | 36,605 | 12.89 | 12.89 |
| 2 | 162,425 | 57.19 | 70.08 |
| 3 | 50,444 | 17.76 | 87.84 |
| 4 | 18,699 | 6.58 | 94.42 |
| 5 | 15,842 | 5.58 | 100.00 |
| **Total** | 284,015 | 100.00 | |

**D4 — SD within-célula** (merge censo2018: Not matched 95,083 master; Matched 1,362,344; `keep if ncel>=2` → 634,869 deletadas):

`sum sd_modal sd_in_bercario sd_qt_salas_existentes`:

| Variável | Obs | Mean | Std. dev. | Min | Max |
|---|---|---|---|---|---|
| sd_modal | 267,993 | 2.15389 | 2.025099 | 0 | 7.071068 |
| sd_in_bercario | 260,657 | .2432052 | .3061635 | 0 | .7071068 |
| sd_qt_salas_existentes | 260,657 | 2.291321 | 2.543106 | 0 | 22.62742 |

- `sum var_modal`: Obs 284,015, Mean **.5985353**, SD .4901955, Min 0, Max 1.

---

## O que o log NÃO permite recuperar

- **diag06_chkmat**: o do-file aborta em `ds *serie* ... *nivel* ...` porque **`*nivel*` não existe** → `r(111)`; o `log close` não roda. Não há saída de `ds *serie* *aluno* ...` (a lista filtrada de variáveis não foi produzida).
- **Caminho divergente**: todos os cabeçalhos de log registram `...\Neighborhood Effects\_audit\...` (com `_audit`), enquanto o `global aud` nos .do é `...\02_audit`. Os arquivos foram lidos de `02_audit`. Não é possível, apenas pelos logs, saber se são dois diretórios distintos ou renomeação.
- **Rótulos de valores não expandidos**: `tp_raca_cor` (1–7), `cd_sexo_aluno` (F/M), `cd_serie_ensino_matricula` (códigos numéricos), `tipo_prioridade_encaminhamento` (categorias 1,3,4,5,6), `sit_al_reprov` (0/1) e os códigos de `cd_serie`/`desc_serie` aparecem sem dicionário completo de significado; os logs não trazem os labels dos valores. Em C2b/C5 o `table` mostra `mean prior` (fração com prioridade não-missing) mas a interpretação de cada código de prioridade não está nos logs.
- **`ym` em formato numérico interno**: em diag06_C a tabela mensal usa os valores numéricos 624–659 (o formato `%tm` aplicado não é convertido para AAAAmM na saída do `table`). O mapeamento exato para mês/ano não é impresso.
- **Variáveis derivadas de bases não lidas aqui**: `estoque_1km` (usado em C3), `dt_mat_first`, `dt_sol`, `ever_mat`, `ano_sol`, `estoque` etc. vêm de `child_expo.dta`/`B_novo.dta`; os logs não mostram como foram construídas. `cep_cei_pairs_novo.dta`, `escolas_parsed.dta`, `censo2018.dta`, `cep_renda_pop_2010.dta` são insumos cuja origem/construção não aparece.
- **B3 merge**: 22 observações "from master" (RAIS sem correspondência em B_novo) são contadas mas não detalhadas.
- **diag06_serie — tab cd_serie**: a lista completa de códigos é muito extensa (linhas 105–511 do log); acima transcrevi apenas os códigos usados no pipeline (fundamental e EI). Os demais (198, 269–1020, 20001–20345) constam no log com freq/percent/cum próprios, não reproduzidos integralmente aqui.
- **Sem regras de decisão explícitas**: os logs contêm apenas cálculos e tabelas; nenhum log imprime critérios de aprovação/reprovação, limiares ou vereditos do diagnóstico. As "regras de decisão" do relatório original (o que cada teste A1–A6, B, C, D, E deveria concluir) não são recuperáveis dos logs.
- **Nenhum log truncado ou vazio** entre os 11 pares lidos; todos abrem e encerram normalmente, exceto `diag06_chkmat` que termina em erro `r(111)` antes do `log close`.
