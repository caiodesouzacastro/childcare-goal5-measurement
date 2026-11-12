* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global ba "$NE_ROOT\dados_restritos\Ciro\01_dados\processados\bases_analise"
cap log close
log using "$NE_ROOT\02_audit\_pspserie.log", text replace
foreach y in 2017 2018 2019 {
    di "==== PSP `y' : desc_serie ===="
    use desc_serie using "$ba/psp_`y'.dta", clear
    tab desc_serie
}
log close
