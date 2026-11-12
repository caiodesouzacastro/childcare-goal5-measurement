# DIAG11 — Construção e teste do desenho de choque de capacidade

**Data:** 2026-07-22 · Build (não auditoria). Downloads em `_sme_publico\`; scripts e
derivadas em `…\_audit\`. **Nada em `Dropbox\` ou `<D>\` foi modificado** (só leituras).

> **REGRA CRÍTICA CUMPRIDA:** capacidade veio **exclusivamente** de `MODULO`/`VAGOFER`
> (perfil) e `vagas_contratadas` (parcerias) — **capacidade autorizada**. `MATRIC`/
> `MATRICULA` (matrícula) **nunca** foi usada para definir capacidade.

> **VEREDITO:** a camada de capacidade é construível de forma limpa e a variação existe
> (1.885 reduções de VAGOFER, 283 fechamentos confirmados, 3.194 aumentos). **Mas o
> primeiro estágio, embora com sinal correto, é pequeno, DESAPARECE sob efeito fixo de
> setor×semestre, e falha o placebo pré-solicitação** (o choque nos 180 dias ANTERIORES
> à solicitação prevê os desfechos tão forte quanto o choque real). Os fechamentos são
> **economicamente selecionados** (repasse baixo → 74% de fechamento). O choque de
> capacidade **não é exógeno** — segue tendências de setor, a mesma endogeneidade que
> matou o desenho C.

---

## PARTE A — SÉRIE COMPLETA

- **A1.** `perfil-das-turmas`: baixados **13 semestres, 2013s1 a 2019s1** (jun+dez). O
  arquivo dez/2019 (`turmas122019.csv`) tem estrutura incompatível (**0 turmas CRECHE
  reconhecidas** — colunas diferentes) → excluído. Nenhum outro falhou.
- **A2.** `parcerias-ed-infantil`: baixados **31 snapshots CSV** (`conveniosmar2016` a
  `parceria_marco_2026`). ⚠️ Os arquivos de **2024–2026 usam cabeçalhos acentuados**
  (`Código Escola`, `Data do Encerramento`) e os de **2016–2023 usam minúsculas**
  (`codigo_escola`, `data_do_encerramento`). Usei `parcerias032023` (minúsculas), que
  carrega o histórico cumulativo com todos os encerramentos até 2023 → cobre a janela
  2013–2019.
- **A3.** Painel `escola × agrupamento × semestre` (CRECHE), capacidade = soma de
  `VAGOFER`: **2.734 escolas, 13 semestres, 87.178 células.** `VAGOFER` 100% preenchido.
  Capacidade autorizada por agrupamento (2013s1 → 2019s1):

| agrupamento | 2013s1 | 2015s1 | 2017s1 | 2019s1 |
|---|---:|---:|---:|---:|
| Berçário I | 19.843 | 25.157 | 25.743 | 32.620 |
| Berçário II | 47.548 | 51.759 | 64.593 | 86.402 |
| Mini Grupo I | 73.147 | 76.217 | 93.028 | 104.040 |
| Mini Grupo II | 74.276 | 90.259 | 107.145 | 115.831 |

---

## PARTE B — RESCISÃO É FECHAMENTO OU RENOVAÇÃO?

- **B1.** 3.434 encerramentos datados → **RENOVAÇÃO 894 · TROCA 738 · FECHAMENTO 1.802.**
  Por ano (fechamentos): 2015→55 · 2016→78 · **2017→1.078** · 2018→345 · 2019→84.
  (2017 concentra os fechamentos — a reestruturação em massa.)
- **B2 (teste decisivo).** Dos 1.587 fechamentos testáveis no perfil (2013–2019), **só
  283 (17,8%) se confirmam** (a escola-creche some do perfil no semestre seguinte). Os
  outros **1.304 não se confirmam** — a escola continua operando (rotatividade
  administrativa, não perda de capacidade). **O encerramento de parceria é um sinal
  ruidoso de perda de capacidade real.**
- **B3. Fechamentos CONFIRMADOS (variação utilizável):** ~283 na janela 2013–2019
  (por ano de encerramento: 2015→23 · 2016→59 · 2017→65 · 2018→110 · 2019→84;
  vagas perdidas: 2018→14.505, 2019→12.158, 2017→7.869). Por DRE: Itaquera, São Miguel,
  Campo Limpo, Freguesia, Ipiranga lideram.
- **B4. Aberturas** (1ª parceria da escola): 2013→341 (49.830 vagas) · 2014→194 ·
  **2015→692 (96.397 vagas)** · 2016→241 · 2017→183 · 2018→238 · 2019→185. As aberturas
  superam largamente os fechamentos (a expansão domina).
- **B5. Mudanças de VAGOFER no perfil** (escola-creche, |Δ|≥7 ≈ 1 turma):
  **3.194 aumentos** (mediana +35) e **1.885 reduções** (mediana −22) ao longo de
  2014–2019. É a maior fonte de variação de capacidade — muito além dos 283 fechamentos.

---

## PARTE C — EXPOSIÇÃO DA CRIANÇA

Universo: 1ª solicitação, idade 0–22m (Berçário I/II), coortes 2013–2018, sem prioridade.

- **C1.** **587.008 crianças**; conjunto elegível (CEIs ≤2 km): **mediana 33** (p10=14,
  p90=68). Confirma "um choque marginal é 1 de 33".
- **C2.** `choque_neg` (vagas perdidas no conjunto elegível em 180 dias): média 27,7,
  **39,5% das crianças com >0** (234.675). `choque_pos`: média 55,4, **57,3% com >0**.
  `choque_pre` (placebo, 180d antes): 33% com >0. `cap_base` (capacidade Berçário
  elegível): mediana 986 vagas.
- **C3.** Solicitação em 2017 (reestruturação): **103.583 crianças (17,4%)** — separadas.

---

## PARTE D — PRIMEIRO ESTÁGIO E PLACEBOS (o teste que decide)

Coeficientes por **100 vagas** de choque. Sinal esperado: perda de capacidade →
mais espera, menos encaminhamento, maior idade de entrada.

### D1. Primeiro estágio — `dep = choque_neg + choque_pos + cap_base`

| DEP | Spec A: distrito#sem · b(neg) [ep] | Spec B: cep · b(neg) [ep] | **Spec C: setor#sem · b(neg) [ep]** |
|---|---|---|---|
| espera (dias) | **+3,29** [1,13] | +6,95 [0,92] | +0,42 [1,17] |
| enc180 (0/1) | **−0,0063** [0,0024] | −0,068 [0,003] | −0,0004 [0,0029] |
| idade_entrada (m) | **+0,107** [0,054] | +0,417 [0,036] | −0,035 [0,068] |
| mat365 (0/1) | **−0,0080** [0,0030] | +0,000 [0,002] | −0,0015 [0,0037] |

- **Spec A** (distrito×semestre, N≈586 mil): sinal correto, significante, **mas pequeno**
  (100 vagas perdidas → +3,3 dias de espera; −0,6 p.p. de encaminhamento em 180d; +0,11
  mês de idade de entrada).
- **Spec B** (CEP): coeficientes maiores, mas **`choque_neg` e `choque_pos` têm o MESMO
  sinal** (ambos aumentam idade/espera) → confunde: CEP em fluxo de capacidade tem
  tendência própria. Não confiável.
- **Spec C** (setor×semestre, FE mais fino que distrito): **o efeito DESAPARECE** (todos
  não-significantes). O efeito da Spec A vinha de variação entre-setores-dentro-de-
  distrito, não de choque local.

### D2. PLACEBO 1 — choque nos 180 dias ANTERIORES à solicitação (deveria ser nulo)

| DEP | b(pre) [ep] | (vs efeito real Spec A) |
|---|---|---|
| espera | **+4,87** [1,16] | **MAIOR** que o real (+3,29) |
| enc180 | −0,0086 [0,0034] | mesmo sinal/magnitude |
| idade_entrada | **+0,140** [0,054] | **MAIOR** que o real (+0,107) |
| mat365 | −0,0044 [0,0032] | idem |

**O choque de capacidade que ocorre ANTES de a criança se inscrever prevê os desfechos
tão forte (ou mais) quanto o choque real.** Como um evento pré-inscrição não pode
afetar causalmente a criança (além do estoque, que controlamos), isto significa que o
"choque" apenas rastreia a **tendência local** — o desenho **falha o placebo.**

### D3. PLACEBO 2 — choque futuro (366–545d após): também não-nulo (enc180 +0,014, sig, sinal errado).

### D5. Dose-resposta (por quartil de `choque_neg/cap_base`): **não-monotônica** — Q1
(perda pequena) vai ao contrário (enc180 0,506 > 0,455 do Q0; espera 167 < 228), Q2–Q4
monotônicos piores. A "fração perdida" correlaciona com características de base do setor.

---

## PARTE E — AMEAÇAS

- **E2 (seleção econômica — confirmada).** Contratos de conveniada com **repasse per
  capita baixo fecham muito mais**: por quartil de R$/vaga, taxa de encerramento
  Q1 (R$600)→**73,7%** · Q2 (R$822)→57,3% · Q3 (R$868)→46,9% · Q4 (R$991)→53,9%.
  Encerrados: repasse médio R$794 vs ativos R$857; duração média até fechar 1,99 ano.
  **O fechamento não é idiossincrático — é economicamente selecionado** (OSCs/áreas de
  repasse baixo), o que se correlaciona com o território. Corrobora o placebo D2.
- **E1 (predição por território) e E3 (recomposição/substituição):** **não estimados
  separadamente** — o mecanismo de endogeneidade já ficou estabelecido por D2 (placebo
  pré não-nulo) + E2 (seleção por repasse). Fica em aberto a regressão setor-semestre
  formal (E1) e a série de recomposição (E3).

---

## PARTE F — O QUE FICOU EM ABERTO

1. **Confirmação da regra crítica:** **nenhuma** medida de capacidade usou matrícula.
   `MODULO`/`VAGOFER`/`vagas_contratadas` (autorizadas) apenas; `MATRIC` só como coluna
   de comparação (Parte B do DIAG10, não aqui).
2. **O desenho não entrega primeiro estágio limpo:** pequeno em Spec A, some sob
   setor×semestre (Spec C), e **falha o placebo pré-solicitação (D2)**. Fechamentos são
   selecionados por repasse (E2). O choque de VAGOFER/parceria **não é exógeno**.
3. **Fechamentos confirmados são poucos (~283, 2013–2019)** e concentrados em 2018–2019;
   a maioria dos "encerramentos" (82%) não corresponde a perda de capacidade no perfil.
4. **dez/2019 do perfil incompatível** (0 turmas CRECHE reconhecidas) — série útil termina
   em 2019s1; `MODULO` explícito só de 2018 em diante (usei `VAGOFER` em toda a série).
5. **Cabeçalhos de parcerias mudam** (acentuado 2024–2026 vs minúsculo 2016–2023) — usei
   um snapshot minúsculo com histórico; não harmonizei os acentuados.
6. **E1/E3 não estimados** (regressão setor-semestre de fechamento; recomposição de
   capacidade pós-evento) — o veredito de endogeneidade já vem de D2+E2.
7. **Conjunto elegível** usa `cep_cei_pairs_novo` (CEIs com coordenada; ~2.313), não
   necessariamente todos os CEIs ≤2km; a "capacidade autorizada elegível" pode subestimar
   levemente.
8. **Nada em `Dropbox\` (exceto `_audit`) ou `<D>\` foi tocado.** Downloads em
   `_sme_publico\`; scripts/derivadas em `_audit\`.

### Arquivos gerados
Downloads (`_sme_publico\`): 13 CSV de perfil + 31 de parcerias + dicionários.
Derivadas (`_audit\`): `perfil_panel_creche.csv`, `esc_sem_cap.csv`, `eventos_conv.csv`,
`cap_full.dta`, `cap_events.dta`, `cap_levels.dta`, `berc_child.dta`, `berc_design.dta`,
`child_shock.dta`; scripts `diag11_*.py/.do`. Entregável:
`<NE_ROOT>\dados_externos\DIAG11_choques_capacidade.md`.
