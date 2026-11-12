> RECONSTRUÇÃO. Este arquivo foi gerado a partir dos logs em 02_audit\ e não
> é o relatório original, que não foi preservado em .md. Os números vêm dos
> logs; a estrutura e as regras de decisão foram reconstruídas e podem estar
> incompletas. Fonte primária: os arquivos .log listados ao final.

## Arquivos lidos

| Arquivo | Linhas | O que o .do faz (pelos comandos) |
|---|---|---|
| `diag05_A.do` | 98 | Abre `escolas_parsed.dta`; define `cei` por `tipoesc` (CEI/CR.P/CEMEI/CCI) e mantém só CEIs. A1: cobertura das 3 datas (`dt_criacao_d`, `dt_ini_func_d`, `dt_ini_conv_d`) por `tipoesc` via `table`. A2: diferenças em dias entre datas com `_pctile` (p10/p50/p90). A3: constrói `dt_abertura` (conv→func→criacao→none), tabula `fonte` e ano, salva `cei_openings_novo.dta`. A4: merge por `codinep` contra `censo2018.dta` e checa fração com `dt_abertura < 01jan2018`. |
| `diag05_A.log` | 271 | Log da execução de `diag05_A.do`. |
| `diag05_Bprep.do` | 75 | Constrói pares CEP-CEI: grade 0.02° 3×3 a partir de `cei_openings_novo.dta`, junta a `cepcentroide.dta`, calcula `dist_km` (Haversine), mantém `<=2km` e salva `cep_cei_pairs_novo.dta`. Constrói `B_novo.dta`: Pass 1 (primeira matrícula por criança do `Fila1018.dta`), Pass 2 (primeira solicitação + covariáveis, filtra nasc+cep válidos, junta matrícula). Tabula por `ano_sol`. |
| `diag05_Bprep.log` | 187 | Log da execução de `diag05_Bprep.do`. |
| `diag05_B.do` | 72 | Abre `B_novo.dta`, `joinby cep` com `cep_cei_pairs_novo.dta`; define janelas relativas a `dt_sol` (expo [sol, sol+365], pre [sol-365, sol], post [sol+366, sol+730], estoque [<=sol]) e raios (0.5/1/2 km); `collapse (sum)` por criança; salva `child_expo_raw.dta` e `child_expo.dta`. Programa `distrib` tabula distribuições 0/1/2/3+. Seções B1–B4. |
| `diag05_B.log` | 252 | Log da execução de `diag05_B.do`. |
| `diag05_C.do` | 82 | Abre `child_expo.dta`; cria desfechos `mat12`, `idade_entrada`, `espera_dias`, `valid`. FE `setoryear` = group(setor, ano_sol). Programa `run1` roda `reg` (spec1) ou `areg` FE setor×ano (spec2). C1/C2 (instr=`expo12_1km`), C3 placebo (`pre12_1km`), C4 placebo (`post_1km`); imprime linhas `RES|`. |
| `diag05_C.log` | 181 | Log da execução de `diag05_C.do`. |
| `diag05_D1D2.do` | 77 | D1: cardinalidade de `setor`/`coddist`/`distrito` em `escolas_parsed.dta` e top-15 setores. D2a: `cep_renda_pop_2010.dta` (distintos `nm_distrit`, `cod_setor`). D2b: atribui CEP→setor pela escola mais próxima (grade 3×3, Haversine), salva `cep_setor.dta`. |
| `diag05_D1D2.log` | 212 | Log da execução de `diag05_D1D2.do`. |
| `diag05_D3.do` | 91 | Painel setor-ano: aberturas de `cei_openings_novo.dta` → setor via `escolas_parsed`; grade setores×anos 2005-2018, `estoque` acumulado, salva `panel_open.dta`. Cohort por setor-ano_sol de `child_expo.dta`, salva `panel_cohort.dta`. D3 junta painel final e descreve colunas. D4/D5: setores com/sem abertura 2010-2016. |
| `diag05_D3.log` | 367 | Log da execução de `diag05_D3.do`. |
| `diag05_E.do` | 89 | Mapa criança→`ano_nasc` (`cid_ano.dta`). E1: ano de nascimento dos que fizeram PSP 2º ano (2018 e 2019). E2: coorte modal × universo `B_novo` × casamento com PSP. E3: expo12 e taxa de matrícula por coorte. |
| `diag05_E.log` | 173 | Log da execução de `diag05_E.do` — **interrompido com erro r(459)** (ver seção final). |
| `diag05_E2.do` | 58 | Deduplica ids PSP 2º ano (`p18_2ano_ids.dta`, `p19_2ano_ids.dta`); merge `1:1` com `child_expo.dta`; E2 conta casamentos por coorte; E3 expo12 e taxa de matrícula por coorte. |
| `diag05_E2.log` | 168 | Log da execução de `diag05_E2.do` (versão corrigida de E). |

