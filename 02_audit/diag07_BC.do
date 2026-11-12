* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global fila "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
cap log close
log using "$aud\diag07_BC.log", text replace

*==============================================================
di "########## PARTE B — quem e o adulto (rais_panel, sem CPF/nome) ##########"
use "$aud\rais_panel.dta", clear
di "N linhas painel = " _N
egen tagc = tag(cd_aluno_sme)
di "N criancas distintas no painel = "
count if tagc==1

di ""
di "--- B1: sexo do adulto (1? 2?) ---"
tab sexo, miss
di "  (checar codificacao; reportar % de cada categoria)"

di ""
di "--- B2: idade do adulto no ANO DO NASCIMENTO da crianca ---"
gen idade_no_nasc = idade - (ano - ano_nasc)
_pctile idade_no_nasc, p(5 25 50 75 95)
di "  p5=" r(r1) " p25=" r(r2) " p50=" r(r3) " p75=" r(r4) " p95=" r(r5)

di ""
di "--- B3: idade por sexo do adulto ---"
table sexo, stat(p50 idade_no_nasc) stat(mean idade_no_nasc) stat(count idade_no_nasc)

di ""
di "--- B4: nº de responsaveis (respid) distintos por crianca ---"
preserve
    keep cd_aluno_sme respid
    duplicates drop
    bysort cd_aluno_sme: gen nresp=_N
    by cd_aluno_sme: keep if _n==1
    tab nresp
restore

*==============================================================
di ""
di "########## B5 — cpf_resp em B_novo e casamento com RAIS ##########"
* cpf_resp nao-missing por crianca (Fila) -- indicador apenas, sem valor
use cd_aluno_sme cpf_resp_aluno using "$fila", clear
gen byte tem_resp = !missing(cpf_resp_aluno) & cpf_resp_aluno>0
collapse (max) tem_resp, by(cd_aluno_sme)
merge 1:1 cd_aluno_sme using "$aud\B_novo.dta", keep(match) keepusing(cd_aluno_sme) nogen
di "N B_novo = " _N
di "--- % com cpf_resp nao-missing ---"
sum tem_resp
* casar com rais_panel (crianca tem responsavel no RAIS)
preserve
    use cd_aluno_sme using "$aud\rais_panel.dta", clear
    duplicates drop
    gen byte tem_rais=1
    tempfile r
    save `r'
restore
merge 1:1 cd_aluno_sme using `r', keep(master match) nogen
replace tem_rais=0 if missing(tem_rais)
di "--- % de B_novo com responsavel no RAIS ---"
sum tem_rais
di "--- entre os com cpf_resp: % que casa com RAIS ---"
sum tem_rais if tem_resp==1

*==============================================================
di ""
di "########## PARTE C — primeiro estagio 31/03 (coortes 2009-2015) ##########"
use "$aud\B_novo.dta", clear
keep if inrange(ano_nasc,2009,2015)
gen idade_ei = (year(dt_mat_first)-ano_nasc)*12 + (month(dt_mat_first)-mes_nasc) if ever_mat==1
gen byte ei12 = (ever_mat==1 & idade_ei<12)
gen byte ei18 = (ever_mat==1 & idade_ei<18)
gen byte ei24 = (ever_mat==1 & idade_ei<24)
gen byte ei36 = (ever_mat==1 & idade_ei<36)
keep if inlist(mes_nasc,3,4)
gen byte abril = mes_nasc==4

di "--- C1: P(EI antes dos 12m) marco vs abril, por coorte ---"
forvalues c=2009/2015 {
    qui sum ei12 if ano_nasc==`c' & abril==0
    local m3=r(mean)
    qui sum ei12 if ano_nasc==`c' & abril==1
    local m4=r(mean)
    qui ttest ei12 if ano_nasc==`c', by(abril)
    di "  coorte `c': marco=" %5.3f `m3' "  abril=" %5.3f `m4' "  dif=" %6.3f r(mu_1)-r(mu_2) "  se=" %6.4f r(se) "  p=" %6.4f r(p)
}
di ""
di "--- C2: antes 18/24/36 meses (por coorte) ---"
foreach x in ei18 ei24 ei36 {
    di "  ==== `x' ===="
    forvalues c=2009/2015 {
        qui sum `x' if ano_nasc==`c' & abril==0
        local m3=r(mean)
        qui sum `x' if ano_nasc==`c' & abril==1
        local m4=r(mean)
        qui ttest `x' if ano_nasc==`c', by(abril)
        di "    coorte `c': marco=" %5.3f `m3' " abril=" %5.3f `m4' " dif=" %6.3f r(mu_1)-r(mu_2) " p=" %6.4f r(p)
    }
}
di ""
di "--- C3: idade mediana 1a matricula EI, marco vs abril, por coorte ---"
forvalues c=2009/2015 {
    qui _pctile idade_ei if ano_nasc==`c' & abril==0, p(50)
    local md3=r(r1)
    qui _pctile idade_ei if ano_nasc==`c' & abril==1, p(50)
    local md4=r(r1)
    di "  coorte `c': mediana marco=`md3'  abril=`md4'"
}
di ""
di "--- C4: P(alguma vez matriculado em EI) marco vs abril ---"
forvalues c=2009/2015 {
    qui sum ever_mat if ano_nasc==`c' & abril==0
    local m3=r(mean)
    qui sum ever_mat if ano_nasc==`c' & abril==1
    local m4=r(mean)
    qui ttest ever_mat if ano_nasc==`c', by(abril)
    di "  coorte `c': marco=" %5.3f `m3' " abril=" %5.3f `m4' " dif=" %6.3f r(mu_1)-r(mu_2) " p=" %6.4f r(p)
}

*==============================================================
di ""
di "--- C5: P(EI antes 12m) por TODOS os meses (coortes 2009-2015 pooled) ---"
use "$aud\B_novo.dta", clear
keep if inrange(ano_nasc,2009,2015)
gen idade_ei = (year(dt_mat_first)-ano_nasc)*12 + (month(dt_mat_first)-mes_nasc) if ever_mat==1
gen byte ei12 = (ever_mat==1 & idade_ei<12)
table mes_nasc, stat(mean ei12) stat(count ei12)

di "=== FIM BC ==="
log close
