* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global ba "$NE_ROOT\dados_restritos\Ciro\01_dados\processados\bases_analise"
cap log close
log using "$NE_ROOT\02_audit\diag06_serie.log", text replace
use cd_serie desc_serie cd_etapa_ensino desc_etapa_ensino using "$ba\matriculas_2018.dta", clear
di "N linhas = " _N
di "--- desc_serie (todas) ---"
tab desc_serie
di "--- desc_etapa_ensino ---"
tab desc_etapa_ensino
di "--- cd_serie x desc_serie (compacto) ---"
tab cd_serie
log close