## Estatísticas e tabelas encontradas (transcritas)

### diag05_A

Início do log: `opened on: 22 Jul 2026, 11:57:39`.

- `keep if cei==1`: (2,369 observations deleted).
- **N CEI = 2384**

**A1 — cobertura das 3 datas por tipoesc** (`table tnum`):

```
----------------------------------------------
            |  Frequency          Total
            |                 hc    hf      hv
------------+---------------------------------
tnum        |
  CCI/CIPS  |          3       1     3       0
  CEI DIRET |        317     314   317       4
  CEI INDIR |        376     252   149     323
  CEMEI     |         14      14     4       0
  CEU CEI   |         45      45    45       0
  CR.P.CONV |      1,629   1,290   407   1,013
  Total     |      2,384   1,916   925   1,340
----------------------------------------------
```

**A2 — diferenças em dias entre datas (CEIs com ambas)**

- `gen dcf`: (1,678 missing values generated).
- `gen dcv`: (1,507 missing values generated).
- dt_criacao − dt_ini_func: `count if !missing(dcf)` = **706**; p10=-667  p50=-66  p90=3868
- dt_criacao − dt_ini_conv: `count if !missing(dcv)` = **877**; p10=-2038  p50=-9  p90=0

**A3 — dt_abertura**

Mudanças no `replace`: conv 1,013; func 518; criacao 783; none 70.

Fonte da `dt_abertura`:

```
      fonte |      Freq.     Percent        Cum.
------------+-----------------------------------
       conv |      1,013       42.49       42.49
    criacao |        783       32.84       75.34
       func |        518       21.73       97.06
       none |         70        2.94      100.00
------------+-----------------------------------
      Total |      2,384      100.00
```

- N com `dt_abertura` não-missing: `count if !missing(dt_abertura)` = **2,314**

Distribuição por ano (2008-2016):

```
      yr_ab |      Freq.     Percent        Cum.
------------+-----------------------------------
       2008 |         75        5.95        5.95
       2009 |         72        5.71       11.67
       2010 |        133       10.56       22.22
       2011 |         97        7.70       29.92
       2012 |        175       13.89       43.81
       2013 |        114        9.05       52.86
       2014 |        192       15.24       68.10
       2015 |        269       21.35       89.44
       2016 |        133       10.56      100.00
------------+-----------------------------------
      Total |      1,260      100.00
```

- Ao salvar `cei_openings_novo.dta`: `keep if !missing(dt_abertura) & !missing(lat,lon)` (71 obs deleted); **N CEI openings novo (com coord e dt_abertura) = 2313**.

**A4 — sanidade vs censo2018 (codinep)**

- `duplicates drop` no censo: (0 observations are duplicates); `drop if missing(codinep)`: (0 deleted).
- merge `m:1 codinep`:

```
    Not matched                           180
        from master                       180  (mc==1)
        from using                          0  (mc==2)
    Matched                             2,204  (mc==3)
```

- CEIs no censo2018 com `dt_abertura`: **2,134**
- destes, com `dt_abertura < 01jan2018`: **2,062**
- fração: **2062 / 2134 = 0.9663**

`=== FIM diag05_A ===`. Log fechado `22 Jul 2026, 11:57:41`.

### diag05_Bprep

Início: `opened on: 22 Jul 2026, 11:58:56`.

**Pares CEP-CEI (grade 0.02° 3×3)**

- `expand 9`: (18,504 observations created).
- `keep if dist_km <= 2`: (2,390,415 observations deleted).
- **N pares novo (<=2km) = 1326550**

