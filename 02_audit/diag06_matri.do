* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global ba  "$NE_ROOT\dados_restritos\Ciro\01_dados\processados\bases_analise"
cap log close
log using "$aud\diag06_matri.log", text replace

di "########## Construindo trajetoria (fundamental 110-120 + EI) dos paineis ##########"
tempfile acc
clear
gen byte _x=.
save `acc', emptyok
foreach y in 2010 2011 2012 2013 2014 2015 2016 2017 2018 {
    di "  ... `y'"
    use cd_aluno_sme an_letivo cd_serie ano_nasc_aluno mes_nasc_aluno sit_al_reprov ///
        using "$ba\matriculas_`y'.dta", clear
    keep if inlist(cd_serie,110,111,112,115,116,117,118,119,120) | inlist(cd_serie,241,242,267,268,270,274)
    append using `acc'
    save `acc', replace
}
di "N linhas trajetoria = " _N
compress
save "$aud\matri_traj.dta", replace

*==============================================================
di ""
di "########## A3 — entrada no 1o ano fundamental (cd_serie==110) ##########"
use "$aud\matri_traj.dta", clear
keep if cd_serie==110
* primeira aparicao no 1o ano por crianca
bysort cd_aluno_sme (an_letivo): keep if _n==1
di "N criancas distintas com 1o ano observado = " _N
di "--- cruzamento mes_nasc x ano de entrada no 1o ano (freq) ---"
tab mes_nasc_aluno an_letivo
di ""
di "--- por coorte de nascimento: ano modal de entrada no 1o ano ---"
forvalues c=2008/2012 {
    di "  coorte `c':"
    tab an_letivo if ano_nasc_aluno==`c'
}
di "--- SALTO marco/abril: para coorte 2011, ano de entrada por mes_nasc ---"
tab mes_nasc_aluno an_letivo if ano_nasc_aluno==2011

di "=== FIM matri ==="
log close
