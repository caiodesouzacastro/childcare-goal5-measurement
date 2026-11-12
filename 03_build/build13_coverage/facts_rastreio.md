# Rastreio de números do texto sem linha anterior em facts.md (25/10/2026, bloco B do checklist)

## OQ-20: números herdados da versão submetida
- **3,3 milhões de linhas** (§3.1): 3.298.064 linhas do `Fila1018.dta` bruto. Fontes: `00_diagnosticos/DIAG04_reconstruido.md:30` ("N linhas Fila = 3298064"), `DIAG02_reconstruido.md:260`, `DIAG06_reconstruido.md:57`; checado em `02_audit/verificacao_final.py` (V1.fila_linhas).
- **98,1% com CPF** (§3.1): a unidade é **criança**, não registro: "1,175,658 responsáveis (cpf válido) cobrindo 1,495,127 crianças (98.1% do painel)" (`03_build/build05/build05.log:4`; o `build11/p4.log:1` dá 1.175.659 e 1.495.152, também 98,1%). **O texto dizia "of records"; foi corrigido para "of children" em 25/10.**
- **110.205 → 341.031 encaminhamentos** (§2.3): `tab an_letivo_encaminhamento` em `02_audit/diag06_C.log:219` e na linha seguinte; `DIAG06_reconstruido.md:430–431`. A unidade é a linha de encaminhamento por **ano letivo** do encaminhamento (inclui repetições). **O texto passou a dizer "for the 2012 school year ... for 2013".**

## OQ-19: contagens de centros
- **2.384 unidades de creche, 1.629 conveniadas** (§2.1): cadastro de escolas da SME (`escolassite.dta` → `escolas_parsed.dta`), flag `cei` = tipo CEI/CR.P/CEMEI/CCI; `02_audit/diag04_A2fix.log:79–109`: CEI DIRET 317, CEI INDIR 376, CEMEI 14, CEU CEI 45, CCI/CIPS 3, CR.P.CONV 1.629; total 2.384. A data do cadastro não está no log.
- **2.406** (centros com ao menos uma turma de creche em 2019; `build01/facts.md` T7a, perfil de turmas); **2.734** (centros no painel de capacidade 2013S1–2019S1; §3.2); **2.313** (cadastro geolocalizado; `build01/facts.md`, "O que NÃO saiu").

## OQ-18: correlação de ranking (§2.2)
- 0,885 (diagnóstico original em Stata) e 0,96 (recálculo independente em pandas, mesmo universo de N = 1.884.018 linhas de encaminhamento não prioritárias em células centro × faixa × ano com ≥5 crianças), segundo `04_paper/REPLICATION_NOTES.md:19–28` e `02_audit/verificacao_final.py:331–345` (V14). **A saída numérica da V14 não está salva em log.** Ver OQ-18 sobre a casa citável.
- **Inconsistência encontrada:** o `REPLICATION_NOTES.md` diz que "about a third of applications share their second, a signature of batch entry", mas a tab:N1 e a §3.1 dizem 2,7% das primeiras solicitações com segundo compartilhado e nenhum lote grande, salvo 2015. Os universos diferem (linhas de encaminhamento ordenadas por `sol` dentro da célula, contra primeiras solicitações na cidade inteira), mas a expressão "signature of batch entry" contradiz o paper. **Não corrigido** (documento de apoio, não o paper).

## OQ-26: números derivados por aritmética de células
| Texto | Valor | Fórmula | Fonte |
|---|---|---|---|
| §4.2 | 0,095 | 0,563 − 0,468 | tab:P2end, coorte 2010 |
| §4.2 | 0,129 | 0,876 − 0,747 | tab:P2end, coorte 2016 |
| §4.2 | ≈5 semanas | 218 − 181 = 37 dias | tab:P2end |
| §4.2 | "um em três → um em dois" | 0,362 → 0,522 | tab:E1cohort, ref$_{180}$ |
| §6.1 | 25.036 | 125.437 − 100.401 | tab:T12, 2010 |
| §6.1 | 88.273 | 132.365 − 44.092 | tab:T12, 2017 |
| §6.1 | 80% / 33% | 100.401/125.437; 44.092/132.365 | tab:T12 |
| §8.2 | 2× → 15% | 129.594/64.436 = 2,01; 44.092/296.260 = 0,149 | tab:T11 |
| §2.1 nota | até 9% | 1 − (mun.+conv.)/SME: 0,001–0,089 (texto corrigido de "between 1 and 9" para "up to 9") | `build13_coverage/facts.md` (reconciliação) |
| §2.1 nota | 1,0% | 569.975/564.210 − 1 | `build13_coverage/facts.md` |
| §2.1 nota | <0,5 ponto | 0,6584 − 0,6547; 0,5578 − 0,5547 | `cobertura_sp_seade.csv` |

## OQ-5: tab:C6 com 64 distritos
- Causa: `build10.py:522–526` lê `nm_distrit` de `cep_renda_pop_2010.dta`, onde os 32 distritos com acento chegam como escapes literais em minúsculas ("s<c3>o miguel"), e não casam com o `evolucaodemanda.csv`. Os builds 03, 04 e 05 usam `fixhex()` e não têm o problema. O `build_p3.py` usa o distrito só como rótulo de célula dentro de uma fonte e não é afetado.
- Reprodução e correção: `02_audit/build13_c6fix.py` → `c6_fix.csv`. Original reproduzido exatamente (+0,0043 [0,0139], −0,0049 [0,0123], +0,0115 [0,0185]; N = 448; 64 distritos). Corrigido: **+0,0086 (0,0097), −0,0079 (0,0111), +0,0031 (0,0134); N = 672; 96 distritos.** Não inserido (regra: mostrar antes).
