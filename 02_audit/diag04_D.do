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
log using "$aud\diag04_D.log", text replace

*==============================================================
di "########## D1 — describe dos arquivos PSP ##########"
foreach f in "$ba\psp_2017.dta" "$ba\psp_2018.dta" "$ba\psp_2019.dta" "$dsme\Microdados_PSP_2018_2ano.dta" {
    di ""
    di "==== `f' ===="
    cap describe using "`f'", short
    cap describe using "`f'"
}

*==============================================================
di ""
di "########## D2/D3 — match com universo_B4 ##########"
* universo
use cd_aluno_sme using "$aud\universo_B4.dta", clear
duplicates drop
gen byte inuniv = 1
tempfile univ
save `univ'
di "N universo (cd_aluno distintos) = " _N

* processar cada PSP -> distinct cd_aluno com proficiencia
local yr 2017 2018 2019
foreach y of local yr {
    di ""
    di "===== PSP `y' ====="
    use cd_aluno_sme proficiencia_mat proficiencia_lp using "$ba\psp_`y'.dta", clear
    cap destring proficiencia_mat proficiencia_lp, replace force dpcomma
    gen byte hasprof = !missing(proficiencia_mat) | !missing(proficiencia_lp)
    di "  N linhas PSP `y' = " _N
    keep if hasprof==1
    keep cd_aluno_sme
    duplicates drop
    di "  N criancas distintas com proficiencia = " _N
    gen byte psp`y' = 1
    save "$aud\psp`y'_ids.dta", replace
    * match com universo
    merge 1:1 cd_aluno_sme using `univ', keep(match) nogen
    di "  N casadas com universo B4 = " _N
}

*==============================================================
di ""
di "########## D3 — universo B4 x PSP (algum ano) ##########"
use `univ', clear
foreach y in 2017 2018 2019 {
    merge 1:1 cd_aluno_sme using "$aud\psp`y'_ids.dta", keep(master match) nogen
    replace psp`y' = 0 if missing(psp`y')
}
gen byte psp_any = (psp2017==1 | psp2018==1 | psp2019==1)
di "--- N universo com PSP em ALGUM ano (N do paper) ---"
count if psp_any==1
di "--- por ano ---"
foreach y in 2017 2018 2019 {
    qui count if psp`y'==1
    di "  PSP `y' (no universo): " r(N)
}
di "--- so 2018 ---"
count if psp2018==1
di "--- em >=2 anos ---"
gen npsp = psp2017+psp2018+psp2019
tab npsp

di "=== FIM D ==="
log close
