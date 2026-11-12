* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud  "$NE_ROOT\02_audit"
global dsme "$NE_ROOT\dados_restritos\Dados - SME\Atual (25.06)"
global fila "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
cap log close
log using "$aud\diag04_A.log", text replace

*==============================================================
di "########## Códigos de escola presentes em Fila1018 ##########"
use cd_esc_encaminhamento cd_esc_matricula using "$fila", clear
di "N linhas Fila = " _N
preserve
    keep cd_esc_encaminhamento
    rename cd_esc_encaminhamento codesc
    drop if missing(codesc)
    tempfile a
    save `a'
restore
keep cd_esc_matricula
rename cd_esc_matricula codesc
drop if missing(codesc)
append using `a'
keep codesc
duplicates drop
di "N códigos distintos (enc+mat) em Fila = " _N
save "$aud\fila_codesc.dta", replace

*==============================================================
di ""
di "########## A parsing de escolassite ##########"
use "$dsme\escolas\escolassite.dta", clear
di "N=" _N

* --- parse datas str (DD/MM/YYYY) ---
foreach d in dt_criacao dt_ini_func dt_ini_conv dt_autoriza {
    gen `d'_d = date(`d', "DMY")
    format `d'_d %td
}
* --- parse coordenadas (separadores de milhar; parte inteira 2 dígitos) ---
foreach c in latitude longitude {
    gen `c'_s = subinstr(`c', ".", "", .)
    gen neg = strpos(`c'_s,"-")>0
    replace `c'_s = subinstr(`c'_s,"-","",.)
    gen double `c'_n = real(`c'_s) / (10^(strlen(`c'_s)-2))
    replace `c'_n = -`c'_n if neg==1
    drop neg `c'_s
}
rename latitude_n lat
rename longitude_n lon

* --- flag CEI ---
gen byte cei = inlist(tipoesc,"CEI DIRET","CEI INDIR","CEU CEI","CR.P.CONV","CEMEI","CCI/CIPS")

save "$aud\escolas_parsed.dta", replace

*==============================================================
di ""
di "########## A2 — datas de criação/inauguração ##########"
foreach d in dt_criacao_d dt_ini_func_d dt_ini_conv_d {
    di "==== `d' ===="
    qui count if !missing(`d')
    di "  N nao-missing = " r(N)
    sum `d'
    di "  min = " %td r(min) "   max = " %td r(max)
    gen yr_`d' = year(`d')
    di "  --- distribuicao por ano (2005-2018) ---"
    tab yr_`d' if inrange(yr_`d',2005,2018)
}

*==============================================================
di ""
di "########## A3 — tipo de unidade ##########"
tab tipoesc, miss
di "--- CEI (flag) por tipoesc ---"
tab tipoesc cei, miss
di "--- total CEI ---"
count if cei==1

*==============================================================
di ""
di "########## A5 — sanidade das coordenadas ##########"
sum lat lon, detail
gen byte fora_sp = !(inrange(lat,-24.1,-23.3) & inrange(lon,-46.9,-46.3))
di "--- coord non-missing ---"
count if !missing(lat,lon)
di "--- fora do retangulo de SP (entre as non-missing) ---"
count if !missing(lat,lon) & fora_sp==1
di "--- dentro do retangulo ---"
count if !missing(lat,lon) & fora_sp==0

*==============================================================
di ""
di "########## A4 — CEIs com criacao 2008-2016 + coord + casa com Fila ##########"
gen long codesc = escola
merge m:1 codesc using "$aud\fila_codesc.dta", gen(mfila)
* mfila==2 sao codigos do Fila sem cadastro em escolassite; remover para nao contaminar
drop if mfila==2
gen byte in_fila = (mfila==3)

di "--- usando dt_criacao ---"
count if cei==1 & inrange(year(dt_criacao_d),2008,2016) & !missing(lat,lon) & in_fila==1
di "--- usando dt_ini_func ---"
count if cei==1 & inrange(year(dt_ini_func_d),2008,2016) & !missing(lat,lon) & in_fila==1
di "--- (sem exigir casar com Fila) dt_criacao ---"
count if cei==1 & inrange(year(dt_criacao_d),2008,2016) & !missing(lat,lon)
di "--- quantos CEI casam com Fila (qualquer data) ---"
count if cei==1 & in_fila==1

di "=== FIM diag04_A ==="
log close
