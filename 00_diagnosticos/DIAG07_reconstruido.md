> RECONSTRUÇÃO. Este arquivo foi gerado a partir dos logs em 02_audit\ e não
> é o relatório original, que não foi preservado em .md. Os números vêm dos
> logs; a estrutura e as regras de decisão foram reconstruídas e podem estar
> incompletas. Fonte primária: os arquivos .log listados ao final.

# DIAG07 — reconstrução a partir dos logs de auditoria

## Arquivos lidos

| Arquivo | Linhas | Conteúdo (a partir dos comandos do .do) |
|---|---|---|
| `diag07_build.do` | 91 | Monta o painel RAIS. A1: para cada `cpf_fila_101/102/11/12/13/14` faz `use ano cd_aluno_sme` e `tab ano`. Empilha (`append`) `cpf_fila_11..14` (exclui 101/102, "esquema antigo sem idade/SM"), renomeia variáveis (`vínculoativo3112`→`vinc`, `vlremunmédiasm`→`remun_s`, `qtdhoracontr`→`horas`, `escolaridadeapós2005`→`escol`, `sexotrabalhador`→`sexo`), gera `respid` via `egen group(cpf)`, `destring remun_s`, `emp=(vinc==1)`, faz `collapse (max) emp remun horas (firstnm) sexo idade escol ano_nasc mes_nasc, by(cd_aluno_sme respid ano)` e salva `rais_panel.dta`. A2: nº de anos RAIS distintos por criança (`tab nc`, `sum nanos, detail`). A3: crianças de `B_novo` com registro RAIS por ano (`tab ano`). A4: vínculo em ano anterior ao nascimento (`pre = ano<ano_nasc`). |
| `diag07_build.log` | 313 | Log da execução acima. **Termina com erro `r(2000)` (no observations)** no bloco A4 (`duplicates drop` sobre 0 obs). |
| `diag07_BC.do` | 134 | Parte B (quem é o adulto, `rais_panel`): B1 `tab sexo`; B2 `idade_no_nasc=idade-(ano-ano_nasc)`, `_pctile` p5/25/50/75/95; B3 `table sexo` (p50/mean/count idade); B4 nº de `respid` distintos por criança. B5: `cpf_resp_aluno` na Fila (`$fila = Fila1018.dta`) como indicador (`tem_resp`), `collapse (max)`, merge com `B_novo`, merge com `rais_panel` (`tem_rais`). Parte C (primeiro estágio, corte 31/03, coortes 2009–2015): `idade_ei` em meses, indicadores `ei12/ei18/ei24/ei36`, `abril=mes_nasc==4`; C1 P(EI<12m) março vs abril por coorte com `ttest`; C2 idem 18/24/36m; C3 mediana `idade_ei`; C4 P(`ever_mat`); C5 `table mes_nasc` de `ei12` (pooled). |
| `diag07_BC.log` | 379 | Log completo da Parte B e Parte C. Termina em `=== FIM BC ===`. |
| `diag07_DE.do` | 108 | Parte D (desfechos de trabalho): D1 taxa `emp` por ano sobre todo `B_novo` (não-RAIS=0); D2 event study cru `emp` por `reltime=ano-ano_nasc` (março e abril); D3 `remun` por reltime | emp; D4 `horas` por reltime | emp; D5 N com emp em ≥3 anos incl. ≥1 pré-nascimento. Parte E: E1 `table ano_nasc grp` de `elig_berc1`; E2 razão marco/abril; E3 balanço `ttest` (`fem`, `idade_no_nasc`, `escol`, `remun`). |
| `diag07_DE.log` | 317 | Log da Parte D (completa) e início da Parte E. **Termina com erro `r(109)` em E1**: "string variables not allowed in layout; grp is a string variable". E2/E3 não rodaram neste log. |
| `diag07_E.do` | 43 | Reexecução isolada da Parte E, contornando o erro: E1 imprime elegibilidade via `di` (sem `table`); E2 razão marco/abril de N por coorte (sobre `B_novo`); E3 balanço marco vs abril (`ttest` de `fem`, `idade_no_nasc`, `escol`, `remun`) com `tab mes_nasc`. |
| `diag07_E.log` | 111 | Log completo da Parte E. Termina em `=== FIM E ===`. |

