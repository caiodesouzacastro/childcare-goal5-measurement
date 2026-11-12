* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global ba  "$NE_ROOT\dados_restritos\Ciro\01_dados\processados\bases_analise"
global dsme "$NE_ROOT\dados_restritos\Dados - SME\Atual (25.06)"
cap log close
log using "$aud\diag04_E.log", text replace

*==============================================================
di "########## D1 (compl.) — vars de proficiencia nos PSP ##########"
foreach fy in "psp_2017" "psp_2018" "psp_2019" {
    di "==== `fy' (1 obs) ===="
    use "$ba/`fy'.dta" in 1, clear
    ds *prof* *serie* cd_aluno*
}
di "==== Microdados_PSP_2018_2ano (1 obs) ===="
use "$dsme\Microdados_PSP_2018_2ano.dta" in 1, clear
ds

*==============================================================
di ""
di "########## E1 — matriculas por escola-ano-serie (tamanho de turma) ##########"
use "$dsme\matriculas\matriculas1018.dta", clear
di "N linhas = " _N
* matriculas1018.dta ja possui serie_aluno (nao recriar)
di "--- tab serie_aluno (existente) ---"
tab serie_aluno, miss
keep if !missing(cd_esc_matricula) & !missing(an_letivo_matricula) & !missing(serie_aluno)
contract cd_esc_matricula an_letivo_matricula serie_aluno, freq(turma)
di "N celulas escola-ano-serie = " _N
di "--- distribuicao do tamanho de turma (todas as series) ---"
sum turma, detail
di "--- so serie 1 (bercario I) ---"
sum turma if serie_aluno==1, detail
di "--- so serie 2 ---"
sum turma if serie_aluno==2, detail

*==============================================================
di ""
di "########## E2 — censo2018 casa com CEIs de Fila? ##########"
* CEI presentes no Fila: codigos CEI (escola) que casam com fila_codesc
use "$aud\escolas_parsed.dta", clear
cap drop cei
gen byte cei = (strpos(tipoesc,"CEI")>0 | strpos(tipoesc,"CR.P")>0 | strpos(tipoesc,"CEMEI")>0 | strpos(tipoesc,"CCI")>0)
keep if cei==1
gen long codesc = escola
merge m:1 codesc using "$aud\fila_codesc.dta", keep(match) nogen
di "N CEI que casam com Fila = " _N
keep escola codinep
gen byte tem_codinep = !missing(codinep) & codinep>0
di "  destes, com codinep valido: "
count if tem_codinep==1
* codinep distinto no censo2018
preserve
    use codinep using "$dsme\escolas\censo2018.dta", clear
    duplicates drop
    gen byte no_censo=1
    tempfile cs
    save `cs'
restore
rename codinep codinep
merge m:1 codinep using `cs', keep(master match) gen(mc)
di "--- CEI-em-Fila cujo codinep casa com censo2018 ---"
count if mc==3
di "--- total CEI-em-Fila com codinep ---"
count if tem_codinep==1
di "--- taxa de casamento (dos que tem codinep) ---"
count if mc==3 & tem_codinep==1

di ""
di "--- variaveis de infraestrutura em censo2018 (amostra) ---"
use "$dsme\escolas\censo2018.dta" in 1, clear
ds in_* qt_* tp_dependencia

di "=== FIM E ==="
log close
