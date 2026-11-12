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
log using "$aud\diag04_Eredo.log", text replace

*==============================================================
di "########## E1 — tamanho de turma via matriculas do Fila ##########"
use cd_aluno_sme cd_esc_matricula an_letivo_matricula cd_serie_ensino_matricula dt_matricula ///
    using "$fila", clear
gen double dt_mat = date(dt_matricula,"DMY hms")
keep if !missing(dt_mat) & !missing(cd_esc_matricula) & !missing(an_letivo_matricula)
gen serie_aluno = .
replace serie_aluno = 1 if inlist(cd_serie_ensino_matricula,1,2,3)
replace serie_aluno = 2 if inlist(cd_serie_ensino_matricula,4,5,6)
replace serie_aluno = 3 if inlist(cd_serie_ensino_matricula,11,27)
replace serie_aluno = 4 if inlist(cd_serie_ensino_matricula,28,29)
replace serie_aluno = 5 if inlist(cd_serie_ensino_matricula,23,24)
replace serie_aluno = 6 if inlist(cd_serie_ensino_matricula,25,26)
keep if !missing(serie_aluno)
* dedup: 1 registro por crianca x escola x ano x serie
duplicates drop cd_aluno_sme cd_esc_matricula an_letivo_matricula serie_aluno, force
contract cd_esc_matricula an_letivo_matricula serie_aluno, freq(turma)
di "N celulas escola-ano-serie = " _N
di "--- distribuicao tamanho de turma (todas series creche/pre 1-6) ---"
sum turma, detail
foreach s in 1 2 3 {
    di "--- serie `s' ---"
    sum turma if serie_aluno==`s', detail
}

*==============================================================
di ""
di "########## E2 — censo2018 casa com CEIs de Fila? ##########"
use "$aud\escolas_parsed.dta", clear
cap drop cei
gen byte cei = (strpos(tipoesc,"CEI")>0 | strpos(tipoesc,"CR.P")>0 | strpos(tipoesc,"CEMEI")>0 | strpos(tipoesc,"CCI")>0)
keep if cei==1
gen long codesc = escola
merge m:1 codesc using "$aud\fila_codesc.dta", keep(match) nogen
di "N CEI que casam com Fila = " _N
keep escola codinep
gen byte tem_codinep = !missing(codinep) & codinep>0
di "  com codinep valido:"
count if tem_codinep==1
preserve
    use codinep using "$dsme\escolas\censo2018.dta", clear
    duplicates drop
    drop if missing(codinep)
    gen byte no_censo=1
    tempfile cs
    save `cs'
    di "  codinep distintos em censo2018 = " _N
restore
merge m:1 codinep using `cs', keep(master match) gen(mc)
di "--- CEI-em-Fila cujo codinep casa com censo2018 ---"
count if mc==3
di "--- CEI-em-Fila com codinep valido ---"
count if tem_codinep==1
di "--- taxa: casam / com codinep ---"
count if mc==3 & tem_codinep==1

di ""
di "--- variaveis de infraestrutura em censo2018 ---"
use "$dsme\escolas\censo2018.dta" in 1, clear
ds qt_* in_bercario in_agua_rede_publica in_esgoto_rede_publica in_energia_rede_publica in_banheiro_ei in_parque_infantil in_cozinha in_refeitorio tp_dependencia in_conveniada_pp

di "=== FIM Eredo ==="
log close
