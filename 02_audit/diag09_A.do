* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag09_A.log", text replace

use "$aud\panel_es.dta", clear
gen rel = rais_year - ano_nasc

di "########## A2 — coorte 2011: emp por ANO CALENDARIO vs TEMPO RELATIVO ##########"
di "--- emp por ano calendario (matched, coorte nasc 2011) ---"
table rais_year if ano_nasc==2011, stat(mean emp) stat(count emp)
di "  (2008/2009 = 1.000 por construcao do arquivo; 2010 e a partir = ~0.7)"
di "--- os mesmos numeros por TEMPO RELATIVO (rel=ano-2011) ---"
table rel if ano_nasc==2011 & inrange(rel,-5,6), stat(mean emp)

di ""
di "########## A3 — PLACEBO: responsavel FEMININO vs MASCULINO, emp por tempo rel ##########"
di "--- FEMININO (fem==1) ---"
table rel if fem==1 & inrange(rel,-5,6), stat(mean emp) stat(count emp)
di "--- MASCULINO (fem==0) ---"
table rel if fem==0 & inrange(rel,-5,6), stat(mean emp) stat(count emp)

di ""
di "########## A4 — emp por tempo relativo, por coorte (2009-2013), so FEMININO ##########"
forvalues c=2009/2013 {
    di "--- coorte `c' ---"
    table rel if ano_nasc==`c' & fem==1 & inrange(rel,-3,5), stat(mean emp) nototals
}

di ""
di "########## A5 — painel BALANCEADO (responsavel em todos os 8 anos 2007-2014) ##########"
bysort cd_aluno_sme respid: gen nyr = _N
di "--- N (crianca,resp) com 8 anos observados ---"
count if nyr==8 & rais_year==2007
preserve
    keep if nyr==8
    di "--- emp por tempo relativo (balanceado, feminino) ---"
    table rel if fem==1 & inrange(rel,-5,6), stat(mean emp) stat(count emp)
restore

di "=== FIM A ==="
log close