> Nota: o cabeçalho de todos os `.log` grava o caminho como `...\_audit\diag07_*.log` (com `_audit`, não `02_audit`). Transcrito como está nos logs.

## Estatísticas e tabelas encontradas (transcritas)

### diag07_build.log

**A1 — N e cobertura de `ano` por arquivo `cpf_fila`**

| Arquivo | N | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 |
|---|---|---|---|---|---|---|---|---|---|---|
| cpf_fila_101 | 256.765 | 12.477 | 14.699 | 28.887 | 29.297 | 27.593 | 27.820 | 34.680 | 30.168 | 51.144 |
| cpf_fila_102 | 346.485 | 16.745 | 19.988 | 39.640 | 40.043 | 38.284 | 38.088 | 47.545 | 38.861 | 67.291 |
| cpf_fila_11 | 677.823 | 31.627 | 39.439 | 73.246 | 76.162 | 73.380 | 74.340 | 91.224 | 79.339 | 139.066 |
| cpf_fila_12 | 706.676 | 31.672 | 41.888 | 77.990 | 75.041 | 74.219 | 76.928 | 96.659 | 82.516 | 149.763 |
| cpf_fila_13 | 731.684 | 31.437 | 41.930 | 83.434 | 80.297 | 73.095 | 78.185 | 101.027 | 87.069 | 155.210 |
| cpf_fila_14 | 744.703 | 30.746 | 41.496 | 82.666 | 84.233 | 76.453 | 75.403 | 100.604 | 88.950 | 164.152 |

(Percentuais/cumulativos por ano constam do log; ex.: em cpf_fila_101, 2018 = 19,92%.)

**Montagem do painel (cpf_fila_11..14):**
- `N linhas empilhadas (11-14) = 2860886`
- `destring remun_s ... remun generated as double` (all characters numeric)
- `compress ... (0 bytes saved)`
- `rais_panel.dta ... not found` (mensagem: arquivo prévio não existia) → `saved`
- `N (crianca x responsavel x ano) = 757122`

**A2 — nº de anos RAIS distintos por criança**

| nc | Freq. | Percent | Cum. |
|---|---|---|---|
| 1 | 757.122 | 100,00 | 100,00 |
| Total | 757.122 | 100,00 | |

`sum nanos, detail`: todos os percentis (1%,5%,10%,25%,50%,75%,90%,95%,99%) = 1; Obs = 757.122; Mean = 1; Std. dev. = 0; Variance = 0; Skewness = . ; Kurtosis = .

**A3 — crianças de B_novo com ≥1 registro RAIS por ano** (`merge`: Matched = 757.102, Not matched = 0)

| Ano | Freq. | Percent | Cum. |
|---|---|---|---|
| 2010 | 31.668 | 4,18 | 4,18 |
| 2011 | 42.673 | 5,64 | 9,82 |
| 2012 | 84.084 | 11,11 | 20,93 |
| 2013 | 85.186 | 11,25 | 32,18 |
| 2014 | 80.694 | 10,66 | 42,84 |
| 2015 | 80.873 | 10,68 | 53,52 |
| 2016 | 103.093 | 13,62 | 67,13 |
| 2017 | 89.401 | 11,81 | 78,94 |
| 2018 | 159.430 | 21,06 | 100,00 |
| Total | 757.102 | 100,00 | |

**A4 — vínculo em ano antes do nascimento (`pre = ano<ano_nasc`)**
- `count if pre==1` → `0`
- `keep if pre==1` → `(757,122 observations deleted)`
- `duplicates drop` → `no observations` → `r(2000)` (fim do do-file com erro)

### diag07_BC.log

**Parte B (`rais_panel.dta`)**
- `N linhas painel = 757122`
- `count if tagc==1` (crianças distintas) → `757,122`

**B1 — `tab sexo, miss` (firstnm)**

| sexo | Freq. | Percent | Cum. |
|---|---|---|---|
| 1 | 101.913 | 13,46 | 13,46 |
| 2 | 655.209 | 86,54 | 100,00 |
| Total | 757.122 | 100,00 | |

