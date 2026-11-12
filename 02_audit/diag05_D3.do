* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag05_D3.log", text replace

*==============================================================
di "########## Painel: aberturas + estoque por setor-ano ##########"
* aberturas: cei_openings_novo (ceicode=escola) -> setor via escolas_parsed
use "$aud\cei_openings_novo.dta", clear
rename ceicode escola
merge m:1 escola using "$aud\escolas_parsed.dta", keepusing(setor) keep(master match) nogen
gen ano = year(dt_abertura)
keep if !missing(setor) & inrange(ano,2005,2018)
contract setor ano, freq(aberturas)
tempfile ab
save `ab'

* grade setores (do cep_setor) x anos 2005-2018 (para acumular estoque desde 2005)
use "$aud\cep_setor.dta", clear
keep setor_cep
rename setor_cep setor
duplicates drop
expand 14
bysort setor: gen ano = 2004+_n
merge 1:1 setor ano using `ab', keep(master match) nogen
replace aberturas=0 if missing(aberturas)
sort setor ano
by setor: gen estoque = sum(aberturas)
* manter janela 2010-2018 para o painel
keep if inrange(ano,2010,2018)
save "$aud\panel_open.dta", replace

*==============================================================
di ""
di "########## Cohort por setor-ano_sol: solic, matric, idade, espera ##########"
use "$aud\child_expo.dta", clear
rename cep_aluno cep
merge m:1 cep using "$aud\cep_setor.dta", keep(master match) nogen
gen idade_entrada = (year(dt_mat_first)-ano_nasc)*12 + (month(dt_mat_first)-mes_nasc) if ever_mat==1
replace idade_entrada = . if !inrange(idade_entrada,0,72)
gen espera_dias = dt_mat_first - dt_sol if ever_mat==1 & !missing(idade_entrada)
gen byte matriculou = ever_mat
keep if !missing(setor_cep) & inrange(ano_sol,2010,2018)
collapse (count) n_solic=cd_aluno_sme (sum) n_matric=matriculou ///
         (mean) idade_media=idade_entrada (median) espera_med=espera_dias, ///
         by(setor_cep ano_sol)
rename setor_cep setor
rename ano_sol ano
save "$aud\panel_cohort.dta", replace

*==============================================================
di ""
di "########## D3 — painel final ##########"
use "$aud\panel_open.dta", clear
merge 1:1 setor ano using "$aud\panel_cohort.dta", keep(master match) nogen
foreach v in n_solic n_matric {
    replace `v'=0 if missing(`v')
}
di "N linhas painel = " _N
di "--- primeiras 20 linhas ---"
sort setor ano
list setor ano aberturas estoque n_solic n_matric idade_media espera_med in 1/20, noobs
di ""
di "--- estatisticas descritivas de cada coluna ---"
sum aberturas estoque n_solic n_matric idade_media espera_med, detail

*==============================================================
di ""
di "########## D4 — setores com >=1 abertura 2010-2016 ##########"
use "$aud\panel_open.dta", clear
keep if inrange(ano,2010,2016)
gen byte teve = aberturas>0
bysort setor: egen anos_com_abertura = total(teve)
bysort setor: egen tot_ab = total(aberturas)
by setor: keep if _n==1
di "--- N setores no painel (com >=1 CEP atribuido) = " _N
count if tot_ab>0
di "  setores com >=1 abertura em 2010-2016 = " r(N)
di "--- distribuicao do nº de anos (2010-2016) com abertura por setor ---"
tab anos_com_abertura

di ""
di "########## D5 — setores NUNCA com abertura no periodo (2010-2016) ##########"
count if tot_ab==0
di "  setores nunca-tratados (0 aberturas 2010-2016) = " r(N)

di "=== FIM D3 ==="
log close