**B_novo — todas crianças com sol+nasc+cep**

- Pass 1 (matrícula): `gen dt_mat` → (1,169,483 missing values generated); `keep if !missing(dt_mat)` → (1,169,483 deleted). **N crianças com alguma matrícula = 1320889**
- Pass 2 (solicitação): `keep if !missing(dt_sol)` → (0 deleted); `by cd_aluno_sme: keep if _n==1` → (1,773,411 deleted). **N crianças com alguma solicitação = 1524653**
- `keep if nasc_ok & cep_ok` → (93 deleted). **N com nasc+cep válidos = 1524560**
- merge `1:1` com matf:

```
    Not matched                       203,715
        from master                   203,715
        from using                          0
    Matched                         1,320,845
```

- `replace ever_mat = 0`: (203,715 real changes made).
- **N B_novo = 1524560**; **nunca matricularam (`ever_mat==0`) = 203,715**

Por ano de solicitação:

```
    ano_sol |      Freq.     Percent        Cum.
------------+-----------------------------------
       2008 |      7,747        0.51        0.51
       2009 |     39,560        2.60        3.11
       2010 |     81,004        5.33        8.44
       2011 |    124,240        8.17       16.61
       2012 |    220,922       14.53       31.13
       2013 |    191,149       12.57       43.70
       2014 |    174,676       11.49       55.19
       2015 |    179,869       11.83       67.02
       2016 |    172,341       11.33       78.35
       2017 |    163,922       10.78       89.13
       2018 |    165,331       10.87      100.00
------------+-----------------------------------
      Total |  1,520,761      100.00
```

`=== FIM Bprep ===`. Log fechado `22 Jul 2026, 11:59:25`.

### diag05_B

Início: `opened on: 22 Jul 2026, 12:00:04`.

- **N B_novo = 1524560**
- `joinby cep`: **N linhas após joinby = 54845925**
- `gen in_expo/in_pre/in_post/in_stk`: cada um (21,827 missing values generated).
- merge `1:1` (child_expo_raw): Not matched 0, Matched 1,524,560.
- `replace ... =0 if missing`: (0 real changes made) para todas 6 variáveis.
- `compress`: 6 variáveis double→byte (64,031,520 bytes saved).

**B1 — expo12 (janela [sol, sol+365])**

`expo12_500` (recodificado 3+; 2,256 real changes):

```
        __c |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |  1,261,454       82.74       82.74
          1 |    215,686       14.15       96.89
          2 |     37,723        2.47       99.36
          3 |      9,697        0.64      100.00
------------+-----------------------------------
      Total |  1,524,560      100.00
```
media expo12_500 = .21184604 ; N >=1 = 263106 (17.26%)

`expo12_1km` (53,587 real changes):

```
        __c |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |    856,293       56.17       56.17
          1 |    384,388       25.21       81.38
          2 |    160,250       10.51       91.89
          3 |    123,629        8.11      100.00
------------+-----------------------------------
      Total |  1,524,560      100.00
```
media expo12_1km = .76808981 ; N >=1 = 668267 (43.83%)

`expo12_2km` (420,814 real changes):

```
        __c |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |    379,354       24.88       24.88
          1 |    315,812       20.71       45.60
          2 |    242,175       15.88       61.48
          3 |    587,219       38.52      100.00
------------+-----------------------------------
      Total |  1,524,560      100.00
```
media expo12_2km = 2.6222097 ; N >=1 = 1145206 (75.12%)

**B2 — pre12 (janela [sol-365, sol]) placebo**

`pre12_1km` (52,880 real changes):

```
        __c |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |    866,060       56.81       56.81
          1 |    380,058       24.93       81.74
          2 |    158,094       10.37       92.11
          3 |    120,348        7.89      100.00
------------+-----------------------------------
      Total |  1,524,560      100.00
```
media pre12_1km = .75577347 ; N >=1 = 658500 (43.19%)

**B3 — post (janela [sol+366, sol+730])**

`post_1km` (44,855 real changes):

