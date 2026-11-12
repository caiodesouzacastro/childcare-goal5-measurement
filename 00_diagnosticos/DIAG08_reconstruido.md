> RECONSTRUÇÃO. Este arquivo foi gerado a partir dos logs em 02_audit\ e não
> é o relatório original, que não foi preservado em .md. Os números vêm dos
> logs; a estrutura e as regras de decisão foram reconstruídas e podem estar
> incompletas. Fonte primária: os arquivos .log listados ao final.

## Arquivos lidos

Todos em `<NE_ROOT>\02_audit\`. (Observação: o cabeçalho `log:` interno de cada .log aponta para uma pasta `_audit\`, e não `02_audit\`.)

| Par | .do (linhas) | .log (linhas) | Abertura → fechamento (log) |
|-----|--------------|---------------|------------------------------|
| diag08_A1 | 48 | 116 | 22 Jul 2026, 14:22:57 → 14:23:51 |
| diag08_panel | 83 | 209 | 22 Jul 2026, 14:27:20 → 14:27:56 |
| diag08_A2A3 | 78 | 184 | 22 Jul 2026, 14:25:28 → 14:26:01 |
| diag08_B | 67 | 259 | 22 Jul 2026, 14:29:01 → 14:30:48 |
| diag08_C | 96 | 288 | 22 Jul 2026, 14:32:04 → 14:32:57 |
| diag08_C4D | 86 | 294 | 22 Jul 2026, 14:34:23 → 14:35:15 |

O que cada .do faz (apenas pelos comandos):

- **diag08_A1.do** — Instala/checa `ftools` e `reghdfe` (via `ssc install`). Depois, para cada arquivo `cpf_fila_*` da pasta Ciro `rais_cpf` (`cpf_fila_07, 081, 092, 101, 102, 11, 12, 13, 14`), confirma existência do `.dta`, faz `use`, imprime N e k (número de variáveis), lista as 10 primeiras variáveis (`unab`/`tokenize`) e roda `cap tab ano`.
- **diag08_panel.do** — Monta um painel RAIS empilhando os `cpf_fila_*` (pasta `rais_cpf`), atribuindo `rais_year` pelo sufixo do nome do arquivo. Grupo 1 (antigo, variável `empem3112`): 07→2007, 081→2008, 092→2009, 101→2010, 102→2010. Grupo 2 (novo, variável `vínculoativo3112`): 11→2011, 12→2012, 13→2013, 14→2014. Cria `emp=(emp_raw==1)`, `respid=group(cpf)`, faz `collapse (max) emp by(cd_aluno_sme respid rais_year ano_nasc mes_nasc)`, salva `panel_rais.dta`. Bloco **A5**: nº de anos de RAIS distintos por criança (`tab`, `sum`). Bloco **A6**: crianças com RAIS antes do nascimento (`rais_year < ano_nasc`), por coorte, e distribuição de `npre`.
- **diag08_A2A3.do** — Bloco **A4**: `ds *ano* *base* *compet* *rais* *ref*` em `cpf_fila_14` e `cpf_fila_11` (pasta `$dsme = <NE_ROOT>\dados_restritos\Dados - SME\Atual (25.06)`) para achar variável de ano de RAIS. Blocos **A2/A3**: compara `cpf_fila_11` vs `cpf_fila_14` para mesma criança-responsável; carrega `cd_aluno_sme cpf vlremunmédianom tempoemprego vínculoativo3112`, empilha (src=11/14), define `respid=group(cpf)`, mantém vínculo principal (maior remun) por (criança,resp,arquivo), `reshape wide`, conta interseção/união a nível de par e de criança, e calcula fração com valores diferentes entre 11 e 14 (`dif_remun`, `dif_tempo`, `dif_vinc`).
- **diag08_B.do** — Painel emprego criança×ano de RAIS a partir de `panel_rais.dta` (`collapse (max) emp`). Cruza com `B_novo.dta` (`ano_nasc mes_nasc`) e `child_expo.dta` (`expo12_1km`), expande para 8 anos (2007–2014), define `rel = rais_year - ano_nasc`, `emp=0` para não observados. **B1**: `emp` médio por ano relativo (todo B_novo). **B2**: idem separando março (`mes_nasc==3`) vs abril (`mes_nasc==4`). **B3**: idem por `expo12_1km==0` vs `>=1`. **B4**: nº de crianças com ≥2 anos pré-nascimento E ≥3 pós, por coorte 2008–2014 (observados no painel `cy`).
- **diag08_C.do** — Universo C: primeiro encaminhamento SEM prioridade, a partir de `Fila1018.dta`. Converte datas, filtra `dt_enc`/escola/CEP não-missing, exclui `tipo_prioridade_encaminhamento` preenchido, fica com 1 registro por criança (menor `dt_enc`). Cria idade na solicitação, `feminino`, `branco`, distância CEP→escola (Haversine) após merges com `escolas_parsed.dta`, `censo2018.dta` e `cepcentroide.dta`; define célula `cell=group(cep ym_sol)` e `ncell`. Salva `c_assign.dta`. **C1**: N pós-exclusão e células ≥2. **C2**: média/SD total/SD within (rmse de `reghdfe absorb(cell)`) de características da escola. **C3**: balanço (`reghdfe dep feminino branco mes_nasc idade_sol, absorb(cell) vce(cluster cep)`) + teste F conjunto. **C5**: nº de células com variação utilizável (range `qt_salas`≥2; variação em `in_bercario`).
- **diag08_C4D.do** — **C4**: irmão já matriculado prediz escola atribuída? Constrói `sib_mat` (1ª matrícula do irmão via `cpf_resp_aluno` e `dt_mat_first` de `child_expo.dta`), merge em `c_assign.dta` (células ≥2), define `irmao_matric = sib_mat < dt_sol`, roda `reghdfe dep irmao_matric, absorb(cell) vce(cluster cep)`. **D1**: subamostra em células com variação de salas ≥2; conta PSP (2017/2018/2019), 1º e 3º ano fundamental (`traj_child.dta`). **D2**: `sum ... , detail` de `qt_salas_existentes` e `in_bercario`. **D3**: `pwcorr` bruta entre `qt_salas_existentes`, `in_bercario` e `proficiencia_mat` (de `psp_2018.dta`).

## Estatísticas e tabelas encontradas (transcritas)

### diag08_A1

Instalação/checagem:
- `ftools JA instalado`
- `reghdfe JA instalado`
- `reghdfe disponivel? rc=0`

Cada `cpf_fila_*` (N = observações, k = variáveis; 10 primeiras variáveis):

| Arquivo | N | k | Primeiras 10 variáveis |
|---------|---|---|------------------------|
| cpf_fila_07 | 409227 | 94 | municipio clascnae95 empem3112 tpvinculo causadesli mesdeslig indalvara tipoadm tiposal ocupacao94 |
| cpf_fila_081 | 289810 | 94 | municipio clascnae95 empem3112 tpvinculo causadesli mesdeslig indalvara tipoadm tiposal ocupacao94 |
| cpf_fila_092 | 311423 | 94 | municipio clascnae95 empem3112 tpvinculo causadesli mesdeslig indalvara tipoadm tiposal ocupacao94 |
| cpf_fila_101 | 256765 | 90 | municipio empem3112 tpvinculo causadesli mesdeslig indalvara tipoadm tiposal grinstrucao genero |
| cpf_fila_102 | 346485 | 90 | municipio empem3112 tpvinculo causadesli mesdeslig indalvara tipoadm tiposal grinstrucao genero |
| cpf_fila_11 | 677823 | 92 | município cnae95classe vínculoativo3112 tipovínculo motivodesligamento mêsdesligamento indvínculoalvará tipoadmissão tiposalário cbo94ocupação |
| cpf_fila_12 | 706676 | 92 | município cnae95classe vínculoativo3112 tipovínculo motivodesligamento mêsdesligamento indvínculoalvará tipoadmissão tiposalário cbo94ocupação |
| cpf_fila_13 | 731684 | 92 | município cnae95classe vínculoativo3112 tipovínculo motivodesligamento mêsdesligamento indvínculoalvará tipoadmissão tiposalário cbo94ocupação |
| cpf_fila_14 | 744703 | 93 | município cnae95classe vínculoativo3112 tipovínculo motivodesligamento mêsdesligamento indvínculoalvará tipoadmissão tiposalário cbo94ocupação |

O `cap tab ano` de cada arquivo não produziu nenhuma saída no log (nem tabela, nem a mensagem `(sem variavel 'ano')`).

### diag08_panel

Empilhamento (Grupo 1: 07→2007, 081→2008, 092→2009, 101→2010, 102→2010; Grupo 2: 11→2011, 12→2012, 13→2013, 14→2014) — cada `use`/`append`/`save` reportado como salvo no tempfile.

- `destring` não aplicado aqui; `compress` → `(0 bytes saved)`.
- **N (crianca x resp x ano_rais) = 3592213** (linhas de `panel_rais.dta`).

**A5 — nº de anos de RAIS distintos por criança** (`duplicates drop`: 0 duplicatas; após ficar com 1 linha/criança foram deletadas 2.779.959 obs):

`tab nc`:

| nc | Freq. | Percent | Cum. |
|----|-------|---------|------|
| 1 | 113,964 | 14.03 | 14.03 |
| 2 | 109,292 | 13.46 | 27.49 |
| 3 | 99,621 | 12.26 | 39.75 |
| 4 | 99,990 | 12.31 | 52.06 |
| 5 | 96,069 | 11.83 | 63.89 |
| 6 | 88,178 | 10.86 | 74.74 |
| 7 | 89,691 | 11.04 | 85.79 |
| 8 | 115,449 | 14.21 | 100.00 |
| **Total** | **812,254** | 100.00 | |

`sum nyr, detail`:
- Obs = 812,254; Mean = 4.422524; Std. dev. = 2.359143; Variance = 5.565556; Skewness = .0721429; Kurtosis = 1.718518
- Percentis: 1%=1, 5%=1, 10%=1, 25%=2, 50%=4, 75%=7, 90%=8, 95%=8, 99%=8; Smallest=1; Largest=8

**A6 — crianças com RAIS antes do nascimento** (`pre = rais_year < ano_nasc`):
- `count if pre==1` → **2,189,447** linhas.

Por coorte (`N(painel)` = crianças da coorte no painel; `com pre-nasc` = com ≥1 ano pré-nascimento):

| Coorte | N(painel) | com pré-nasc |
|--------|-----------|--------------|
| 2008 | 48500 | 23871 |
| 2009 | 56821 | 32452 |
| 2010 | 67423 | 42891 |
| 2011 | 81183 | 60306 |
| 2012 | 88333 | 73956 |
| 2013 | 87657 | 79851 |
| 2014 | 86478 | 84002 |

`tab npc` (npre truncado em 4; 190,861 mudanças ao aplicar `npc=4 if npre>=4`):

| npc | Freq. | Percent | Cum. |
|-----|-------|---------|------|
| 0 | 176,091 | 21.68 | 21.68 |
| 1 | 146,901 | 18.09 | 39.76 |
| 2 | 119,235 | 14.68 | 54.44 |
| 3 | 95,516 | 11.76 | 66.20 |
| 4 | 274,511 | 33.80 | 100.00 |
| **Total** | **812,254** | 100.00 | |

### diag08_A2A3

**A4** — `ds *ano* *base* *compet* *rais* *ref*` em `cpf_fila_14` e `cpf_fila_11`: nenhuma variável listada no log (saída vazia em ambos).

**A2/A3** — preparação:
- `destring vlremunmédianom, ... dpcomma` → "all characters numeric; remun generated as double"
- `destring tempoemprego, ... dpcomma` → "all characters numeric; tempo generated as double"
- `by ... keep if _n==1` → (325,322 observations deleted)
- `reshape wide`: Long 1,097,204 → Wide 705,884; variáveis 6 → 8; j (src) valores 11 e 14; xij: remun→remun11 remun14, tempo→tempo11 tempo14, vinc→vinc11 vinc14

A2 — interseção e união (criança-responsável):
- `count` → 705,884 → **N pares (crianca,resp) totais (uniao) = 705884**
- `count if !missing(remun11) & !missing(remun14)` → 391,320 → **N em AMBOS (interseccao 11 e 14) = 391320**

A nível de criança (`collapse (max) in11 in14 by(cd_aluno_sme)`):
- criancas distintas (uniao) = 705884
- criancas em ambos = 391320
- criancas em cpf_fila_11 = 517522
- criancas em cpf_fila_14 = 579682

**A3** — fração com valores diferentes entre 11 e 14 (`keep if` ambos não-missing → 314,564 deletadas):
- **N pares comparaveis = 391320**

`sum dif_remun dif_tempo dif_vinc`:

| Variable | Obs | Mean | Std. dev. | Min | Max |
|----------|-----|------|-----------|-----|-----|
| dif_remun | 391,320 | .9980374 | .0442577 | 0 | 1 |
| dif_tempo | 391,320 | .994286 | .0753748 | 0 | 1 |
| dif_vinc | 391,320 | .3712844 | .4831489 | 0 | 1 |

% diferentes:
- dif_remun: 0.9980 (N=391320)
- dif_tempo: 0.9943 (N=391320)
- dif_vinc: 0.3713 (N=391320)

### diag08_B

Montagem:
- merge B_novo × child_expo: Matched 1,524,560; Not matched 0
- `expand 8` → (10,671,920 observations created)
- merge com painel `cy` (criança×rais_year): Matched 3,592,138; Not matched 8,604,342 (todos from master)
- `replace emp = 0 if missing(emp)` → (8,604,342 real changes made)

**B1 — emp por ano relativo ao nascimento (todo B_novo, sem RAIS=0)** — `table rel, stat(mean emp) stat(count emp)`:

| rel | Mean | N (não-missing) |
|-----|------|-----------------|
| -5 | .2222932 | 890,846 |
| -4 | .239752 | 1,037,539 |
| -3 | .2535614 | 1,115,864 |
| -2 | .2653275 | 1,124,286 |
| -1 | .2633618 | 1,098,561 |
| 0 | .2202253 | 999,499 |
| 1 | .2030573 | 894,777 |
| 2 | .2208341 | 771,688 |
| 3 | .2230145 | 632,793 |
| 4 | .2191915 | 486,456 |
| 5 | .2144432 | 358,356 |
| 6 | .2098856 | 243,871 |
| **Total** | .2346406 | 9,654,536 |

**B2 — MARCO (mes_nasc==3)**:

| rel | Mean | N |
|-----|------|---|
| -5 | .2277036 | 85,765 |
| -4 | .2460264 | 98,713 |
| -3 | .2596964 | 103,286 |
| -2 | .2701386 | 102,614 |
| -1 | .2567969 | 98,280 |
| 0 | .1921484 | 87,651 |
| 1 | .2127107 | 76,959 |
| 2 | .2225094 | 65,395 |
| 3 | .2242346 | 52,231 |
| 4 | .2220894 | 39,304 |
| 5 | .2122683 | 28,219 |
| 6 | .2075513 | 18,169 |
| **Total** | .2353074 | 856,586 |

**B2 — ABRIL (mes_nasc==4)**:

| rel | Mean | N |
|-----|------|---|
| -5 | .2261672 | 80,666 |
| -4 | .242077 | 93,210 |
| -3 | .2537551 | 98,134 |
| -2 | .2633675 | 98,167 |
| -1 | .2531369 | 95,158 |
| 0 | .192102 | 86,022 |
| 1 | .2063218 | 76,909 |
| 2 | .2203211 | 65,577 |
| 3 | .2211038 | 53,744 |
| 4 | .2195104 | 41,219 |
| 5 | .2167878 | 30,546 |
| 6 | .2075773 | 20,667 |
| **Total** | .2313471 | 840,019 |

**B3 — emp médio por ano relativo, `expo12_1km==0` vs `>=1`** (`table rel, stat(mean emp)`):

| rel | Mean (expo==0) | Mean (expo>=1) |
|-----|----------------|-----------------|
| -5 | .2259366 | .2179658 |
| -4 | .2426611 | .2362661 |
| -3 | .2543857 | .2525838 |
| -2 | .2667753 | .2635317 |
| -1 | .2622675 | .2647191 |
| 0 | .2196196 | .2209789 |
| 1 | .2033935 | .2026157 |
| 2 | .2210246 | .2205718 |
| 3 | .2238163 | .2218712 |
| 4 | .2194127 | .2188641 |
| 5 | .2152774 | .2131708 |
| 6 | .2098026 | .210018 |
| **Total** | .2350909 | .2340635 |

**B4 — N crianças com ≥2 anos pré-nasc E ≥3 pós** (merge `cy` × B_novo: Matched 3,592,138; após 1 linha/criança: 2,779,908 deletadas):

| Coorte | N |
|--------|---|
| 2008 | 0 |
| 2009 | 15599 |
| 2010 | 22990 |
| 2011 | 30652 |
| 2012 | 30900 |
| 2013 | 0 |
| 2014 | 0 |
| **Total (2008–2014)** | **100,141** |

### diag08_C

Construção do universo C:
- `date(dt_encaminhamento,...)` → (417,675 missing values generated)
- `keep if !missing(dt_enc) & ...` → (417,680 observations deleted)
- `keep if missing(tipo_prioridade_encaminhamento)` → (314,091 observations deleted)
- `by cd_aluno_sme: keep if _n==1` → (1,214,140 observations deleted)

Merges:
- escolas_parsed: Matched 1,286,458; Not matched 65,695 (from master)
- censo2018 (codinep): Matched 1,267,747; Not matched 84,406 (from master)
- cepcentroide (cep): Matched 1,346,216; Not matched 5,937 (from master)
- `gen a` / `gen dist_km` → (71,631 missing values generated) cada
- `c_assign.dta` salvo

**C1**:
- **N criancas (1o enc, sem prioridade) = 1352153**
- **N criancas em celulas >=2 = 738810**
- **N celulas (>=2 criancas) = 259165**

**C2 — características da escola atribuída (células ≥2)** (média, SD total, SD within = rmse de `reghdfe absorb(cell)`):

| Variável | media | SD_total | SD_within (rmse) |
|----------|-------|----------|-------------------|
| qt_salas_existentes | 8.638 | 3.951 | 3.368 |
| in_bercario | 0.565 | 0.496 | 0.394 |
| qt_funcionarios | 36.195 | 51.244 | 45.716 |
| dist_km | 2.451 | 13.711 | 3.206 |
| conveniada | 0.459 | 0.498 | 0.432 |

**C3 — balanço** (`reghdfe dep feminino branco mes_nasc idade_sol, absorb(cell) vce(cluster cep)`), coeficientes (se) e F conjunto:

| DEP | b_fem (se) | b_branco (se) | b_mesnasc (se) | b_idadesol (se) | F | p | N |
|-----|------------|---------------|----------------|------------------|---|---|---|
| qt_salas_existentes | 0.0005 (0.0102) | -0.0957 (0.0125) | 0.0007 (0.0015) | -0.0323 (0.0007) | 629.071 | 0.0000 | 672298 |
| in_bercario | 0.0009 (0.0011) | 0.0011 (0.0013) | 0.0001 (0.0002) | -0.0108 (0.0001) | 2754.346 | 0.0000 | 672298 |
| qt_funcionarios | 0.2351 (0.1363) | 0.1377 (0.1628) | -0.0102 (0.0196) | 0.1297 (0.0045) | 211.543 | 0.0000 | 672298 |
| dist_km | -0.0226 (0.0094) | 0.1242 (0.0119) | 0.0037 (0.0014) | 0.0041 (0.0003) | 70.986 | 0.0000 | 689471 |
| conveniada | 0.0007 (0.0012) | -0.0041 (0.0015) | 0.0019 (0.0002) | -0.0075 (0.0001) | 3464.471 | 0.0000 | 738810 |

Graus de liberdade do teste F (do bloco `test`): qt_salas F(4, 26411); in_bercario F(4, 26411); qt_funcionarios F(4, 26411); dist_km F(4, 26444); conveniada F(4, 27195).

**C5 — células com variação utilizável**:
- `sd_salas`/`sd_berc` → (44,421 missing values generated) cada; `mx_salas`/`mn_salas` → (7,581 missing values generated) cada
- células com range qt_salas ≥2: **154,792** (de **259165** células)
- células com variação em in_bercario: **94,835**

### diag08_C4D

**C4 — irmão já matriculado**:
- `keep if !missing(cpf_resp_aluno) & cpf_resp_aluno>0` → (35,987 observations deleted)
- merge child_expo (dt_mat_first): Matched 1,495,127; Not matched 0
- `sibmin1` → (131,896 missing); `sibmin2` → (1,013,586 missing); `sib_mat` → (971,822 missing)
- merge sibmat em c_assign (células ≥2): Matched 730,567; Not matched 8,243 (from master)

`sum irmao_matric`:

| Variable | Obs | Mean | Std. dev. | Min | Max |
|----------|-----|------|-----------|-----|-----|
| irmao_matric | 738,810 | .1567656 | .3635799 | 0 | 1 |

`reghdfe dep irmao_matric, absorb(cell) vce(cluster cep)`:

| DEP | b_irmao (se) | p | N |
|-----|--------------|---|---|
| qt_salas_existentes | 0.1412 (0.0157) | 0.0000 | 672298 |
| in_bercario | 0.0349 (0.0018) | 0.0000 | 672298 |
| conveniada | 0.0161 (0.0019) | 0.0000 | 738810 |
| dist_km | 0.0440 (0.0151) | 0.0036 | 689471 |

**D1 — subamostra com variação de salas ≥2**:
- `mx`/`mn` → (7,581 missing generated) cada; `keep if (mx-mn)>=2 & ...` → (239,524 observations deleted)
- **N criancas em celulas com variacao de salas >=2 = 499286**
- Merges PSP: psp2017 Matched 14,088 (Not matched 485,198); psp2018 Matched 40,846 (Not matched 458,440); psp2019 Matched 52,897 (Not matched 446,389)
- merge traj_child (tem1ano tem3ano): Matched 429,994; Not matched 69,292 (from master)
- com PSP algum ano: **59,423**
- com 1º ano fundamental: **73,557**
- com 3º ano fundamental: **32,772**

**D2 — `sum ... , detail` (subamostra)**:

QT_SALAS_EXISTENTES — Obs 482,631; Mean 8.840298; Std. dev. 4.168015; Variance 17.37235; Skewness 2.004586; Kurtosis 9.519718.
Percentis: 1%=3, 5%=4, 10%=5, 25%=6, 50%=8, 75%=10, 90%=14, 95%=16, 99%=25. Smallest=2; Largest=36.

IN_BERCARIO — Obs 482,631; Mean .5634802; Std. dev. .4959544; Variance .2459708; Skewness -.2559922; Kurtosis 1.065532.
Percentis: 1%=0, 5%=0, 10%=0, 25%=0, 50%=1, 75%=1, 90%=1, 95%=1, 99%=1. Smallest=0; Largest=1.

**D3 — correlação bruta escola × proficiência PSP**:
- destring `proficiencia_mat` (dpcomma, force); merge com psp_2018: Matched 43,502; Not matched 455,784 (from master)

`pwcorr qt_salas_existentes in_bercario proficiencia_mat, sig obs`:

| | qt_salas | in_bercario | profic_mat |
|--|----------|-------------|------------|
| qt_salas_existentes | 1.0000 (N=4.8e+05) | | |
| in_bercario | 0.1923 (p=0.0000; N=4.8e+05) | 1.0000 (N=4.8e+05) | |
| proficiencia_mat | -0.0515 (p=0.0000; N=37423) | -0.1432 (p=0.0000; N=37423) | 1.0000 (N=38430) |

## O que o log NÃO permite recuperar

- **A1 — `tab ano`**: para todos os `cpf_fila_*`, o `cap tab ano` não gerou nenhuma saída (sem tabela e sem a mensagem `(sem variavel 'ano')`). O log não permite dizer se a variável `ano` existe ou o resultado do comando em cada arquivo.
- **A4 (diag08_A2A3) — variável de ano de RAIS**: o `ds *ano* *base* *compet* *rais* *ref*` não listou nenhuma variável em `cpf_fila_14` nem em `cpf_fila_11` (saída vazia). Não é possível recuperar quais variáveis (se alguma) casariam com esses padrões.
- **Duas fontes distintas dos `cpf_fila_*`**: A1 e panel usam a pasta Ciro `rais_cpf` (`$rc`); A2A3 usa `$dsme = <NE_ROOT>\dados_restritos\Dados - SME\Atual (25.06)`. Os N reportados no `reshape` de A2A3 (11: 677.823 no A1) vêm do `$dsme`; o log não confirma se são os mesmos arquivos das outras seções.
- **`pwcorr` — N arredondado**: os pares qt_salas×in_bercario aparecem como `4.8e+05` (notação abreviada do Stata); o N exato desses pares não é impresso (embora `sum` em D2 mostre 482,631 obs).
- **Contagens intermediárias não impressas**: nomes/valores por trás de vários `count`/`egen` (ex.: composição exata dos 71,631 missing de `dist_km` em C, ou dos 8,243 não casados de sibmat) não são detalhados.
- **Objetos referenciados mas não exibidos no conteúdo**: variáveis dos `.dta` além das 10 primeiras (A1), rótulos de valores, e o conteúdo das bases auxiliares (`B_novo.dta`, `child_expo.dta`, `escolas_parsed.dta`, `censo2018.dta`, `cepcentroide.dta`, `traj_child.dta`, `psp*_ids.dta`, `psp_2018.dta`) — apenas resultados de merge/estatísticas aparecem.
- **Caminho do log**: o cabeçalho interno dos `.log` aponta para `...\Neighborhood Effects\_audit\...` (pasta `_audit`), enquanto os arquivos estão em `02_audit\`. Não é possível, só pelo log, saber se houve renomeação da pasta ou apenas `$aud` diferente na execução.
- Nenhum log está vazio ou truncado; todos abrem e fecham corretamente com `=== FIM ... ===`.

---

Fonte primária (arquivos .log): `diag08_A1.log`, `diag08_panel.log`, `diag08_A2A3.log`, `diag08_B.log`, `diag08_C.log`, `diag08_C4D.log` — todos em `<NE_ROOT>\02_audit\`.
