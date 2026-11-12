> RECONSTRUÇÃO. Este arquivo foi gerado a partir dos logs em 02_audit\ e não
> é o relatório original, que não foi preservado em .md. Os números vêm dos
> logs; a estrutura e as regras de decisão foram reconstruídas e podem estar
> incompletas. Fonte primária: os arquivos .log listados ao final.

## Arquivos lidos

Todos em `<NE_ROOT>\02_audit\`. Contagens de linha por `wc -l` (número de quebras de linha; o arquivo pode não terminar em nova linha).

| Arquivo | Linhas | O que faz / contém |
|---|---|---|
| `diag09_build.do` | 44 | Constrói `panel_es.dta`. Programa `pick` de harmonização; laço sobre 9 arquivos `cpf_fila_*` (2007–2014, com 2010 em dois arquivos), harmonizando `emp_raw` (empem3112/vínculoativo3112), `sex_raw` (genero/sexotrabalhador), `estabsz`, `njur`, `wnom`, `hrs`, `maeb` (ano nasc. mãe = ano − idade, ou de `dtnasciment`). Empilha (`append`), gera `respid=group(cpf)`, `emp=(emp_raw==1)`, `fem=(sex_raw==2)`, salário mínimo por ano, `wage_sm=wnom/minw`, `publico=njur∈[1000,1999]`. Salva o painel e roda `tab fem`, `tab publico`, `sum wage_sm, detail`, `count if !missing(maeb)`. |
| `diag09_build.log` | 282 | Log da execução acima. Cabeçalho de log grava caminho `...\_audit\...` (não `02_audit`). |
| `diag09_build2.do` | 91 | **A1**: para cada arquivo, média de `empem3112`/`vínculoativo3112` (detecta arquivos "só-empregados", média=1). Reconstrói `panel_es.dta` "corrigido": `fem` via string (`genero=="FEMININO"`), `wsm` (salário em SM direto, remmedia/vlremunmédiasm), `hrs`, `estabsz`, `njur`, `maeb`. Colapsa por (cd_aluno_sme, respid, rais_year) pegando vínculo principal (maior `wsm`). Salva painel e roda `table rais_year` (mean fem, mean emp, p50 wsm, count wsm). |
| `diag09_build2.log` | 228 | Log da execução acima. |
| `diag09_A.do` | 44 | Usa `panel_es.dta`; `rel = rais_year − ano_nasc`. **A2** coorte 2011: emp por ano calendário vs tempo relativo. **A3** placebo emp por `rel` feminino vs masculino. **A4** emp por `rel` por coorte 2009–2013 (só feminino). **A5** painel balanceado (resp. observado nos 8 anos): `count if nyr==8 & rais_year==2007` e emp por `rel` (balanceado, feminino). |
| `diag09_A.log` | 250 | Log da execução acima. |
| `diag09_BCDE.do` | 91 | **Parte B** (amostra event-study, mães): `firstbirth=min(ano_nasc)` por respid; `keep if fem==1`. B1 crianças/mães distintas; B2 mães com 1º filho 2009–2013; B3 `tab npre npos` (anos RAIS pré/pós nasc.) e N com ≥2 pré & ≥3 pós; B4 idade da mãe no 1º nasc. (`sum detail`, contagens <18, >40, missing); B5 nota (escolaridade não retida). **Parte C** (desfechos por `rel`, 1º filho 2009–2013): colapsa mãe-ano; C1 emp; C2 salário SM incondicional (`wsm0`); C3 salário SM condicional (mean, p50); C4 horas condicional; C5 setor público condicional. Apesar do nome, o `.do` termina após a Parte C ("=== FIM BCDE ==="); D e E não estão neste `.do`. |
| `diag09_BCDE.log` | 335 | Log da execução acima (B e C). |
| `diag09_DE.do` | 81 | **Parte D**: usa painel; `fem==1`; `firstbirth` 2009–2013; `firstchild`, `nkids`, `rel`; colapsa mãe-ano; merge com `child_expo.dta` (expo12_1km, estoque_1km, dt_mat_first, ever_mat, cep) e `cep_renda_pop_2010.dta` (renda). D1 emp por `rel` × expo12 (0 vs ≥1) e por quartil de estoque; D2 emp por `rel` × quartil de renda; D3 emp por `rel` × EI antes 12m; D4 emp por `rel` × nº filhos (1 vs 2+). **Parte E**: recarrega painel; `ultimo`/`primeiro` ano por mãe; E1 `tab ultimo` + `count if ultimo<2014`; E2 `tab dif` (ultimo − firstbirth). |
| `diag09_DE.log` | 234 | Log da execução acima. **Interrompe com erro** em D4 ("2+ filhos"): `r(3301)` `_table::compute(): subscript invalid`. A Parte E deste `.do` **não chegou a rodar** neste log. |
| `diag09_E.log` | 76 | **Só existe o `.log`; não há `diag09_E.do`.** Contém a re-execução isolada da Parte E (E1 `tab ultimo`, `count if ultimo<2014`; E2 `tab dif`), que aparentemente foi rodada à parte por causa do erro que interrompeu `diag09_DE`. |

Observação geral: em todos os logs o cabeçalho grava o caminho como `...\Neighborhood Effects\_audit\...` (com `_audit`, não `02_audit`).

## Estatísticas e tabelas encontradas (transcritas)

### diag09_build.log

Mensagens do laço de construção (valores missing gerados por arquivo, repetidos 7× cada): 2007 = 409.227; 2008 = 289.810; 2009 = 311.423; 2010 (cpf_fila_101) = 256.765; 2010 (cpf_fila_102) = 346.485; 2011 = 677.823; 2012 = 706.676; 2013 = 731.684; 2014 = 744.703. Cada iteração imprime "`<arquivo>` (`<ano>`) carregado".

`minw` — mudanças reais por ano: 2007=409.227; 2008=289.810; 2009=311.423; 2010=603.250; 2011=677.823; 2012=706.676; 2013=731.684; 2014=744.703.

`gen wage_sm = wnom/minw ...` → (67.392 missing values generated).

`compress`: variable hrs was double now byte (31.322.172 bytes saved).

`di "N painel rico = " _N` →

```
N painel rico = 4474596
```

`tab fem, miss`:

```
        fem |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |  2,049,706       45.81       45.81
          1 |  2,424,890       54.19      100.00
