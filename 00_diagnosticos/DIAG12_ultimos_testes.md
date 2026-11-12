# DIAG12 — Quatro testes finais de identificação

**Data:** 2026-07-22 · Scripts em `…\Neighborhood Effects\_audit\diag12_*.py`; downloads em
`_sme_publico\`. **Nada modificado em `Dropbox\` (fora de `_audit`) ou `<D>\`.** Não foi usado
nenhum artefato do pipeline invalidado (dt_corte, rvar, trat_ber*). Reaproveitados B_novo,
cap_full, eventos_conv, perfil_turma (BUILD01), cep_cei_pairs_novo, child_shock, child_cei,
berc_design.

## VEREDITO

| Teste | Fonte de variação | Estatística-chave | Resultado |
|---|---|---|---|
| **1. Degraus da fórmula de repasse** | Bunching de `vagas_contratadas` em 60/90/120 | Excesso de massa: +0,35 / −1,34 / +0,45 (EP 0,44/0,32/0,34) — nenhum | **REPROVADO** |
| **2. CEIs pivotais (concentração)** | Choque em conjuntos elegíveis concentrados | Q4 (mais concentrado): 1º estágio sem sinal correto; placebo pré ≠ 0 | **REPROVADO** |
| **3. Maimonides (feito corretamente)** | Regra turmas = ⌈N/M⌉, M=7/9/12/25 | **F = 53,5 / 575 / 282 / 1208** (todos ≫10); há massa acima de kM | **APROVADO** (único sobrevivente) |
| **4. Reforma jul/2016 e endereço-base** | Quebra na atribuição em jul/2016 | Quebra +0,037 km (EP 0,026), n.s.; placebo ≠ 0; dispersão >2km ampla | **REPROVADO** |

**Um único desenho sobrevive: Maimonides (Teste 3).** Tem primeiro estágio forte e nítido
(F entre 53 e 1.208). Ressalvas honestas abaixo. Os outros três morrem pelas regras de decisão
pré-especificadas.

---

## TESTE 1 — DEGRAUS DA FÓRMULA DE REPASSE · **REPROVADO**
Base: `parc_parcerias032023.csv`, 5.926 contratos (5.926 com vagas>0). Fonte: `diag12_t1.py`.

**T1a — contagens exatas** (a massa está NOS números redondos, não logo abaixo):
- Em torno de 60: … 58:6 · **59:43 · 60:57** · 61:18 · 62:19 · 63:26 · 64:15 · 65:31
- Em torno de 90: 88:22 · 89:27 · **90:55** · 91:38 · 92:33 · 93:44 · 94:51 · 95:35
- Em torno de 120: 118:40 · 119:28 · **120:79** · 121:30 · 122:41 · 123:40 · 124:39

Há picos EM 60, 90 e 120 (números focais de contrato), mas nenhum acúmulo logo *abaixo* do limiar.

**T1b — excesso de massa em [limiar−3, limiar]** (contrafactual polinomial grau 5, EP bootstrap 500):
- 60: obs 111 vs contraf. 102,1 → **+0,35 (EP 0,44)** · 90: **−1,34 (EP 0,32)** · 120: **+0,45 (EP 0,34)**.
Nenhum excesso de massa significante. **Não há bunching.**

**T1c — repasse per capita (`valor_mensal`/`vagas_contratadas`) por faixa:**
≤60 = R$1.195,8 · 61–90 = R$947,4 · 91–120 = R$879,8 · >120 = R$819,1 (declínio monotônico).
Spline linear de `valor_mensal ~ vagas` (inclinação marginal R$/vaga): 61–90 = 715 · 91–120 = 626 ·
>120 = 780. **Sem quebra de inclinação nítida em 90/120** (o degrau em 60 vem da região esparsa n=137).

**T1d — adicional de berçário:** o repasse per capita é uma **função determinística** da composição
do contrato — coef. da fração de berçário sobre o per capita = R$380,6 (**EP ≈ 0,0**). Só **1 de 5.597**
contratos tem berçário = 0, então não há variação residual para comparar faixas.

**T1e — série do per capita médio por faixa e ano** (níveis nominais sobem; estrutura de faixas estável):
- 2019-03 (n4.602): 781 / 623 / 573 / 535 · 2020-03: 862 / 672 / 617 / 575 · 2021-03: 848 / 670 / 616 / 575
- 2022-09: 1.100 / 864 / 801 / 748 · 2023-03: 1.196 / 947 / 880 / 819. (2018-03 não parseou — cabeçalho antigo.)
Os reajustes entre anos são **choques de nível para toda a rede** (mesma tabela para todos), não variação transversal.

> **Decisão:** T1a/T1b sem bunching e T1c sem quebra de inclinação → a fórmula não morde.
> O repasse é determinístico (T1d, EP≈0); não gera descontinuidade manipulável. **Caminho morto.**

---

## TESTE 2 — CEIs PIVOTAIS (a diluição é o problema?) · **REPROVADO**
`child_cei.dta` + `berc_design.dta`; 1º estágio com absorb(setor#semestre), cluster(CEI mais próximo),
por quartil de concentração. Fonte: `diag12_t2.py`. N = 585.434.

**T2a — concentração do conjunto elegível (muito baixa em toda parte):**
- `share` do maior CEI: p10 0,049 · p25 0,072 · **p50 0,116** · p75 0,174 · p90 0,264 · média 0,143.
- HHI: p10 0,023 · **p50 0,064** · p90 0,161 (todo o suporte é "não concentrado", HHI<0,15).
Mesmo o quartil mais concentrado tem o maior CEI ≈ ¼ da capacidade; um fechamento é 1 de muitos.

**T2b — primeiro estágio (coef. de `choque_neg100`) por quartil de concentração:**

| DEP | Q1 (share 0,05) | Q2 (0,09) | Q3 (0,14) | **Q4 (0,24)** |
|---|---|---|---|---|
| espera | +0,68 (1,21) | −1,71 (2,72) | +2,30 (3,54) | −3,40 (4,93) |
| enc180 | +0,000 (0,004) | +0,005 (0,006) | +0,008 (0,008) | −0,011 (0,008) |
| idade_entrada | −0,02 (0,088) | +0,16 (0,149) | −0,03 (0,218) | **−0,52 (0,271)** |
| mat365 | +0,003 (0,005) | +0,008 (0,008) | −0,017 (0,011) | −0,000 (0,013) |

Nenhum quartil tem primeiro estágio com o sinal esperado e significante. No Q4, `idade_entrada`
é **negativo** (perda de capacidade associada a entrada *mais cedo* — sinal errado).

**T2c — placebo pré-solicitação (coef. de `choque_pre100`) por quartil:** não-nulo.
Q1 espera **+3,52 (1,12, sig)** / idade −0,16 · Q3 espera +7,09 / idade +0,36 · Q4 espera +7,40 (7,58) /
idade **+0,57 (0,41)**. No quartil concentrado o placebo pré é *maior* que qualquer 1º estágio real.

**T2d — o quartil concentrado é uma subpopulação selecionada** (Q4 vs demais):
renda do CEP **+R$601** (1.678 vs 1.076) · IPVS −0,25 (menos vulnerável) · **nº de CEIs elegíveis 17,6 vs 43,7**
(−26) · dist. ao centro −2,5 km. Concentração = poucos CEIs = áreas de renda alta.

> **Decisão:** exige efeito no quartil concentrado E placebo pré nulo nesse quartil. Nenhum dos dois
> ocorre (Q4 sem 1º estágio correto; placebo pré grande). Ainda seleciona por renda. **Morto.**

---

## TESTE 3 — MAIMONIDES, FEITO CORRETAMENTE · **APROVADO** (único sobrevivente)
Escola × agrupamento × semestre (perfil 2013–2019); N = matrícula efetiva, M = módulo legal
(7/9/12/25); turmas previstas = ⌈N/M⌉. Fonte: `diag12_t3.py`. Unidades: 86.824. **M é legal, nunca
derivado de matrícula; N (matrícula) é a variável de forçamento do desenho, não a capacidade.**

**T3b — suporte acima do limiar** (contagem em kM, kM+1, kM+2, kM+3 — tabela decisiva; há massa acima):

| Agrup. (M) | k=1 (kM/+1/+2/+3) | k=2 | k=3 |
|---|---|---|---|
| Berçário I (7) | 1272 / 18 / 30 / 18 | 5105 / 80 / 62 / 22 | 3134 / 43 / 42 / 38 |
| Berçário II (9) | 564 / 23 / 12 / 46 | 4062 / 39 / 85 / **189** | 2969 / 168 / 73 / 167 |
| Mini I (12) | 330 / 13 / 17 / 45 | 3189 / 129 / 125 / 77 | 2798 / 110 / 99 / 112 |
| Mini II (25) | 1731 / 129 / 64 / 96 | 1595 / **218** / 128 / 139 | 730 / 112 / 50 / 69 |

A massa concentra-se EM kM (matrícula censurada na capacidade), com cauda **fina, porém não nula**,
acima — dezenas a centenas de unidades por limiar (mais robusta em Berçário II e Mini II).

**T3c — nº médio de turmas salta em kM+1** (abaixo → acima de kM):
Berçário I: 1,01→1,52 (em 7); 2,00→2,29 (14); 3,00→3,61 (21). Berçário II: 1,04→1,86 (9); 2,01→2,85 (18).
Mini I: 1,03→1,37 (12). Mini II: 1,04→1,65 (25). O salto de turma ocorre no limiar previsto.

**T3d — tamanho real ≈ previsto:** corr(real, previsto) = 0,382 (Berç.I) · 0,661 (Berç.II) · 0,517 (Mini I) ·
0,740 (Mini II); médias reais 6,90/8,66/11,43/21,07 ≈ previstas 6,86/8,67/11,39/21,56.

**T3e — primeiro estágio** (tamanho_real ~ tamanho_previsto + N + N² + FE escola + FE semestre; cluster escola):

| Agrup. | b(previsto) | EP | **F** | N | escolas |
|---|---|---|---|---|---|
| Berçário I | 0,431 | 0,059 | **53,5** | 15.573 | 1.940 |
| Berçário II | 0,736 | 0,031 | **575,2** | 22.881 | 2.479 |
| Mini I | 0,538 | 0,032 | **282,5** | 24.558 | 2.543 |
| Mini II | 0,642 | 0,018 | **1208,0** | 23.812 | 2.586 |

> **Decisão:** há massa em kM+1 (T3b) **e** F ≫ 10 em todos os agrupamentos (T3e). **Sobrevive.**
>
> **Ressalvas honestas (a fazer antes de usar):** (a) N é censurado na capacidade — a maior parte da
> massa está exatamente em kM, com cauda fina acima; a variação identificadora (escolas que cruzam kM
> e abrem turma) é rara relativa ao pico. (b) O F alto reflete em parte a relação mecânica ⌈N/M⌉ entre
> previsto e real. (c) A **validade** (o cruzamento de kM é quase-aleatório ou segue a demanda?) não
> foi testada aqui — é o passo seguinte. Aprovado no sentido das regras deste diagnóstico (1º estágio
> forte), não como identificação já validada.

---

## TESTE 4 — REFORMA DE JULHO/2016 E O ENDEREÇO-BASE · **REPROVADO**
Série mensal 2014–2018 dos encaminhamentos (2.166.919 eventos). Fonte: `diag12_t4.py`, `diag12_t4d.py`.
Cobertura de distância (par CEP–CEI existe, ≤~2km) = 59,7%.

**T4a — série mensal (jan/2016–out/2016), sem quebra em jul–set/2016:**
dist. mediana ~0,80–0,85 km e %≤2km ~50–57% em todos os meses; jul 0,833/52,6% · ago 0,807/54,9% ·
set 0,797/54,5% — indistinguíveis de abr–jun (0,847/0,824/0,854). (Picos de dez são lotes de matrícula.)

**T4b — regressão de quebra** (dep ~ 1[pós-jul/2016] + tendência + FE mês-do-ano + FE distrito; cluster mês):
dist. ao CEI **+0,037 km (EP 0,026)** · ≤2km **+0,002 (EP 0,050)** · espera **+5,3 dias (EP 14,1)**.
**Todos não-significantes — sem quebra.**

**T4c — placebos:** jul/2014 (dados 2014–2015): dist +0,009 (0,009); **≤2km +0,070 (EP 0,035) — não-nulo**.
jul/2015 (janela 2015–jun/2016): **não estimável** (colinearidade com FE de distrito na janela estreita).

**T4d — decomposição dos atribuídos fora do conjunto ≤2km** (coordenadas brutas, haversine CEP↔CEI;
o `cep_cei_pairs` está truncado em ~2km, então o >2km exige coordenadas):
- (i) **escola sem coordenada válida: 377.901 (28,6%)**.
- (ii) **geolocalizada com dist>2km: 137.662 (10,4%)** — distribuição **amplamente dispersa**:
  mediana 4,73 km · p75 11,2 · p90 25,6 · p95 36,4 km (máx. absurdos até 1.072 km = coordenada ruim).
  Dessas: ≤3km 29,8% · 3–5km 22,2% · **>5km 48,0% · >10km 27,6%**.
  Não é massa logo acima de 2km (erro de medida): é **dispersão ampla**, compatível com endereço-base
  diferente do CEP registrado.

**T4e — quem é atribuído "fora"** (>2km/sem coord vs dentro): renda do CEP **+R$163** (1.302 vs 1.139) ·
prioridade **−4,1 p.p.** (13,6% vs 17,7%) · coortes mais antigas (2013,5 vs 2014,6) · irmão matriculado
~igual (34,8% vs 35,5%) · **dist. ao CEI mais próximo quase igual (0,32 vs 0,27 km)** — ou seja, tinham
CEI perto e ainda assim foram alocados longe.

> **Decisão:** sem quebra em jul/2016 (T4b), com placebo não-nulo (T4c) **e** dispersão ampla em T4d.
> Qualquer um bastaria; os três ocorrem. **Morto.**

---

## O QUE ISSO SIGNIFICA
Três dos quatro caminhos morrem exatamente como os desenhos anteriores (DIAG01–11): a oferta, o preço
e a alocação alinham-se à demanda/território, sem descontinuidade exógena. **O único sobrevivente é
Maimonides** — a regra de formação de turmas ⌈N/M⌉ produz um primeiro estágio forte (F 53–1.208).
Ele não está validado (censura em kM, cauda fina acima, exogeneidade do cruzamento por testar), mas é
o primeiro desenho em toda a auditoria com um primeiro estágio nítido e uma regra legal explícita por
trás. Próximo passo natural: testar se o cruzamento de kM é quase-aleatório (balanço de covariáveis e
placebo de matrícula em torno de kM) e estimar o segundo estágio sobre desfechos de criança.

### Arquivos
`_audit\diag12_t1.py` (Teste 1) · `diag12_t2.py` (Teste 2) · `diag12_t3.py` (Teste 3) ·
`diag12_t4.py` + `diag12_t4d.py` (Teste 4). Derivadas em `BUILD01\_staging\` (t1_hist.csv,
t3_hist_*.csv, t3e_firststage.csv, t4_serie_mensal.csv, t4d_dist_far.csv).
