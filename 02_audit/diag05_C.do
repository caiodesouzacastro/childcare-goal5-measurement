* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag05_C.log", text replace

use "$aud\child_expo.dta", clear
di "N = " _N

* --- DESFECHOS (dt_matricula so aqui) ---
gen byte mat12 = (ever_mat==1 & dt_mat_first<=dt_sol+365)
gen idade_entrada = (year(dt_mat_first)-ano_nasc)*12 + (month(dt_mat_first)-mes_nasc) if ever_mat==1
gen espera_dias = dt_mat_first - dt_sol if ever_mat==1
gen byte valid = inrange(idade_entrada,0,72)
di "--- mat12 (matriculou <=365d da solicitacao) ---"
tab mat12
di "--- idade_entrada valida (0..72) N ---"
count if valid==1

* FE setor x ano
gen setor = floor(cep_aluno/10000)
egen setoryear = group(setor ano_sol)
di "N setores (floor cep/10000): "
codebook setor, compact

program define run1
    * args: dep instr spec  ; usa global cond
    args dep instr spec
    if `spec'==1 {
        qui reg `dep' `instr' estoque_1km i.ano_sol i.mes_nasc $cond
    }
    else {
        qui areg `dep' `instr' estoque_1km i.mes_nasc $cond, absorb(setoryear)
    }
    qui test `instr'
    di "RES| `dep' | `instr' | spec`spec' | coef=" %10.5f _b[`instr'] " se=" %9.5f _se[`instr'] ///
       " t=" %8.2f _b[`instr']/_se[`instr'] " N=" %9.0f e(N) " r2=" %6.4f e(r2) " F=" %10.2f r(F)
end

*==============================================================
di ""
di "########## C1 (spec1) e C2 (spec2, FE setor x ano) — instrumento = expo12_1km ##########"
global cond ""
run1 mat12 expo12_1km 1
run1 mat12 expo12_1km 2
global cond "if valid==1"
run1 idade_entrada expo12_1km 1
run1 idade_entrada expo12_1km 2
run1 espera_dias  expo12_1km 1
run1 espera_dias  expo12_1km 2

*==============================================================
di ""
di "########## C3 — PLACEBO 1 = pre12_1km ##########"
global cond ""
run1 mat12 pre12_1km 1
run1 mat12 pre12_1km 2
global cond "if valid==1"
run1 idade_entrada pre12_1km 1
run1 idade_entrada pre12_1km 2
run1 espera_dias  pre12_1km 1
run1 espera_dias  pre12_1km 2

*==============================================================
di ""
di "########## C4 — PLACEBO 2 = post_1km ##########"
global cond ""
run1 mat12 post_1km 1
run1 mat12 post_1km 2
global cond "if valid==1"
run1 idade_entrada post_1km 1
run1 idade_entrada post_1km 2
run1 espera_dias  post_1km 1
run1 espera_dias  post_1km 2

di ""
di "########## C5 — coeficientes (spec2 FE) lado a lado: ver linhas RES spec2 acima ##########"

di "=== FIM diag05_C ==="
log close