------------+-----------------------------------
      Total |  4,474,596      100.00
```

`tab publico, miss`:

```
    publico |      Freq.     Percent        Cum.
------------+-----------------------------------
          0 |  4,286,382       95.79       95.79
          1 |    188,214        4.21      100.00
------------+-----------------------------------
      Total |  4,474,596      100.00
```

`sum wage_sm, detail`:

```
                           wage_sm
-------------------------------------------------------------
      Percentiles      Smallest
 1%     .0018039       .0005882
 5%     .0024706       .0005882
10%     .0029474       .0005882       Obs           4,407,204
25%     .0046316       .0005882       Sum of wgt.   4,407,204

50%     1.201945                      Mean           1.262054
                        Largest       Std. dev.      1.684304
75%     1.695223       143.3628
90%     2.630627       145.1833       Variance       2.836881
95%     3.674941       145.7529       Skewness       10.84614
99%     6.875994       146.2577       Kurtosis       451.9045
```

`count if !missing(maeb)` →

```
  2,967,493
```

### diag09_build2.log

**A1 — média de empem3112/vínculoativo3112 por arquivo:**

```
  cpf_fila_07  ( 2007): empem3112 media=0.615  N=409227  (1.000 => so empregados)
  cpf_fila_081 ( 2008): empem3112 media=1.000  N=289810  (1.000 => so empregados)
  cpf_fila_092 ( 2009): empem3112 media=1.000  N=311423  (1.000 => so empregados)
  cpf_fila_101 ( 2010): empem3112 media=0.000  N=256765  (1.000 => so empregados)
  cpf_fila_102 ( 2010): empem3112 media=1.000  N=346485  (1.000 => so empregados)
  cpf_fila_11  ( 2011): vinc media=0.553  N=677823
  cpf_fila_12  ( 2012): vinc media=0.561  N=706676
  cpf_fila_13  ( 2013): vinc media=0.560  N=731684
  cpf_fila_14  ( 2014): vinc media=0.561  N=744703
