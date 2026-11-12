* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
cap log close
log using "$NE_ROOT\02_audit\_peek_escolas.log", text replace
use "$NE_ROOT\dados_restritos\Dados - SME\Atual (25.06)\escolas\escolassite.dta", clear
di "N=" _N
describe, fullnames
di "==== amostra de valores (str das datas / tipo / situacao / coord) ===="
list escola tipoesc situacao dt_criacao dt_ini_conv dt_ini_func dt_autoriza latitude longitude in 1/15, noobs
di "==== tab tipoesc ===="
tab tipoesc, miss
di "==== tab situacao ===="
tab situacao, miss
di "==== tab rede ===="
tab rede, miss
log close
