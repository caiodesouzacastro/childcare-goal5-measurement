* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global dsme "$NE_ROOT\dados_restritos\Dados - SME\Atual (25.06)"
global fila "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
cap log close
log using "$aud\diag06_B.log", text replace

*==============================================================
di "########## B1 — cpf_fila_*.dta: N obs e N vars ##########"
foreach f in cpf_fila_101 cpf_fila_102 cpf_fila_11 cpf_fila_12 cpf_fila_13 cpf_fila_14 {
    cap describe using "$dsme\\`f'.dta", short
    di "  `f': N=" r(N) "  k=" r(k)
}

*==============================================================
di ""
di "########## B2 — pessoa linkada = adulto? (cpf_fila_14) ##########"
use cpf idade ano cd_aluno_sme datadenascimento using "$dsme\cpf_fila_14.dta", clear
di "N linhas = " _N
di "--- idade (do linkado): resumo ---"
sum idade, detail
di "--- cpf nao-missing ---"
count if !missing(cpf) & cpf>0
di "--- ano (cobertura) ---"
tab ano

*==============================================================
di ""
di "########## B3 — B_novo casa com cpf_fila? adultos e filhos/adulto ##########"
* empilhar cd_aluno + cpf de todos cpf_fila
clear
tempfile acc
gen x=.
save `acc', emptyok
foreach f in cpf_fila_101 cpf_fila_102 cpf_fila_11 cpf_fila_12 cpf_fila_13 cpf_fila_14 {
    use cd_aluno_sme cpf using "$dsme\\`f'.dta", clear
    append using `acc'
    save `acc', replace
}
duplicates drop
di "N pares (aluno,cpf) distintos = " _N
* criancas distintas com algum registro RAIS
preserve
    keep cd_aluno_sme
    duplicates drop
    gen byte tem_rais=1
    tempfile kids
    save `kids'
    di "  criancas distintas com RAIS = " _N
restore
* casar com B_novo
merge m:1 cd_aluno_sme using "$aud\B_novo.dta", keepusing(cd_aluno_sme)
di "  (match==3 = em B_novo E com RAIS) ; master-only = RAIS sem B_novo"
* filhos por adulto (cpf)
use `acc', clear
keep if !missing(cpf) & cpf>0
bysort cpf: gen nfilhos = _N
by cpf: keep if _n==1
di "--- distribuicao de filhos por CPF adulto (RAIS) ---"
sum nfilhos, detail
di "  N adultos distintos = " _N

*==============================================================
di ""
di "########## B5 — IRMAOS via cpf_resp_aluno (Fila) ##########"
use cd_aluno_sme cpf_resp_aluno using "$fila", clear
keep if !missing(cpf_resp_aluno) & cpf_resp_aluno>0
collapse (firstnm) cpf_resp_aluno, by(cd_aluno_sme)
* manter so criancas de B_novo
merge 1:1 cd_aluno_sme using "$aud\child_expo.dta", keep(match) keepusing(dt_mat_first dt_sol ano_nasc mes_nasc ever_mat) nogen
gen idade_entrada = (year(dt_mat_first)-ano_nasc)*12 + (month(dt_mat_first)-mes_nasc) if ever_mat==1
replace idade_entrada=. if !inrange(idade_entrada,0,72)
* nº de filhos (em B_novo) por responsavel
bysort cpf_resp_aluno: gen nfilhos_bnovo = _N
di "--- distribuicao nº de filhos (B_novo) por responsavel ---"
preserve
    by cpf_resp_aluno: keep if _n==1
    gen fc = nfilhos_bnovo
    replace fc=5 if nfilhos_bnovo>=5
    tab fc
    di "  N responsaveis distintos = " _N
restore
di "--- criancas de B_novo com >=1 irmao em B_novo ---"
count if nfilhos_bnovo>=2
di "--- familias com exatamente 2 filhos: diff de idade de entrada ---"
preserve
    keep if nfilhos_bnovo==2 & !missing(idade_entrada)
    bysort cpf_resp_aluno: gen n2 = _N
    keep if n2==2
    bysort cpf_resp_aluno: egen mx = max(idade_entrada)
    bysort cpf_resp_aluno: egen mn = min(idade_entrada)
    gen diff = mx-mn
    by cpf_resp_aluno: keep if _n==1
    di "  N familias 2-filhos com ambos idade valida = " _N
    di "  --- diff de idade de entrada entre irmaos (meses) ---"
    sum diff, detail
    count if diff>=6
    di "  pares de irmaos com diff idade entrada >=6 meses = " r(N)
restore

di "=== FIM B ==="
log close
