* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag11_D.log", text replace

* --- escola mais proxima + distrito/setor por CEP ---
use codesc distrito setor using "$aud\cap_full.dta", clear
rename codesc ceicode
bysort ceicode: keep if _n==1
tempfile escmeta
save `escmeta'
use cep ceicode dist_km using "$aud\cep_cei_pairs_novo.dta", clear
bysort cep (dist_km): keep if _n==1
rename ceicode esc_prox
tempfile nearest
save `nearest'

use "$aud\berc_design.dta", clear
merge m:1 cep using `nearest', keep(master match) nogen
rename esc_prox ceicode
merge m:1 ceicode using `escmeta', keep(master match) nogen
egen distid = group(distrito)
egen setorid = group(setor)
gen dsem = distid*100 + sol_sidx
gen ssem = setorid*100 + sol_sidx
* escalar choques para 100 vagas
foreach v in choque_neg choque_pos choque_pre choque_fut cap_base {
    gen `v'100 = `v'/100
}
di "N = " _N

program define R
    args dep xs absv
    qui reghdfe `dep' `xs', absorb(`absv') vce(cluster ceicode)
    di "  [`dep' | abs=`absv'] N=" %9.0f e(N) ///
       "  bNEG=" %8.4f _b[choque_neg100] " (se " %7.4f _se[choque_neg100] ")" ///
       "  bPOS=" %8.4f _b[choque_pos100] " (se " %7.4f _se[choque_pos100] ")"
end

di ""
di "########## D1 — primeiro estagio (choque_neg/pos + cap_base) ##########"
di "  Deps: espera(dias), enc180(0/1), idade_entrada(m), mat365(0/1)."
di "  --- spec A: absorb(distrito#semestre) ---"
foreach d in espera enc180 idade_entrada mat365 {
    R `d' "choque_neg100 choque_pos100 cap_base100" dsem
}
di "  --- spec B: absorb(cep) ---"
foreach d in espera enc180 idade_entrada mat365 {
    R `d' "choque_neg100 choque_pos100 cap_base100" cep
}
di "  --- spec C: absorb(setor#semestre) ---"
foreach d in espera enc180 idade_entrada mat365 {
    R `d' "choque_neg100 choque_pos100 cap_base100" ssem
}

di ""
di "########## D2 — PLACEBO 1: choque nos 180d ANTERIORES (deve ser nulo) ##########"
foreach d in espera enc180 idade_entrada mat365 {
    qui reghdfe `d' choque_pre100 choque_pos100 cap_base100, absorb(dsem) vce(cluster ceicode)
    di "  [`d'] bPRE=" %8.4f _b[choque_pre100] " (se " %7.4f _se[choque_pre100] ")  N=" e(N)
}

di ""
di "########## D3 — PLACEBO 2: choque futuro (366-545d) ##########"
foreach d in espera enc180 idade_entrada mat365 {
    qui reghdfe `d' choque_fut100 choque_pos100 cap_base100, absorb(dsem) vce(cluster ceicode)
    di "  [`d'] bFUT=" %8.4f _b[choque_fut100] " (se " %7.4f _se[choque_fut100] ")  N=" e(N)
}

di ""
di "########## D5 — dose-resposta: efeito por quartil de (choque_neg/cap_base) ##########"
gen fracperda = choque_neg/cap_base if cap_base>0
replace fracperda = 0 if choque_neg==0
xtile qperda = fracperda if choque_neg>0, nq(4)
replace qperda = 0 if choque_neg==0
di "--- media de enc180 e espera por quartil de fracao de capacidade perdida ---"
table qperda, stat(mean enc180) stat(mean espera) stat(mean idade_entrada) stat(count enc180)

di "=== FIM D ==="
log close
