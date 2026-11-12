* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag06_AE.log", text replace

*==============================================================
di "########## A4 — regra 31/03 na Educacao Infantil? ##########"
use "$aud\matri_traj.dta", clear
* EI series: 241 BercI, 242 BercII, 267 MiniI, 268 MiniII, 270 InfI, 274 InfII
* primeira aparicao por (crianca, serie)
bysort cd_aluno_sme cd_serie (an_letivo): keep if _n==1
di "--- Bercario I (241): mes_nasc x ano de entrada, coorte 2015 ---"
tab mes_nasc_aluno an_letivo if cd_serie==241 & ano_nasc_aluno==2015
di "--- Infantil I (270): mes_nasc x ano de entrada, coorte 2011 ---"
tab mes_nasc_aluno an_letivo if cd_serie==270 & ano_nasc_aluno==2011

*==============================================================
di ""
di "########## A5 — DOSE: anos de EI antes do 1o ano (marco vs abril) ##########"
use "$aud\matri_traj.dta", clear
gen byte is_ei = inlist(cd_serie,241,242,267,268,270,274)
keep if is_ei
* n de anos letivos distintos em EI por crianca
bysort cd_aluno_sme an_letivo: keep if _n==1
bysort cd_aluno_sme: gen n_ei_anos = _N
by cd_aluno_sme: keep if _n==1
di "--- coorte 2011: anos de EI por mes de nascimento ---"
table mes_nasc_aluno if ano_nasc_aluno==2011, stat(count n_ei_anos) stat(mean n_ei_anos) stat(p50 n_ei_anos)
di "--- coorte 2010 ---"
table mes_nasc_aluno if ano_nasc_aluno==2010, stat(mean n_ei_anos) stat(p50 n_ei_anos)

*==============================================================
di ""
di "########## E1/E2/E3 — desfechos administrativos ##########"
use "$aud\matri_traj.dta", clear
di "--- tab sit_al_reprov ---"
tab sit_al_reprov, miss
* por crianca: tem 1o ano, tem 3o ano, primeira serie 110 ano, ever reprov
gen byte s110 = cd_serie==110
gen byte s112 = cd_serie==112
gen byte rep = (sit_al_reprov==1)
gen ano110 = an_letivo if s110==1
collapse (max) tem1ano=s110 tem3ano=s112 ever_reprov=rep (min) ano_ent_1ano=ano110 ///
         (firstnm) ano_nasc_aluno mes_nasc_aluno, by(cd_aluno_sme)
* on-time: esperado = ano_nasc+6 se mes<=3, senao +7
gen esperado = ano_nasc_aluno + cond(mes_nasc_aluno<=3,6,7)
gen byte ontime = (ano_ent_1ano==esperado) if tem1ano==1
save "$aud\traj_child.dta", replace

di "--- E1: por coorte, N com 1o ano e 3o ano observados ---"
forvalues c=2008/2012 {
    qui count if ano_nasc_aluno==`c'
    local nt=r(N)
    qui count if ano_nasc_aluno==`c' & tem1ano==1
    local n1=r(N)
    qui count if ano_nasc_aluno==`c' & tem3ano==1
    local n3=r(N)
    di "  coorte `c': N traj=`nt'  ; 1o ano=`n1'  ; 3o ano=`n3'"
}
di ""
di "--- E2: taxa on-time no 1o ano e taxa de repeticao (fundamental), por coorte ---"
forvalues c=2008/2012 {
    qui sum ontime if ano_nasc_aluno==`c' & tem1ano==1
    local ot=r(mean)
    local n1=r(N)
    qui sum ever_reprov if ano_nasc_aluno==`c'
    local rr=r(mean)
    di "  coorte `c': on-time(1oano)=" %5.3f `ot' " (N=`n1')  ; taxa reprov=" %5.3f `rr'
}
di ""
di "--- E3: N disponivel por desfecho administrativo (coortes 2008-2012) ---"
count if inrange(ano_nasc_aluno,2008,2012) & tem1ano==1
di "  com 1o ano fundamental: " r(N)
count if inrange(ano_nasc_aluno,2008,2012) & tem3ano==1
di "  com 3o ano fundamental: " r(N)
count if inrange(ano_nasc_aluno,2008,2012) & !missing(ontime)
di "  com on-time calculavel: " r(N)
di "  (comparar com ~27 mil / ~115 mil da PSP)"

di "=== FIM AE ==="
log close