```
        __c |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |    925,917       60.73       60.73
          1 |    345,773       22.68       83.41
          2 |    146,078        9.58       93.00
          3 |    106,792        7.00      100.00
------------+-----------------------------------
      Total |  1,524,560      100.00
```
media post_1km = .67929435 ; N >=1 = 598643 (39.27%)

**B4 — estoque (CEIs <=1km abertos na data de solicitação)**

`sum estoque_1km, detail`:

```
                         (sum) stk1
 1%            0        Obs           1,524,560
 5%            1        Sum of wgt.   1,524,560
10%            1        Mean           6.711639
25%            3        Std. dev.      5.363832
50%            5        Variance       28.77069
75%            9        Skewness       1.483419
90%           14        Kurtosis       5.701086
95%           18
99%           25
Smallest: 0,0,0,0    Largest: 38,38,38
```

`ec` (6+ recodificado; 621,342 real changes):

```
         ec |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |     68,800        4.51        4.51
          1 |     98,388        6.45       10.97
          2 |    142,518        9.35       20.31
          3 |    166,091       10.89       31.21
          4 |    163,877       10.75       41.96
          5 |    141,244        9.26       51.22
          6 |    743,642       48.78      100.00
------------+-----------------------------------
      Total |  1,524,560      100.00
```

`=== FIM diag05_B ===`. Log fechado `22 Jul 2026, 12:05:28`.

### diag05_C

Início: `opened on: 22 Jul 2026, 12:12:45`.

- **N = 1524560**
- `gen idade_entrada`: (203,715 missing values generated); `gen espera_dias`: (203,715 missing).

`tab mat12`:

```
      mat12 |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |    541,871       35.54       35.54
          1 |    982,689       64.46      100.00
------------+-----------------------------------
      Total |  1,524,560      100.00
```

- `count if valid==1` (idade_entrada 0..72) = **1,314,879**
- `codebook setor`: Obs 1524560, Unique **729**, Mean 508.6476, Min 0, Max 9999.

**C1 (spec1) e C2 (spec2, FE setor×ano) — resultados `RES|`**

Instrumento = `expo12_1km`:

| dep | instr | spec | coef | se | t | N | r2 | F |
|---|---|---|---|---|---|---|---|---|
| mat12 | expo12_1km | spec1 | 0.01836 | 0.00034 | 53.91 | 1524560 | 0.0853 | 2906.32 |
| mat12 | expo12_1km | spec2 | 0.00904 | 0.00043 | 21.00 | 1524560 | 0.1861 | 441.02 |
| idade_entrada | expo12_1km | spec1 | -0.11199 | 0.01340 | -8.36 | 1314879 | 0.1018 | 69.87 |
| idade_entrada | expo12_1km | spec2 | -0.04386 | 0.01767 | -2.48 | 1314879 | 0.1336 | 6.16 |
| espera_dias | expo12_1km | spec1 | -6.38533 | 0.18450 | -34.61 | 1314879 | 0.0794 | 1197.73 |
| espera_dias | expo12_1km | spec2 | -1.01451 | 0.22793 | -4.45 | 1314879 | 0.2207 | 19.81 |

**C3 — PLACEBO 1 = pre12_1km**

| dep | instr | spec | coef | se | t | N | r2 | F |
|---|---|---|---|---|---|---|---|---|
| mat12 | pre12_1km | spec1 | 0.01638 | 0.00038 | 43.15 | 1524560 | 0.0847 | 1861.91 |
| mat12 | pre12_1km | spec2 | 0.00119 | 0.00048 | 2.49 | 1524560 | 0.1859 | 6.20 |
| idade_entrada | pre12_1km | spec1 | -0.08424 | 0.01492 | -5.64 | 1314879 | 0.1018 | 31.86 |
| idade_entrada | pre12_1km | spec2 | 0.03452 | 0.01958 | 1.76 | 1314879 | 0.1336 | 3.11 |
| espera_dias | pre12_1km | spec1 | -11.06174 | 0.20539 | -53.86 | 1314879 | 0.0806 | 2900.69 |
| espera_dias | pre12_1km | spec2 | -3.06110 | 0.25257 | -12.12 | 1314879 | 0.2207 | 146.89 |

**C4 — PLACEBO 2 = post_1km**