```

`compress`: hrs double→byte, estabsz double→byte (50.290.982 bytes saved).

`di "N painel (crianca x resp x ano) = " _N` →

```
N painel (crianca x resp x ano) = 3592213
```

`table rais_year` (mean fem, mean emp, p50 wsm, count wsm):

```
---------------------------------------------------------------------------------------
          |             Mean             50th percentile   Number of non-missing values
          |  (firstnm) fem   (max) emp         (max) wsm                      (max) wsm
----------+----------------------------------------------------------------------------
rais_year |
  2007    |       .8222343    .7498276              1.74                        327,746
  2008    |       .8226376           1              1.72                        281,982
  2009    |       .8274435           1              1.66                        303,970
  2010    |        .838625    .7217069              1.58                        468,815
  2011    |       .8459408    .7077438              1.61                        517,522
  2012    |       .8503929    .7095253              1.56                        545,335
  2013    |       .8542178    .7051948              1.56                        567,161
  2014    |       .8566869     .702354              1.59                        579,682
  Total   |       .8431454     .760076              1.62                      3,592,213
---------------------------------------------------------------------------------------
```

### diag09_A.log

**A2 — coorte 2011: emp por ano calendário** (`table rais_year if ano_nasc==2011`):

```
----------------------------------------------------
          |      Mean   Number of non-missing values
----------+-----------------------------------------
rais_year |
  2007    |  .7472832                         35,336
  2008    |         1                         30,732
  2009    |         1                         33,964
  2010    |  .7131355                         51,669
  2011    |  .7149157                         45,804
  2012    |  .6535185                         50,248
  2013    |  .6907393                         53,657
  2014    |  .6970241                         56,285
  Total   |  .7543522                        357,695
----------------------------------------------------
```

Nota impressa: "(2008/2009 = 1.000 por construcao do arquivo; 2010 e a partir = ~0.7)".

**A2 — os mesmos por tempo relativo** (`table rel if ano_nasc==2011 & inrange(rel,-5,6)`):

```
-------------------
        |      Mean
--------+----------
rel     |
  -4    |  .7472832
  -3    |         1
  -2    |         1
  -1    |  .7131355
  0     |  .7149157
  1     |  .6535185
  2     |  .6907393
  3     |  .6970241
  Total |  .7543522
-------------------
```

**A3 — placebo, FEMININO (fem==1)** (`table rel ... stat(mean emp) stat(count emp)`):

```
--------------------------------------------------
        |      Mean   Number of non-missing values
--------+-----------------------------------------
rel     |
  -5    |  .7965923                        212,986
  -4    |  .7796927                        273,518
  -3    |  .7658457                        316,142
  -2    |  .7557682                        337,323
  -1    |  .7443721                        329,072
  0     |  .7503681                        240,414
  1     |  .6558803                        220,525
  2     |  .7034808                        195,070
  3     |  .7063497                        160,875
  4     |  .7045494                        121,357
  5     |  .7056608                         86,825
  6     |  .7075595                         57,239
  Total |  .7400404                      2,551,346
--------------------------------------------------
```

**A3 — placebo, MASCULINO (fem==0):**

```
--------------------------------------------------
        |      Mean   Number of non-missing values
