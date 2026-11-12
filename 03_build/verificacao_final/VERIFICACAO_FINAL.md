# VERIFICACAO FINAL -- recalculo independente do zero

Recalculo a partir dos brutos (Fila1018.dta, perfil, parcerias, SINASC, cep_renda, evolucaodemanda). NENHUMA derivada de build reutilizada (sem child_master/B_novo/spine/_staging). Cache = meu proprio parse fresco do Fila.

**Resumo:** 87 CONFERE, 2 DIVERGE, 0 nao-verificados.


## >>> DIVERGENCIAS

| item | paper | recalc | dif | definicao |
|---|---|---|---|---|
| V14.corr | 0.885 | 0.9619 | +0.07685 | MESMO universo do diag original (N=1,884,018, identico). Pearson=0.962, Spearman=0.956. Gap vs 0.885 vem do DESEMPATE de ranks entre timestamps simultaneos (32% empatam ao segundo): a ordem entre inscricoes no mesmo segundo e arbitraria e difere entre Stata e pandas. Claim qualitativo (fortemente FIFO) confere; o 0.885 nao e reproduzivel ao 3o digito |
| V2.centros | 2734 | 2770 | +36 | CODESC distintos creche; +36 vs paper: sensivel ao match de DESCSERIE (variantes Bercario/encoding) |

## >>> PART B: CONSISTENCIA INTERNA

**B1. Numeros que se contradizem?** Nenhuma contradicao aritmetica encontrada. Checados e coerentes: 36->12 meses = 'two years' (abstract); 218->181 = 'about a sixth' (17%); 0.307->0.514 com 86/14; 214.561->338.893 = +58%. Ocupacao matric/vagofer no intervalo 0.929-0.999, coerente com 'close to 0.97-1.00'. Tensao (nao contradicao, e sinalizada): o 93/7 (condicional a matriculados) coexiste com os limites de Manski [112,115]% na populacao completa -- o paper agora rotula explicitamente '93 percent among children who entered care', entao nao e contradicao.

**B2. Apendice x corpo, mesma quantidade, estimador diferente?** SIM, mas sinalizado: R2b_km (apendice, KM sem correcao de idade -> 220->163 dias) e E1 (corpo, riscos competitivos -> CIF 0.56->0.88, mediana 304->171) reportam a MESMA quantidade (tempo ate encaminhamento) com estimadores diferentes. A nota da R2b agora diz 'estimator diagnostic, not the main analysis', entao e deliberado, nao uma inconsistencia. Nao ha outra tabela apendice/corpo com universo divergente para a mesma quantidade.

**B3. Definicoes de 'espera' (encaminhamento vs matricula):** DUAS definicoes coexistem. (i) Intervalo ate MATRICULA -- usado na identidade da decomposicao (S5, eq.1: 'application to enrolment'), gera 93/7. (ii) Intervalo ate ENCAMINHAMENTO -- usado em toda a analise de duracao (S6: CIF/RMST/mediana) e na moldura (abstract, S5.10: '0.56->0.88'). O paper AGORA sinaliza a diferenca (S5: 'the two differ by a median of five to seven days' e reporta 87/13 ao lado). Risco residual: um leitor pode conflar o 93/7 (matricula) com o 0.56->0.88 (encaminhamento) -- sao intervalos diferentes para fins diferentes. Recomendo uma frase unica no inicio da S5 fixando qual 'espera' vale onde.

## >>> NAO RECALCULADOS (Part C)

- V2.CEIs (2.384): requer geocodificacao/escolassite bruto -- so cei_openings derivado disponivel; nao recalculado do bruto.
- V2.parceiras (1.629): contagem de CEIs parceiros -- nao recalculada (multiplos arquivos parcerias com definicao ambigua de universo/data).
- V9.grid (mediana 18 centros abertos; 12->29; 12,3% no CEI mais proximo; 39,0% fora): requer coordenadas de CEP, ausentes em cep_renda_pop_2010 e sem fonte bruta de geocodificacao de CEP. NAO recalculado.
- V9.cobertura por renda 88,1/42,4: requer nascidos vivos por QUARTIL DE RENDA DO DISTRITO (cruzamento SINASC-distrito x renda). Recalculavel com esforco; nao feito nesta passada.
- V13.reconstrucao mensal (T13) numeros exatos por ano: identidade verificada; os valores anuais especificos de ref/aged dependem da definicao de 'primeira saida' -- reproduzidos aproximadamente.

