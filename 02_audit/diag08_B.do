* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag08_B.log", text replace

* painel emprego a nivel crianca x ano de RAIS
use "$aud\panel_rais.dta", clear
collapse (max) emp, by(cd_aluno_sme rais_year)
tempfile cy
save `cy'

* grade B_novo x anos 2007-2014
use cd_aluno_sme ano_nasc mes_nasc using "$aud\B_novo.dta", clear
merge 1:1 cd_aluno_sme using "$aud\child_expo.dta", keep(master match) keepusing(expo12_1km) nogen
expand 8
bysort cd_aluno_sme: gen rais_year = 2006 + _n
merge 1:1 cd_aluno_sme rais_year using `cy', keep(master match) nogen
replace emp = 0 if missing(emp)
gen rel = rais_year - ano_nasc
gen byte abril = mes_nasc==4
gen byte marco = mes_nasc==3
gen byte expo1 = expo12_1km>=1 if !missing(expo12_1km)

di "########## B1 — emp por ano relativo ao nascimento (todo B_novo, sem RAIS=0) ##########"
di "  (so anos de calendario 2007-2014 sao observaveis)"
table rel if inrange(rel,-5,6), stat(mean emp) stat(count emp)

di ""
di "########## B2 — emp por ano relativo: MARCO vs ABRIL ##########"
di "--- MARCO (mes_nasc==3) ---"
table rel if inrange(rel,-5,6) & marco==1, stat(mean emp) stat(count emp)
di "--- ABRIL (mes_nasc==4) ---"
table rel if inrange(rel,-5,6) & abril==1, stat(mean emp) stat(count emp)

di ""
di "########## B3 — emp por ano relativo: expo12_1km 0 vs >=1 ##########"
di "--- expo12_1km==0 ---"
table rel if inrange(rel,-5,6) & expo1==0, stat(mean emp)
di "--- expo12_1km>=1 ---"
table rel if inrange(rel,-5,6) & expo1==1, stat(mean emp)

di ""
di "########## B4 — N com >=2 anos pre-nascimento e >=3 pos (observados no painel) ##########"
* observado = crianca aparece no painel naquele ano (merge do cy) -> usar emp nao-missing original
* recomputar: obs = 1 se (child,year) estava no painel cy
preserve
    use `cy', clear
    merge m:1 cd_aluno_sme using "$aud\B_novo.dta", keep(match) keepusing(ano_nasc) nogen
    gen byte prey = rais_year < ano_nasc
    gen byte posy = rais_year >= ano_nasc
    bysort cd_aluno_sme: egen npre = total(prey)
    bysort cd_aluno_sme: egen npos = total(posy)
    by cd_aluno_sme: keep if _n==1
    di "--- N criancas com >=2 anos pre-nasc E >=3 pos, por coorte ---"
    forvalues c=2008/2014 {
        qui count if ano_nasc==`c' & npre>=2 & npos>=3
        di "  coorte `c': " r(N)
    }
    di "--- total (coortes 2008-2014) ---"
    count if inrange(ano_nasc,2008,2014) & npre>=2 & npos>=3
restore

di "=== FIM B ==="
log close
