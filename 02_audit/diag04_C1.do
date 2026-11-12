* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag04_C1.log", text replace

di "########## C1 — n_aberturas por raio (janela sol..mat) ##########"
use "$aud\universo_B4.dta", clear
di "N universo = " _N
* join com pares CEP-CEI (so criancas cujo CEP tem CEI proximo geram linhas)
rename cep_aluno cep
joinby cep using "$aud\cep_cei_pairs.dta", unmatched(master)
di "N linhas apos joinby = " _N
gen byte matched = !missing(dist_km)
gen byte inwin  = (ceiopen>=dt_sol & ceiopen<=dt_mat) if matched
gen byte post12 = (ceiopen>dt_mat & ceiopen<=dt_mat+365) if matched
gen byte w2  = inwin & dist_km<=2
gen byte w1  = inwin & dist_km<=1
gen byte w05 = inwin & dist_km<=0.5
gen byte p1  = post12 & dist_km<=1
collapse (sum) n_ab_2km=w2 n_ab_1km=w1 n_ab_500=w05 n_post_1km=p1, by(cd_aluno_sme)
save "$aud\child_counts_raw.dta", replace

* merge de volta ao universo (crianca sem par -> 0)
use "$aud\universo_B4.dta", clear
merge 1:1 cd_aluno_sme using "$aud\child_counts_raw.dta", keep(master match) nogen
foreach v in n_ab_2km n_ab_1km n_ab_500 n_post_1km {
    replace `v' = 0 if missing(`v')
}
compress
save "$aud\child_counts.dta", replace

di ""
di "===== distribuicao de n_aberturas_500m ====="
gen c500 = n_ab_500
replace c500=3 if n_ab_500>=3
tab c500
di "===== distribuicao de n_aberturas_1km ====="
gen c1 = n_ab_1km
replace c1=3 if n_ab_1km>=3
tab c1
di "===== distribuicao de n_aberturas_2km ====="
gen c2 = n_ab_2km
replace c2=3 if n_ab_2km>=3
tab c2
di ""
di "--- medias ---"
sum n_ab_500 n_ab_1km n_ab_2km n_post_1km
di "--- % com >=1 abertura ---"
foreach v in n_ab_500 n_ab_1km n_ab_2km {
    qui count if `v'>=1
    di "  `v'>=1 : " r(N) "  (" %5.2f 100*r(N)/_N "%)"
}

di "=== FIM C1 ==="
log close
