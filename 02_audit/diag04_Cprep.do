* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud  "$NE_ROOT\02_audit"
global dsme "$NE_ROOT\dados_restritos\Dados - SME\Atual (25.06)"
cap log close
log using "$aud\diag04_Cprep.log", text replace

*==============================================================
di "########## CEI openings (dt_criacao como data de abertura) ##########"
use "$aud\escolas_parsed.dta", clear
cap drop cei
gen byte cei = (strpos(tipoesc,"CEI")>0 | strpos(tipoesc,"CR.P")>0 | strpos(tipoesc,"CEMEI")>0 | strpos(tipoesc,"CCI")>0)
keep if cei==1 & !missing(lat,lon) & !missing(dt_criacao_d)
di "N CEI com coord e data de criacao = " _N
rename escola ceicode
rename lat ceilat
rename lon ceilon
gen double ceiopen = dt_criacao_d
format ceiopen %td
keep ceicode ceilat ceilon ceiopen
save "$aud\cei_openings.dta", replace
di "  distribuicao por ano de abertura (todas):"
gen yr=year(ceiopen)
tab yr if inrange(yr,2005,2018)

*==============================================================
di ""
di "########## Grade: expandir CEI para 3x3 celulas (0.02 deg ~2km) ##########"
use "$aud\cei_openings.dta", clear
gen clat0 = round(ceilat/0.02)
gen clon0 = round(ceilon/0.02)
expand 9
bysort ceicode: gen j=_n-1
gen clat = clat0 + (mod(j,3)-1)
gen clon = clon0 + (floor(j/3)-1)
keep ceicode ceilat ceilon ceiopen clat clon
save "$aud\cei_grid.dta", replace

*==============================================================
di ""
di "########## CEP centroides + join por celula ##########"
use "$dsme\cepcentroide.dta", clear
rename latitude ceplat
rename longitude ceplon
gen clat = round(ceplat/0.02)
gen clon = round(ceplon/0.02)
di "N CEP = " _N
joinby clat clon using "$aud\cei_grid.dta"
di "N pares (mesma celula/vizinhas) = " _N
* haversine km
gen double a = sin((ceilat-ceplat)*_pi/360)^2 + cos(ceplat*_pi/180)*cos(ceilat*_pi/180)*sin((ceilon-ceplon)*_pi/360)^2
gen double dist_km = 2*6371*asin(sqrt(a))
keep if dist_km <= 2
di "N pares com dist<=2km = " _N
keep cep ceicode ceiopen dist_km
save "$aud\cep_cei_pairs.dta", replace

di ""
di "########## distribuicao de CEIs (<=2km) por CEP ##########"
bysort cep: gen n=_N
by cep: keep if _n==1
sum n, detail
di "N CEP com >=1 CEI <=2km = " _N

di "=== FIM Cprep ==="
log close
