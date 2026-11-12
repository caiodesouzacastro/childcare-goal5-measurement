* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag01b.log", text replace

use "$aud\b1_2011_audit.dta", clear
di "N = " _N

di "########## B6 — não-missing por criança (famílias de variáveis por escola) ##########"
egen nm_dtcorte = rownonmiss(dt_corte_escola1-dt_corte_escola31)
egen nm_cdesc   = rownonmiss(cd_esc_encaminhamento1-cd_esc_encaminhamento31)
egen nm_escD    = rownonmiss(esc1D-esc31D)
egen nm_tratber = rownonmiss(trat_ber_20111-trat_ber_201131)
egen nm_tratber1= rowtotal(trat_ber_20111-trat_ber_201131)
sum nm_dtcorte nm_cdesc nm_escD nm_tratber nm_tratber1
di "--- dt_corte não-missing por criança (=n_escolas) ---"
tab nm_dtcorte
di "--- nº escolas com trat_ber==1 (ofertas) por criança ---"
tab nm_tratber1

di "########## B5 — variáveis candidatas de OFERTA independentes ##########"
foreach v in trat2011ber encaminhado exp_tratamento esc_trat {
    cap confirm variable `v'
    if !_rc {
        di "==== `v' ===="
        tab `v', miss
    }
    else di "==== `v' : NÃO EXISTE ===="
}
di "--- cruzamento encaminhado x trat2011ber ---"
cap tab encaminhado trat2011ber, miss
di "--- cruzamento exp_tratamento x trat2011ber ---"
cap tab exp_tratamento trat2011ber, miss
di "--- esc1D (distância à escola mais próxima, km): resumo ---"
sum esc1D dist_assigned, detail

log close
