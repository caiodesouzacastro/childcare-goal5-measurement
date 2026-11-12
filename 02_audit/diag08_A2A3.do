* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global dsme "$NE_ROOT\dados_restritos\Dados - SME\Atual (25.06)"
cap log close
log using "$aud\diag08_A2A3.log", text replace

*==============================================================
di "########## A4 — variavel que identifique ANO da RAIS (alem de 'ano') ##########"
use "$dsme/cpf_fila_14.dta" in 1, clear
di "  vars candidatas em cpf_fila_14:"
cap ds *ano* *base* *compet* *rais* *ref*
di "  --- em cpf_fila_11 ---"
use "$dsme/cpf_fila_11.dta" in 1, clear
cap ds *ano* *base* *compet* *rais* *ref*

*==============================================================
di ""
di "########## A2/A3 — cpf_fila_11 vs cpf_fila_14: mesma crianca, valores iguais? ##########"
* carregar 11 (cpf so p/ indice; nomes acentuados)
use cd_aluno_sme cpf vlremunmédianom tempoemprego vínculoativo3112 ///
    using "$dsme/cpf_fila_11.dta", clear
gen byte src=11
tempfile t11
save `t11'
use cd_aluno_sme cpf vlremunmédianom tempoemprego vínculoativo3112 ///
    using "$dsme/cpf_fila_14.dta", clear
gen byte src=14
append using `t11'
* indice local do responsavel
egen long respid = group(cpf)
drop cpf
destring vlremunmédianom, gen(remun) force dpcomma
destring tempoemprego, gen(tempo) force dpcomma
rename vínculoativo3112 vinc
* 1 registro por (crianca, resp, arquivo): pegar vinculo principal (maior remun)
gsort cd_aluno_sme respid src -remun
by cd_aluno_sme respid src: keep if _n==1
keep cd_aluno_sme respid src remun tempo vinc
reshape wide remun tempo vinc, i(cd_aluno_sme respid) j(src)
di "--- A2: interseccao e uniao (crianca-responsavel) ---"
count
di "  N pares (crianca,resp) totais (uniao) = " r(N)
count if !missing(remun11) & !missing(remun14)
di "  N em AMBOS (interseccao 11 e 14) = " r(N)
* interseccao a nivel de CRIANCA
preserve
    gen byte in11 = !missing(remun11)
    gen byte in14 = !missing(remun14)
    collapse (max) in11 in14, by(cd_aluno_sme)
    count
    di "  criancas distintas (uniao) = " r(N)
    count if in11==1 & in14==1
    di "  criancas em ambos = " r(N)
    count if in11==1
    di "  criancas em cpf_fila_11 = " r(N)
    count if in14==1
    di "  criancas em cpf_fila_14 = " r(N)
restore

di ""
di "--- A3: fracao com valores DIFERENTES entre 11 e 14 (pares em ambos) ---"
keep if !missing(remun11) & !missing(remun14)
di "  N pares comparaveis = " _N
gen byte dif_remun = abs(remun11-remun14) > 0.001 if !missing(remun11,remun14)
gen byte dif_tempo = abs(tempo11-tempo14) > 0.001 if !missing(tempo11,tempo14)
gen byte dif_vinc  = vinc11 != vinc14 if !missing(vinc11,vinc14)
sum dif_remun dif_tempo dif_vinc
di "  --- % diferentes ---"
foreach v in dif_remun dif_tempo dif_vinc {
    qui sum `v'
    di "    `v': " %6.4f r(mean) "  (N=" r(N) ")"
}

di "=== FIM A2A3 ==="
log close
