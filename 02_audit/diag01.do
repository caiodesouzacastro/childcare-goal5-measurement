* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
* ============================================================
* diag01.do  — AUDITORIA (somente diagnóstico, não altera código do autor)
* Stata 17 (StataMP-64)
* Saída: _audit\diag01.log
* ============================================================
clear all
set more off
set linesize 200

global bruto "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera"
global proc  "$NE_ROOT\dados_restritos\Ciro\01_dados\processados"
global amost "$proc\amostra_rdd\Fila1018_amostraRDD.dta"
global ba    "$proc\bases_analise"
global aud   "$NE_ROOT\02_audit"

cap log close
log using "$aud\diag01.log", text replace

di "==================================================================="
di " RECONSTRUINDO b1_2011 (replicando 04_referee_robustness.do verbatim)"
di "==================================================================="

use "$bruto\trat2011ber.dta", clear
keep if ano_nasc==2010
di "N ano_nasc==2010: `=_N'"
merge m:1 cd_aluno_sme using "$amost", ///
    keepusing(cd_aluno_sme prof_mat prof_lp cd_sexo_aluno tp_raca_cor ///
              ano_nasc mes_nasc an_letivo_matricula) keep(3) nogen
di "N após merge amostra RDD: `=_N'"

gen double dt_sol = date(dt_solicitacao, "DMY hms")
format dt_sol %td

* --- rvar (loop tratado depois fallback) : VERBATIM do autor ---
gen rvar = .
forvalues i = 1/31 {
    cap replace rvar = dt_corte_escola`i' - dt_sol if rvar==. & trat_ber_2011`i'==1
}
forvalues i = 1/31 {
    cap replace rvar = dt_corte_escola`i' - dt_sol if rvar==. & !missing(dt_corte_escola`i')
}
* --- escola_rdd ---
gen escola_rdd = .
forvalues i = 1/31 {
    cap replace escola_rdd = cd_esc_encaminhamento`i' if escola_rdd==. & trat_ber_2011`i'==1
}
forvalues i = 1/31 {
    cap replace escola_rdd = cd_esc_encaminhamento`i' if escola_rdd==. & !missing(dt_corte_escola`i')
}
* --- índice da escola escolhida (para recuperar distância) ---
gen _idx = .
forvalues i = 1/31 {
    cap replace _idx = `i' if _idx==. & trat_ber_2011`i'==1
}
forvalues i = 1/31 {
    cap replace _idx = `i' if _idx==. & !missing(dt_corte_escola`i')
}
* --- fallback e tratamento : VERBATIM ---
gen byte fallback = (rvar!=. & trat2011ber==0)
gen t = trat2011ber
gen exp = "b1_2011"

* --- Padronizar prof_mat / prof_lp dentro de b1_2011 (como o autor) ---
foreach v in prof_mat prof_lp {
    qui sum `v'
    replace `v' = (`v' - r(mean))/r(sd)
}