**B2 — idade do adulto no ano do nascimento (`idade_no_nasc`), percentis**
`p5=17  p25=21  p50=26  p75=31  p95=39`

**B3 — `table sexo` (idade_no_nasc)**

| sexo | 50th pct | Mean | N não-missing |
|---|---|---|---|
| 1 | 28 | 28,50604 | 101.913 |
| 2 | 26 | 26,23249 | 655.209 |
| Total | 26 | 26,53852 | 757.122 |

**B4 — nº de responsáveis (`respid`) distintos por criança**
`duplicates drop` → 0 duplicatas; `tab nresp`: valor 1 = 757.122 (100,00%); Total 757.122.

**B5 — cpf_resp em B_novo e casamento com RAIS**
- merge Fila×`B_novo`: Matched = 1.524.560, Not matched = 0
- `N B_novo = 1524560`
- `sum tem_resp`: Obs = 1.524.560; Mean = ,9806941; Std. dev. = ,1375979; Min = 0; Max = 1
- merge `rais_panel`: Not matched = 767.458 (todos do master), Matched = 757.102; `replace tem_rais=0` → 767.458 real changes
- `sum tem_rais`: Obs = 1.524.560; Mean = ,4966036; Std. dev. = ,4999886; Min = 0; Max = 1
- `sum tem_rais if tem_resp==1`: Obs = 1.495.127; Mean = ,5063797; Std. dev. = ,4999595; Min = 0; Max = 1

**Parte C** (após `keep if inrange(ano_nasc,2009,2015)` → 528.417 obs deletadas; `idade_ei` gera 98.257 missing; `keep if inlist(mes_nasc,3,4)` → 819.702 obs deletadas)

**C1 — P(EI antes 12m), março vs abril, por coorte**

| coorte | março | abril | dif | se | p |
|---|---|---|---|---|---|
| 2009 | 0.033 | 0.043 | -0.010 | 0.0027 | 0.0004 |
| 2010 | 0.028 | 0.026 | 0.002 | 0.0022 | 0.4114 |
| 2011 | 0.020 | 0.026 | -0.006 | 0.0019 | 0.0034 |
| 2012 | 0.211 | 0.186 | 0.026 | 0.0048 | 0.0000 |
| 2013 | 0.233 | 0.210 | 0.023 | 0.0050 | 0.0000 |
| 2014 | 0.255 | 0.229 | 0.026 | 0.0052 | 0.0000 |
| 2015 | 0.230 | 0.384 | -0.153 | 0.0055 | 0.0000 |

**C2 — antes de 18/24/36 meses, por coorte**

*ei18*
| coorte | março | abril | dif | p |
|---|---|---|---|---|
| 2009 | 0.072 | 0.074 | -0.001 | 0.7592 |
| 2010 | 0.058 | 0.050 | 0.008 | 0.0116 |
| 2011 | 0.057 | 0.052 | 0.004 | 0.1442 |
| 2012 | 0.242 | 0.207 | 0.035 | 0.0000 |
| 2013 | 0.263 | 0.238 | 0.026 | 0.0000 |
| 2014 | 0.296 | 0.269 | 0.027 | 0.0000 |
| 2015 | 0.335 | 0.418 | -0.083 | 0.0000 |

*ei24*
| coorte | março | abril | dif | p |
|---|---|---|---|---|
| 2009 | 0.104 | 0.112 | -0.008 | 0.0827 |
| 2010 | 0.089 | 0.091 | -0.002 | 0.6454 |
| 2011 | 0.281 | 0.285 | -0.004 | 0.4585 |
| 2012 | 0.435 | 0.415 | 0.021 | 0.0005 |
| 2013 | 0.438 | 0.539 | -0.101 | 0.0000 |
| 2014 | 0.523 | 0.550 | -0.027 | 0.0000 |
| 2015 | 0.577 | 0.614 | -0.037 | 0.0000 |

