# DIAG10 — Reconstrução (PARCIAL)

> RECONSTRUÇÃO. Este arquivo foi gerado a partir dos logs em 02_audit\ e não
> é o relatório original, que não foi preservado em .md. Os números vêm dos
> logs; a estrutura e as regras de decisão foram reconstruídas e podem estar
> incompletas. Fonte primária: os arquivos .log listados ao final.

## Arquivos lidos

| Arquivo | Linhas | Tem log? | O que faz (a partir do código) |
|---|---|---|---|
| `diag10_III.do` | 66 | — (é o script) | Do-file Stata. Abre `fila_codesc.dta` e exporta `fila_codesc.csv`; bloco III1 lista variáveis do Fila buscando por protocolo/ordem/classificação; III2 mede empates de `dt_solicitacao` (nível **dia**, via `date()`) dentro de escola×série×ano na creche; III3 compara ordem por `dt_sol` vs ordem por `dt_enc` (correlação de ranks + concordância). |
| `diag10_III.log` | 170 | **SIM** — log salvo | Saída da execução de `diag10_III.do` (aberto 22 Jul 2026 18:27:26, fechado 18:27:45). |
| `diag10_III2.log` | 81 | **SIM** — log salvo | Saída de uma execução Stata **sem .do correspondente entre os arquivos listados** (registrar). Repete III2/III3 usando `clock()` (nível **segundo**) em vez de `date()`. Aberto 22 Jul 2026 18:29:36, fechado 18:29:55. |
| `diag10_ii12.py` | 48 | **NÃO** — sem log salvo | Script Python. Lê `turmas_modulo_2016_2017.csv`; conta TIPO ESCOLA / MODALIDADE / DATA BASE; filtra CRECHE; II1 = MODULO (capacidade) modal por SÉRIE; II2 = folga (MODULO − MATRICULA) por SÉRIE (exato/acima/abaixo). |
| `diag10_ii3.py` | 39 | **NÃO** — sem log salvo | Script Python. Lê `fila_codesc.csv`; casa códigos de escola da Fila com `perfil_turmas_jun2018.csv` (CRECHE) e com `parcerias_mar2023.csv`; mede sobreposição de escolas e conveniadas. |
| `diag10_ii45.py` | 66 | **NÃO** — sem log salvo | Script Python. II4 = capacidade (VAGOFER) por escola×agrupamento nos perfis jun2013/2015/2018 (CRECHE); II5 = parcerias (vagas contratadas/berçário, situações, OSC distintas, encerramentos por ano). |

**Observações sobre as fontes:**
- `diag10_III2.log` **não tem .do correspondente** entre os arquivos listados (o log existe, o script que o gerou não foi fornecido).
- Os três `.py` (`diag10_ii12.py`, `diag10_ii3.py`, `diag10_ii45.py`) **não possuem .log salvo**. Sua saída computada **não é recuperável**. Abaixo apenas descrevo, a partir do código, o que calculariam.
- Nota de caminho: os do-files/logs apontam para `...\Neighborhood Effects\_audit\...` no cabeçalho do log, enquanto o `.do` define `global aud` como `...\02_audit`. Transcrito como aparece; sem interpretação.

## Estatísticas e tabelas encontradas (transcritas)

### De `diag10_III.log` (nível DIA, via `date()`)

**Exportação de códigos:**
```
N codigos Fila exportados = 3745
```

**III1 — variáveis de protocolo/ordem/classificação na Fila:**
- Busca por `*protoc* *ordem* *classif* *posic* *rank* *numer* *inscri* *sequenc* *fila* *prior* *data*`: **nenhuma variável listada sob qualquer um desses padrões** (cada `ds *padrão*` não retornou nomes no log).
- Lista completa de variáveis do Fila (`ds`), como aparece (nomes abreviados pelo Stata):
```
ano           cd_esc_sol~o  dt_encamin~o  cd_serie_~to  cd_esc_mat~a  an_letivo~ia  cd_tipo_m~ia  cd_esc_rec~a  tipo_prior~o  mes_nasc      cep_aluno
cd_aluno_sme  an_letivo~ao  an_letivo~to  dt_matricula  cd_serie_~la  cd_esc_des~a  dt_recusa     cd_serie_~sa  cd_sexo_al~o  ano_nasc      cpf_resp_a~o
dt_solicit~o  cd_serie_~ao  cd_esc_enc~o  an_letivo~la  dt_desiste~a  cd_serie_~ia  an_letivo~sa  cd_tipo_m~sa  tp_raca_cor   cd_pais_mec
```

**III2 — empates de `dt_solicitacao` dentro de escola-série (nível dia):**
- `gen dt_enc = date(...)` → `(417,675 missing values generated)`
- `keep if !missing(dt_enc) & !missing(cd_esc_encaminhamento) & missing(tipo_prioridade_encaminhamento)` → `(731,766 observations deleted)`
- `keep if inlist(cd_serie_ensino_encaminhamento,1,4,27,28)` → `(660,118 observations deleted)`
```
N encaminhamentos creche (sem prioridade) = 1906180
```
- `sum empatado` (empatado = emp>0):

| Variable | Obs | Mean | Std. dev. | Min | Max |
|---|---|---|---|---|---|
| empatado | 1,906,180 | .5394192 | .4984438 | 0 | 1 |

- Amostra de `dt_solicitacao` (string), `list ... in 1/5`:
```
6/3/2018 16:20:28
5/3/2018 13:38:04
5/2/2018 15:38:58
5/2/2018 14:04:41
6/3/2018 08:38:57
```

**III3 — ordem de solicitação vs ordem de encaminhamento (nível dia):**
- `keep if ncell>=5` → `(22,162 observations deleted)`
- `corr rank_sol rank_enc` (obs=1,884,018):

