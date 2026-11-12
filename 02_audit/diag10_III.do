* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global fila "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
cap log close
log using "$aud\diag10_III.log", text replace

*==============================================================
di "########## exportar codigos de escola da Fila (para II3) ##########"
use "$aud\fila_codesc.dta", clear
export delimited codesc using "$aud\fila_codesc.csv", replace
di "N codigos Fila exportados = " _N

*==============================================================
di ""
di "########## III1 — variaveis de protocolo/ordem/classificacao na Fila ##########"
use "$fila" in 1, clear
di "--- busca por protocol/ordem/classif/posic/rank/numero/inscri/sequenc ---"
foreach p in protoc ordem classif posic rank numer inscri sequenc fila prior data {
    di "  *`p'*:"
    cap ds *`p'*
}
di "--- lista completa de variaveis do Fila ---"
ds

*==============================================================
di ""
di "########## III2 — empates de dt_solicitacao dentro de escola-serie ##########"
use cd_aluno_sme dt_solicitacao cd_esc_encaminhamento an_letivo_encaminhamento cd_serie_ensino_encaminhamento tipo_prioridade_encaminhamento dt_encaminhamento using "$fila", clear
gen double dt_sol = date(dt_solicitacao,"DMY hms")
gen double dt_enc = date(dt_encaminhamento,"DMY hms")
* faixa etaria (creche): cod 1,2,3 e 4,5,6, 27, 28 etc. Uso o cd_serie diretamente
keep if !missing(dt_enc) & !missing(cd_esc_encaminhamento) & missing(tipo_prioridade_encaminhamento)
keep if inlist(cd_serie_ensino_encaminhamento,1,4,27,28)  /* Berc I, Berc II, Mini I, Mini II aprox */
di "N encaminhamentos creche (sem prioridade) = " _N
* empates de dt_sol dentro de escola x serie x ano
egen cell = group(cd_esc_encaminhamento cd_serie_ensino_encaminhamento an_letivo_encaminhamento)
duplicates tag cell dt_sol, gen(emp)
di "--- fracao de encaminhamentos com dt_sol EMPATADO na celula escola-serie-ano ---"
gen byte empatado = emp>0
sum empatado
* granularidade: dt_solicitacao tem hora? checar se date() perde info
di "--- amostra de dt_solicitacao (string) ---"
list dt_solicitacao in 1/5, noobs

*==============================================================
di ""
di "########## III3 — ordem de solicitacao vs ordem de encaminhamento ##########"
* dentro de escola-serie-ano: rank por dt_sol vs rank por dt_enc
bysort cell (dt_sol): gen rank_sol = _n
bysort cell (dt_enc): gen rank_enc = _n
bysort cell: gen ncell = _N
* so celulas com >=5 crianças
preserve
    keep if ncell>=5
    corr rank_sol rank_enc
    di "  correlacao rank_sol x rank_enc (celulas >=5) = " r(rho)
    * fracao de inversoes: pares onde ordem de sol != ordem de enc
    gen byte concord = (dt_sol<dt_sol[_n+1] & dt_enc<dt_enc[_n+1]) if cell==cell[_n+1]
    qui sum concord
    di "  (concordancia media entre pares consecutivos por dt_sol) = " r(mean)
restore

di "=== FIM III ==="
log close
