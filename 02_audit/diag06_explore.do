* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global dsme "$NE_ROOT\dados_restritos\Dados - SME\Atual (25.06)"
global ba  "$NE_ROOT\dados_restritos\Ciro\01_dados\processados\bases_analise"
global fila "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
cap log close
log using "$aud\diag06_explore.log", text replace

di "########## Fila: codigos de serie e vars de pessoa ##########"
use "$fila" in 1, clear
ds
di "--- serie de matricula / encaminhamento existem? sexo/raca/cpf_resp ---"

use cd_serie_ensino_matricula cd_serie_ensino_encaminhamento cd_sexo_aluno tp_raca_cor cpf_resp_aluno using "$fila", clear
di "--- tab cd_serie_ensino_matricula ---"
tab cd_serie_ensino_matricula, miss
di "--- tab cd_sexo_aluno ---"
tab cd_sexo_aluno, miss
di "--- tab tp_raca_cor ---"
tab tp_raca_cor, miss
di "--- cpf_resp_aluno: N nao-missing, N distintos ---"
count if !missing(cpf_resp_aluno) & cpf_resp_aluno>0
preserve
    keep cpf_resp_aluno
    keep if !missing(cpf_resp_aluno) & cpf_resp_aluno>0
    duplicates drop
    di "  CPF resp distintos = " _N
restore

di ""
di "########## cpf_fila_14.dta (maior) — estrutura ##########"
use "$dsme\cpf_fila_14.dta" in 1, clear
di "vars:"
ds
di "--- describe completo ---"
describe, fullnames

di "=== FIM explore ==="
log close
