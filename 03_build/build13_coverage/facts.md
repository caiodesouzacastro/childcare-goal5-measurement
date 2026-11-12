# build13_coverage — cobertura de creche no município de São Paulo (EXT-1), 25/10/2026

Scripts: `02_audit/build13_coverage.py` (numerador) e `02_audit/build13_rates.py` (taxas).
Saídas: `creche_mat_sp.csv` (ano × rede), `cobertura_sp.csv` (taxas 2010–2018), `sidra_1378_sp_2010_0a4.json`.
Descritivo; nenhum número travado do paper foi alterado.

## Fontes
- **Numerador:** `Compartilhado/Microdados_Creches_SME/originais/auxiliares_publicos/censo_escolar_inep/microdados_ed_basica_{ano}.csv`
  (INEP, nível escola), `CO_MUNICIPIO == 3550308`. Etapa: `QT_MAT_INF_CRE`. Idade: `QT_MAT_BAS_0_3` (matrículas de até 3 anos em qualquer etapa).
- **Rede municipal + conveniada:** `TP_DEPENDENCIA == 3` (municipal) + (`TP_DEPENDENCIA == 4` & `IN_CONVENIADA_PP == 1` & `TP_CONVENIO_PODER_PUBLICO` ∈ {1 municipal, 3 estadual e municipal}). Conveniadas só com o estado ficam fora (953 matrículas em 2010; 42 em 2018). Nenhuma conveniada sem `TP_CONVENIO` em 2010–2018.
- **Denominador A (Censo 2010):** SIDRA tabela 1378, idades simples 0, 1, 2 e 3 anos, município 3550308: 142.843 + 139.018 + 140.151 + 142.198 = **564.210**.
- **Denominador B (SINASC):** nascidos vivos residentes no município (`sme_dados_abertos/sinasc_nv_distrito_2006_2026.csv`, linha Total), anos Y−3 a Y (mesma definição do pool da Figura A1/F7). 2010: **693.240**. 2018: **678.201**. Razão B/A em 2010 = 1,2287.
- **Não existe estimativa IBGE de população municipal por idade para 2018** (as estimativas municipais do IBGE são de população total; as projeções por idade são por UF). Por isso o denominador B é usado nos dois anos.

## Números (no texto: §2.1 e nota de rodapé 1)
| | 2010 | 2018 |
|---|---|---|
| Matrículas etapa creche, total | 170.720 | 365.854 |
| Matrículas etapa creche, municipal + conveniada | 128.212 | 309.947 |
| Matrículas 0–3 anos (qualquer etapa), total | 218.470 | 349.750 |
| Matrículas 0–3 anos, municipal + conveniada | 173.334 | 290.249 |
| Cobertura etapa total / SINASC | 0,2463 | 0,5394 |
| Cobertura etapa mun+conv / SINASC | 0,1849 | 0,4570 |
| Cobertura idade total / SINASC | 0,3151 | 0,5157 |
| Cobertura idade mun+conv / SINASC | 0,2500 | 0,4280 |
| Cobertura etapa total / Censo 2010 | 0,3026 | — |
| Cobertura etapa mun+conv / Censo 2010 | 0,2272 | — |
| Cobertura idade total / Censo 2010 | 0,3872 | — |
| Cobertura idade mun+conv / Censo 2010 | 0,3072 | — |

## Quebra 2010→2011 na definição por etapa
- Etapa mun+conv: 128.212 (2010) → 195.348 (2011), +52%; série municipal publicada (tab:T11): 130.412 → 195.561, +50,0%. Os níveis batem com a série da SME.
- Idade mun+conv: 173.334 → 160.054 (cai). Pré-escola mun+conv: 288.648 → 189.191.
- Leitura: em 2010 parte das crianças de 3 anos da rede municipal e conveniada estava em turmas de pré-escola. A definição por etapa é a do serviço racionado pela fila e a que bate com a série da SME.

## 4ª rodada (25/10): denominador SEADE adotado no texto, reconciliação e calendário
**Reconciliação (etapa creche, Censo Escolar maio, contra a série SME de dezembro, tab:T11):**
| Ano | Municipal direta | Privada conveniada (municipal) | Privada sem convênio | Mun. + conv. | SME dez. | Mun.+conv./SME | Direta/SME |
|---|---|---|---|---|---|---|---|
| 2010 | 42.968 | 85.244 | 41.187 | 128.212 | 130.412 | 0,983 | 0,329 |
| 2011 | 55.512 | 139.836 | 48.713 | 195.348 | 195.561 | 0,999 | 0,284 |
| 2012 | 60.621 | 145.056 | 55.751 | 205.677 | 214.094 | 0,961 | 0,283 |
| 2013 | 55.812 | 152.434 | 57.979 | 208.246 | 214.460 | 0,971 | 0,260 |
| 2014 | 57.367 | 163.166 | 60.658 | 220.533 | 228.204 | 0,966 | 0,251 |
| 2015 | 55.663 | 182.021 | 60.421 | 237.684 | 260.785 | 0,911 | 0,213 |
| 2016 | 56.751 | 216.209 | 57.525 | 272.960 | 284.179 | 0,961 | 0,200 |
| 2017 | 56.823 | 229.925 | 56.108 | 286.748 | 296.260 | 0,968 | 0,192 |
| 2018 | 56.719 | 253.228 | 55.682 | 309.947 | — | — | — |
Filtros: direta = `TP_DEPENDENCIA==3`; conveniada = `TP_DEPENDENCIA==4 & IN_CONVENIADA_PP==1 & TP_CONVENIO_PODER_PUBLICO in {1,3}`; sem convênio = `TP_DEPENDENCIA==4 & IN_CONVENIADA_PP!=1`. Ficam fora estadual, federal e conveniada só com o estado (≤1.583 matrículas/ano).

**SEADE (`build13_rates.py`, saída `cobertura_sp_seade.csv`):** 0–3 anos em 2010 = 569.975; 2015 = 563.983; 2018 = 555.696 (interpolação linear 2015–2020; 2020 = 550.172). SEADE 2010/Censo 2010 − 1 = +1,02%. Verificação (b): 0–4 anual 2018 (704.109) × 564.210/710.927 = 558.799.
| | 2010 | 2015 | 2018 (a) | 2018 (b) |
|---|---|---|---|---|
| Etapa, total | 0,2995 | 0,5293 | 0,6584 | 0,6547 |
| Etapa, mun.+conv. | 0,2249 | 0,4214 | 0,5578 | 0,5547 |
| Idade 0–3, total | 0,3833 | 0,5067 | 0,6294 | 0,6259 |
| Idade 0–3, mun.+conv. | 0,3041 | 0,3928 | 0,5223 | 0,5194 |

**Calendário (tab:calendar = Tabela A30; `build13_refcalendar.py` + `build13_calendar_table.py`):** eventos de 2011–2017. Dezembro: 5,7% das primeiras solicitações, 48,9% dos primeiros encaminhamentos, 35,8% das primeiras matrículas. Jan.+fev.: 24,9% / 15,8% / 25,9%. N = 1.227.119 / 1.190.707 / 1.001.825.