*ei36*
| coorte | março | abril | dif | p |
|---|---|---|---|---|
| 2009 | 0.210 | 0.221 | -0.011 | 0.0676 |
| 2010 | 0.378 | 0.381 | -0.003 | 0.7034 |
| 2011 | 0.509 | 0.513 | -0.004 | 0.5119 |
| 2012 | 0.611 | 0.605 | 0.005 | 0.3607 |
| 2013 | 0.667 | 0.696 | -0.029 | 0.0000 |
| 2014 | 0.752 | 0.722 | 0.030 | 0.0000 |
| 2015 | 0.819 | 0.817 | 0.002 | 0.6981 |

**C3 — idade mediana da 1ª matrícula EI (meses), março vs abril**

| coorte | mediana março | mediana abril |
|---|---|---|
| 2009 | 45 | 44 |
| 2010 | 38 | 40 |
| 2011 | 34 | 33 |
| 2012 | 26 | 31 |
| 2013 | 25 | 21 |
| 2014 | 22 | 21 |
| 2015 | 21 | 20 |

**C4 — P(alguma vez matriculado em EI), março vs abril**

| coorte | março | abril | dif | p |
|---|---|---|---|---|
| 2009 | 0.801 | 0.847 | -0.046 | 0.0000 |
| 2010 | 0.849 | 0.873 | -0.025 | 0.0000 |
| 2011 | 0.879 | 0.898 | -0.019 | 0.0000 |
| 2012 | 0.917 | 0.917 | -0.000 | 0.9983 |
| 2013 | 0.929 | 0.929 | 0.001 | 0.8651 |
| 2014 | 0.936 | 0.910 | 0.025 | 0.0000 |
| 2015 | 0.909 | 0.905 | 0.004 | 0.2891 |

**C5 — P(EI antes 12m) por mês de nascimento (coortes 2009–2015 pooled)**
(reload: `keep if inrange(ano_nasc,2009,2015)` → 528.417 deletadas; `idade_ei` 98.257 missing)

| mes_nasc | Mean | N não-missing |
|---|---|---|
| 1 | .1551031 | 82.616 |
| 2 | .1607973 | 79.765 |
| 3 | .1543127 | 90.025 |
| 4 | .166983 | 86.416 |
| 5 | .153455 | 88.293 |
| 6 | .1377705 | 83.102 |
| 7 | .1200099 | 84.568 |
| 8 | .1006541 | 82.252 |
| 9 | .0825809 | 82.174 |
| 10 | .0671932 | 79.011 |
| 11 | .05462 | 75.888 |
| 12 | .0445065 | 82.033 |
| Total | .1177331 | 996.143 |

`=== FIM BC ===`

### diag07_DE.log

**D1 — taxa de `emp` por ano sobre todo B_novo** (merge 1:m: Not matched 767.458 do master, Matched 757.102; `count if tag==1` = 1.524.560 = denominador NB)

| ano | emp médio (sobre B_novo) | N emp |
|---|---|---|
| 2010 | 0.0178 | 27.097 |
| 2011 | 0.0236 | 35.946 |
| 2012 | 0.0461 | 70.341 |
| 2013 | 0.0465 | 70.824 |
| 2014 | 0.0437 | 66.683 |
| 2015 | 0.0444 | 67.729 |
| 2016 | 0.0566 | 86.345 |
| 2017 | 0.0488 | 74.429 |
| 2018 | 0.0880 | 134.236 |

Distribuição do único ano RAIS (entre com RAIS) — `tab ano`: idêntica à tabela A3 acima (2010=31.668 … 2018=159.430; Total 757.102).

**D2 — event study cru: `emp` por `reltime = ano - ano_nasc`**
(merge Matched 757.102; `keep if inrange(ano_nasc,2009,2015)` → 244.042 deletadas)
`sum reltime`: Obs = 513.060; Mean = 2,490122; Std. dev. = 1,651303; Min = 0; Max = 9.

*março (mes_nasc==3):*
| reltime | Mean emp | N |
|---|---|---|
| 0 | .8748224 | 7.741 |
| 1 | .8341232 | 9.284 |
| 2 | .8156885 | 8.860 |
| 3 | .8164181 | 8.247 |
| 4 | .8139483 | 8.890 |
| 5 | .8035773 | 3.019 |
| 6 | .8333333 | 24 |
| 7 | .5 | 4 |
| 8 | .6666667 | 3 |
| Total | .8283122 | 46.072 |