| | rank_sol | rank_enc |
|---|---|---|
| rank_sol | 1.0000 | |
| rank_enc | 0.8853 | 1.0000 |

```
correlacao rank_sol x rank_enc (celulas >=5) = .88525532
```
- `gen concord = ...` → `(50,189 missing values generated)`
```
(concordancia media entre pares consecutivos por dt_sol) = .26846451
```
- Encerramento: `=== FIM III ===`

### De `diag10_III2.log` (nível SEGUNDO, via `clock()`)

- `gen clk_enc = clock(...)` → `(417,675 missing values generated)`
- `keep if !missing(clk_enc) & ...` → `(731,766 observations deleted)`
- `keep if inlist(cd_serie_ensino_encaminhamento,1,4,27,28)` → `(660,118 observations deleted)`
```
N = 1906180
```

**III2 (clock/segundos) — empates de `dt_solicitacao`:**
- `sum empatado` (empatado = emp>0):

| Variable | Obs | Mean | Std. dev. | Min | Max |
|---|---|---|---|---|---|
| empatado | 1,906,180 | .323993 | .4679975 | 0 | 1 |

**III3 (clock) — ordem sol vs enc:**
- `keep if ncell>=5` → `(22,162 observations deleted)`
- `corr rank_sol rank_enc` (obs=1,884,018):

| | rank_sol | rank_enc |
|---|---|---|
| rank_sol | 1.0000 | |
| rank_enc | 0.8853 | 1.0000 |

```
corr rank_sol x rank_enc (segundos, celulas>=5) = .88528796
```
- `gen inv = ...` → `(50,189 missing values generated)`
```
fracao de inversoes (par consecutivo por sol tem enc invertido) = 0
```

### Dos três `.py` — sem log — resultados não recuperáveis

**`diag10_ii12.py`** — sem log — resultados não recuperáveis. O que o código *calcularia* (sem números):
- Nº de linhas e lista de colunas de `turmas_modulo_2016_2017.csv`.
- Contagens (`Counter`) de TIPO ESCOLA (top 20), MODALIDADE, DATA BASE.
- Nº de turmas CRECHE e contagem por SERIE.
- II1: por SERIE (BERCARIO I/II, MINI GRUPO I/II), N, MODULO modal (top 3) e média de MODULO.
- II2: por SERIE, folga média (MODULO − MATRICULA), contagem/percentual EXATO (folga=0), ACIMA (matrícula>módulo) e ABAIXO.

**`diag10_ii3.py`** — sem log — resultados não recuperáveis. O que o código *calcularia*:
- Nº de códigos distintos de escola na Fila (de `fila_codesc.csv`).
- Perfil jun2018 CRECHE: nº de escolas distintas e quantas/percentual casam com a Fila.
- Parcerias: nº de escolas conveniadas distintas e quantas/percentual casam com a Fila.
- Nº de escolas CRECHE conveniadas (REDE="CON") no perfil 2018 e quantas aparecem em parcerias.

**`diag10_ii45.py`** — sem log — resultados não recuperáveis. O que o código *calcularia*:
- II4 (perfis jun2013/2015/2018, CRECHE): por ano, N turmas CRECHE, dicionário REDE, se tem coluna MODULO, VAGOFER preenchido (>0) e média, N células escola×série com capacidade, N escolas distintas com CRECHE.
- II5 (`parcerias_mar2023.csv`): N linhas, contagem de `situacao`; vagas_contratadas (N/soma/média/min/max); soma vagas_bercario; escolas conveniadas e OSC distintas; parcerias Encerradas e com data; distribuição do ano de encerramento; ano de início (≥2010).

## O que o log NÃO permite recuperar

- **Saída dos três scripts Python** (`diag10_ii12.py`, `diag10_ii3.py`, `diag10_ii45.py`): não há `.log`/stdout salvo. Todos os números que produziriam (II1, II2, II3, II4, II5 — capacidades, folgas, sobreposições Fila×perfil×parcerias, vagas contratadas, encerramentos) **não são recuperáveis** a partir dos arquivos listados.
- **`diag10_III2.log` não tem `.do` correspondente** entre os arquivos fornecidos: o script exato que gerou esse log não está disponível (o log em si está completo — abre e fecha normalmente).
- **III1**: o log mostra os cabeçalhos `*padrão*:` mas nenhuma variável sob eles. O `.do` usa `cap ds *`p'*`; não é possível pelo log distinguir "nenhuma variável casou" de "casou mas `cap`/`ds` suprimiu a exibição" — o log apenas não mostra nomes.
- **Blocos referenciados e não presentes aqui**: as etapas II1–II5 e II3 (parte "II3") são mencionadas nos nomes/comentários dos scripts, mas seus resultados numéricos só existiriam nos logs Python ausentes. `fila_codesc.csv`, `turmas_modulo_2016_2017.csv`, `perfil_turmas_jun{2013,2015,2018}.csv` e `parcerias_mar2023.csv` são insumos referenciados; seu conteúdo não é transcrito aqui.
- **Truncamento**: nenhum dos dois logs Stata aparenta estar truncado — ambos têm linha de abertura e `log close`/`closed on` correspondentes.

## Arquivos-fonte (primários)

- `<NE_ROOT>\02_audit\diag10_III.do`
- `<NE_ROOT>\02_audit\diag10_III.log`
- `<NE_ROOT>\02_audit\diag10_III2.log` (sem .do correspondente)
- `<NE_ROOT>\02_audit\diag10_ii12.py` (sem log)
- `<NE_ROOT>\02_audit\diag10_ii3.py` (sem log)
- `<NE_ROOT>\02_audit\diag10_ii45.py` (sem log)