* --- n_escolas = nº de dt_corte_escola não-missing ---
gen n_escolas = 0
forvalues i = 1/31 {
    cap replace n_escolas = n_escolas + !missing(dt_corte_escola`i')
}

* --- distância à escola atribuída (esc`_idx'D) e à mais próxima (esc1D) ---
gen dist_assigned = .
forvalues i = 1/31 {
    cap replace dist_assigned = esc`i'D if _idx==`i'
}
cap gen dist_nearest = esc1D

* --- renda do CEP ---
rename cep_aluno cep
merge m:1 cep using "$ba\cep_renda_pop_2010.dta", keepusing(renda) keep(master match) nogen

compress
save "$aud\b1_2011_audit.dta", replace
di "Base audit salva: `=_N' obs"

* ============================================================
di ""
di "########## VERIFICAÇÃO FORENSE (B3/B4/B5) ##########"
* trat2011ber == rowmax(trat_ber_2011*) ?
egen _rowmax = rowmax(trat_ber_2011*)
di "--- tab trat2011ber vs rowmax(trat_ber_2011*) ---"
tab trat2011ber _rowmax, miss
* treated (t) vs sinal de rvar
gen byte rvar_pos = (rvar>=0) if !missing(rvar)
di "--- tab t vs 1[rvar>=0] ---"
tab t rvar_pos, miss
drop _rowmax

* ============================================================
di ""
di "########## C1 — rvar por status de tratamento (b1_2011) ##########"
tabstat rvar, by(t) stat(n min max mean p50) col(stat)
di "--- tratados com rvar<0 ---"
count if t==1 & rvar<0 & !missing(rvar)
di "--- controles com rvar>=0 ---"
count if t==0 & rvar>=0 & !missing(rvar)
di "--- fallback (controle atribuído por fallback) ---"
tab fallback if !missing(rvar)

* ============================================================
di ""
di "########## C2 — contagem por valor inteiro de rvar em [-10,10] ##########"
gen rvar_int = round(rvar)
tab rvar_int if inrange(rvar_int,-10,10), miss

* ============================================================
di ""
di "########## C3 — n_escolas ##########"
di "--- (a) distribuição de n_escolas ---"
tab n_escolas
di "--- (b) média n_escolas por t + ttest ---"
tabstat n_escolas, by(t) stat(n mean sd) col(stat)
ttest n_escolas if !missing(t), by(t)
di "--- (c) correlação n_escolas x renda ---"
pwcorr n_escolas renda, sig obs
di "--- (d) média n_escolas por quartil de renda ---"
xtile renda_q = renda if !missing(renda), nq(4)
tabstat n_escolas, by(renda_q) stat(n mean) col(stat)

* ============================================================
di ""
di "########## C4 — especificação principal (math 2018) ##########"
rdrobust prof_mat rvar, c(0) kernel(triangular) bwselect(mserd) vce(cluster escola_rdd)
scalar hl = e(h_l)
scalar hr = e(h_r)
di "h_l=" hl "  h_r=" hr
di "e(N_h_l)=" e(N_h_l) "  e(N_h_r)=" e(N_h_r)
di "tau_cl=" e(tau_cl) "  se_rb=" e(se_tau_rb) "  p_rb=" e(pv_rb)
* contagens dentro da bandwidth efetiva
di "--- ESQUERDA (controles, -h<=rvar<0) ---"
count if rvar>=-hl & rvar<0 & !missing(prof_mat)
count if rvar>=-hl & rvar<0 & !missing(prof_mat) & t==0
egen _tagL = tag(escola_rdd) if rvar>=-hl & rvar<0 & !missing(prof_mat)
count if _tagL==1
di "--- DIREITA (tratados, 0<=rvar<=h) ---"
count if rvar<=hr & rvar>=0 & !missing(prof_mat)
count if rvar<=hr & rvar>=0 & !missing(prof_mat) & t==1
egen _tagR = tag(escola_rdd) if rvar<=hr & rvar>=0 & !missing(prof_mat)
count if _tagR==1
drop _tagL _tagR

* ============================================================
di ""
di "########## C5 — balanço no corte ##########"
foreach v in n_escolas renda dist_assigned dist_nearest {
    di "--- balanço: `v' ---"
    cap rdrobust `v' rvar, c(0) kernel(triangular) bwselect(mserd)
    if !_rc {
        di "  `v': coef(tau_cl)=" %9.4f e(tau_cl) "  se_rb=" %9.4f e(se_tau_rb) "  p_rb=" %6.4f e(pv_rb) "  h=" %6.1f e(h_l) "  N=" e(N_h_l)+e(N_h_r)
    }
    else di "  ERRO rc=`_rc' para `v'"
}

* ============================================================
di ""
di "########## C6 — donut hole (math 2018) ##########"
foreach k in 0 3 7 14 {
    di "--- donut |rvar|<= `k' excluído ---"
    if `k'==0 {
        cap rdrobust prof_mat rvar, c(0) kernel(triangular) bwselect(mserd) vce(cluster escola_rdd)
    }
    else {
        cap rdrobust prof_mat rvar if abs(rvar)>`k', c(0) kernel(triangular) bwselect(mserd) vce(cluster escola_rdd)
    }
    if !_rc {
        scalar hh = e(h_l)
        qui count if abs(rvar)<=hh & rvar>=0 & !missing(prof_mat) & (abs(rvar)>`k')
        local ntr = r(N)
        qui count if abs(rvar)<=hh & rvar<0 & !missing(prof_mat) & (abs(rvar)>`k')
        local nco = r(N)
        di "  k=`k': tau_cl=" %8.4f e(tau_cl) "  se_rb=" %8.4f e(se_tau_rb) ///
           "  p_rb=" %6.4f e(pv_rb) "  h=" %6.1f e(h_l) ///
           "  Nef=" e(N_h_l)+e(N_h_r) "  trat=`ntr'  ctrl=`nco'"
    }
    else di "  ERRO rc=`_rc' para k=`k'"
}

* ============================================================
di ""
di "########## CONFERÊNCIA vs base do autor (trat_PSP_rdd_final.dta, b1_2011) ##########"
use "$proc\trat_PSP_rdd_final.dta", clear
keep if exp=="b1_2011"
di "N autor b1_2011: `=_N'"
tabstat rvar, by(t) stat(n min max mean p50) col(stat)
count if t==1 & rvar<0 & !missing(rvar)
count if t==0 & rvar>=0 & !missing(rvar)
rdrobust prof_mat rvar, c(0) kernel(triangular) bwselect(mserd) vce(cluster escola_rdd)
di "AUTOR C4: tau_cl=" e(tau_cl) "  se_rb=" e(se_tau_rb) "  p_rb=" e(pv_rb) "  h=" e(h_l)

log close
di "FIM diag01"
