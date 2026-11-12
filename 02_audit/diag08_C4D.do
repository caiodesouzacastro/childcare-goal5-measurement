* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global fila "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
cap log close
log using "$aud\diag08_C4D.log", text replace

*==============================================================
di "########## C4 — irmao ja matriculado prediz escola atribuida? ##########"
* dt_mat_first por crianca (child_expo) + cpf_resp (Fila, indice local)
use cd_aluno_sme cpf_resp_aluno using "$fila", clear
keep if !missing(cpf_resp_aluno) & cpf_resp_aluno>0
collapse (firstnm) cpf_resp_aluno, by(cd_aluno_sme)
egen long respid = group(cpf_resp_aluno)
drop cpf_resp_aluno
merge 1:1 cd_aluno_sme using "$aud\child_expo.dta", keep(match) keepusing(dt_mat_first) nogen
* min1/min2 da 1a matricula por responsavel (para excluir a propria crianca)
gsort respid dt_mat_first
by respid: gen double sibmin1 = dt_mat_first[1]
by respid: gen long sibarg1 = cd_aluno_sme[1]
by respid: gen double sibmin2 = dt_mat_first[2]
gen double sib_mat = cond(cd_aluno_sme==sibarg1, sibmin2, sibmin1)
keep cd_aluno_sme sib_mat
save "$aud\sibmat.dta", replace

use "$aud\c_assign.dta", clear
keep if ncell>=2
merge m:1 cd_aluno_sme using "$aud\sibmat.dta", keep(master match) nogen
gen byte irmao_matric = (!missing(sib_mat) & sib_mat < dt_sol)
di "--- % com irmao ja matriculado antes da solicitacao ---"
sum irmao_matric
foreach dep in qt_salas_existentes in_bercario conveniada dist_km {
    di "==== DEP: `dep' ===="
    cap reghdfe `dep' irmao_matric, absorb(cell) vce(cluster cep)
    if !_rc di "  b_irmao=" %8.4f _b[irmao_matric] " (se " %7.4f _se[irmao_matric] ")  p=" %6.4f 2*ttail(e(df_r),abs(_b[irmao_matric]/_se[irmao_matric])) "  N=" e(N)
    else di "  ERRO rc=`=_rc'"
}

*==============================================================
di ""
di "########## D1 — subamostra em celulas com variacao: PSP / 1o / 3o ano ##########"
use "$aud\c_assign.dta", clear
keep if ncell>=2
bysort cell: egen mx = max(qt_salas_existentes)
bysort cell: egen mn = min(qt_salas_existentes)
keep if (mx-mn)>=2 & !missing(mx,mn)   /* celulas com variacao utilizavel */
di "  N criancas em celulas com variacao de salas >=2 = " _N
keep cd_aluno_sme qt_salas_existentes in_bercario
save "$aud\d_subsample.dta", replace
* PSP
foreach y in 2017 2018 2019 {
    merge 1:1 cd_aluno_sme using "$aud\psp`y'_ids.dta", keep(master match) nogen
    cap replace psp`y'=0 if missing(psp`y')
}
gen byte psp_any = (psp2017==1|psp2018==1|psp2019==1)
* trajetoria fundamental
merge 1:1 cd_aluno_sme using "$aud\traj_child.dta", keep(master match) keepusing(tem1ano tem3ano) nogen
di "  com PSP algum ano = "
count if psp_any==1
di "  com 1o ano fundamental = "
count if tem1ano==1
di "  com 3o ano fundamental = "
count if tem3ano==1

di ""
di "########## D2 — distribuicao qt_salas / in_bercario (subamostra) ##########"
sum qt_salas_existentes in_bercario, detail

di ""
di "########## D3 — correlacao bruta escola atribuida x proficiencia PSP ##########"
di "  (merge com psp_2018 para nota de matematica; so descritivo)"
preserve
    use cd_aluno_sme proficiencia_mat using ///
        "$NE_ROOT\dados_restritos\Ciro\01_dados\processados\bases_analise\psp_2018.dta", clear
    cap destring proficiencia_mat, replace force dpcomma
    collapse (firstnm) proficiencia_mat, by(cd_aluno_sme)
    tempfile p
    save `p'
restore
merge 1:1 cd_aluno_sme using `p', keep(master match) nogen
pwcorr qt_salas_existentes in_bercario proficiencia_mat, sig obs

di "=== FIM C4D ==="
log close