--------+-----------------------------------------
rel     |
  -5    |  .8247129                         34,395
  -4    |   .812304                         43,693
  -3    |  .8052783                         50,698
  -2    |  .7960023                         54,481
  -1    |  .7932742                         55,934
  0     |  .7894852                         50,310
  1     |  .7765601                         47,722
  2     |  .7714299                         43,024
  3     |  .7693793                         35,734
  4     |  .7650424                         27,622
  5     |  .7598128                         20,509
  6     |  .7570801                         14,124
  Total |  .7889057                        478,246
--------------------------------------------------
```

**A4 — emp por tempo relativo, por coorte (só feminino), `stat(mean emp) nototals`:**

Coorte 2009:

```
rel  |      Mean
-----+----------
  -2 |   .731986
  -1 |         1
  0  |         1
  1  |  .6424854
  2  |  .6805197
  3  |  .6900144
  4  |  .6920437
  5  |  .7013067
```

Coorte 2010:

```
rel  |      Mean
-----+----------
  -3 |  .7340923
  -2 |         1
  -1 |         1
  0  |  .7194604
  1  |  .6236953
  2  |  .6891999
  3  |  .6904482
  4  |   .690148
```

Coorte 2011:

```
rel  |      Mean
-----+----------
  -3 |         1
  -2 |         1
  -1 |  .7047052
  0  |  .7071481
  1  |  .6351003
  2  |  .6818966
  3  |  .6886179
```

Coorte 2012:

```
rel  |      Mean
-----+----------
  -3 |         1
  -2 |   .719633
  -1 |  .6964967
  0  |  .7114818
  1  |  .6269869
  2  |  .6864127
```

Coorte 2013:

```
rel  |      Mean
-----+----------
  -3 |  .7236135
  -2 |  .7097536
  -1 |  .7014936
  0  |  .7223396
  1  |  .6136561
```

**A5 — painel balanceado:**

`count if nyr==8 & rais_year==2007` →

```
  115,449
```

`keep if nyr==8` → (2,668,621 observations deleted).

emp por tempo relativo (balanceado, feminino):

```
--------------------------------------------------
        |      Mean   Number of non-missing values
--------+-----------------------------------------
rel     |
  -5    |  .9192711                         56,634
  -4    |  .9157145                         65,468
  -3    |  .9091478                         70,268
  -2    |  .9162031                         70,826
  -1    |  .9510897                         67,634
  0     |  .9142824                         60,011
  1     |  .8381392                         51,569
  2     |  .8819563                         42,713
  3     |  .8873954                         33,924
  4     |  .8845003                         25,065
  5     |  .8827694                         17,231
  6     |  .8867997                         10,424
  Total |  .9052674                        571,767
--------------------------------------------------
```

### diag09_BCDE.log

`keep if fem==1` → (563,455 observations deleted).

**B1:**

```
count if tagcm==1  →  712,639
  criancas com responsavel feminino = 712639
count if tagm==1   →  712,639
  maes distintas = 712639
```

**B2:** `duplicates drop` (respid firstbirth) → (2,316,119 observations deleted).

```
count if inrange(firstbirth,2009,2013)  →  333,746
  maes com 1o filho 2009-2013 = 333746
```

**B3 — `tab npre npos`** (após `keep if inrange(firstbirth,2009,2013)`, 378.893 obs. deleted):

```
           |                                     npos
      npre |         0          1          2          3          4          5          6 |     Total
-----------+-----------------------------------------------------------------------------+----------
         0 |         0     31,544     24,992     15,347      8,661      3,691        692 |    84,927
         1 |    20,628     10,891     13,378      9,747      7,400      4,545      1,836 |    68,425
         2 |    11,479      8,618     13,264      9,615      7,558      6,192      6,609 |    63,335
         3 |     5,666      6,232     11,177      8,308      6,891      7,562          0 |    45,836
         4 |     4,414      4,522     10,003      8,022      8,620          0          0 |    35,581
         5 |     2,322      3,033      8,952      9,167          0          0          0 |    23,474
         6 |       896      1,648      9,624          0          0          0          0 |    12,168
