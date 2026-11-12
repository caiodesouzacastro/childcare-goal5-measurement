* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global dsme "$NE_ROOT\dados_restritos\Dados - SME\Atual (25.06)"
global ba  "$NE_ROOT\dados_restritos\Ciro\01_dados\processados\bases_analise"
cap log close
log using "$aud\diag05_D1D2.log", text replace

*==============================================================
di "########## D1 — setor / coddist / distrito em escolassite ##########"
use "$aud\escolas_parsed.dta", clear
di "N escolas = " _N
di "--- setor: N distintos ---"
codebook setor, compact
di "--- coddist: N distintos ---"
codebook coddist, compact
di "--- distrito: N distintos ---"
egen tagd = tag(distrito)
count if tagd==1
di "--- top 15 setores por freq ---"
contract setor, freq(nesc)
gsort -nesc
list in 1/15, noobs
di "  N setores distintos (via contract) = " _N

*==============================================================
di ""
di "########## D2a — base CEP->distrito existente (cep_renda_pop_2010) ##########"
use "$ba\cep_renda_pop_2010.dta", clear
di "N linhas = " _N
di "--- nm_distrit: N distintos ---"
egen t=tag(nm_distrit)
count if t==1
di "--- cod_setor (IBGE): N distintos ---"
egen t2=tag(cod_setor)
count if t2==1
di "  (cep_renda liga cep -> nm_distrit e cod_setor IBGE)"

*==============================================================
di ""
di "########## D2b — CEP -> setor educacional pela escola MAIS PROXIMA ##########"
* escolas com coord
use "$aud\escolas_parsed.dta", clear
keep if !missing(lat,lon) & !missing(setor)
keep escola setor lat lon
rename lat elat
rename lon elon
gen clat0 = round(elat/0.02)
gen clon0 = round(elon/0.02)
expand 9
bysort escola: gen j=_n-1
gen clat = clat0 + (mod(j,3)-1)
gen clon = clon0 + (floor(j/3)-1)
keep escola setor elat elon clat clon
tempfile eg
save `eg'

use "$dsme\cepcentroide.dta", clear
rename latitude ceplat
rename longitude ceplon
gen clat = round(ceplat/0.02)
gen clon = round(ceplon/0.02)
di "N CEP = " _N
joinby clat clon using `eg'
gen double a = sin((elat-ceplat)*_pi/360)^2 + cos(ceplat*_pi/180)*cos(elat*_pi/180)*sin((elon-ceplon)*_pi/360)^2
gen double dist_km = 2*6371*asin(sqrt(a))
bysort cep (dist_km): keep if _n==1
keep cep setor dist_km
rename setor setor_cep
di "N CEP com setor atribuido (escola <=~2km 3x3) = " _N
sum dist_km, detail
save "$aud\cep_setor.dta", replace

di "=== FIM D1D2 ==="
log close
