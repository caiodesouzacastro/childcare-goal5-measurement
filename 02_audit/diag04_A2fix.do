* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag04_A2fix.log", text replace

use "$aud\escolas_parsed.dta", clear
di "N=" _N

di "===== diagnostico de tipoesc (comprimento e valores entre aspas) ====="
gen L = strlen(tipoesc)
tab L
levelsof tipoesc, local(lv)
foreach t of local lv {
    di "valor=[`t']"
}

di ""
di "===== reconstruindo flag CEI (strpos robusto) ====="
cap drop cei
gen byte cei = (strpos(tipoesc,"CEI")>0 | strpos(tipoesc,"CR.P")>0 | strpos(tipoesc,"CEMEI")>0 | strpos(tipoesc,"CCI")>0)
di "--- A3: tipoesc x cei ---"
tab tipoesc cei, miss
di "--- total CEI ---"
count if cei==1
di "--- CEI por tipo (contagem) ---"
tab tipoesc if cei==1

di ""
di "===== A4 (refeito) ====="
gen long codesc = escola
merge m:1 codesc using "$aud\fila_codesc.dta", gen(mfila)
drop if mfila==2
gen byte in_fila = (mfila==3)
di "CEI total: "
count if cei==1
di "CEI com coord: "
count if cei==1 & !missing(lat,lon)
di "CEI com coord & casa Fila: "
count if cei==1 & !missing(lat,lon) & in_fila==1
di ""
di "--- A4 dt_criacao 2008-2016 + coord + Fila (NUMERO CRITICO) ---"
count if cei==1 & inrange(year(dt_criacao_d),2008,2016) & !missing(lat,lon) & in_fila==1
di "--- idem dt_ini_func ---"
count if cei==1 & inrange(year(dt_ini_func_d),2008,2016) & !missing(lat,lon) & in_fila==1
di "--- idem dt_ini_conv ---"
count if cei==1 & inrange(year(dt_ini_conv_d),2008,2016) & !missing(lat,lon) & in_fila==1
di "--- CEI dt_criacao 2008-2016 + coord (sem exigir Fila) ---"
count if cei==1 & inrange(year(dt_criacao_d),2008,2016) & !missing(lat,lon)
di ""
di "--- distribuicao por ano (dt_criacao) SOMENTE CEI que casam com Fila e tem coord ---"
tab yr_dt_criacao_d if cei==1 & in_fila==1 & !missing(lat,lon) & inrange(yr_dt_criacao_d,2005,2018)

di "=== FIM ==="
log close
