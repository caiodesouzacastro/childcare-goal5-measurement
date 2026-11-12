* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 220
global aud "$NE_ROOT\02_audit"
global dsme "$NE_ROOT\dados_restritos\Dados - SME\Atual (25.06)"
cap log close
log using "$aud\diag05_A.log", text replace

use "$aud\escolas_parsed.dta", clear
cap drop cei
gen byte cei = (strpos(tipoesc,"CEI")>0 | strpos(tipoesc,"CR.P")>0 | strpos(tipoesc,"CEMEI")>0 | strpos(tipoesc,"CCI")>0)
keep if cei==1
di "N CEI = " _N

*==============================================================
di ""
di "########## A1 — cobertura das 3 datas por tipoesc ##########"
gen byte hc = !missing(dt_criacao_d)
gen byte hf = !missing(dt_ini_func_d)
gen byte hv = !missing(dt_ini_conv_d)
encode tipoesc, gen(tnum)
table tnum, stat(frequency) stat(sum hc hf hv)

*==============================================================
di ""
di "########## A2 — diferencas em dias entre datas (CEIs com ambas) ##########"
gen dcf = dt_criacao_d - dt_ini_func_d if hc & hf
gen dcv = dt_criacao_d - dt_ini_conv_d if hc & hv
di "--- dt_criacao - dt_ini_func (N com ambas) ---"
count if !missing(dcf)
_pctile dcf, p(10 50 90)
di "  p10=" r(r1) "  p50=" r(r2) "  p90=" r(r3)
di "--- dt_criacao - dt_ini_conv (N com ambas) ---"
count if !missing(dcv)
_pctile dcv, p(10 50 90)
di "  p10=" r(r1) "  p50=" r(r2) "  p90=" r(r3)

*==============================================================
di ""
di "########## A3 — dt_abertura ##########"
gen byte is_conv = strpos(tipoesc,"CR.P")>0
gen double dt_abertura = .
gen str8 fonte = ""
* CR.P.CONV -> dt_ini_conv
replace dt_abertura = dt_ini_conv_d if is_conv & !missing(dt_ini_conv_d)
replace fonte = "conv" if is_conv & !missing(dt_ini_conv_d)
* demais -> dt_ini_func
replace dt_abertura = dt_ini_func_d if !is_conv & missing(dt_abertura) & !missing(dt_ini_func_d)
replace fonte = "func" if !is_conv & fonte=="" & !missing(dt_ini_func_d)
* fallback dt_criacao
replace dt_abertura = dt_criacao_d if missing(dt_abertura) & !missing(dt_criacao_d)
replace fonte = "criacao" if fonte=="" & !missing(dt_criacao_d)
replace fonte = "none" if fonte==""
format dt_abertura %td
di "--- fonte da dt_abertura ---"
tab fonte
di "--- N com dt_abertura nao-missing ---"
count if !missing(dt_abertura)
di "--- distribuicao por ano (2008-2016) ---"
gen yr_ab = year(dt_abertura)
tab yr_ab if inrange(yr_ab,2008,2016)
* salvar openings novas (para reconstruir pares)
preserve
    keep if !missing(dt_abertura) & !missing(lat,lon)
    keep escola lat lon dt_abertura tipoesc codinep
    rename escola ceicode
    rename lat ceilat
    rename lon ceilon
    save "$aud\cei_openings_novo.dta", replace
    di "  N CEI openings novo (com coord e dt_abertura) = " _N
restore

*==============================================================
di ""
di "########## A4 — sanidade vs censo2018 (codinep) ##########"
* codinep distinto no censo
preserve
    use codinep using "$dsme\escolas\censo2018.dta", clear
    duplicates drop
    drop if missing(codinep)
    gen byte in_censo=1
    tempfile cs
    save `cs'
restore
merge m:1 codinep using `cs', keep(master match) gen(mc)
di "--- CEIs que aparecem no censo2018 ---"
count if mc==3 & !missing(dt_abertura)
di "--- destes, com dt_abertura < 01jan2018 ---"
count if mc==3 & !missing(dt_abertura) & dt_abertura < mdy(1,1,2018)
di "--- fracao ---"
qui count if mc==3 & !missing(dt_abertura)
local den=r(N)
qui count if mc==3 & !missing(dt_abertura) & dt_abertura < mdy(1,1,2018)
di "  " r(N) " / " `den' " = " %6.4f r(N)/`den'

di "=== FIM diag05_A ==="
log close