*abril (mes_nasc==4):*
| reltime | Mean emp | N |
|---|---|---|
| 0 | .872879 | 7.308 |
| 1 | .8264159 | 8.987 |
| 2 | .8244265 | 7.803 |
| 3 | .8129216 | 7.708 |
| 4 | .8090965 | 4.903 |
| 5 | .7987248 | 5.803 |
| 6 | .7891892 | 1.480 |
| 7 | .8695652 | 23 |
| 8 | .75 | 4 |
| Total | .8245985 | 44.019 |

**D3 — remuneração (SM) por reltime | emp**

*março:*
| reltime | Mean | 50th pct | N |
|---|---|---|---|
| 0 | 2.355284 | 1.74 | 6.772 |
| 1 | 2.39657 | 1.79 | 7.744 |
| 2 | 2.483968 | 1.8 | 7.227 |
| 3 | 2.441322 | 1.79 | 6.733 |
| 4 | 2.449431 | 1.77 | 7.236 |
| 5 | 2.306777 | 1.72 | 2.426 |
| 6 | 2.08 | 1.64 | 20 |
| 7 | 1.37 | 1.37 | 2 |
| 8 | 1.73 | 1.73 | 2 |
| Total | 2.417751 | 1.77 | 38.162 |

*abril:*
| reltime | Mean | 50th pct |
|---|---|---|
| 0 | 2.348109 | 1.77 |
| 1 | 2.350672 | 1.75 |
| 2 | 2.502778 | 1.79 |
| 3 | 2.444662 | 1.8 |
| 4 | 2.467018 | 1.77 |
| 5 | 2.371325 | 1.76 |
| 6 | 2.26482 | 1.71 |
| 7 | 2.1925 | 1.85 |
| 8 | 1.79 | 1.82 |
| Total | 2.405861 | 1.77 |

**D4 — horas contratadas por reltime | emp**

*março:*
| reltime | Mean | N |
|---|---|---|
| 0 | 42.8039 | 6.772 |
| 1 | 42.9016 | 7.744 |
| 2 | 42.79563 | 7.227 |
| 3 | 42.81227 | 6.733 |
| 4 | 42.90478 | 7.236 |
| 5 | 43.07502 | 2.426 |
| 6 | 43.6 | 20 |
| 7 | 44 | 2 |
| 8 | 44 | 2 |
| Total | 42.86054 | 38.162 |

*abril:*
| reltime | Mean |
|---|---|
| 0 | 42.82819 |
| 1 | 42.88798 |
| 2 | 42.82326 |
| 3 | 42.82206 |
| 4 | 42.92614 |
| 5 | 42.94908 |
| 6 | 42.99572 |
| 7 | 43 |
| 8 | 44 |
| Total | 42.87021 |

**D5 — N com emp em ≥3 anos incl. ≥1 pré-nascimento**
- `count if tagc==1 & npre>=1` → `0`
- `count if tagc==1 & nyears>=3` → `0`
- `count if tagc==1 & nyears>=3 & npre>=1` → `0`

**Parte E (neste log DE):**
- E1: após `keep if inrange(ano_nasc,2009,2015)` → 528.417 deletadas; `gen grp = cond(...)` → 819.702 missing gerados.
- `table ano_nasc grp ...` → **erro `r(109)`: "string variables not allowed in layout; grp is a string variable"** → fim do do-file. E2 e E3 não executaram neste log.

### diag07_E.log (reexecução da Parte E)

**E1 — elegibilidade Berçário I** (impresso via `di`)

| coorte | elig março | elig abril |
|---|---|---|
| 2009 | 2009 | 2010 |
| 2010 | 2010 | 2011 |
| 2011 | 2011 | 2012 |
| 2012 | 2012 | 2013 |
| 2013 | 2013 | 2014 |
| 2014 | 2014 | 2015 |
| 2015 | 2015 | 2016 |

**E2 — razão março/abril de N por coorte (B_novo)**

