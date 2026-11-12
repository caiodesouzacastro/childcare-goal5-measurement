* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global rc  "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\rais_cpf"
cap log close
log using "$aud\diag08_panel.log", text replace

di "########## Painel RAIS: ano de RAIS = sufixo do nome do arquivo ##########"
tempfile acc
clear
gen byte _x=.
save `acc', emptyok

* Grupo 1 (esquema antigo): empem3112, genero -> anos 2007-2010
foreach spec in "cpf_fila_07 2007" "cpf_fila_081 2008" "cpf_fila_092 2009" "cpf_fila_101 2010" "cpf_fila_102 2010" {
    gettoken f yr : spec
    use cd_aluno_sme cpf empem3112 ano_nasc mes_nasc using "$rc/`f'.dta", clear
    rename empem3112 emp_raw
    gen int rais_year = `yr'
    append using `acc'
    save `acc', replace
}
* Grupo 2 (esquema novo): vínculoativo3112 -> 2011-2014
foreach spec in "cpf_fila_11 2011" "cpf_fila_12 2012" "cpf_fila_13 2013" "cpf_fila_14 2014" {
    gettoken f yr : spec
    use cd_aluno_sme cpf vínculoativo3112 ano_nasc mes_nasc using "$rc/`f'.dta", clear
    rename vínculoativo3112 emp_raw
    gen int rais_year = `yr'
    append using `acc'
    save `acc', replace
}
use `acc', clear
drop _x
egen long respid = group(cpf)
drop cpf
gen byte emp = (emp_raw==1)
collapse (max) emp, by(cd_aluno_sme respid rais_year ano_nasc mes_nasc)
compress
save "$aud\panel_rais.dta", replace
di "N (crianca x resp x ano_rais) = " _N

*==============================================================
di ""
di "########## A5 — nº de ANOS DE RAIS distintos por crianca ##########"
preserve
    keep cd_aluno_sme rais_year
    duplicates drop
    bysort cd_aluno_sme: gen nyr = _N
    by cd_aluno_sme: keep if _n==1
    gen nc = nyr
    replace nc = 8 if nyr>=8
    tab nc
    sum nyr, detail
restore

*==============================================================
di ""
di "########## A6 — criancas com RAIS ANTES do nascimento, por coorte ##########"
gen byte pre = rais_year < ano_nasc
di "--- total linhas com rais_year < ano_nasc ---"
count if pre==1
* por crianca: tem algum ano pre-nascimento
bysort cd_aluno_sme: egen tem_pre = max(pre)
bysort cd_aluno_sme: egen npre = total(pre)
preserve
    by cd_aluno_sme: keep if _n==1
    di "--- criancas com >=1 ano RAIS pre-nascimento, por coorte ---"
    forvalues c=2008/2014 {
        qui count if ano_nasc==`c'
        local nt=r(N)
        qui count if ano_nasc==`c' & tem_pre==1
        di "  coorte `c': N(painel)=`nt'  com pre-nasc=" r(N)
    }
    di "--- distribuicao npre (anos pre-nascimento) ---"
    gen npc=npre
    replace npc=4 if npre>=4
    tab npc
restore

di "=== FIM panel ==="
log close
