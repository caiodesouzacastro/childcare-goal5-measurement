* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag04_C6.log", text replace

di "########## C6 — event study cru (abertura mais proxima no tempo, <=1km) ##########"
use "$aud\cep_cei_pairs.dta", clear
keep if dist_km<=1
rename cep cepk
tempfile p1
save `p1'

use cd_aluno_sme cep_aluno dt_sol idade_entrada using "$aud\universo_B4.dta", clear
rename cep_aluno cepk
joinby cepk using `p1'
di "N linhas (crianca x CEI <=1km) = " _N
gen double relm = (ceiopen - dt_sol)/30.44
gen double absrel = abs(relm)
* abertura mais proxima NO TEMPO por crianca
bysort cd_aluno_sme (absrel): keep if _n==1
di "N criancas com >=1 CEI <=1km = " _N
gen bin = 3*floor(relm/3)
di "--- idade_entrada media por bin de 3 meses (rel. sol -> abertura), -24..+24 ---"
table bin if inrange(relm,-24,24), stat(count idade_entrada) stat(mean idade_entrada)

di "=== FIM C6 ==="
log close
