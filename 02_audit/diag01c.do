* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag01c.log", text replace

use "$aud\b1_2011_audit.dta", clear

* rvar mínimo NÃO-NEGATIVO por criança (regra que o PAPER afirma)
gen rvar_min_nonneg = .
forvalues i = 1/31 {
    cap gen double _r`i' = dt_corte_escola`i' - dt_sol
    cap replace rvar_min_nonneg = min(cond(missing(rvar_min_nonneg),1e12,rvar_min_nonneg), _r`i') ///
        if _r`i' >= 0 & !missing(_r`i')
}
replace rvar_min_nonneg = . if rvar_min_nonneg >= 1e11

* rvar do CÓDIGO (já na base) = rvar
di "########## TESTE: regra do código vs regra do paper (min rvar>=0) ##########"
di "--- Entre TRATADOS (t==1): rvar_codigo == rvar_min_nonneg ? ---"
count if t==1
count if t==1 & !missing(rvar) & !missing(rvar_min_nonneg)
gen byte igual = (abs(rvar - rvar_min_nonneg) < 0.5) if t==1 & !missing(rvar) & !missing(rvar_min_nonneg)
tab igual if t==1
di "--- casos em que diferem (rvar_codigo != min nao-negativo) ---"
count if t==1 & igual==0
list cd_aluno_sme rvar rvar_min_nonneg _idx if t==1 & igual==0 in 1/20, noobs

di "--- distribuição da diferença (rvar_codigo - rvar_min_nonneg) entre tratados ---"
gen dif = rvar - rvar_min_nonneg if t==1
sum dif, detail

di "########## CONTROLES: o paper não define rvar>=0; o código atribui rvar<0 ##########"
count if t==0 & !missing(rvar)
count if t==0 & missing(rvar_min_nonneg)
di "controles com rvar (código) atribuído mas SEM nenhum rvar>=0 (indefinido no paper): "
count if t==0 & !missing(rvar) & missing(rvar_min_nonneg)

log close
