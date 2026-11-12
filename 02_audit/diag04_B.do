* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud  "$NE_ROOT\02_audit"
global fila "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
cap log close
log using "$aud\diag04_B.log", text replace

di "########## Fila -> nivel-crianca (1a matricula). Sem preserve. ##########"
use cd_aluno_sme dt_solicitacao dt_matricula an_letivo_matricula ///
    cd_serie_ensino_matricula ano_nasc mes_nasc cep_aluno ///
    using "$fila", clear
di "N linhas Fila = " _N

gen double dt_sol = date(dt_solicitacao, "DMY hms")
gen double dt_mat = date(dt_matricula,   "DMY hms")
format dt_sol dt_mat %td
drop dt_solicitacao dt_matricula

gen serie_aluno = .
replace serie_aluno = 1 if inlist(cd_serie_ensino_matricula,1,2,3)
replace serie_aluno = 2 if inlist(cd_serie_ensino_matricula,4,5,6)
replace serie_aluno = 3 if inlist(cd_serie_ensino_matricula,11,27)
replace serie_aluno = 4 if inlist(cd_serie_ensino_matricula,28,29)
replace serie_aluno = 5 if inlist(cd_serie_ensino_matricula,23,24)
replace serie_aluno = 6 if inlist(cd_serie_ensino_matricula,25,26)
replace serie_aluno = 7 if inlist(cd_serie_ensino_matricula,8,9,10)
replace serie_aluno = 8 if inlist(cd_serie_ensino_matricula,12,14)
replace serie_aluno = 9 if inlist(cd_serie_ensino_matricula,15,16)
replace serie_aluno = 10 if inlist(cd_serie_ensino_matricula,17,18)

* manter apenas linhas com matricula, depois 1a matricula por crianca
keep if !missing(dt_mat)
di "N linhas com matricula = " _N
bysort cd_aluno_sme (dt_mat): keep if _n==1
di "N criancas distintas com matricula = " _N

gen idade_entrada = (year(dt_mat)-ano_nasc)*12 + (month(dt_mat)-mes_nasc) if !missing(ano_nasc) & !missing(mes_nasc)
gen espera_dias  = dt_mat - dt_sol if !missing(dt_sol)
gen ano_solic    = year(dt_sol)
compress
save "$aud\child_firstmat.dta", replace

*==============================================================
di ""
di "########## B1 — idade_entrada (nivel crianca, 1a matricula) ##########"
di "N nao-missing idade_entrada:"
count if !missing(idade_entrada)
_pctile idade_entrada, p(5 10 25 50 75 90 95)
di "  p5="  r(r1) "  p10=" r(r2) "  p25=" r(r3) "  p50=" r(r4) "  p75=" r(r5) "  p90=" r(r6) "  p95=" r(r7)
sum idade_entrada, detail

*==============================================================
di ""
di "########## B2 — por ano letivo e por serie ##########"
di "--- por an_letivo_matricula (2010-2018) ---"
table an_letivo_matricula if inrange(an_letivo_matricula,2010,2018), ///
    stat(count idade_entrada) stat(p10 idade_entrada) stat(p50 idade_entrada) stat(p90 idade_entrada) stat(mean idade_entrada) stat(sd idade_entrada)
di "--- por serie_aluno ---"
table serie_aluno, ///
    stat(count idade_entrada) stat(p10 idade_entrada) stat(p50 idade_entrada) stat(p90 idade_entrada) stat(mean idade_entrada)

*==============================================================
di ""
di "########## B3 — espera_dias ##########"
di "N nao-missing:"
count if !missing(espera_dias)
sum espera_dias, detail
di "--- por ano de matricula ---"
table an_letivo_matricula if inrange(an_letivo_matricula,2010,2018), ///
    stat(count espera_dias) stat(p10 espera_dias) stat(p50 espera_dias) stat(p90 espera_dias) stat(mean espera_dias)

*==============================================================
di ""
di "########## B4 — universo potencial ##########"
gen byte cep_ok = !missing(cep_aluno) & cep_aluno>0
gen byte nasc_ok = !missing(ano_nasc) & !missing(mes_nasc)
gen byte sol_ok = !missing(dt_sol)
gen byte univ = cep_ok & nasc_ok & sol_ok   /* dt_mat ja garantido */
di "--- N universo B4 (total) ---"
count if univ==1
di "--- por ano de solicitacao ---"
tab ano_solic if univ==1 & inrange(ano_solic,2008,2018)
keep if univ==1
keep cd_aluno_sme dt_sol dt_mat idade_entrada espera_dias cep_aluno ano_solic an_letivo_matricula serie_aluno ano_nasc mes_nasc
save "$aud\universo_B4.dta", replace
di "N universo salvo = " _N

di "=== FIM diag04_B ==="
log close