-----------+-----------------------------------------------------------------------------+----------
     Total |    45,405     66,488     91,390     60,206     39,130     21,990      9,137 |   333,746
```

```
count if npre>=2 & npos>=3  →  78,544
  N maes com >=2 pre E >=3 pos = 78544
```

**B4 — idade da mãe no 1º nasc.** `duplicates drop` → (1,893,508 deleted); `gen idade_mae` → (439,107 missing); `keep if inrange(firstbirth,2009,2013)` → (597,503 deleted).

`sum idade_mae, detail`:

```
                          idade_mae
-------------------------------------------------------------
      Percentiles      Smallest
 1%            4             -4
 5%           17             -3
10%           19             -3       Obs             321,022
25%           22             -3       Sum of wgt.     321,022

50%           26                      Mean           28.25794
                        Largest       Std. dev.      14.00427
75%           32            112
90%           37            112       Variance       196.1196
95%           40            112       Skewness       3.775904
99%          106            112       Kurtosis         21.826
```

```
count if idade_mae<18 & !missing(idade_mae)  →  20,977   ("<18 anos: 20977")
count if idade_mae>40 & !missing(idade_mae)  →  15,960   (">40 anos: 15960")
count if missing(idade_mae)                  →  216,725  ("missing: 216725")
```

B5: nota "escolaridade NAO foi retida no painel (grinstrucao vs escolaridadeapos2005 = escalas diferentes)".

**Parte C** — nota impressa: "ATENCAO: 2008/2009 sao arquivos so-empregados -> emp inflado nesses anos (artefato)". `keep if inrange(firstbirth,2009,2013)` → (1,612,275 deleted). `collapse (max) emp wsm hrs publico (firstnm) estabsz, by(respid rel firstbirth)`.

**C1 — emp (incondicional):**

```
--------------------------------------------------
        |      Mean   Number of non-missing values
--------+-----------------------------------------
rel     |
  -5    |  .8645537                         56,192
  -4    |  .9106694                         84,775
  -3    |  .8464257                        126,766
  -2    |  .7995873                        174,470
  -1    |  .7643662                        193,805
  0     |  .7415916                        173,249
  1     |  .6267074                        198,035
  2     |  .6847042                        159,501
  3     |  .6895842                        116,650
  4     |  .6909993                         71,372
  5     |  .7013067                         32,371
  Total |  .7461033                      1,387,186
--------------------------------------------------
```

**C2 — salário SM incondicional (`wsm0`, sem vínculo=0)** — `replace wsm0=0 ...` (352,668 real changes):

```
rel     |      Mean
--------+----------
  -5    |  1.887325
  -4    |   1.92862
  -3    |  1.776151
  -2    |  1.679981
  -1    |  1.597908
  0     |  1.549758
  1     |  1.347755
  2     |  1.424429
  3     |  1.417676
  4     |  1.422691
  5     |   1.47552
  Total |  1.567754
```

**C3 — salário SM condicional a emprego (mean, p50):**

```
        |      Mean   50th percentile
--------+----------------------------
rel     |
  -5    |  2.183005              1.71
  -4    |  2.117805              1.67
  -3    |  2.098414              1.65
  -2    |  2.101061              1.65
  -1    |    2.0905              1.62
  0     |  2.089772               1.6
  1     |  2.150533              1.63
  2     |  2.080357               1.6
  3     |  2.055841              1.59
  4     |  2.058889              1.61
  5     |  2.103958              1.64
  Total |  2.101256              1.63
```

**C4 — horas condicional a emprego:**

```
rel     |      Mean
--------+----------
  -5    |         .
  -4    |         .
  -3    |         .
  -2    |  41.92881
  -1    |  41.97332
  0     |  41.79841
  1     |  41.77743
  2     |  41.90566
  3     |  41.98504
  4     |  42.01109
  5     |  42.03894
  Total |  41.90026
