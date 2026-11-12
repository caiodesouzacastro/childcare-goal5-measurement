* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global ba  "$NE_ROOT\dados_restritos\Ciro\01_dados\processados\bases_analise"
global fila "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
cap log close
log using "$aud\diag06_A6.log", text replace

di "########## A6 — balanco MARCO vs ABRIL (nascidos) ##########"
* sexo/raca do Fila
use cd_aluno_sme cd_sexo_aluno tp_raca_cor using "$fila", clear
gen byte fem = cd_sexo_aluno=="F"
gen byte branco = tp_raca_cor==1
collapse (firstnm) fem branco, by(cd_aluno_sme)
tempfile sr
save `sr'

* distancia ao CEI mais proximo por cep
use cep dist_km using "$aud\cep_cei_pairs_novo.dta", clear
bysort cep (dist_km): keep if _n==1
rename dist_km dist_nearest_cei
tempfile dn
save `dn'

use "$aud\B_novo.dta", clear
merge 1:1 cd_aluno_sme using `sr', keep(master match) nogen
rename cep_aluno cep
merge m:1 cep using "$ba\cep_renda_pop_2010.dta", keepusing(renda) keep(master match) nogen
merge m:1 cep using `dn', keep(master match) nogen
keep if inlist(mes_nasc,3,4)
gen byte abril = mes_nasc==4
di "--- N marco / abril ---"
tab mes_nasc
foreach v in fem branco renda dist_nearest_cei {
    di "==== `v' : marco vs abril ===="
    ttest `v', by(abril)
}
di "=== FIM A6 ==="
log close
