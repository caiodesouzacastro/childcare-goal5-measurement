# DIAG13 — Validade do desenho de Maimonides

**Data:** 2026-07-22 · Scripts em `…\_audit\diag13_*.py`. Reaproveitados perfil_turma (BUILD01),
cap_full, B_novo/child_master, traj_child, Fila1018, PSP. **Nada modificado em `Dropbox\` (fora de
`_audit`) ou `<D>\`; nenhum artefato do pipeline invalidado usado; capacidade = VAGOFER (autorizada),
N = matrícula apenas como variável de forçamento, nunca como capacidade.**

Painel escola × agrupamento × semestre (perfil 2013–2019): **86.824 unidades, 6.824 cruzamentos** de kM.

## VEREDITO

| Teste | O que decide | Resultado |
|---|---|---|
| **V1 · Direção da causalidade** | VAGOFER sobe **junto** com o cruzamento (94,9% em t); 100% das unidades N>kM já têm VAGOFER>kM | **REPROVADO** |
| **V2 · Origem da massa acima do limiar** | Vem de muitas escolas (não anomalia), mas **selecionadas** (maiores, renda maior) | **REPROVADO** (seleção) |
| **V3 · Balanço em torno do limiar** | Balanço rejeitado (cruzar kM correlaciona com VAGOFER/CAPREAL/renda) + bunching forte | **REPROVADO** |
| **V4 · Elo criança–turma / potência** | A fila **não registra turma**; janela ±3 cobre 74% das unidades (M=7/9/12 densos demais) | **REPROVADO** |

> **CONCLUSÃO: o desenho de Maimonides é INVÁLIDO.** O primeiro estágio forte do DIAG12 (F 53–1.208)
> era **mecânico**: em São Paulo a capacidade autorizada (VAGOFER) é fixada administrativamente e a
> matrícula a preenche, **nunca a excede** (N>VAGOFER em ~0%). Logo a matrícula só cruza kM porque a
> turma extra **já foi autorizada** — o "instrumento" é a decisão administrativa, não a regra legal.
> Ao contrário de Angrist–Lavy (onde a lei impõe divisão da turma ao 41º aluno), aqui não há divisão
> mecânica exógena. Toda a auditoria converge: não há margem exógena neste sistema.

---

## V1 — DIREÇÃO DA CAUSALIDADE (decisivo) · **REPROVADO**
Fonte: `diag13_v1v3.py`. Cruzamento = ⌈N/M⌉ sobe entre t−1 e t (exige uma turma a mais).

**V1a — tempo relativo da mudança de VAGOFER em torno do cruzamento** (6.824 cruzamentos):

| Momento | ΔVAGOFER médio | % que subiu |
|---|---|---|
| t−1 (antes) | +0,2 | 4,7% |
| **t (junto)** | **+19,3** | **94,9%** |
| t+1 (depois) | −1,1 | 4,6% |

A capacidade autorizada salta **exatamente no semestre do cruzamento** (94,9%), não antes nem depois.

**V1b — lead-lag** (VAGOFER_t ~ cruzamento(lead/now/lag) + FE escola-agrup + FE semestre; cluster escola-agrup):
- cruzamento em t+1 (lead): **−8,27 (EP 0,18)** · cruzamento em t (now): **+13,38 (EP 0,20)** · em t−1 (lag): +10,88 (EP 0,21).
O lead é negativo (VAGOFER ainda não subiu antes do cruzamento) e o salto é **contemporâneo** ao cruzamento.

**V1c — a turma extra já estava autorizada?** Entre unidades com N>kM (⌈N/M⌉≥2):
VAGOFER>kM em **100,0%** dos casos, em todos os agrupamentos; turmas reais ≥ previstas em 96–98%.
Como a matrícula respeita a capacidade autorizada (V2c), N só ultrapassa kM depois de a vaga existir.

> **Decisão:** a capacidade sobe **junto** com o cruzamento na esmagadora maioria (94,9%), e a turma
> extra já está autorizada em 100% dos casos. O instrumento é a decisão administrativa de autorizar a
> vaga, não a regra ⌈N/M⌉. **MORTO.**

---

## V2 — DE ONDE VEM A MASSA ACIMA DO LIMIAR · **REPROVADO** (seleção)

**V2a — não é um punhado de escolas recorrentes.** Unidades em [kM+1, kM+3]:
Berç.I 475 unid./217 escolas · Berç.II 1.404/485 · Mini I 1.272/530 · Mini II 1.098/442.
Aparições por escola: mediana 1–2, p90 5–7. A massa vem de **muitas escolas distintas** — não é anomalia
de poucas unidades.

**V2b — mas são unidades selecionadas** (média [kM+1,kM+3] vs N=kM):
VAGOFER **+10,5** (42,3 vs 31,8) · nº turmas **+0,80** (3,8 vs 3,0) · CAPREAL **+12,0** · renda do setor **+R$84,8**
(1.291 vs 1.206). Escolas acima do limiar são **maiores e de entorno mais rico**.

**V2c — não são erros de dado.** Fração com N>VAGOFER (matrícula acima da capacidade autorizada, irregular):
em [kM+1,kM+3] = 0,0–0,6%; no geral ≈ 0%. **A matrícula praticamente nunca excede a capacidade autorizada**
— o que reforça V1: cruzar kM exige a vaga já autorizada.

> **Decisão:** a massa é real, mas vem de escolas sistematicamente maiores e mais ricas — variação
> **selecionada**, não quase-aleatória. **MORTO (seleção).**

---

## V3 — BALANÇO EM TORNO DO LIMIAR · **REPROVADO**

**V3a — balanço em [kM−3, kM+3], regressão de 1[N>kM] (FE semestre):** rejeitado.

| Característica | coef. 1[N>kM] | EP |
|---|---|---|
| VAGOFER | **+8,66** | 0,306 |
| CAPREAL | **+10,34** | 3,052 |
| nº turmas | +0,74 | 0,024 |
| Renda do setor | **+66,9** | 13,44 |

Cruzar o limiar está fortemente associado a mais capacidade autorizada, mais salas reais e maior renda
do entorno. (Modalidade %conveniada quase igual: 78,7% acima vs 80,7% abaixo.) **Balanço rejeitado.**

**V3b — bunching/densidade de N em torno de kM:** massa exatamente em múltiplos de M =
**78,7% (Berç.I) · 58,5% (Berç.II) · 46,3% (Mini I) · 18,4% (Mini II)**. Ex.: Berç.I N=14→5.105 vs N=15→80;
Berç.II N=18→4.062 vs N=19→39. Densidade altamente não-suave, com pico em kM e vale imediatamente acima —
um teste de McCrary rejeitaria a continuidade com folga.

> **Decisão:** balanço rejeitado **e** bunching maciço em kM. **MORTO.**

---

## V4 — O ELO CRIANÇA–TURMA EXISTE? · **REPROVADO**
Fonte: `diag13_v4.py`.

**V4a — a fila NÃO registra a turma.** Variáveis de matrícula em Fila1018: `dt_matricula`,
`cd_esc_matricula` (escola), `cd_serie_ensino_matricula` (série/agrupamento). **Não há identificador de
turma.** Logo o tamanho de turma só pode ser atribuído no nível **escola × agrupamento × semestre** — nunca
à turma específica da criança. Mesmo com desenho válido, o segundo estágio usaria o tamanho médio da
unidade, não a turma frequentada.

**V4b — N do segundo estágio:** 85.846 crianças com PSP (2º ano, 2018/2019); 55.993 com matrícula de creche
identificável; **22.470 em unidade escola×agrup×semestre dentro de [kM−3, kM+3]** (Berç.I 782 · Berç.II 5.761 ·
Mini I 10.379 · Mini II 5.548). O N bruto supera 5.000.

**PORÉM — a janela ±3 cobre 74% das unidades** (64.218 de 86.824). Com M=7/9/12, os múltiplos ficam a cada
7/9/12 crianças, então "±3 de algum kM" abrange praticamente todo o suporte: **não há região "longe do
limiar"** para servir de contrafactual. Só Mini II (M=25) tem intervalos genuínos. A potência nominal existe,
mas não há RD limpo a estimar.

> **Decisão:** o elo criança-turma não existe (só escola×série), e os limiares são densos demais (M pequeno)
> para formar um RD com contrafactual. **REPROVADO.**

---

## SÍNTESE
O único desenho que passara no teste de primeiro estágio (DIAG12, Teste 3) **falha na validade**. A razão é
a mesma que derrubou todos os desenhos anteriores: em São Paulo a **capacidade autorizada é uma decisão
administrativa** que precede e acompanha a matrícula (VAGOFER sobe junto com o cruzamento em 94,9% dos casos;
N nunca excede VAGOFER), o balanço em torno do limiar é rejeitado, a densidade tem bunching maciço em kM, e a
fila sequer registra a turma. Não há regra mecânica exógena à la Angrist–Lavy. **Encerra-se a busca por um
desenho causal: o sistema de fila centralizada não gera variação exógena explorável.** O caminho restante é
o descritivo (BUILD01).

### Arquivos
`_audit\diag13_v1v3.py` (V1–V3) · `diag13_v4.py` (V4).