| dep | instr | spec | coef | se | t | N | r2 | F |
|---|---|---|---|---|---|---|---|---|
| mat12 | post_1km | spec1 | -0.00678 | 0.00036 | -18.75 | 1524560 | 0.0838 | 351.42 |
| mat12 | post_1km | spec2 | -0.00435 | 0.00046 | -9.49 | 1524560 | 0.1859 | 90.15 |
| idade_entrada | post_1km | spec1 | 0.20665 | 0.01427 | 14.48 | 1314879 | 0.1019 | 209.68 |
| idade_entrada | post_1km | spec2 | 0.07773 | 0.01882 | 4.13 | 1314879 | 0.1336 | 17.06 |
| espera_dias | post_1km | spec1 | 3.36999 | 0.19660 | 17.14 | 1314879 | 0.0788 | 293.83 |
| espera_dias | post_1km | spec2 | 1.48616 | 0.24275 | 6.12 | 1314879 | 0.2207 | 37.48 |

C5 sem números novos (aponta para as linhas `RES spec2` acima).

`=== FIM diag05_C ===`. Log fechado `22 Jul 2026, 12:15:54`.

### diag05_D1D2

Início: `opened on: 22 Jul 2026, 12:17:47`.

**D1 — setor / coddist / distrito em escolassite**

- **N escolas = 4753**
- `codebook setor`: Obs 4753, Unique **455**, Mean 4724.011, Min 0, Max 9608.
- `codebook coddist`: Obs 4753, Unique **97**, Mean 47.20345, Min 0, Max 96.
- distrito distintos (`count if tagd==1`) = **96**

Top 15 setores por freq (`list in 1/15`):

```
  | setor   nesc |
  |  6801     51 |
  |  4603     50 |
  |  2502     39 |
  |  1302     37 |
  |  9302     36 |
  |  6101     33 |
  |  1104     33 |
  |  2203     32 |
  |  3610     31 |
  |  1103     31 |
  |  6304     29 |
  |  6802     29 |
  |  3402     29 |
  |  8105     28 |
  |  4602     28 |
```
N setores distintos (via contract) = **455**

**D2a — cep_renda_pop_2010**

- **N linhas = 43495**
- `nm_distrit` distintos (`count if t==1`) = **96**
- `cod_setor` (IBGE) distintos (`count if t2==1`) = **13,639**

**D2b — CEP → setor educacional pela escola mais próxima**

- `keep if !missing(lat,lon) & !missing(setor)`: (26 obs deleted).
- `expand 9`: (37,816 observations created).
- **N CEP = 46258**
- `bysort cep (dist_km): keep if _n==1`: (7,620,660 obs deleted).
- **N CEP com setor atribuído (escola <=~2km 3x3) = 45362**

`sum dist_km, detail`:

```
                           dist_km
 1%     .0207283    Smallest .0000102   Obs        45,362
 5%      .052369             .0000204   Mean      .2847075
10%     .0773203             .0000232   Std.dev.  .3485882
25%     .1295235             .0000349   Variance  .1215137
50%     .2115853    Largest  4.710374   Skewness  5.693497
75%     .3218937             4.746738   Kurtosis  46.05538
90%      .474061             4.764523
95%     .6466198             5.026402
99%     2.097206
```

`=== FIM D1D2 ===`. Log fechado `22 Jul 2026, 12:18:30`.

### diag05_D3

Início: `opened on: 22 Jul 2026, 12:20:00`.

**Painel: aberturas + estoque por setor-ano**

- merge `m:1 escola` (openings→escolas_parsed): Not matched 0, Matched **2,313**.
- `keep if !missing(setor) & inrange(ano,2005,2018)`: (497 obs deleted).
- grade setores: `duplicates drop` (44,908 deleted); `expand 14` (5,902 created).
- merge `1:1 setor ano`: Not matched 5,061 (master); Matched **1,295**.
- `replace aberturas=0`: (5,061 real changes).
- `keep if inrange(ano,2010,2018)`: (2,270 obs deleted).

**Cohort por setor-ano_sol**

