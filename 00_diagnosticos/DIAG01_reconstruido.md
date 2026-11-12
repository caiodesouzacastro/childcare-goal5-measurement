> RECONSTRUÇÃO. Este arquivo foi gerado a partir dos logs em 02_audit\ e não
> é o relatório original, que não foi preservado em .md. Os números vêm dos
> logs; a estrutura e as regras de decisão foram reconstruídas e podem estar
> incompletas. Fonte primária: os arquivos .log listados ao final.

# DIAG01 — Reconstrução a partir dos logs de auditoria

## Arquivos lidos

| Arquivo | Linhas | O que o .do faz (com base apenas nos comandos) |
|---|---|---|
| `02_audit\diag01.do` | 206 | Reconstrói a base `b1_2011` replicando (segundo o comentário) `04_referee_robustness.do` verbatim. Carrega `trat2011ber.dta`, filtra `ano_nasc==2010`, faz `merge m:1 cd_aluno_sme` com a amostra RDD (`keep(3)`). Gera `dt_sol` a partir de `dt_solicitacao`; constrói `rvar` (dois loops `1/31`: primeiro para `trat_ber_2011`i'==1`, depois fallback para `dt_corte_escola`i'` não-missing), `escola_rdd`, `_idx`, `fallback`, `t=trat2011ber`, `exp="b1_2011"`. Padroniza `prof_mat`/`prof_lp` (z-score). Conta `n_escolas` (nº de `dt_corte_escola`i'` não-missing), calcula `dist_assigned` (`esc`_idx'D`) e `dist_nearest` (`esc1D`). Faz merge de `renda` por `cep`. Salva `b1_2011_audit.dta`. Depois roda verificações forenses (B3/B4/B5), blocos C1–C6 (rvar por tratamento, contagem inteira de rvar, `n_escolas`, `rdrobust` principal em `prof_mat`, balanço no corte, donut hole) e uma conferência final contra a base do autor `trat_PSP_rdd_final.dta` (subconjunto `exp=="b1_2011"`). |
| `02_audit\diag01.log` | 674 | Log de execução de `diag01.do`. |
| `02_audit\diag01b.do` | 40 | Recarrega `b1_2011_audit.dta`. Bloco B6: `rownonmiss`/`rowtotal` das famílias `dt_corte_escola1-31`, `cd_esc_encaminhamento1-31`, `esc1D-esc31D`, `trat_ber_20111-31`; `sum` e `tab` de `nm_dtcorte` e `nm_tratber1`. Bloco B5: `tab` de candidatas a variável de oferta (`trat2011ber`, `encaminhado`, `exp_tratamento`, `esc_trat`); cruzamentos `encaminhado`×`trat2011ber` e `exp_tratamento`×`trat2011ber`; `sum ... , detail` de `esc1D` e `dist_assigned`. |
| `02_audit\diag01b.log` | 1069 | Log de execução de `diag01b.do`. |
| `02_audit\diag01c.do` | 41 | Recarrega `b1_2011_audit.dta`. Constrói `rvar_min_nonneg` (mínimo `dt_corte_escola`i'-dt_sol` ≥ 0 por criança — "regra do paper") e compara com `rvar` do código entre tratados (`igual = abs(rvar-rvar_min_nonneg)<0.5`), lista divergências, resume `dif`, e conta controles com `rvar` atribuído mas sem nenhum valor ≥ 0. |
| `02_audit\diag01c.log` | 113 | Log de execução de `diag01c.do`. |

Observação: em todos os três logs o cabeçalho registra o caminho `...\_audit\` (uma única barra/underscore) enquanto o `.do` define `$aud` como `...\02_audit`. Os logs foram lidos de `02_audit\`.

## Estatísticas e tabelas encontradas (transcritas)

### diag01.log — construção da base `b1_2011`

- `keep if ano_nasc==2010` → `(0 observations deleted)`
- `di "N ano_nasc==2010:"` → **N ano_nasc==2010: 5522**
- `merge m:1 cd_aluno_sme using "$amost" ... keep(3)`:

```
    Result                      Number of obs
    -----------------------------------------
    Not matched                             0
    Matched                               991
    -----------------------------------------
```

- `di "N após merge amostra RDD:"` → **N após merge amostra RDD: 991**
- `gen rvar = .` → (991 missing values generated)
- `gen escola_rdd = .` → (991 missing values generated)
- `gen _idx = .` → (991 missing values generated)
- `gen t = trat2011ber` → (1 missing value generated)
- Padronização `prof_mat`/`prof_lp`: **(862 real changes made)** e **(861 real changes made)**
- `gen dist_assigned = .` → (991 missing values generated)
- `merge m:1 cep using cep_renda_pop_2010.dta`:

```
    Result                      Number of obs
    -----------------------------------------
    Not matched                            18
        from master                        18
        from using                          0
    Matched                               973
    -----------------------------------------
```

- `compress`: **(251,714 bytes saved)** (várias variáveis recastadas; entre elas `rvar was float now int`, `dt_sol was double now int`, `dt_desistencia was str19 now str1`)
- `save b1_2011_audit.dta`: `file ... saved`
- `di "Base audit salva:"` → **Base audit salva: 991 obs**

### diag01.log — VERIFICAÇÃO FORENSE (B3/B4/B5)

`tab trat2011ber _rowmax, miss` (`_rowmax = rowmax(trat_ber_2011*)`; 1 missing value generated):

```
trat2011be |             _rowmax
         r |         0          1          . |     Total
-----------+---------------------------------+----------
         0 |       821          0          0 |       821
         1 |         0        169          0 |       169
         . |         0          0          1 |         1
-----------+---------------------------------+----------
     Total |       821        169          1 |       991
```

`gen byte rvar_pos = (rvar>=0) if !missing(rvar)` → (214 missing values generated)

`tab t rvar_pos, miss`:

```
           |             rvar_pos
         t |         0          1          . |     Total
-----------+---------------------------------+----------
         0 |       608          0        213 |       821
         1 |         0        169          0 |       169
         . |         0          0          1 |         1
-----------+---------------------------------+----------
     Total |       608        169        214 |       991
```

### diag01.log — C1: rvar por status de tratamento (b1_2011)

`tabstat rvar, by(t) stat(n min max mean p50) col(stat)`:

```
       t |         N       Min       Max      Mean       p50
---------+--------------------------------------------------
       0 |       608      -612        -2 -154.9359      -132
       1 |       169         0       236  64.40828        37
---------+--------------------------------------------------
   Total |       777      -612       236 -107.2278       -91
```

- `count if t==1 & rvar<0 & !missing(rvar)` → **0** (tratados com rvar<0)
- `count if t==0 & rvar>=0 & !missing(rvar)` → **0** (controles com rvar>=0)
- `tab fallback if !missing(rvar)`:

```
   fallback |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |        169       21.75       21.75
          1 |        608       78.25      100.00
------------+-----------------------------------
      Total |        777      100.00
```

### diag01.log — C2: contagem por valor inteiro de rvar em [-10,10]

`gen rvar_int = round(rvar)` → (214 missing values generated). `tab rvar_int if inrange(rvar_int,-10,10), miss`:

```
   rvar_int |      Freq.     Percent        Cum.
------------+-----------------------------------
         -9 |          1        1.75        1.75
         -8 |          3        5.26        7.02
         -7 |          4        7.02       14.04
         -6 |          4        7.02       21.05
         -5 |          1        1.75       22.81
         -4 |          3        5.26       28.07
         -3 |          3        5.26       33.33
         -2 |          1        1.75       35.09
          0 |         21       36.84       71.93
          1 |          3        5.26       77.19
          2 |          2        3.51       80.70
          4 |          1        1.75       82.46
          5 |          1        1.75       84.21
          6 |          2        3.51       87.72
          8 |          3        5.26       92.98
          9 |          1        1.75       94.74
         10 |          3        5.26      100.00
------------+-----------------------------------
      Total |         57      100.00
```

### diag01.log — C3: n_escolas

(a) `tab n_escolas`:

```
  n_escolas |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |        214       21.59       21.59
          1 |        216       21.80       43.39
          2 |        122       12.31       55.70
          3 |         97        9.79       65.49
          4 |         51        5.15       70.64
          5 |         67        6.76       77.40
          6 |         85        8.58       85.97
          7 |         43        4.34       90.31
          8 |         71        7.16       97.48
          9 |         24        2.42       99.90
         10 |          1        0.10      100.00
------------+-----------------------------------
      Total |        991      100.00
```

(b) `tabstat n_escolas, by(t) stat(n mean sd) col(stat)`:

```
       t |         N      Mean        SD
---------+------------------------------
       0 |       821  2.768575  2.788484
       1 |       169  3.680473  2.268765
---------+------------------------------
   Total |       990  2.924242   2.72748
```

`ttest n_escolas if !missing(t), by(t)`:

```
   Group |     Obs        Mean    Std. err.   Std. dev.   [95% conf. interval]
---------+--------------------------------------------------------------------
       0 |     821    2.768575    .0973188    2.788484    2.577552    2.959598
       1 |     169    3.680473    .1745204    2.268765    3.335938    4.025009
---------+--------------------------------------------------------------------
Combined |     990    2.924242     .086685     2.72748    2.754135     3.09435
---------+--------------------------------------------------------------------
    diff |           -.9118985     .228674               -1.360641    -.463156
------------------------------------------------------------------------------
    diff = mean(0) - mean(1)                                      t =  -3.9878
H0: diff = 0                                     Degrees of freedom =      988
    Ha: diff < 0                 Ha: diff != 0                 Ha: diff > 0
 Pr(T < t) = 0.0000         Pr(|T| > |t|) = 0.0001          Pr(T > t) = 1.0000
```

(c) `pwcorr n_escolas renda, sig obs`:

```
             | n_esco~s    renda
-------------+------------------
   n_escolas |   1.0000
             |      991
       renda |  -0.1692   1.0000
             |   0.0000
             |      973      973
```

(d) `xtile renda_q = renda if !missing(renda), nq(4)`; `tabstat n_escolas, by(renda_q) stat(n mean) col(stat)`:

```
 renda_q |         N      Mean
---------+--------------------
       1 |       244  3.422131
       2 |       244  3.454918
       3 |       243  3.251029
       4 |       242  1.636364
---------+--------------------
   Total |       973  2.943474
```

### diag01.log — C4: especificação principal (math 2018)

`rdrobust prof_mat rvar, c(0) kernel(triangular) bwselect(mserd) vce(cluster escola_rdd)` — "Mass points detected in the running variable."

```
      Cutoff c = 0 | Left of c  Right of c            Number of obs =        673
-------------------+----------------------            BW type       =      mserd
     Number of obs |       529         144            Kernel        = Triangular
Eff. Number of obs |       100          84            VCE method    =    Cluster
    Order est. (p) |         1           1
    Order bias (q) |         2           2
       BW est. (h) |    54.550      54.550
       BW bias (b) |    90.533      90.533
         rho (h/b) |     0.603       0.603
        Unique obs |       267          83
Number of clusters |        68          59

                   | Point         | Robust Inference
                   | Estimate      | z-stat        P>|z|    [95% Conf. Interval]
-------------------+------------------------------------------------------------
         RD Effect |  .68313       | 2.4551        0.014     .159492     1.42215
```

Escalares e contagens:
- **h_l=54.549695  h_r=54.549695**
- **e(N_h_l)=100  e(N_h_r)=84**
- **tau_cl=.68313277  se_rb=.32211144  p_rb=.0140842**
- ESQUERDA: `count if rvar>=-hl & rvar<0 & !missing(prof_mat)` → **100**; com `t==0` → **100**; `count if _tagL==1` (clusters `escola_rdd`) → **48**
- DIREITA: `count if rvar<=hr & rvar>=0 & !missing(prof_mat)` → **84**; com `t==1` → **84**; `count if _tagR==1` → **55**

### diag01.log — C5: balanço no corte

`rdrobust `v' rvar, c(0) kernel(triangular) bwselect(mserd)` para cada `v`:

| v | tau_cl | se_rb | p_rb | h | N (N_h_l+N_h_r) |
|---|---|---|---|---|---|
| n_escolas | 0.7970 | 0.7199 | 0.1516 | 61.1 | 247 |
| renda | -268.0743 | 440.8859 | 0.3997 | 64.2 | 257 |
| dist_assigned | -0.1796 | 0.2177 | 0.2358 | 51.4 | 221 |
| dist_nearest | -0.0286 | 0.0840 | 0.4796 | 65.4 | 266 |

### diag01.log — C6: donut hole (math 2018)

| k | tau_cl | se_rb | p_rb | h | Nef (N_h_l+N_h_r) | trat | ctrl |
|---|---|---|---|---|---|---|---|
| 0 | 0.6831 | 0.3221 | 0.0141 | 54.5 | 184 | 66 | 100 |
| 3 | 0.1769 | 0.4280 | 0.7033 | 71.6 | 214 | 69 | 145 |
| 7 | -0.0495 | 0.5136 | 0.8157 | 69.2 | 197 | 64 | 133 |
| 14 | 0.2090 | 1.4011 | 0.9359 | 39.9 | 75 | 37 | 38 |

### diag01.log — CONFERÊNCIA vs base do autor (trat_PSP_rdd_final.dta, b1_2011)

- `use trat_PSP_rdd_final.dta` ; `keep if exp=="b1_2011"` → `(3,721 observations deleted)`
- `di "N autor b1_2011:"` → **N autor b1_2011: 991**
- `tabstat rvar, by(t) ...` (idêntico ao C1):

```
       t |         N       Min       Max      Mean       p50
---------+--------------------------------------------------
       0 |       608      -612        -2 -154.9359      -132
       1 |       169         0       236  64.40828        37
---------+--------------------------------------------------
   Total |       777      -612       236 -107.2278       -91
```

- `count if t==1 & rvar<0 & !missing(rvar)` → **0**
- `count if t==0 & rvar>=0 & !missing(rvar)` → **0**
- `rdrobust prof_mat rvar ... vce(cluster escola_rdd)`: mesma tabela do C4 (Number of obs=673; Eff. 100/84; h=54.550; RD Effect=.68313; z=2.4551; P>|z|=0.014; IC [.159492, 1.42215])
- `di "AUTOR C4:"` → **tau_cl=.68313277  se_rb=.32211144  p_rb=.0140842  h=54.549695**
- `di "FIM diag01"` — (linha do `.do`; o log fecha em `log close` sem ecoar essa `di`, ver seção final)

### diag01b.log — B6: não-missing por criança

`di "N ="` → **N = 991**

`sum nm_dtcorte nm_cdesc nm_escD nm_tratber nm_tratber1`:

```
    Variable |        Obs        Mean    Std. dev.       Min        Max
-------------+---------------------------------------------------------
  nm_dtcorte |        991    62.86075    3.380393          0         70
    nm_cdesc |        991     63.7669    3.321366          0         70
     nm_escD |        991    30.96872    .9847475          0         31
  nm_tratber |        991    63.76488    3.337606          0         71
 nm_tratber1 |        991     8551547    579453.8          0   1.01e+07
```

`tab nm_dtcorte` (dt_corte não-missing por criança):

```
 nm_dtcorte |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |          1        0.10        0.10
         60 |        213       21.49       21.59
         61 |        216       21.80       43.39
         62 |        122       12.31       55.70
         63 |         97        9.79       65.49
         64 |         51        5.15       70.64
         65 |         67        6.76       77.40
         66 |         85        8.58       85.97
         67 |         43        4.34       90.31
         68 |         71        7.16       97.48
         69 |         24        2.42       99.90
         70 |          1        0.10      100.00
------------+-----------------------------------
      Total |        991      100.00
```

`tab nm_tratber1` (nº escolas com `trat_ber==1` por criança — via `rowtotal`): tabela extensa com 991 obs; os valores da variável são somas de códigos de escola (não contagens), variando de **0** a **1.01e+07**. Extremos: valor `0` → Freq. 1 (0.10%); menor valor não-zero `6982296` → 1; maior antes do topo `9923591` → 1; duas linhas finais rotuladas `1.01e+07` → 1 cada (Total 991). (A tabela lista centenas de valores distintos, a maioria com Freq. 1; ver log linhas 62–885 para a listagem completa.)

### diag01b.log — B5: variáveis candidatas de OFERTA

`tab trat2011ber, miss`:

```
trat2011ber |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |        821       82.85       82.85
          1 |        169       17.05       99.90
          . |          1        0.10      100.00
------------+-----------------------------------
      Total |        991      100.00
```

`tab encaminhado, miss`:

```
encaminhado |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |         19        1.92        1.92
          1 |        972       98.08      100.00
------------+-----------------------------------
      Total |        991      100.00
```

`tab exp_tratamento, miss`:

```
exp_tratame |
        nto |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |          2        0.20        0.20
          1 |          6        0.61        0.81
          2 |          5        0.50        1.31
          3 |         33        3.33        4.64
          4 |         48        4.84        9.49
          5 |         56        5.65       15.14
          6 |         59        5.95       21.09
          7 |         72        7.27       28.36
          8 |         91        9.18       37.54
          9 |        111       11.20       48.74
         10 |        154       15.54       64.28
         11 |        205       20.69       84.96
         12 |         66        6.66       91.62
         13 |         80        8.07       99.70
          . |          3        0.30      100.00
------------+-----------------------------------
      Total |        991      100.00
```

`tab esc_trat, miss`: 991 obs; valor **`.` (missing) → 822 (82.95%)**; 169 obs distribuídos em códigos de escola de `306406` a `400721`, cada um com Freq. 1–10 (destaques: `400278` → 10; `306943` → 7; `307200` → 7; `327219` → 6; `400275` → 6; `400611` → 5; `400432` → 5). Ver log linhas 940–1016 para a listagem completa.

Cruzamentos:
- `cap tab encaminhado trat2011ber, miss` → **executado sob `cap`; nenhuma tabela ecoada no log** (só a linha do `di` de rótulo aparece).
- `cap tab exp_tratamento trat2011ber, miss` → **executado sob `cap`; nenhuma tabela ecoada no log**.

`sum esc1D dist_assigned, detail`:

```
                            esc1D
      Percentiles      Smallest
 1%     .0167275        .000307
 5%     .0537174       .0041294
10%     .0725493       .0074904       Obs                 990
25%      .125555       .0093744       Sum of wgt.         990
50%     .2011517                      Mean           .8823936
                        Largest       Std. dev.      12.85467
75%     .3023854       53.35186
90%     .4313568        86.4602       Variance       165.2424
95%     .5411658       86.99696       Skewness       27.06595
99%     3.324648       382.1444       Kurtosis       787.5459

                        dist_assigned
      Percentiles      Smallest
 1%     .0192197       .0167275
 5%     .1313654       .0167275
10%      .186316       .0167275       Obs                 777
25%     .3071377       .0167275       Sum of wgt.         777
50%     .5926816                      Mean           .7528396
                        Largest       Std. dev.      .6239538
75%     .9907423       4.097778
90%     1.474692       4.365386       Variance       .3893184
95%     1.962317        4.48828       Skewness       2.256608
99%     3.303489       4.987705       Kurtosis       11.39165
```

### diag01c.log — regra do código vs regra do paper (min rvar≥0)

- `replace rvar_min_nonneg = . if rvar_min_nonneg >= 1e11` → **(0 real changes made)**
- `count if t==1` → **169**
- `count if t==1 & !missing(rvar) & !missing(rvar_min_nonneg)` → **169**
- `gen byte igual = (abs(rvar - rvar_min_nonneg) < 0.5) if ...` → (822 missing values generated)
- `tab igual if t==1`:

```
      igual |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |         56       33.14       33.14
          1 |        113       66.86      100.00
------------+-----------------------------------
      Total |        169      100.00
```

- `count if t==1 & igual==0` → **56**
- `list cd_aluno_sme rvar rvar_min_nonneg _idx if t==1 & igual==0 in 1/20, noobs`:

```
  +-----------------------------------+
  | cd_alu~e   rvar   rvar_m~g   _idx |
  |-----------------------------------|
  |  5195467     36         29     15 |
  |  5169660     97         20      3 |
  |  5133694    100         55      4 |
  |  5197865     66         21      2 |
  +-----------------------------------+
```

(Observação: o comando pedia `in 1/20`, mas o log lista apenas 4 observações.)

- `sum dif, detail` (`dif = rvar - rvar_min_nonneg if t==1`; 822 missing values generated):

```
                             dif
      Percentiles      Smallest
 1%            0              0
 5%            0              0
10%            0              0       Obs                 169
25%            0              0       Sum of wgt.         169
50%            0                      Mean           21.34911
                        Largest       Std. dev.      43.68695
75%           16            162
90%          104            176       Variance        1908.55
95%          126            176       Skewness       2.159352
99%          176            202       Kurtosis       6.769555
```

### diag01c.log — CONTROLES

- `count if t==0 & !missing(rvar)` → **608**
- `count if t==0 & missing(rvar_min_nonneg)` → **821**
- `count if t==0 & !missing(rvar) & missing(rvar_min_nonneg)` (controles com rvar do código atribuído mas sem nenhum rvar≥0) → **608**

## O que o log NÃO permite recuperar

- **Globais/macros não resolvidos nos logs**: os caminhos `$bruto`, `$proc`, `$amost`, `$ba`, `$aud` não são ecoados expandidos nas linhas de comando dos logs (aparecem literais, ex.: `use "$bruto\trat2011ber.dta"`). Os valores completos só constam do `.do` (`diag01.do`, linhas 10–14). Além disso, os cabeçalhos dos três logs registram o caminho como `...\_audit\` enquanto `$aud` no `.do` é `...\02_audit`; não é possível pelos logs determinar qual árvore foi efetivamente usada.
- **Cruzamentos B5 sob `cap`**: `tab encaminhado trat2011ber` e `tab exp_tratamento trat2011ber` foram chamados com `cap` e **não produziram tabela no log** (apenas os `di` de rótulo). Não é possível recuperar esses cruzamentos.
- **`tab nm_tratber1` (B6)**: a variável é uma soma de códigos (`rowtotal` de `trat_ber_20111-31`), não uma contagem de ofertas como sugere o rótulo do `.do`; os valores altos (até 1.01e+07) e sua interpretação como "nº de ofertas" não são recuperáveis/coerentes a partir do log — apenas a distribuição bruta está registrada.
- **Listagem C-c truncada por dados**: `list ... in 1/20` retornou apenas 4 linhas; as demais divergências (56 casos com `igual==0`, dos quais só 4 listados) não constam do log.
- **`di "FIM diag01"`**: consta como comando final em `diag01.do` (linha 205, após `log close`), portanto **não é ecoado no log** (o log já havia sido fechado). Não há confirmação em log dessa linha.
- **`nm_tratber` vs `nm_dtcorte` vs `nm_cdesc`**: os máximos diferem (70, 70, 71 / esc D máx 31) mas o log não explica a discrepância entre as famílias de variáveis por escola.
- **Conteúdo das bases `.dta` de origem**: os logs não listam o dicionário completo de variáveis; famílias como `esc`i'D`, `cd_esc_encaminhamento`i'`, `dt_corte_escola`i'` só aparecem indiretamente (via `compress`, `rownonmiss`, loops). Rótulos e definições originais não são recuperáveis.
- Nenhum dos logs está vazio ou truncado no fecho; os três abrem e fecham normalmente (`opened on` / `closed on` presentes).

## Arquivos .log (fonte primária)

- `<NE_ROOT>\02_audit\diag01.log`
- `<NE_ROOT>\02_audit\diag01b.log`
- `<NE_ROOT>\02_audit\diag01c.log`
