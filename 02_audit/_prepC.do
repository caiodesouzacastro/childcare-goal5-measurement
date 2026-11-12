* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud  "$NE_ROOT\02_audit"
global dsme "$NE_ROOT\dados_restritos\Dados - SME\Atual (25.06)"
cap log close
log using "$aud\_prepC.log", text replace

di "===== cepcentroide.dta ====="
use "$dsme\cepcentroide.dta", clear
di "N=" _N
describe
list in 1/5

di ""
di "===== geonear instalado? ====="
cap which geonear
di "  rc which geonear = " _rc
cap which vincenty
di "  rc which vincenty = " _rc

di ""
di "===== distinct CEP no universo_B4 ====="
use "$aud\universo_B4.dta", clear
di "N criancas=" _N
egen tagcep = tag(cep_aluno)
count if tagcep==1
di "  CEP distintos no universo"

di ""
di "===== casamento cep_aluno x cepcentroide ====="
* verificar var chave em cepcentroide
log close
