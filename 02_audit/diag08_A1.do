* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global rc  "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\rais_cpf"
cap log close
log using "$aud\diag08_A1.log", text replace

di "########## Instalar ftools + reghdfe ##########"
cap which ftools
if _rc {
    di "  instalando ftools..."
    ssc install ftools, replace
}
else di "  ftools JA instalado"
cap which reghdfe
if _rc {
    di "  instalando reghdfe..."
    ssc install reghdfe, replace
}
else di "  reghdfe JA instalado"
cap which reghdfe
di "  reghdfe disponivel? rc=" _rc

*==============================================================
di ""
di "########## A1 — cada cpf_fila_* (pasta Ciro rais_cpf) ##########"
foreach f in cpf_fila_07 cpf_fila_081 cpf_fila_092 cpf_fila_101 cpf_fila_102 cpf_fila_11 cpf_fila_12 cpf_fila_13 cpf_fila_14 {
    cap confirm file "$rc/`f'.dta"
    if _rc {
        di "  `f' : NAO ENCONTRADO"
        continue
    }
    use "$rc/`f'.dta", clear
    di ""
    di "==== `f' : N=`=_N'  k=`=c(k)' ===="
    di "  primeiras 10 variaveis:"
    unab all : *
    tokenize `all'
    di "    `1' `2' `3' `4' `5' `6' `7' `8' `9' `10'"
    di "  --- tab ano ---"
    cap tab ano
    if _rc di "    (sem variavel 'ano')"
}

di "=== FIM A1 ==="
log close