| coorte | N março | N abril | razão mar/abr |
|---|---|---|---|
| 2009 | 10.071 | 9.903 | 1.017 |
| 2010 | 11.109 | 10.692 | 1.039 |
| 2011 | 12.948 | 12.544 | 1.032 |
| 2012 | 14.562 | 13.178 | 1.105 |
| 2013 | 13.688 | 13.741 | 0.996 |
| 2014 | 13.656 | 13.279 | 1.028 |
| 2015 | 13.991 | 13.079 | 1.070 |

**E3 — balanço março vs abril nas vars do responsável (RAIS)**
(merge Matched 757.102; `keep if inrange(ano_nasc,2009,2015) & inlist(mes_nasc,3,4)` → 667.006 deletadas)

`tab mes_nasc` (com RAIS): 3 = 46.075 (51,14%); 4 = 44.021 (48,86%); Total = 90.096.

| var | março | abril | dif | se | p |
|---|---|---|---|---|---|
| fem | 0.866 | 0.866 | -0.0002 | 0.0023 | 0.9189 |
| idade_no_nasc | 26.829 | 26.615 | 0.2141 | 0.0463 | 0.0000 |
| escol | 6.598 | 6.598 | -0.0003 | 0.0091 | 0.9777 |
| remun | 2.269 | 2.253 | 0.0160 | 0.0158 | 0.3113 |

`=== FIM E ===`

## O que o log NÃO permite recuperar

- **`diag07_build.log` termina em erro `r(2000)`** no bloco A4: a linha `criancas distintas com vinculo pre-nascimento = _N` (`di`) não chegou a ser impressa; o valor não consta. (Confirma-se indiretamente por A4/D5: nenhum registro com `ano<ano_nasc`.)
- **`diag07_DE.log` termina em erro `r(109)`** no bloco E1 (variável string em `table`): os resultados E2 e E3 **não aparecem neste log**. Foram obtidos apenas na reexecução `diag07_E.log`.
- **Macros/parâmetros não expandidos no log:** os globais `$aud`, `$dsme` (`<NE_ROOT>\dados_restritos\Dados - SME\Atual (25.06)`) e `$fila` (`...\fila_espera\Fila1018.dta`) constam apenas dos `.do`; os `.log` não reexibem seus valores literais (exceto via caminhos de arquivos citados).
- **`B_novo.dta`**: não há no conjunto de logs um `.do`/`.log` que documente a construção de `B_novo.dta` (apenas é lido/mergeado). N total de `B_novo` = 1.524.560 (crianças distintas) aparece em BC/DE, mas a origem/variáveis completas não são mostradas.
- **`rais_panel.dta`**: as variáveis do painel são conhecidas pelos comandos (`emp, remun, horas, sexo, idade, escol, ano_nasc, mes_nasc, respid, ano, cd_aluno_sme`), mas rótulos de valor (ex.: codificação de `sexo` 1/2, escala de `escol`) não são exibidos nos logs.
- **Percentuais/cumulativos** de várias tabelas `tab` (A1 por ano) constam parcialmente no log; nesta reconstrução foram transcritas as frequências e (quando relevante) exemplos de percentuais, sem repetir todas as colunas Cum. de cada arquivo.
- **Discrepâncias de N entre execuções** aparecem nos logs mas não são explicadas por eles: em BC/DE a merge Fila×RAIS reporta "com RAIS" = 757.102 crianças (merge) enquanto `rais_panel` tem 757.122 linhas/crianças; em E3 `tab mes_nasc` soma 90.096 (46.075+44.021) enquanto BC parte C usa 90.025+86.416 etc. (contextos de filtro distintos). Os logs não trazem reconciliação.
- **Nenhum CPF ou nome aparece nos logs** (uso de `respid` via `egen group(cpf)` e `drop cpf`; indicadores `tem_resp` sem valor). Nada a redigir.

---
### Fonte primária (arquivos .log)
- `<NE_ROOT>\02_audit\diag07_build.log`
- `<NE_ROOT>\02_audit\diag07_BC.log`
- `<NE_ROOT>\02_audit\diag07_DE.log`
- `<NE_ROOT>\02_audit\diag07_E.log`

(.do correspondentes no mesmo diretório: `diag07_build.do`, `diag07_BC.do`, `diag07_DE.do`, `diag07_E.do`.)