- merge `m:1 cep` (child_expo→cep_setor): Not matched 15,969 (master); Matched **1,508,591**.
- `gen idade_entrada`: (203,715 missing generated); `replace idade_entrada=. if !inrange(0,72)`: (5,966 real changes to missing).
- `gen espera_dias`: (209,681 missing generated).
- `keep if !missing(setor_cep) & inrange(ano_sol,2010,2018)`: (66,015 obs deleted).

**D3 — painel final**

- merge `1:1 setor ano`: Not matched 4 (master); Matched **4,082**.
- `replace n_solic/n_matric=0`: (4 real changes cada).
- **N linhas painel = 4086**

Primeiras 20 linhas (`list ... in 1/20`):

```
| setor  ano  aberturas estoque n_solic n_matric idade_media espera_med |
|  101  2010      1        2      120     103     33.55        20    |
|  101  2011      0        2      212     164   35.33742      223    |
|  101  2012      0        2      366     299   33.98997      199    |
|  101  2013      0        2      286     250   33.39113      136    |
|  101  2014      1        3      265     236   29.13617      189    |
|  101  2015      0        3      292     260   26.96154      200    |
|  101  2016      0        3      261     232   26.43044      168    |
|  101  2017      0        3      320     299   28.58725     175.5   |
|  101  2018      0        3      270     212    23.8673      140    |
|  102  2010      1        2      150     113   43.19643       28    |
|  102  2011      0        2      224     175   37.77143      296    |
|  102  2012      0        2      525     457   35.14286      193    |
|  102  2013      2        4      414     369    31.6712     101.5   |
|  102  2014      0        4      395     344   29.06997      138    |
|  102  2015      1        5      400     373   26.90885      132    |
|  102  2016      0        5      344     307   24.52769      107    |
|  102  2017      0        5      361     326   25.03077      143    |
|  102  2018      0        5      344     286   22.82867       76    |
|  103  2010      0        0       37      28   36.32143     110.5   |
|  103  2011      0        0       73      63   36.63492      406    |
```

`sum ... , detail` (colunas do painel):

`aberturas` (Frequency): Obs 4,086; Mean .3707783; Std.dev .7717901; p50 0; p75 1; p90 1; p95 2; p99 3; Largest 6,7,7; Variance .59566; Skewness 2.945082; Kurtosis 15.36519.

`estoque`: Obs 4,086; Mean 2.344591; Std.dev 3.05914; p50 1; p75 3; p90 6; p95 8; p99 14; Largest 21,22,23,24; Variance 9.358339; Skewness 2.396303; Kurtosis 10.62042.

`n_solic` ((count) cd_aluno_sme): Obs 4,086; Mean 356.9616; Std.dev 314.7304; p1 6; p5 34; p10 54; p25 123; p50 274; p75 504; p90 758; p95 966; p99 1507; Largest 2168,2250,2420,2437; Variance 99055.21; Skewness 1.75823; Kurtosis 7.584987.

`n_matric` ((sum) matriculou): Obs 4,086; Mean 312.6373; Std.dev 281.6456; p1 5; p5 27; p10 45; p25 103; p50 237.5; p75 442; p90 674; p95 848; p99 1292; Largest 1957,2077,2166,2190; Variance 79324.23; Skewness 1.785145; Kurtosis 7.782285.

`idade_media` ((mean) idade_entrada): Obs 4,081; Mean 30.20214; Std.dev 6.972258; p1 17.4332; p25 24.71605; p50 29.62446; p75 35.05833; p90 39.5; p95 42.19737; p99 47.93333; Smallest 4,10.66667,10.875,12.68182; Largest 54.21545,57,57.23077,70; Variance 48.61238; Skewness .4178759; Kurtosis 3.004236.

`espera_med` ((p50) espera_dias): Obs 4,081; Mean 206.4923; Std.dev 122.3317; p1 15; p25 120.5; p50 182; p75 273; p90 385; p95 443; p99 565; Smallest 1,2,5,6; Largest 747.5,755.5,762,807; Variance 14965.06; Skewness .9557635; Kurtosis 3.931229.

**D4 — setores com >=1 abertura 2010-2016**

- `keep if inrange(ano,2010,2016)`: (908 obs deleted).
- `by setor: keep if _n==1`: (2,724 obs deleted).
- **N setores no painel (com >=1 CEP atribuído) = 454**
- `count if tot_ab>0`: **328** → setores com >=1 abertura em 2010-2016 = **328**

