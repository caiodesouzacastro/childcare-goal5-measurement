* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud  "$NE_ROOT\02_audit"
global dsme "$NE_ROOT\dados_restritos\Dados - SME\Atual (25.06)"
cap log close
log using "$aud\diag02_ABD.log", text replace

*==============================================================
di "########## A2 — estatísticas das variáveis candidatas ##########"
*--- corteescolaunique: dt_corte, dt_corte_escola ---
use "$dsme\corteescolaunique.dta", clear
di "corteescolaunique.dta: N=" _N
foreach v in dt_corte dt_corte_escola {
    qui count if !missing(`v')
    di "  `v': N nao-missing=" r(N)
    sum `v', detail
    di "    (mostrar como data) min=" %td r(min) "  max=" %td r(max)
}

*--- tipo_prioridade_encaminhamento no fila bruto ---
use "$dsme\matriculas\fila1018.dta", clear
di "matriculas/fila1018.dta: N=" _N
di "--- tabulate tipo_prioridade_encaminhamento (miss) ---"
tab tipo_prioridade_encaminhamento, miss

*==============================================================
di ""
di "########## A3 — corteescolaunique: 1 linha por escola-ano-serie? ##########"
use "$dsme\corteescolaunique.dta", clear
duplicates report an_letivo_encaminhamento serie_aluno cd_esc_encaminhamento
di "--- tab serie_aluno x ano (contagem de escolas) ---"
tab serie_aluno an_letivo_encaminhamento

*==============================================================
di ""
di "########## B2/B3/B5/B6/D — base b1_2011 ##########"
use "$aud\b1_2011_audit.dta", clear
di "N b1_2011 = " _N

* datas de matricula
gen double dt_mat = date(dt_matricula, "DMY hms")
format dt_mat %td
gen mat_nm  = !missing(dt_mat)
gen esc_trat_nm = !missing(esc_trat)
gen anmat_nm = !missing(an_letivo_matricula)
gen esc_mat_nm = !missing(cd_esc_matricula)

di ""
di "===== B2 — tabulate exp_tratamento (b1_2011) ====="
tab exp_tratamento, miss

di ""
di "===== B3 — cruzamentos exp_tratamento x ... ====="
di "--- exp_tratamento x dt_matricula não-missing ---"
tab exp_tratamento mat_nm, miss
di "--- exp_tratamento x an_letivo_matricula ---"
tab exp_tratamento an_letivo_matricula, miss
di "--- exp_tratamento x esc_trat não-missing ---"
tab exp_tratamento esc_trat_nm, miss
di "--- exp_tratamento x trat2011ber ---"
tab exp_tratamento trat2011ber, miss
di "--- exp_tratamento x encaminhado ---"
tab exp_tratamento encaminhado, miss

di ""
di "===== B4 (cruzamentos) — encaminhado x esc_trat/ dt_matricula ====="
tab encaminhado esc_trat_nm, miss
tab encaminhado mat_nm, miss

di ""
di "===== B5 — dt_matricula / an_letivo_matricula ====="
di "N dt_matricula não-missing = "
count if mat_nm==1
di "N an_letivo_matricula não-missing = "
count if anmat_nm==1
di "--- distribuição por an_letivo_matricula ---"
tab an_letivo_matricula, miss
di "--- distribuição por ano de dt_matricula ---"
gen ano_mat = year(dt_mat)
tab ano_mat, miss
* idade em meses na matricula (usa ano_nasc/mes_nasc; sem dia de nascimento)
gen idade_mat_meses = (year(dt_mat) - ano_nasc)*12 + (month(dt_mat) - mes_nasc) if mat_nm==1
di "--- idade em meses na data de matricula ---"
sum idade_mat_meses, detail

di ""
di "===== B6 — quantas crianças têm matrícula em CEI (algum momento) ====="
di "com an_letivo_matricula não-missing:"
count if anmat_nm==1
di "com cd_esc_matricula não-missing:"
count if esc_mat_nm==1
di "com dt_matricula não-missing:"
count if mat_nm==1
di "NUNCA (an_letivo_matricula missing):"
count if anmat_nm==0
di "NUNCA (cd_esc_matricula missing):"
count if esc_mat_nm==0

*==============================================================
di ""
di "########## D — quantificar o artefato rvar==0 ##########"
* padronização de prof_mat já feita dentro de b1_2011 no build audit
scalar h = 54.549695
di "===== D1 — prof_mat: rvar==0 vs tratados 0<rvar<=h vs controles -h<=rvar<0 ====="
di "--- (i) rvar==0 ---"
sum prof_mat if rvar==0
di "--- (ii) tratados 0<rvar<=h ---"
sum prof_mat if rvar>0 & rvar<=h & !missing(rvar)
di "--- (iii) controles -h<=rvar<0 ---"
sum prof_mat if rvar>=-h & rvar<0 & !missing(rvar)

di ""
di "===== D2 — especificação principal excluindo APENAS rvar==0 ====="
rdrobust prof_mat rvar if rvar!=0, c(0) kernel(triangular) bwselect(mserd) vce(cluster escola_rdd)
di "D2: tau_cl=" e(tau_cl) "  se_rb=" e(se_tau_rb) "  p_rb=" e(pv_rb) "  h=" e(h_l) "  Nl=" e(N_h_l) "  Nr=" e(N_h_r)

di "=== FIM diag02_ABD ==="
log close
