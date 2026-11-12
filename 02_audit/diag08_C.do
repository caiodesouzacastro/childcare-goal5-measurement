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
log using "$aud\diag08_C.log", text replace

di "########## Universo C: 1o encaminhamento, SEM prioridade ##########"
use cd_aluno_sme dt_solicitacao dt_encaminhamento cd_esc_encaminhamento cep_aluno ///
    cd_sexo_aluno tp_raca_cor mes_nasc ano_nasc tipo_prioridade_encaminhamento ///
    using "$fila", clear
gen double dt_sol = date(dt_solicitacao,"DMY hms")
gen double dt_enc = date(dt_encaminhamento,"DMY hms")
keep if !missing(dt_enc) & !missing(cd_esc_encaminhamento) & !missing(cep_aluno)
keep if missing(tipo_prioridade_encaminhamento)   /* EXCLUI prioridade */
gsort cd_aluno_sme dt_enc
by cd_aluno_sme: keep if _n==1
gen ym_sol = ym(year(dt_sol),month(dt_sol))
gen idade_sol = (year(dt_sol)-ano_nasc)*12 + (month(dt_sol)-mes_nasc)
gen byte feminino = cd_sexo_aluno=="F"
gen byte branco = tp_raca_cor==1
rename cep_aluno cep
rename cd_esc_encaminhamento escola
* atributos da escola atribuida
merge m:1 escola using "$aud\escolas_parsed.dta", keepusing(tipoesc codinep lat lon) keep(master match) nogen
merge m:1 codinep using "$dsme\escolas\censo2018.dta", keepusing(in_bercario qt_salas_existentes qt_funcionarios) keep(master match) nogen
* distancia CEP -> escola
merge m:1 cep using "$dsme\cepcentroide.dta", keepusing(latitude longitude) keep(master match) nogen
gen double a = sin((lat-latitude)*_pi/360)^2 + cos(latitude*_pi/180)*cos(lat*_pi/180)*sin((lon-longitude)*_pi/360)^2
gen double dist_km = 2*6371*asin(sqrt(a))
cap encode tipoesc, gen(modal)
gen byte conveniada = strpos(tipoesc,"CR.P")>0
* celula
egen cell = group(cep ym_sol)
bysort cell: gen ncell = _N
save "$aud\c_assign.dta", replace

di ""
di "########## C1 — N apos exclusao de prioridade e celulas >=2 ##########"
di "  N criancas (1o enc, sem prioridade) = " _N
count if ncell>=2
di "  N criancas em celulas >=2 = " r(N)
preserve
    keep if ncell>=2
    egen tagcell = tag(cell)
    count if tagcell==1
    di "  N celulas (>=2 criancas) = " r(N)
restore

di ""
di "########## C2 — caracteristicas da escola atribuida (celulas >=2) ##########"
keep if ncell>=2
foreach v in qt_salas_existentes in_bercario qt_funcionarios dist_km conveniada {
    qui sum `v'
    local m=r(mean)
    local sd=r(sd)
    qui reghdfe `v', absorb(cell) nocons
    di "  `v': media=" %8.3f `m' "  SD_total=" %8.3f `sd' "  SD_within(rmse)=" %8.3f e(rmse)
}

di ""
di "########## C3 — BALANCO: caract. escola ~ chars da crianca, absorb(cell) cluster(cep) ##########"
foreach dep in qt_salas_existentes in_bercario qt_funcionarios dist_km conveniada {
    di ""
    di "==== DEP: `dep' ===="
    cap reghdfe `dep' feminino branco mes_nasc idade_sol, absorb(cell) vce(cluster cep)
    if !_rc {
        di "  b_fem=" %8.4f _b[feminino] " (se " %7.4f _se[feminino] ")  b_branco=" %8.4f _b[branco] " (se " %7.4f _se[branco] ")"
        di "  b_mesnasc=" %8.4f _b[mes_nasc] " (se " %7.4f _se[mes_nasc] ")  b_idadesol=" %8.4f _b[idade_sol] " (se " %7.4f _se[idade_sol] ")"
        test feminino branco mes_nasc idade_sol
        di "  >>> F conjunto = " %8.3f r(F) "  p = " %6.4f r(p) "  N=" e(N)
    }
    else di "  ERRO rc=`=_rc'"
}

di ""
di "########## C5 — celulas com variacao utilizavel ##########"
egen tagcell = tag(cell)
bysort cell: egen sd_salas = sd(qt_salas_existentes)
bysort cell: egen mx_salas = max(qt_salas_existentes)
bysort cell: egen mn_salas = min(qt_salas_existentes)
gen byte var_salas2 = (mx_salas-mn_salas)>=2 & !missing(mx_salas,mn_salas)
bysort cell: egen sd_berc = sd(in_bercario)
gen byte var_berc = sd_berc>0 & !missing(sd_berc)
di "--- celulas com range qt_salas >=2 ---"
count if tagcell==1 & var_salas2==1
qui count if tagcell==1
di "    de " r(N) " celulas"
di "--- celulas com variacao em in_bercario ---"
count if tagcell==1 & var_berc==1

di "=== FIM C ==="
log close