```

**C5 — setor público condicional a emprego:**

```
rel     |      Mean
--------+----------
  -5    |  .0532719
  -4    |  .0527059
  -3    |  .0515946
  -2    |  .0505864
  -1    |  .0507162
  0     |  .0588652
  1     |  .0661993
  2     |  .0606349
  3     |  .0610269
  4     |  .0625127
  5     |  .0657651
  Total |  .0566666
```

### diag09_DE.log

`keep if fem==1` → (563,455 deleted); `keep if inrange(firstbirth,2009,2013)` → (1,612,275 deleted).

merge com `child_expo.dta`:

```
    Result                      Number of obs
    -----------------------------------------
    Not matched                            10
        from master                        10
        from using                          0
    Matched                         1,416,473
    -----------------------------------------
```

`gen idade_ei ...` → (136,606 missing). merge com `cep_renda_pop_2010.dta`:

```
    Result                      Number of obs
    -----------------------------------------
    Not matched                        22,031
        from master                    22,031
        from using                          0
    Matched                         1,394,452
    -----------------------------------------
```

**D1 — emp por rel × expo12_1km** (`gen expo1=expo12_1km>=1`; 10 missing). expo12==0:

```
rel  |      Mean
-----+----------
  -3 |  .8506053
  -2 |  .8042536
  -1 |  .7724413
  0  |  .7460293
  1  |   .631192
  2  |  .6883929
  3  |  .6928643
  4  |  .6924114
```

expo12>=1:

```
rel  |      Mean
-----+----------
  -3 |  .8412883
  -2 |  .7937993
  -1 |  .7544459
  0  |  .7360388
  1  |  .6210809
  2  |  .6798924
  3  |  .6851609
  4  |  .6890215
```

**D1 — por quartil de estoque_1km (rel 0,+1):**

```
    |          4 quantiles of estoque_1km
    |         1          2          3          4
----+-------------------------------------------
rel |
  0 |  .7506687   .7450543   .7417825    .723454
  1 |  .6326039   .6281512   .6271986   .6151195
```

**D2 — emp por rel × quartil de renda do CEP:**

```
     |             4 quantiles of renda
     |         1          2          3          4
-----+-------------------------------------------
rel  |
  -1 |  .7432155   .7546042   .7689462   .7908654
  0  |  .7254503   .7331199   .7440726   .7632265
  1  |  .6096134   .6179727   .6301782   .6498913
  2  |  .6674571   .6751618   .6898202   .7090816
```

**D3 — emp por rel × EI antes 12m.** 1º filho matriculado EI <12m (ei12==1):

```
rel  |      Mean
-----+----------
  -3 |  .8440591
  -2 |  .7607786
  -1 |  .7619799
  0  |  .7509765
  1  |  .6679109
  2  |  .7090641
  3  |  .7185919
  4  |  .7279188
```

não <12m (ei12==0):

```
rel  |      Mean
-----+----------
  -3 |  .8467571
  -2 |  .8049752
  -1 |  .7646846
  0  |  .7403155
  1  |  .6209954
  2  |   .682439
  3  |  .6884082
  4  |  .6894047
```

**D4 — emp por rel × nº de filhos.** 1 filho (multi==0):

```
rel  |      Mean
-----+----------
  -3 |  .8464257
  -2 |  .7995873
  -1 |  .7643662
  0  |  .7415916
  1  |  .6267074
  2  |  .6847042
  3  |  .6895842
  4  |  .6909993
```

2+ filhos (multi==1): **erro, sem tabela produzida:**

```
       _table::compute():  3301  subscript invalid
      st_collect_table():     -  function returned error
                 <istmt>:     -  function returned error
r(3301);

end of do-file
r(3301);
```

O log termina aqui; a Parte E deste `.do` não foi executada neste log.

### diag09_E.log (só existe o .log; não há diag09_E.do)

Re-execução isolada da Parte E. `keep if fem==1` → (563,455 deleted); `by respid: keep if _n==1` → (2,316,119 deleted).

**E1 — `tab ultimo` (último ano observado por mãe):**

```
     ultimo |      Freq.     Percent        Cum.
