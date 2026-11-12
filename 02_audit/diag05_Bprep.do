* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global dsme "$NE_ROOT\dados_restritos\Dados - SME\Atual (25.06)"
global fila "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
cap log close
log using "$aud\diag05_Bprep.log", text replace

*==============================================================
di "########## Pares CEP-CEI com dt_abertura (grade 0.02deg 3x3) ##########"
use "$aud\cei_openings_novo.dta", clear
gen clat0 = round(ceilat/0.02)
gen clon0 = round(ceilon/0.02)
expand 9
bysort ceicode: gen j=_n-1
gen clat = clat0 + (mod(j,3)-1)
gen clon = clon0 + (floor(j/3)-1)
keep ceicode ceilat ceilon dt_abertura clat clon
tempfile grid
save `grid'

use "$dsme\cepcentroide.dta", clear
rename latitude ceplat
rename longitude ceplon
gen clat = round(ceplat/0.02)
gen clon = round(ceplon/0.02)
joinby clat clon using `grid'
gen double a = sin((ceilat-ceplat)*_pi/360)^2 + cos(ceplat*_pi/180)*cos(ceilat*_pi/180)*sin((ceilon-ceplon)*_pi/360)^2
gen double dist_km = 2*6371*asin(sqrt(a))
keep if dist_km <= 2
keep cep ceicode dt_abertura dist_km
di "N pares novo (<=2km) = " _N
save "$aud\cep_cei_pairs_novo.dta", replace

*==============================================================
di ""
di "########## B_novo: TODAS criancas com sol+nasc+cep (incl. nao-matriculadas) ##########"
* Pass 1 - primeira matricula por crianca (DESFECHO)
use cd_aluno_sme dt_matricula using "$fila", clear
gen double dt_mat = date(dt_matricula,"DMY hms")
keep if !missing(dt_mat)
collapse (min) dt_mat_first=dt_mat, by(cd_aluno_sme)
gen byte ever_mat = 1
tempfile matf
save `matf'
di "N criancas com alguma matricula = " _N

* Pass 2 - primeira solicitacao por crianca + covariaveis
use cd_aluno_sme dt_solicitacao ano_nasc mes_nasc cep_aluno an_letivo_solicitacao using "$fila", clear
gen double dt_sol = date(dt_solicitacao,"DMY hms")
keep if !missing(dt_sol)
gsort cd_aluno_sme dt_sol
by cd_aluno_sme: keep if _n==1
di "N criancas com alguma solicitacao = " _N
* validade
gen byte nasc_ok = !missing(ano_nasc) & !missing(mes_nasc)
gen byte cep_ok  = !missing(cep_aluno) & cep_aluno>0
keep if nasc_ok & cep_ok
di "N com nasc+cep validos = " _N
gen ano_sol = year(dt_sol)
* juntar matricula (desfecho)
merge 1:1 cd_aluno_sme using `matf', keep(master match) nogen
replace ever_mat = 0 if missing(ever_mat)
compress
save "$aud\B_novo.dta", replace
di "--- N B_novo = " _N
di "--- nunca matricularam ---"
count if ever_mat==0
di "--- por ano de solicitacao ---"
tab ano_sol if inrange(ano_sol,2008,2018)

di "=== FIM Bprep ==="
log close
