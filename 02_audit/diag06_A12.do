* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global ba  "$NE_ROOT\dados_restritos\Ciro\01_dados\processados\bases_analise"
cap log close
log using "$aud\diag06_A12.log", text replace

use "$aud\B_novo.dta", clear
di "N B_novo = " _N

*==============================================================
di ""
di "########## A1 — distribuicao mes_nasc + qui-quadrado vs uniforme ##########"
tab mes_nasc, miss
* chi2 GOF vs uniforme
qui count if inrange(mes_nasc,1,12)
local Ntot = r(N)
local exp = `Ntot'/12
local chi2 = 0
forvalues m=1/12 {
    qui count if mes_nasc==`m'
    local o = r(N)
    local chi2 = `chi2' + (`o'-`exp')^2/`exp'
}
di "N (mes 1-12) = `Ntot' ; esperado/mes = `exp'"
di "Qui-quadrado(11 df) vs uniforme = " `chi2'
di "  p-valor = " chi2tail(11,`chi2')

*==============================================================
di ""
di "########## A2 — mes_nasc por quartil de renda do CEP ##########"
rename cep_aluno cep
merge m:1 cep using "$ba\cep_renda_pop_2010.dta", keepusing(renda) keep(master match) nogen
qui sum renda, detail
xtile rq = renda if !missing(renda), nq(4)
di "--- % nascidos em MARCO (3) e ABRIL (4) por quartil de renda ---"
forvalues q=1/4 {
    qui count if rq==`q'
    local nq=r(N)
    qui count if rq==`q' & mes_nasc==3
    local m3=r(N)
    qui count if rq==`q' & mes_nasc==4
    local m4=r(N)
    di "  Q`q' (N=`nq'): marco=" %5.2f 100*`m3'/`nq' "%  abril=" %5.2f 100*`m4'/`nq' "%  (razao mar/abr=" %5.3f `m3'/`m4' ")"
}
di "--- tabela completa mes_nasc x quartil (%) ---"
tab mes_nasc rq, col nofreq

di "=== FIM A12 ==="
log close
