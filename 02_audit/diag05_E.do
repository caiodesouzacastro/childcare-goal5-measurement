* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global ba  "$NE_ROOT\dados_restritos\Ciro\01_dados\processados\bases_analise"
global fila "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
cap log close
log using "$aud\diag05_E.log", text replace

*==============================================================
di "########## Mapa crianca -> ano_nasc (do Fila) ##########"
use cd_aluno_sme ano_nasc using "$fila", clear
collapse (firstnm) ano_nasc, by(cd_aluno_sme)
save "$aud\cid_ano.dta", replace
di "N criancas no mapa = " _N

*==============================================================
di ""
di "########## E1 — ano_nascimento dos que fizeram PSP 2o ano ##########"
* 2017 nao tem 2o ano (menor serie = 3.ANO)
di "PSP 2017: 2o ano NAO EXISTE (menor serie = C.I 3.ANO F9)."

* 2018: C.I 2.ANO F9
use cd_aluno_sme desc_serie using "$ba/psp_2018.dta", clear
keep if strpos(desc_serie,"2.ANO")>0
merge m:1 cd_aluno_sme using "$aud\cid_ano.dta", keep(master match) nogen
gen ano_psp=2018
save "$aud\psp2018_2ano.dta", replace
di "--- PSP 2018 2o ano: N=" _N " ; distribuicao ano_nasc ---"
tab ano_nasc, miss

* 2019: 2 Ano
use cd_aluno_sme desc_serie using "$ba/psp_2019.dta", clear
keep if strpos(desc_serie,"2 Ano")>0
merge m:1 cd_aluno_sme using "$aud\cid_ano.dta", keep(master match) nogen
gen ano_psp=2019
save "$aud\psp2019_2ano.dta", replace
di "--- PSP 2019 2o ano: N=" _N " ; distribuicao ano_nasc ---"
tab ano_nasc, miss

*==============================================================
di ""
di "########## E2 — coorte modal x universo B_novo x casamento ##########"
* coorte modal 2018 = 2011 ; 2019 = 2012 (confirmar acima). Reporto para 2010,2011,2012.
use "$aud\child_expo.dta", clear
di "--- N B_novo por ano_nasc (2009-2013) ---"
tab ano_nasc if inrange(ano_nasc,2009,2013)

foreach c in 2010 2011 2012 {
    di "===== coorte `c' ====="
    qui count if ano_nasc==`c'
    di "  B_novo nascidos em `c': " r(N)
    * casam com PSP 2018 2o ano
    preserve
        keep if ano_nasc==`c'
        merge 1:1 cd_aluno_sme using "$aud\psp2018_2ano.dta", keep(match) nogen
        di "    casam c/ PSP2018-2ano: " _N
    restore
    preserve
        keep if ano_nasc==`c'
        merge 1:1 cd_aluno_sme using "$aud\psp2019_2ano.dta", keep(match) nogen
        di "    casam c/ PSP2019-2ano: " _N
    restore
}

*==============================================================
di ""
di "########## E3 — maior coorte: expo12 e taxa de matricula ##########"
* usar a coorte com maior N em B_novo dentre 2010-2012 (reporto 2011)
use "$aud\child_expo.dta", clear
foreach c in 2011 2012 {
    di "===== coorte `c' ====="
    di "  N = "
    count if ano_nasc==`c'
    di "  --- expo12_1km distribuicao ---"
    gen ec = expo12_1km if ano_nasc==`c'
    replace ec=3 if expo12_1km>=3 & ano_nasc==`c'
    tab ec if ano_nasc==`c'
    qui sum expo12_1km if ano_nasc==`c'
    di "  media expo12_1km = " r(mean)
    di "  --- taxa de matricula (ever_mat) ---"
    qui sum ever_mat if ano_nasc==`c'
    di "  taxa ever_mat = " r(mean)
    drop ec
}

di "=== FIM diag05_E ==="
log close