------------+-----------------------------------
       2007 |     17,575        2.47        2.47
       2008 |      9,913        1.39        3.86
       2009 |      1,118        0.16        4.01
       2010 |     22,628        3.18        7.19
       2011 |     34,671        4.87       12.05
       2012 |     49,840        6.99       19.05
       2013 |     80,288       11.27       30.31
       2014 |    496,606       69.69      100.00
------------+-----------------------------------
      Total |    712,639      100.00
```

```
count if ultimo<2014  →  216,033
    de 712639 maes (total)
```

**E2 — `tab dif` (ultimo − firstbirth), inrange(dif,-5,7):**

```
        dif |      Freq.     Percent        Cum.
------------+-----------------------------------
         -5 |     10,668        1.57        1.57
         -4 |     34,345        5.07        6.64
         -3 |     60,523        8.93       15.58
         -2 |     77,127       11.38       26.96
         -1 |     93,414       13.79       40.75
          0 |     69,354       10.24       50.99
          1 |     71,587       10.57       61.56
          2 |     66,243        9.78       71.33
          3 |     60,799        8.97       80.31
          4 |     49,523        7.31       87.62
          5 |     39,507        5.83       93.45
          6 |     31,269        4.62       98.07
          7 |     13,106        1.93      100.00
------------+-----------------------------------
      Total |    677,465      100.00
```

## O que o log NÃO permite recuperar

- **Não há `diag09_E.do`.** Só o `.log` foi preservado; o código exato que gerou `diag09_E.log` é inferido a partir das linhas de comando ecoadas no próprio log (e do trecho E de `diag09_DE.do`), não de um `.do` fonte.
- **`diag09_DE` interrompeu em D4 (2+ filhos) com `r(3301)`** ("subscript invalid"): a tabela de emp por rel para mães com 2+ filhos não existe em nenhum log, e a Parte E de `diag09_DE.do` não rodou nessa execução (só foi obtida depois em `diag09_E.log`).
- **`panel_es.dta` é sobrescrito.** `diag09_build.do` salva uma versão (N=4.474.596, painel empilhado por vínculo) e `diag09_build2.do` salva outra por cima (N=3.592.213, colapsado por criança×resp×ano). As análises A–E usam `panel_es.dta`; os contornos de amostra (ex.: `keep if fem==1` deletando 563.455 obs.) correspondem à versão de `build2`. Qual arquivo estava em disco no momento de cada rodada não é verificável só pelos logs.
- **Arquivos de origem não mostrados:** os `cpf_fila_*.dta` (brutos RAIS-CPF), `child_expo.dta` e `cep_renda_pop_2010.dta` são usados mas seu conteúdo/dicionário não aparece; só se veem contagens de merge e de missing.
- **Variáveis descartadas antes de estatísticas:** ex.: no build, `wnom`, `njur`, `sex_raw` não têm distribuição impressa além do que sobrou em `fem`/`publico`/`wage_sm`; `hrs`/`estabsz` só aparecem via `compress`.
- **Macros/laços:** os laços `foreach spec` e `forvalues c` imprimem resultados por iteração, mas os valores intermediários das macros locais (`f`, `yr`, `c`) só aparecem quando ecoados por `di`.
- **B4 idade_mae:** há valores implausíveis nas caudas (Smallest −4/−3; Largest 112; p99=106); o log mostra os números mas não como foram tratados adiante.
- **C4 horas:** rel −5, −4, −3 aparecem como `.` (missing) — o log não permite saber se por ausência da variável `hrs` nesses anos ou por filtro.
- **Caminho no cabeçalho dos logs** grava `...\_audit\...` (não `02_audit`); não é possível confirmar pelos logs se é o mesmo diretório renomeado.
- **Contagens de linha** são por `wc -l` (quebras de linha); arquivos sem nova linha final podem ter uma linha de conteúdo a mais do que o número indicado.
