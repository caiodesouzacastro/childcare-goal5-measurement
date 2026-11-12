* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag07_E.log", text replace

di "########## E1 — ano de elegibilidade ao Bercario I vs quebra de 2013 ##########"
di "  elegibilidade = ano_nasc (marco/mes<=3) ou ano_nasc+1 (abril/mes>=4)"
di "  coorte | elig marco | elig abril | (>=2013 = pos-quebra)"
forvalues c=2009/2015 {
    di "  `c'     |   `c'     |   " `c'+1 "     "
}

di ""
di "########## E2 — razao marco/abril de N por coorte (B_novo) ##########"
use "$aud\B_novo.dta", clear
forvalues c=2009/2015 {
    qui count if ano_nasc==`c' & mes_nasc==3
    local n3=r(N)
    qui count if ano_nasc==`c' & mes_nasc==4
    local n4=r(N)
    di "  coorte `c': N marco=`n3'  N abril=`n4'  razao mar/abr=" %5.3f `n3'/`n4'
}

di ""
di "########## E3 — balanco marco vs abril nas vars do responsavel (RAIS) ##########"
di "  NOTA: remuneracao no ano ANTES do nascimento NAO existe (RAIS sem pre-parto); uso o ano observado."
use "$aud\rais_panel.dta", clear
gen idade_no_nasc = idade - (ano - ano_nasc)
gen byte fem = sexo==2
merge m:1 cd_aluno_sme using "$aud\B_novo.dta", keep(match) keepusing(mes_nasc) nogen
keep if inrange(ano_nasc,2009,2015) & inlist(mes_nasc,3,4)
gen byte abril = mes_nasc==4
di "  N marco / abril (com RAIS):"
tab mes_nasc
foreach v in fem idade_no_nasc escol remun {
    qui ttest `v', by(abril)
    di "  `v': marco=" %8.3f r(mu_1) "  abril=" %8.3f r(mu_2) "  dif=" %8.4f r(mu_1)-r(mu_2) "  se=" %8.4f r(se) "  p=" %6.4f r(p)
}
di "=== FIM E ==="
log close
