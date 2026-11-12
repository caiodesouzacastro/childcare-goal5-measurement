* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag05_E2.log", text replace

* dedup ids PSP 2o ano
use cd_aluno_sme using "$aud\psp2018_2ano.dta", clear
duplicates drop
gen byte p18=1
save "$aud\p18_2ano_ids.dta", replace
di "PSP2018-2ano cd_aluno distintos = " _N
use cd_aluno_sme using "$aud\psp2019_2ano.dta", clear
duplicates drop
gen byte p19=1
save "$aud\p19_2ano_ids.dta", replace
di "PSP2019-2ano cd_aluno distintos = " _N

*==============================================================
di ""
di "########## E2 — coorte x B_novo x casamento PSP-2ano ##########"
use "$aud\child_expo.dta", clear
merge 1:1 cd_aluno_sme using "$aud\p18_2ano_ids.dta", keep(master match) nogen
merge 1:1 cd_aluno_sme using "$aud\p19_2ano_ids.dta", keep(master match) nogen
replace p18=0 if missing(p18)
replace p19=0 if missing(p19)
foreach c in 2010 2011 2012 {
    di "===== coorte `c' ====="
    qui count if ano_nasc==`c'
    di "  B_novo nascidos `c': " r(N)
    qui count if ano_nasc==`c' & p18==1
    di "    casam PSP2018-2ano: " r(N)
    qui count if ano_nasc==`c' & p19==1
    di "    casam PSP2019-2ano: " r(N)
}

*==============================================================
di ""
di "########## E3 — maior coorte: expo12 e taxa de matricula ##########"
foreach c in 2010 2011 {
    di "===== coorte `c' (N total B_novo) ====="
    qui count if ano_nasc==`c'
    di "  N = " r(N)
    gen ec = expo12_1km if ano_nasc==`c'
    replace ec=3 if expo12_1km>=3 & ano_nasc==`c'
    di "  --- distribuicao expo12_1km ---"
    tab ec if ano_nasc==`c'
    qui sum expo12_1km if ano_nasc==`c'
    di "  media expo12_1km = " r(mean)
    qui sum ever_mat if ano_nasc==`c'
    di "  taxa de matricula (ever_mat) = " r(mean)
    drop ec
}

di "=== FIM E2 ==="
log close