Distribuição do nº de anos (2010-2016) com abertura por setor:

```
anos_com_ab |
     ertura |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |        126       27.75       27.75
          1 |        115       25.33       53.08
          2 |         89       19.60       72.69
          3 |         58       12.78       85.46
          4 |         38        8.37       93.83
          5 |         21        4.63       98.46
          6 |          4        0.88       99.34
          7 |          3        0.66      100.00
------------+-----------------------------------
      Total |        454      100.00
```

**D5 — setores NUNCA com abertura (2010-2016)**

- `count if tot_ab==0`: **126** → setores nunca-tratados = **126**

`=== FIM D3 ===`. Log fechado `22 Jul 2026, 12:20:06`.

### diag05_E

Início: `opened on: 22 Jul 2026, 12:22:01`. **Este log terminou com erro (ver seção final); nem todas as seções foram executadas.**

**Mapa criança → ano_nasc**

- **N crianças no mapa = 1524653**

**E1 — ano de nascimento dos que fizeram PSP 2º ano**

- Nota impressa: `PSP 2017: 2o ano NAO EXISTE (menor serie = C.I 3.ANO F9).`
- PSP 2018: `keep if strpos(desc_serie,"2.ANO")>0`: (347,326 obs deleted). merge `m:1`: Not matched 9,183 (master); Matched **37,531**. N=**46714**.

`tab ano_nasc, miss` (PSP 2018 2º ano):

```
   ano_nasc |      Freq.     Percent        Cum.
------------+-----------------------------------
       2005 |          2        0.00        0.00
       2006 |          4        0.01        0.01
       2007 |         12        0.03        0.04
       2008 |         77        0.16        0.20
       2009 |        454        0.97        1.18
       2010 |     26,894       57.57       58.75
       2011 |     10,088       21.60       80.34
          . |      9,183       19.66      100.00
------------+-----------------------------------
      Total |     46,714      100.00
```

- PSP 2019: `keep if strpos(desc_serie,"2 Ano")>0`: (339,570 obs deleted). merge `m:1`: Not matched 2,949 (master); Matched **36,438**. N=**39387**.

`tab ano_nasc, miss` (PSP 2019 2º ano):

```
   ano_nasc |      Freq.     Percent        Cum.
------------+-----------------------------------
       2005 |          3        0.01        0.01
       2006 |          5        0.01        0.02
       2007 |          2        0.01        0.03
       2008 |         23        0.06        0.08
       2009 |         74        0.19        0.27
       2010 |        531        1.35        1.62
       2011 |     25,882       65.71       67.33
       2012 |      9,918       25.18       92.51
          . |      2,949        7.49      100.00
------------+-----------------------------------
      Total |     39,387      100.00
```

**E2 — coorte modal x universo B_novo x casamento**

`tab ano_nasc if inrange(ano_nasc,2009,2013)` (B_novo):

```
   ano_nasc |      Freq.     Percent        Cum.
------------+-----------------------------------
       2009 |    114,708       16.43       16.43
       2010 |    128,352       18.39       34.82
       2011 |    146,693       21.01       55.83
       2012 |    155,292       22.25       78.08
       2013 |    153,033       21.92      100.00
------------+-----------------------------------
      Total |    698,078      100.00
```

- coorte 2010: `B_novo nascidos em 2010: 128352`; `keep if ano_nasc==2010` (1,396,208 obs deleted).
- **ERRO**: `variable cd_aluno_sme does not uniquely identify observations in the using data` → `r(459)`; `end of do-file r(459)`. As seções E2 (casamentos) e E3 **não foram concluídas** neste log.

(O log de `diag05_E` não registra `=== FIM diag05_E ===`.)

### diag05_E2

Início: `opened on: 22 Jul 2026, 12:26:13`. (Versão corrigida — deduplica ids PSP antes do merge `1:1`.)

- `duplicates drop` PSP2018: (1 observation deleted). **PSP2018-2ano cd_aluno distintos = 46713**
- `duplicates drop` PSP2019: (0 duplicates). **PSP2019-2ano cd_aluno distintos = 39387**

**E2 — coorte x B_novo x casamento PSP-2ano**

