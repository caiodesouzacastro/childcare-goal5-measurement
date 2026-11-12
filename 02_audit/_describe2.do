* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
global proc  "$NE_ROOT\dados_restritos\Ciro\01_dados\processados"
global ba    "$proc\bases_analise"
log using "$NE_ROOT\02_audit\_describe2.log", text replace

di "==================== trat_PSP_rdd_final.dta ===================="
use "$proc\trat_PSP_rdd_final.dta", clear
di "N = " _N
describe
di "---- tab exp ----"
tab exp
di "---- tab t ----"
tab t, miss
di "---- sum rvar prof_mat prof_lp ----"
sum rvar prof_mat prof_lp

di "==================== cep_renda_pop_2010.dta ===================="
use "$ba\cep_renda_pop_2010.dta", clear
di "N = " _N
describe
sum
list in 1/5

log close
