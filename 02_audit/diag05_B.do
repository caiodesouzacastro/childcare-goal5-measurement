* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag05_B.log", text replace

use "$aud\B_novo.dta", clear
di "N B_novo = " _N
rename cep_aluno cep
joinby cep using "$aud\cep_cei_pairs_novo.dta", unmatched(master)
di "N linhas apos joinby = " _N
gen byte m = !missing(dist_km)
* janelas relativas a dt_sol (NUNCA usa dt_matricula)
gen byte in_expo = (dt_abertura>=dt_sol & dt_abertura<=dt_sol+365) if m
gen byte in_pre  = (dt_abertura>=dt_sol-365 & dt_abertura<=dt_sol) if m
gen byte in_post = (dt_abertura>=dt_sol+366 & dt_abertura<=dt_sol+730) if m
gen byte in_stk  = (dt_abertura<=dt_sol) if m
* radios
gen byte expo05 = in_expo & dist_km<=0.5
gen byte expo1  = in_expo & dist_km<=1
gen byte expo2  = in_expo & dist_km<=2
gen byte pre1   = in_pre  & dist_km<=1
gen byte post1  = in_post & dist_km<=1
gen byte stk1   = in_stk  & dist_km<=1
collapse (sum) expo12_500=expo05 expo12_1km=expo1 expo12_2km=expo2 ///
               pre12_1km=pre1 post_1km=post1 estoque_1km=stk1, by(cd_aluno_sme)
save "$aud\child_expo_raw.dta", replace

use "$aud\B_novo.dta", clear
merge 1:1 cd_aluno_sme using "$aud\child_expo_raw.dta", keep(master match) nogen
foreach v in expo12_500 expo12_1km expo12_2km pre12_1km post_1km estoque_1km {
    replace `v'=0 if missing(`v')
}
compress
save "$aud\child_expo.dta", replace

program define distrib
    args v
    di "--- `v' : distribuicao 0/1/2/3+ e media ---"
    gen __c = `v'
    replace __c = 3 if `v'>=3
    tab __c
    qui sum `v'
    di "  media `v' = " r(mean) "   % >=1 = " %5.2f 100*(1 - (`=r(N)'>0)*0)  /* placeholder */
    qui count if `v'>=1
    di "  N >=1 = " r(N) "  (" %5.2f 100*r(N)/_N "%)"
    drop __c
end

di ""
di "########## B1 — expo12 (janela [sol, sol+365]) ##########"
distrib expo12_500
distrib expo12_1km
distrib expo12_2km
di ""
di "########## B2 — pre12 (janela [sol-365, sol]) placebo ##########"
distrib pre12_1km
di ""
di "########## B3 — post (janela [sol+366, sol+730]) ##########"
distrib post_1km
di ""
di "########## B4 — estoque (CEIs <=1km abertos na data de solicitacao) ##########"
di "--- distribuicao estoque_1km ---"
sum estoque_1km, detail
gen ec=estoque_1km
replace ec=6 if estoque_1km>=6
tab ec

di "=== FIM diag05_B ==="
log close