- merge `1:1` p18: Not matched 1,487,030 (master); Matched **37,530**.
- merge `1:1` p19: Not matched 1,488,122 (master); Matched **36,438**.
- `replace p18=0`: (1,487,030 real changes); `replace p19=0`: (1,488,122 real changes).

| coorte | B_novo nascidos | casam PSP2018-2ano | casam PSP2019-2ano |
|---|---|---|---|
| 2010 | 128352 | 26894 | 531 |
| 2011 | 146693 | 10087 | 25882 |
| 2012 | 155292 | 0 | 9918 |

**E3 — maior coorte: expo12 e taxa de matrícula**

Coorte 2010 (N = **128352**); `gen ec` (1,396,208 missing generated); `replace ec=3` (4,989 real changes):

```
         ec |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |     74,037       57.68       57.68
          1 |     30,862       24.04       81.73
          2 |     12,802        9.97       91.70
          3 |     10,651        8.30      100.00
------------+-----------------------------------
      Total |    128,352      100.00
```
media expo12_1km = .75928696 ; taxa de matrícula (ever_mat) = .87480522

Coorte 2011 (N = **146693**); `gen ec` (1,377,867 missing generated); `replace ec=3` (6,174 real changes):

```
         ec |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |     81,910       55.84       55.84
          1 |     36,409       24.82       80.66
          2 |     15,151       10.33       90.99
          3 |     13,223        9.01      100.00
------------+-----------------------------------
      Total |    146,693      100.00
```
media expo12_1km = .80247865 ; taxa de matrícula (ever_mat) = .8985364

`=== FIM E2 ===`. Log fechado `22 Jul 2026, 12:26:19`.

## O que o log NÃO permite recuperar

- **diag05_E interrompido (`r(459)`)**: o log de `diag05_E.log` termina em erro na coorte 2010 (merge `1:1` com `psp2018_2ano.dta` cujo `cd_aluno_sme` tinha duplicata). Não há resultados de casamento por coorte, nem de E3, nem linha `=== FIM diag05_E ===` nesse log. Esses resultados só aparecem na versão corrigida `diag05_E2.log`. O valor `casam PSP2018-2ano` para a coorte 2011 difere entre a leitura por-crianca (E1: 10,088 nascidos 2011 no arquivo PSP2018) e o casamento com B_novo em E2 (**10,087**) — a diferença de 1 não é explicada no log (compatível com a 1 duplicata removida em E2, mas o log não o afirma).
- **Caminho do log divergente do `$aud`**: em todos os `.do`, `global aud` aponta para `...\Neighborhood Effects\02_audit`, mas o cabeçalho/rodapé de cada `.log` registra `...\Neighborhood Effects\_audit\...` (sem o `02`). Os logs não esclarecem essa divergência de caminho.
- **Conteúdo dos arquivos `.dta` de entrada não é mostrado**: variáveis e valores de `escolas_parsed.dta`, `censo2018.dta`, `cepcentroide.dta`, `Fila1018.dta`, `cep_renda_pop_2010.dta`, `psp_2017/2018/2019.dta` só aparecem na medida usada; estrutura completa não é recuperável.
- **PSP 2017**: apenas a nota `di` afirma que o 2º ano não existe (menor série = C.I 3.ANO F9); nenhuma tabela/contagem sobre 2017 é mostrada.
- **Placeholder no programa `distrib` (diag05_B)**: a linha `% >=1 = ... 100*(1 - (...)*0)` é marcada `/* placeholder */` e imprime sempre `100.00`; esse número **não é um percentual real** e deve ser ignorado (o percentual válido de >=1 está na linha `N >=1 = ...`).
- **C5**: não gera números próprios; apenas remete às linhas `RES| ... spec2` de C1–C4.
- **Coordenadas / distâncias individuais**: `dist_km` por par CEP-CEI e por par CEP-escola só aparecem em forma agregada (`sum`, contagens); os valores individuais não são recuperáveis do log.
- **`cei_openings_novo.dta`**: A3 salva N=2313 (com coord), mas D3 usa 2,313 e depois deleta 497 fora de 2005-2018 (não há detalhamento por CEI de quais foram excluídos).
