* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag04_C2.log", text replace

use "$aud\child_counts.dta", clear
di "N = " _N
* proxy de distrito: setor do CEP (primeiros digitos) x ano de solicitacao
gen regiao = floor(cep/10000)
egen regyear = group(regiao ano_solic)
di "N regioes (setor CEP): "
codebook regiao, compact
di "N regiao#ano grupos: "
codebook regyear, compact

program define showfs
    args yv xv
    di "  coef=" _b[`xv'] "  se=" _se[`xv'] "  t=" _b[`xv']/_se[`xv'] "  N=" e(N) "  r2=" e(r2)
    test `xv'
    di "  F(instrumento) = " r(F) "  p = " r(p)
end

*==============================================================
di ""
di "########## C2 — idade_entrada ~ n_ab_1km ##########"
di "--- (1) reg idade_entrada n_ab_1km i.ano_solic i.mes_nasc ---"
reg idade_entrada n_ab_1km i.ano_solic i.mes_nasc
showfs idade_entrada n_ab_1km
di "--- (2) + FE regiao#ano (areg absorb) ---"
areg idade_entrada n_ab_1km i.mes_nasc, absorb(regyear)
showfs idade_entrada n_ab_1km

*==============================================================
di ""
di "########## C3 — espera_dias ~ n_ab_1km ##########"
di "--- (1) reg espera_dias n_ab_1km i.ano_solic i.mes_nasc ---"
reg espera_dias n_ab_1km i.ano_solic i.mes_nasc
showfs espera_dias n_ab_1km
di "--- (2) + FE regiao#ano ---"
areg espera_dias n_ab_1km i.mes_nasc, absorb(regyear)
showfs espera_dias n_ab_1km

*==============================================================
di ""
di "########## C5 — PLACEBO: aberturas 12m DEPOIS da matricula ##########"
di "--- reg idade_entrada n_post_1km i.ano_solic i.mes_nasc ---"
reg idade_entrada n_post_1km i.ano_solic i.mes_nasc
showfs idade_entrada n_post_1km
di "--- + FE regiao#ano ---"
areg idade_entrada n_post_1km i.mes_nasc, absorb(regyear)
showfs idade_entrada n_post_1km

di "=== FIM C2 ==="
log close