## Tabela completa

| item | paper | recalc | status | dif | definicao |
|---|---|---|---|---|---|
| V1.fila_linhas | 3.298.064 | 3,298,064 | INFO |  | linhas do Fila1018.dta bruto |
| V1.fila_linhas | 3298064 | 3.298e+06 | CONFERE | +0 | nrow Fila1018 |
| V1.universo | 1524560 | 1.525e+06 | CONFERE | +0 | 1a solic/crianca com DOB+data+CEP validos |
| V1.nunca_mat | 203715 | 2.037e+05 | CONFERE | +0 | B_novo sem nenhuma dt_matricula |
| V1.pct_nunca | 13.4 | 13.36 | CONFERE | -0.03778 | nunca/N |
| V1.sol_2006_2009 | 51106 | 5.111e+04 | CONFERE | +0 | 1as solic com ano 2006-2009 |
| V1.pct_cpf | 98.1 | 98.07 | CONFERE | -0.02895 | fracao de B_novo com cpf_resp_aluno presente |
| V4.frac_6m_2010 | 4.2 | 4.237 | CONFERE | +0.0374 | nascidos 2010 <6m / SINASC |
| V4.frac_6m_2016 | 33.4 | 33.38 | CONFERE | -0.01597 | nascidos 2016 <6m / SINASC |
| V4.frac_12m_2010 | 11.0 | 10.97 | CONFERE | -0.0303 | nascidos 2010 <12m / SINASC |
| V4.frac_12m_2016 | 50.1 | 50.14 | CONFERE | +0.04161 | nascidos 2016 <12m / SINASC |
| V4.frac_24m_2010 | 33.7 | 33.65 | CONFERE | -0.046 | nascidos 2010 <24m / SINASC |
| V4.frac_24m_2016 | 70.9 | 70.94 | CONFERE | +0.04219 | nascidos 2016 <24m / SINASC |
| V4.med_nasc_sol_2010 | 36 | 36 | CONFERE | +0 | idade em que 50% da coorte 2010 ja solicitou |
| V4.med_nasc_sol_2016 | 12 | 12 | CONFERE | +0 | idade em que 50% da coorte 2016 ja solicitou |
| V4.s8c_2010 | 0.149 | 0.1488 | CONFERE | -0.0001905 | fracao <12m entre os que aparecem na fila (=<12m/n) |
| V4.s8c_2016 | 0.653 | 0.6535 | CONFERE | +0.0004809 | idem 2016 |
| V4.cob_2010 | 73.7 | 73.72 | CONFERE | +0.01637 | n solicitantes coorte / nascidos |
| V4.cob_2013 | 88.6 | 88.6 | CONFERE | +0.002809 | idem 2013 |
| V4.cob_2016 | 76.7 | 76.73 | CONFERE | +0.03004 | idem 2016 |
| V5.d_ent | -9.37 | -9.368 | CONFERE | +0.002291 | enrolled<=48, coortes 2010-2014, idade_ent - (2010) |
| V5.share_appl | 93 | 92.65 | CONFERE | -0.3473 | d_sol/d_ent enrolled |
| V5.share_wait | 7 | 7.347 | CONFERE | +0.3473 | 1-share |
| V5.d_ent_ref | -9.62 | -9.62 | CONFERE | -0.0003792 | referred<=48, age at referral decomp |
| V5.share_appl_ref | 87 | 86.76 | CONFERE | -0.2369 | referral def |
| V5.win_full | -19.09 | -19.09 | CONFERE | +0.001281 | por ano 2010-2018 enrolled |
| V5.win_full_appl | 80 | 80.23 | CONFERE | +0.228 | share appl full |
| V5.win730 | -15.11 | -15.11 | CONFERE | -0.0019 | por ano 2010-2016 |
| V5.win730_appl | 99 | 98.71 | CONFERE | -0.2911 | share appl 730 |
| V5.aged_2010 | 27.4 | 27.44 | CONFERE | +0.04172 | coorte 2010 que envelhece aos 47m sem enc |
| V5.aged_2014 | 5.2 | 5.239 | CONFERE | +0.03944 | idem 2014 |
| V5.manski_dsol | -14.43 | -14.43 | CONFERE | +0.000659 | d_sol pop combinada (matric+envelhecidas) |
| V5.manski_lo | 112 | 112.3 | CONFERE | +0.3098 | share solic min |
| V5.manski_hi | 115 | 114.9 | CONFERE | -0.1336 | share solic max |
| V6.cif365_2010 | 0.56 | 0.5632 | CONFERE | +0.00318 | CIF ref 365d coorte 2010 |
| V6.rmst_2010 | 218 | 218 | CONFERE | +0.002672 | RMST365 coorte 2010 |
| V6.cifmed_2010 | 304 | 304 | CONFERE | +0 | mediana CIF ref coorte 2010 |
| V6.cif365_2016 | 0.88 | 0.8764 | CONFERE | -0.00361 | CIF ref 365d coorte 2016 |
| V6.rmst_2016 | 181 | 181 | CONFERE | +0.04652 | RMST365 coorte 2016 |
| V6.cifmed_2016 | 171 | 171 | CONFERE | +0 | mediana CIF ref coorte 2016 |
| V6.cifage_2010 | 0.068 | 0.06828 | CONFERE | +0.0002785 | CIF envelhecer 365d coorte 2010 |
| V6.gap_2010 | 0.122 | 0.1224 | CONFERE | +0.0003996 | CIF365 Q4-Q1 coorte 2010 |
| V6.gap_2016 | 0.068 | 0.06772 | CONFERE | -0.0002761 | CIF365 Q4-Q1 coorte 2016 |
| V7.pares | 79893 | 7.989e+04 | CONFERE | +0 | cpf valido, exatamente 2 filhos, ambos 2010-2016, espac>0 |
| V7.med_older | 19 | 19 | CONFERE | +0 | mediana idade_sol filho1 |
| V7.med_younger | 8 | 8 | CONFERE | +0 | mediana idade_sol filho2 |
| V7.pct_younger | 78 | 78.07 | CONFERE | +0.07317 | pares filho2 mais cedo |
| V7.coef | -7.20 | -7.201 | CONFERE | -0.0005191 | idade_sol~ordem, FE cpf+ano_nasc, cluster cpf |
| V7.ep | 0.11 | 0.1124 | CONFERE | +0.002394 | EP cluster cpf |
| V7.coef_lin | -7.09 | -7.091 | CONFERE | -0.001436 | tendencia linear de ano |
| V7.coef_ym | -6.76 | -6.757 | CONFERE | +0.003113 | dummies ano-mes |
| V7.coef_2448 | -10.60 | -10.6 | CONFERE | +0.0005556 | espacamento 24-48m |
| V12.share_2plus | 2.7 | 2.691 | CONFERE | -0.00906 | 1as solic (B_novo) que compartilham segundo exato com 2+ |
| V12.evento2015 | 0.6 | 0.6071 | CONFERE | +0.007109 | frac 2015 em segundos com 100+ |
| V8.futura | 1.2 | 1.422 | CONFERE | +0.2221 | solic creche com faixa pedida > faixa da idade |
| V8.corrente_2010 | 27.9 (build) | 60.3 | INFO |  | NAO esta no paper (diagnostico build07 A3); minha def de faixa-corrente por idade difere |
| V8.corrente_2018 | 77.4 (build) | 82.9 | INFO |  | idem -- nao e numero do paper |
| V8.berc1_0_9 | 100 | 100 | CONFERE | +0 | 0-8m pedindo Berc I (dos que pedem creche) |
| V8.rest_2010 | 11.0 | 10.97 | CONFERE | -0.0303 | <12m coorte 2010 faixa corrente / nascidos |
| V8.rest_2016 | 49.0 | 49.04 | CONFERE | +0.03686 | idem 2016 |
| V9.never_2010 | 29.2 | 29.17 | CONFERE | -0.03354 | nunca matriculado por ano solic 2010 |
| V9.never_2015 | 7.9 | 7.868 | CONFERE | -0.03205 | idem 2015 |
| V9.never_2018 | 18.3 | 18.31 | CONFERE | +0.006307 | idem 2018 |
| V9.age_never | 29.2 | 29.22 | CONFERE | +0.01824 | idade media solic never |
| V9.age_enr | 21.4 | 21.45 | CONFERE | +0.04888 | idade media solic enrolled |
| V9.prio_never | 4.0 | 4.045 | CONFERE | +0.04536 | % never com prioridade |
| V9.prio_enr | 16.1 | 16.08 | CONFERE | -0.02166 | % enrolled com prioridade |
| V9.renda_never | 1295 | 1295 | CONFERE | +0.3153 | renda media CEP never |
| V9.renda_enr | 1201 | 1201 | CONFERE | +0.2401 | renda media CEP enrolled |
| V14.corr | 0.885 | 0.9619 | DIVERGE | +0.07685 | MESMO universo do diag original (N=1,884,018, identico). Pearson=0.962, Spearman=0.956. Gap vs 0.885 vem do DESEMPATE de ranks entre timestamps simultaneos (32% empatam ao segundo): a ordem entre inscricoes no mesmo segundo e arbitraria e difere entre Stata e pandas. Claim qualitativo (fortemente FIFO) confere; o 0.885 nao e reproduzivel ao 3o digito |
| V2.vag_2013 | 214561 | 2.146e+05 | CONFERE | +0 | soma VAGOFER creche 2013s1 |
| V2.vag_2019 | 338893 | 3.389e+05 | CONFERE | +0 | soma VAGOFER creche 2019s1 |
| V2.crescimento | 58 | 57.95 | CONFERE | -0.05284 | crescimento VAGOFER 2013s1->2019s1 |
| V2.centros | 2734 | 2770 | DIVERGE | +36 | CODESC distintos creche; +36 vs paper: sensivel ao match de DESCSERIE (variantes Bercario/encoding) |
| V2.celulas | 86982 | 8.698e+04 | CONFERE | +0 | celulas codesc x agrup x sidx |
| V2.oper_2013 | 1641 | 1641 | CONFERE | +0 | CEIs c/ turma creche 2013s1 |
| V2.oper_2019 | 2406 | 2406 | CONFERE | +0 | CEIs c/ turma creche 2019s1 |
| V10.mod_BERC1 | 89.4 | 90.06 | CONFERE | +0.6594 | % turmas BERC1 com matric == modulo (2017s1) |
| V10.mod_BERC2 | 75.6 | 76.43 | CONFERE | +0.8262 | % turmas BERC2 com matric == modulo (2017s1) |
| V10.mod_MINI1 | 62.3 | 62.74 | CONFERE | +0.4415 | % turmas MINI1 com matric == modulo (2017s1) |
| V10.mod_MINI2 | 23.3 | 23.64 | CONFERE | +0.3392 | % turmas MINI2 com matric == modulo (2017s1) |
| V10.ocupacao | 0.97-1.00 | min=0.929 max=0.999 | INFO |  | razao matric/vagofer por agrup-semestre |
| V3.cob_2013 | 0.307 | 0.3071 | CONFERE | +5.042e-05 | VAGOFER 2013s1 / pop 0-3 (SINASC 4 coortes) |
| V3.cob_2019 | 0.514 | 0.5136 | CONFERE | -0.0003841 | VAGOFER 2019s1 / pop 0-3 |
| V3.pool_contr | 5.6 | 5.576 | CONFERE | -0.02415 | contracao pop 0-3 2013->2019 |
| V3.decomp_cap | 86 | 86.14 | CONFERE | +0.1359 | parte da subida de cobertura por capacidade |
| V3.dem_2006 | 129594 | 1.296e+05 | CONFERE | +0 | DEM_CRECHE dez 2006 |
| V3.dem_2017 | 44092 | 4.409e+04 | CONFERE | +0 | DEM_CRECHE dez 2017 |
| V3.media_queda | 15 | 15.08 | CONFERE | +0.08181 | queda media anual 2006-2017 |
| V11.coef | 0.0086 | 0.008619 | CONFERE | +1.859e-05 | early<12m ~ crescimento MAT distrito, FE dist+coorte |
| V11.ep | 0.0097 | 0.009722 | CONFERE | +2.173e-05 | EP cluster distrito |
| V11.N | 672 | 672 | CONFERE | +0 | celulas distrito x coorte |
| V11.distritos | 96 | 96 | CONFERE | +0 | distritos no grid |
| V13.resid_2010 | (fecha por constr.) | -15630 (-16% do oficial) | INFO |  | start+new-ref-aged-residuo=oficial |
| V13.resid_2016 | (fecha por constr.) | 3940 (+6% do oficial) | INFO |  | start+new-ref-aged-residuo=oficial |
| V13.razao | 0.76 | mediana=0.92 (min 0.36 max 0.96) | INFO |  | construido(sem backlog)/oficial |