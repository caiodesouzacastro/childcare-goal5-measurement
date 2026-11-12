* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global ba  "$NE_ROOT\dados_restritos\Ciro\01_dados\processados\bases_analise"
cap log close
log using "$aud\diag09_DE.log", text replace

use "$aud\panel_es.dta", clear
keep if fem==1
bysort respid: egen firstbirth = min(ano_nasc)
keep if inrange(firstbirth,2009,2013)
* primeiro filho (menor ano_nasc) e nº de filhos
gsort respid ano_nasc cd_aluno_sme
by respid: gen firstchild = cd_aluno_sme[1]
egen tagrc = tag(respid cd_aluno_sme)
bysort respid: egen nkids = total(tagrc)
* colapsar mae-ano
gen rel = rais_year - firstbirth
collapse (max) emp (firstnm) firstchild nkids firstbirth, by(respid rel)
* caracteristicas do 1o filho
rename firstchild cd_aluno_sme
merge m:1 cd_aluno_sme using "$aud\child_expo.dta", keep(master match) keepusing(expo12_1km estoque_1km dt_mat_first ano_nasc mes_nasc ever_mat cep_aluno) nogen
gen idade_ei = (year(dt_mat_first)-ano_nasc)*12 + (month(dt_mat_first)-mes_nasc) if ever_mat==1
gen byte ei12 = (ever_mat==1 & idade_ei<12)
rename cep_aluno cep
merge m:1 cep using "$ba\cep_renda_pop_2010.dta", keepusing(renda) keep(master match) nogen

di "########## D1 — emp por rel x expo12_1km (0 vs >=1) ##########"
gen byte expo1 = expo12_1km>=1 if !missing(expo12_1km)
di "--- expo12==0 ---"
table rel if inrange(rel,-3,4) & expo1==0, stat(mean emp) nototals
di "--- expo12>=1 ---"
table rel if inrange(rel,-3,4) & expo1==1, stat(mean emp) nototals
di ""
di "--- por quartil de estoque_1km (rel 0,+1) ---"
xtile eq = estoque_1km, nq(4)
table rel eq if inlist(rel,0,1), stat(mean emp) nototals

di ""
di "########## D2 — emp por rel x quartil de renda do CEP ##########"
xtile rq = renda if !missing(renda), nq(4)
table rel rq if inrange(rel,-1,2), stat(mean emp) nototals

di ""
di "########## D3 — emp por rel x EI antes 12m (endogeno) ##########"
di "--- 1o filho matriculado EI <12m ---"
table rel if inrange(rel,-3,4) & ei12==1, stat(mean emp) nototals
di "--- nao <12m ---"
table rel if inrange(rel,-3,4) & ei12==0, stat(mean emp) nototals

di ""
di "########## D4 — emp por rel x nº de filhos (1 vs 2+) ##########"
gen byte multi = nkids>=2
di "--- 1 filho ---"
table rel if inrange(rel,-3,4) & multi==0, stat(mean emp) nototals
di "--- 2+ filhos ---"
table rel if inrange(rel,-3,4) & multi==1, stat(mean emp) nototals

*==============================================================
di ""
di "########## PARTE E — ameacas ##########"
use "$aud\panel_es.dta", clear
keep if fem==1
bysort respid: egen firstbirth = min(ano_nasc)
bysort respid: egen ultimo = max(rais_year)
bysort respid: egen primeiro = min(rais_year)
preserve
    by respid: keep if _n==1
    di "--- E1: ultimo ano observado por mae (censura a direita) ---"
    tab ultimo
    di "  maes cujo ultimo ano < 2014 (somem e nao voltam ate 2014): "
    count if ultimo<2014
    di "    de " _N " maes"
    di "--- E2: (ultimo ano) - (ano do 1o filho) ---"
    gen dif = ultimo - firstbirth
    tab dif if inrange(dif,-5,7)
restore

di "=== FIM DE ==="
log close
