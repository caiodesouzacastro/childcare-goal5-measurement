* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global dsme "$NE_ROOT\dados_restritos\Dados - SME\Atual (25.06)"
cap log close
log using "$aud\diag06_D2.log", text replace

*==============================================================
di "########## D1 — rank de distancia da escola atribuida ##########"
* rank dos CEIs dentro de cada CEP (1 = mais proximo)
use cep ceicode dist_km using "$aud\cep_cei_pairs_novo.dta", clear
bysort cep (dist_km): gen rank_in_cep = _n
bysort cep: gen n_cei_cep = _N
rename ceicode esc_atrib
tempfile ranks
save `ranks'

use "$aud\d_assign.dta", clear
di "N criancas com encaminhamento = " _N
merge m:1 cep esc_atrib using `ranks', keep(master match) gen(mr)
di "--- escola atribuida esta entre CEIs<=2km com dt_abertura (mr==3) ---"
count if mr==3
di "--- NAO esta (mr==1): atribuida sem dt_abertura ou >2km ---"
count if mr==1
di "--- distribuicao do RANK de distancia da escola atribuida (1=mais proxima) ---"
gen rc = rank_in_cep
replace rc = 6 if rank_in_cep>=6 & !missing(rank_in_cep)
tab rc
di "--- % rank==1 entre as com rank definido ---"
qui count if !missing(rank_in_cep)
local den=r(N)
qui count if rank_in_cep==1
di "  rank==1: " r(N) " / " `den' " = " %6.4f r(N)/`den'

*==============================================================
di ""
di "########## D2 — celulas CEP x mes_sol com >=2 criancas: variacao de escola ##########"
use "$aud\d_assign.dta", clear
egen cellid = group(cep ym_sol)
bysort cellid: gen ncel = _N
preserve
    keep if ncel>=2
    bysort cellid esc_atrib: gen firstesc = _n==1
    bysort cellid: egen nescolas = total(firstesc)
    bysort cellid: keep if _n==1
    di "  N celulas (>=2 criancas) = " _N
    gen byte variou = nescolas>=2
    qui count if variou==1
    di "  celulas com >=2 escolas distintas = " r(N)
    qui sum variou
    di "  % celulas com variacao de escola = " %6.4f r(mean)
    di "  --- distribuicao nescolas por celula ---"
    gen nc=nescolas
    replace nc=5 if nescolas>=5
    tab nc
restore

*==============================================================
di ""
di "########## D4 — SD within-celula da qualidade (>=2 criancas) ##########"
use "$aud\d_assign.dta", clear
merge m:1 codinep using "$dsme\escolas\censo2018.dta", ///
    keepusing(in_bercario qt_salas_existentes) keep(master match) nogen
cap encode tipoesc, gen(modal)
egen cellid = group(cep ym_sol)
bysort cellid: gen ncel=_N
keep if ncel>=2
foreach v in modal in_bercario qt_salas_existentes {
    bysort cellid: egen sd_`v' = sd(`v')
}
bysort cellid: keep if _n==1
di "--- media do SD within-celula (celulas >=2 criancas) ---"
sum sd_modal sd_in_bercario sd_qt_salas_existentes
gen byte var_modal = sd_modal>0 & !missing(sd_modal)
di "--- % celulas com variacao de MODALIDADE da escola atribuida ---"
sum var_modal

di "=== FIM D2 ==="
log close
