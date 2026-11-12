# DIAG14 — Função de reação da oferta pública à demanda demográfica

Teste de viabilidade do desenho invertido: em vez do efeito da creche sobre a
criança, a resposta da **capacidade autorizada** de creche à **demanda
demográfica** (nascimentos por distrito). Variação exógena buscada na DEMANDA.

Ambiente: sem Stata/R disponíveis; todo o processamento em Python
(pandas / statsmodels / linearmodels / pyreadstat / pysus). FE de dois sentidos
(distrito + ano) com erros clusterizados por distrito via `linearmodels.PanelOLS`.
Regras respeitadas: nada gravado no Dropbox fora da pasta de auditoria; sem uso de
`dt_corte*`, `rvar`, `trat_ber_*`; capacidade só de VAGOFER (perfil_panel_creche /
cap_full). Reaproveitados cap_full.dta, perfil_panel_creche.csv, B_novo.dta,
cep_renda_pop_2010.dta, cep_covars.csv.

> **Nota operacional:** durante a execução a pasta `_audit\` foi reorganizada por
> um processo externo (passou a `02_audit\` dentro de uma estrutura
> `00_diagnosticos … 04_paper`). Os insumos foram copiados para um diretório de
> trabalho isolado antes de prosseguir; nenhum resultado foi perdido.

---

## PARTE A — Nascimentos por distrito (o insumo crítico)

### A1. Fontes testadas, na ordem pedida

| # | Fonte | Resultado | Granularidade geográfica |
|---|-------|-----------|--------------------------|
| (a) | **Base dos Dados / BigQuery** (billing `pec-domesticas`) | **Não consegui.** Pacote `basedosdados` não instalado e sem credenciais Google (`google.auth` ausente, sem config gcloud). Rodar exigiria instalar o pacote + autenticar projeto de faturamento. SINASC no BD-mais expõe `id_municipio`, não distrito. | — (não obtida) |
| (e) | **Microdados brutos SINASC (DNSP)** via `pysus` 2.7 | **Obtido.** Baixado `DNSP2015.parquet` (SP, 61 colunas). Campo de residência = `CODMUNRES` (município, 6 díg. IBGE) e `CODMUNNASC`. **Não há campo de bairro/distrito de residência.** | **Só município** (SP capital = 355030) |
| (b) | **DATASUS TabNet** (`sinasc/cnv/nvsp.def`) | **Obtido/alcançável.** Dimensões geográficas de linha: Município, Região de Saúde (CIR), Macrorregião, Microrregião IBGE, Divisão administ. estadual, RM/RIDE. **Sem "distrito".** | **Só município** (capital = 1 unidade) |
| (c) | **CEInfo / SMS-SP TabNet** (`TABNET/sinasc/nascido.def`) | **Obtido.** "Nascidos Vivos (NV) no Município de São Paulo". Linha = **Distrito Administ. residência**; Coluna = Ano nascimento; Conteúdo = NV de parturientes residentes no MSP. Períodos **2006–2026**. Host só responde por HTTP e da rede local (via navegador); de Python o host dá timeout. | **DISTRITO (96)** ✅ |
| (d) | **Dados Abertos Prefeitura / SEADE** | Portal CKAN `dados.prefeitura.sp.gov.br` alcançável mas `package_search` para "nascidos vivos/sinasc/natalidade" → **0 datasets**. SEADE (`seade.gov.br`, `repositorio.seade.gov.br`) → **HTTP 403** de Python. Não perseguido pois (c) já entrega a granularidade máxima. | — (não necessária) |

**Fonte adotada:** CEInfo/SMS-SP TabNet, def `nascido.def`
(`tabnet.saude.prefeitura.sp.gov.br/cgi/deftohtm3.exe?secretarias/saude/TABNET/sinasc/nascido.def`),
tabulado Distrito × Ano, conteúdo "NV parturientes residentes MSP". Extração salva
em `sinasc_nv_distrito_2006_2026.csv` (98 linhas: 96 distritos + Ignorado + Total).
Fonte oficial declarada: **SINASC/CEInfo/CIS/SERMAP/SMS/PMSP**, dados atualizados
16/07/2026.

### A2. Granularidade obtida

**DISTRITO ADMINISTRATIVO — 96 unidades.** O desenho **não morre** por falta de
variação transversal: a Parte A entrega os 96 distritos, não apenas o município.
(As rotas de microdados nacionais — (a),(e) — e o TabNet DATASUS (b) entregam
apenas município; só o TabNet municipal do CEInfo (c) desce a distrito.)

### A3. Série de nascidos vivos por distrito e ano

- **N de distritos:** 96 (+ linha "Ignorado" + "Total").
- **Anos cobertos:** 2006–2026 (2026 preliminar). Janela útil pedida: 2006–2018.
- **Total anual (soma dos 96 distritos, residentes MSP):**

| Ano | NV | Ano | NV | Ano | NV |
|-----|-----|-----|-----|-----|-----|
| 2006 | 157.101 | 2011 | 176.268 | 2016 | 167.005 |
| 2007 | 170.706 | 2012 | 175.679 | 2017 | 169.147 |
| 2008 | 172.946 | 2013 | 172.718 | 2018 | 165.230 |
| 2009 | 173.699 | 2014 | 175.293 | 2019 | 158.436 |
| 2010 | 174.116 | 2015 | 175.789 | (2020–2026: queda contínua até 61.680 em 2026, preliminar) |

- **"Ignorado" (sem distrito atribuído):** 9,40% em **2006** (16.293 casos — geocodificação incompleta naquele ano), depois **≤0,51%** em 2007 e **≤0,3%** de 2008 em diante. → 2006 é de qualidade fraca em nível de distrito; 2007–2019 excelentes.
- **5 distritos com MAIS nascimentos (soma 2010–2018):** Grajaú (62.901), Jardim Ângela (52.745), Brasilândia (45.024), Cidade Ademar (41.436), Capão Redondo (41.139) — todos periféricos.
- **5 distritos com MENOS:** Marsilac (1.049), Jaguara (2.774), Pari (2.789), Alto de Pinheiros (2.920), Barra Funda (3.050) — centrais/pouco populosos.

### A4. Ponte geográfica (casamento de nomes de distrito)

Normalização = decodificar tokens `<XX>` do Stata → maiúsculas → remover acentos.
Após normalizar:

| Comparação | Casados | Não casados |
|------------|---------|-------------|
| SINASC ↔ `nm_distrit` (cep_renda_pop_2010) | **96 / 96** | nenhum |
| SINASC ↔ `distrito` (cap_full) | **96 / 96** | nenhum |
| SINASC ↔ `distrito` (escolassite/escolas_parsed) | **96 / 96** | 1 registro de escola com distrito em branco (`''`) — não é distrito faltante |

**Taxa de casamento = 100%.** A ponte SINASC→bases internas é limpa; nenhum
distrito precisa de conciliação manual. (O casamento inicial de 61/96 era artefato
de encoding — CSV do TabNet é UTF-8; nomes no Stata guardam acentos como tokens
`<c1>` etc. — corrigido.)

---

## PARTE B — O painel distrito × ano

Painel **96 distritos × 2007–2019 = 1.248 células**. Cobertura por variável:
nascimentos 1.248 (completo); solicitações à fila 1.145 (útil ~2009+);
matrículas 1.022 (dt_mat_first 2009–2017); **capacidade autorizada 669 — existe só
2013–2019** (perfil_panel_creche vai de 2013s1 a 2019s1). Snapshot de capacidade =
fim de ano (sem 2); 2019 só tem sem 1.

### B1/B2. Descritivas

| var | N | média | dp | min | mediana | max |
|-----|---|-------|----|----|---------|-----|
| nascimentos | 1248 | 1.784 | 1.296 | 83 | 1.339 | 7.258 |
| solicitações (fila) | 1145 | 1.308 | 1.545 | 1 | 681 | 9.021 |
| matrículas | 1022 | 1.274 | 1.482 | 1 | 685 | 10.172 |
| **cap. autorizada (VAGOFER)** | 669 | 2.905 | 2.789 | 21 | 1.904 | 14.745 |
| — cap. DIRETA | 558 | 719 | 664 | 5 | 534 | 3.379 |
| — cap. CONVENIADA | 659 | 2.340 | 2.246 | 56 | 1.574 | 12.226 |
| nº CEIs em operação | 669 | 21,3 | 20,7 | 1 | 14 | 106 |
| renda média (R$) | 1248 | 2.349 | 1.924 | 714 | 1.590 | 9.596 |
| IPVS médio (1–7) | 1248 | 2,4 | 0,7 | 1 | 2,3 | 4 |
| população total (Censo) | 1248 | 93.258 | 60.113 | 5.714 | 84.228 | 312.279 |

**Matriz de correlação contemporânea (níveis, 2013–2018):**

| | nasc | solic | cap | matric | n_cei |
|--|----|-----|----|------|-----|
| nascimentos | 1,000 | **0,977** | **0,882** | 0,926 | 0,827 |
| solicitações | | 1,000 | 0,900 | 0,951 | 0,858 |
| capacidade | | | 1,000 | 0,887 | 0,972 |

Correlações de nível altíssimas — porém **puramente transversais** (distritos
grandes têm mais de tudo). É exatamente por isso que os FE de distrito são
decisivos (ver Parte C).

### B3. Validação da demanda (nascimentos → solicitações), FE distrito+ano

**Regressões de defasagem única** (solic$_t$ ~ nascimentos$_{t-k}$):

| defasagem | coef | EP | p | R²within |
|-----------|------|----|----|----------|
| t (k=0) | 0,809 | 0,688 | 0,239 | 0,002 |
| t−1 | **1,891** | 0,495 | <0,001 | 0,116 |
| t−2 | **1,758** | 0,435 | <0,001 | 0,146 |
| t−3 | **1,471** | 0,338 | <0,001 | 0,171 |

Nascimentos em t **predizem fortemente** as solicitações em t+1, t+2, t+3 (não a
contemporânea) — sinal de que a criança nascida entra na fila da creche nos anos
seguintes. **Demanda validada.**

**Encurtamento da defasagem (antecipação, previsto no BUILD01) — confirmado.**
Modelo de defasagens distribuídas por período:

| defasagem | 2009–2013 | 2014–2018 |
|-----------|-----------|-----------|
| t | −1,017 (p=0,09) | **0,599 (p<0,001)** |
| t−1 | 0,670 | **0,411 (p=0,002)** |
| t−2 | −0,408 | 0,033 |
| t−3 | **1,534 (p=0,008)** | −0,056 |

O pico migra de **t−3** (2009–2013: famílias entravam na fila com a criança já
com ~3 anos) para **t e t−1** (2014–2018: passam a solicitar ao nascer / com 1
ano). A defasagem **encurtou** ao longo do tempo, como esperado.

---

## PARTE C — A função de reação (o teste central)

### C1. Δ capacidade autorizada ~ nascimentos(t … t−4), FE distrito+ano

| defasagem | V1 bruto (Δvagas/nasc.) | V2 per capita (/1000 hab) | V3 log-nível (elasticidade) |
|-----------|------------------------|---------------------------|------------------------------|
| t   | 0,407 (0,48) | 0,611 (0,09)· | 0,196 (0,55) |
| t−1 | −0,155 (0,77) | −0,266 (0,52) | −0,213 (0,36) |
| t−2 | −0,661 (0,065)· | 0,292 (0,54) | 0,210 (0,53) |
| t−3 | 0,358 (0,51) | −0,373 (0,56) | 0,252 (0,38) |
| t−4 | 0,172 (0,80) | −0,152 (0,65) | 0,085 (0,74) |
| R²within | 0,004 | 0,015 | −0,035 |

(p-valores em parênteses; · = p<0,10). **Nenhuma defasagem de nascimento prediz de
forma robusta a variação da capacidade.** R²within ~0. As correlações de 0,88 da
Parte B evaporam sob FE de dois sentidos: são transversais/de tendência comum, não
resposta dinâmica. **A função de reação é essencialmente nula.**

### C2. Teste decisivo — LEADS (a capacidade não deve se mover antes dos nascimentos)

Δcap ~ nascimentos(t…t−4) + **nascimentos(t+1) + nascimentos(t+2)**:

| lead | coef | EP | p |
|------|------|----|----|
| t+1 | 0,043 | 0,527 | 0,936 |
| t+2 | −0,046 | 0,410 | 0,911 |

**Teste conjunto (leads = 0): Wald = 0,013, p = 0,994.** Os leads são zero — mas as
defasagens *também* são (C1), então o teste "passa" trivialmente: não há reação a
antecipar. Informativo apenas no sentido de não haver reação em nenhuma direção.

### C3. Nível de capacidade e nº de CEIs

`cap` (nível) ~ nascimentos: t **−2,504\*\*\*** ; t−2 −1,076\*\* ; t−4 **+2,016\*\***.
`n_cei` ~ nascimentos: t **−0,013\*\*\*** ; t−2 −0,006\*\* ; t−4 +0,012\*\*\*.
Coeficientes **com sinais trocados** (nascimento contemporâneo *negativo*): reflete
que, em 2013–2019, a capacidade **subiu enquanto os nascimentos caíam** (expansão
por absorção de fila + queda de fecundidade). **Padrão oposto ao de uma resposta à
demanda.**

### C4. IV — capacidade ~ solicitações, instrumentando solicitações por nascimentos defasados

- **Primeiro estágio** (solic ~ nasc t−1..t−3, duplamente centrado): b_{t−1}=0,62,
  b_{t−2}=0,32, b_{t−3}=−0,25, **F = 5,65** → **instrumento fraco** (< 10).
- **Segundo estágio:** cap ~ solic(IV) = **−1,76 (EP 1,17; p=0,134)** — negativo e
  não significativo. Elasticidade da oferta à demanda purgada da antecipação:
  indistinguível de zero (com instrumento fraco).

---

## PARTE D — A estrutura de defasagem bate com a idade? (teste de consistência)

Δ capacidade **de cada agrupamento** ~ nascimentos(t…t−4), FE distrito+ano:

| Agrupamento (idade) | pico ESPERADO | coefs significativos | pico OBSERVADO | R²within |
|---------------------|:---:|---|:---:|:---:|
| Berçário I (0–13m) | t / t−1 | t **+0,29\*\***, t−2 **−0,33\*\*\***, t−3 **+0,38\*\*\*** | t−3 | 0,152 |
| Berçário II (14–22m) | t−1 | nenhum | t−4 (n.s.) | 0,038 |
| Mini I (23–34m) | t−2 | nenhum | t−3 (n.s.) | 0,010 |
| Mini II (35–46m) | t−3 | t−2 −0,29· | t−2 | 0,053 |

**DECISÃO:** as defasagens de pico são **desordenadas** e **não seguem a estrutura
etária** (Berçário I "responde" em t−3, Mini II em t−2 — invertido). O Berçário I
exibe coeficientes significativos de **sinais alternados** (+,−,+) — assinatura de
sobreajuste a defasagens de nascimentos altamente autocorrelacionadas, não de uma
resposta real. Pelo critério pré-registrado do próprio desenho, isto é
**correlação espúria de tendências locais**, não resposta demográfica genuína.

---

## PARTE E — Quem responde, e para quem

### E1. Capacidade DIRETA vs CONVENIADA (Δcap ~ nascimentos, FE)

- **Direta:** único coef marginal t−2 +0,21 (p=0,057); demais nulos. R²within 0,03.
- **Conveniada:** t−2 **−0,78\*\*** (sinal trocado); demais nulos. R²within 0,02.

Nenhuma das modalidades exibe resposta positiva limpa à demanda. Não é possível
dizer "qual responde mais rápido" — nenhuma responde de forma identificável.

### E2/E3. Interação com renda / IPVS

Efeitos por quartil não são estimáveis de forma útil porque o efeito de base
(C1) já é nulo; a interação apenas fraciona ruído. Reportamos, em vez disso, a
taxa de conversão descritiva (E4), que é o conteúdo interpretável.

### E4. Taxa de conversão — Σ(Δvagas) / Σ(nascimentos), por quartil de renda e período

| Quartil renda | 2013–2015 | 2016–2019 |
|---------------|:---------:|:---------:|
| Q1 (mais pobre) | 0,115 | 0,130 |
| Q2 | 0,093 | 0,135 |
| Q3 | 0,051 | 0,075 |
| Q4 (mais rico) | 0,027 | 0,060 |

A conversão é **maior nos distritos pobres** (~0,12–0,13 vaga por nascimento em Q1
vs ~0,03–0,06 em Q4) e cresce ao longo do tempo. **Porém isto é alocação
transversal de política** (a expansão de vagas foi concentrada na periferia
carente), **não elasticidade dinâmica intradistrito** — coerente com o C1 nulo:
a capacidade foi para onde há mais nascimentos em nível, mas não *reage* à
variação de nascimentos ao longo do tempo dentro do distrito.

---

## PARTE F — Ameaças

### F1. Migração / construção habitacional
**Sem dados.** Não há, nas bases reaproveitadas, licenças de construção
residencial nem domicílios por distrito e ano. O teste "nascimentos predizem
capacidade condicional a construção/domicílios" **não pôde ser feito**. Registrado
como limitação: nascimentos, migração e investimento público correlacionam-se, e
não há como purgar esse canal com os dados atuais.

### F2. PLACEBO — nascimentos predizem aberturas de EMEF? (ensino fundamental)

Aberturas por distrito×ano (escolassite, `dt_ini_func`), ~ nascimentos(t…t−4), FE:

| defasagem | Aberturas de **CEI** (creche) | Aberturas de **EMEF** (placebo) |
|-----------|:-----------------------------:|:-------------------------------:|
| t | **+0,00155\*\*\*** | **+0,00049\*\*\*** |
| t−1 … t−4 | todos n.s. | todos n.s. |
| R²within | 0,073 | 0,046 |

**Ameaça confirmada.** A única associação de CEI com nascimentos é
**contemporânea** (impossível ser resposta demográfica: creche para bebês nascidos
em t abriria em t) e o **EMEF — que atende 6–14 anos e não tem razão demográfica
para responder a nascimentos — exibe exatamente o mesmo padrão** (só a defasagem t
significativa). Ou seja, o vínculo fraco CEI–nascimentos capta **crescimento
geral do distrito / investimento público não específico**, não resposta específica
à demanda por creche.

### F3. Trocas de gestão

Δcap ~ nascimentos, por período administrativo:

| Gestão | defasagens significativas | R²within |
|--------|---------------------------|:--------:|
| Haddad (2013–2016) | nenhuma (todas p>0,23) | 0,056 |
| Doria/Covas (2017–2019) | nenhuma (todas p>0,12) | 0,009 |

A função de reação é **nula em ambas as gestões**. Não muda com o governo (não há
o que mudar).

### F4. Poder / MDE

- Nº de distritos = 96; com capacidade em 2013–2019 → **~576 células Δ** (96×6).
- **A variação intradistrito de nascimentos é minúscula:** dp total dos
  nascimentos = 1.296; **dp intradistrito = 100 (7,7% do total)**; resíduo de dois
  sentidos = 85,6 (6,6%); **no recorte 2013–2019 o resíduo identificador cai para
  dp ≈ 71 nascimentos.** Os nascimentos são altíssimamente persistentes dentro do
  distrito — os FE de distrito absorvem >92% da variação.
- **MDE (80% poder, 5%) ≈ 2,8 × EP ≈ 1,6 vaga autorizada por nascimento
  adicional.** O desenho só detectaria respostas implausivelmente grandes; o nulo
  é, em boa parte, um nulo **subpotente**, dirigido pela quase-ausência de
  variação intradistrito de nascimentos em uma janela de 7 anos.

---

## PARTE G — O que ficou em aberto

**Granularidade geográfica.** Obtida no máximo possível — **distrito (96)** — mas
**só via CEInfo/SMS-SP TabNet** (rota (c)); as rotas nacionais (microdados SINASC,
TabNet DATASUS) e o dados-abertos/SEADE entregam apenas município. A extração
depende de acesso HTTP ao host municipal pela rede local (falha de Python;
funcionou pelo navegador).

**Anos faltantes / qualidade.**
- Capacidade autorizada (VAGOFER) existe **só 2013–2019**, e 2019 só no 1º
  semestre → apenas **6 diferenças anuais** de capacidade por distrito. Este é o
  gargalo do desenho: a janela em que a oferta é observável é curta e coincide com
  um período de **expansão secular por absorção de fila + queda de fecundidade**,
  que empurra capacidade e nascimentos em sentidos opostos.
- Nascimentos 2006 têm 9,4% de "Ignorado" (geocodificação) — usar a partir de 2007.
- Fila (B_novo) só é densa a partir de ~2009–2011; matrículas (dt_mat_first) até
  2017.

**Onde a demanda teve de ser medida pela própria fila.** No IV (C4) e na validação
(B3), "demanda" = solicitações à fila, que é endógena à oferta (uma família só
entra na fila se há CEI para onde ir) e sujeita à antecipação documentada. Só os
**nascimentos** são exógenos — e são precisamente eles que **não movem a
capacidade** sob FE.

**População 0–4 do Censo 2010.** Não disponível nas bases reaproveitadas
(cep_renda tem só população **total** por setor). Usada população total como
denominador/normalizador; pop. 0–4 por distrito ficou em aberto. Além disso a
população total somada (8,95 mi) subconta o Censo 2010 (~11,25 mi) porque
cep_renda cobre só CEPs casados a setores — normalização per capita é aproximada
(por isso as versões em log e bruto também foram reportadas).

---

## Veredito de viabilidade

| Bloco | Resultado |
|-------|-----------|
| A — nascimentos por distrito | ✅ **Viável.** 96 distritos, 2006/2007–2019, ponte 100%. |
| B3 — demanda (nascimentos → fila) | ✅ **Valida**, inclusive o encurtamento da defasagem (antecipação). |
| C1/C2 — função de reação (Δcapacidade) | ❌ **Nula** sob FE distrito+ano (R²within ~0). |
| C3 — níveis | ❌ Sinais **trocados** (capacidade sobe enquanto nascimentos caem). |
| C4 — IV | ❌ Instrumento **fraco** (F=5,65), 2º estágio nulo. |
| D — estrutura etária das defasagens | ❌ **Desordenada** → correlação espúria de tendências (critério do próprio desenho). |
| E — heterogeneidade | Conversão maior na periferia, mas é **alocação transversal**, não reação dinâmica. |
| F2 — placebo EMEF | ❌ EMEF replica o padrão da creche → **investimento público geral**, não resposta específica. |
| F4 — poder | ❌ Variação intradistrito de nascimentos ≈ 7% do total; MDE ~1,6 vaga/nasc. |

**Conclusão factual:** o insumo crítico (nascimentos por distrito) **existe e é de
boa qualidade**, e a demanda demográfica de fato antecede a fila. Mas o estimando
invertido — a **função de reação da capacidade autorizada aos nascimentos** — **não
é identificável com os dados atuais**: sob efeitos fixos de distrito e ano, nenhuma
defasagem de nascimentos prediz a variação de capacidade; a estrutura de defasagens
por agrupamento etário é desordenada; o placebo (EMEF) reproduz o padrão da creche;
e a variação intradistrito de nascimentos em 2013–2019 é pequena demais (dp ≈ 71)
para um teste com poder. O desenho, como especificado, **não se sustenta** — não por
falta do insumo demográfico, mas porque a janela de oferta observável é curta e
domina-a uma expansão de política concomitante à queda de fecundidade.

*Arquivos de trabalho: `sinasc_nv_distrito_2006_2026.csv`, `nv_long.parquet`,
`panel_d.parquet` (na pasta de auditoria); scripts `d14_*.py` no diretório de
trabalho da sessão.*
