* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
cap log close
log using "$NE_ROOT\02_audit\_chkfila.log", text replace
* Fila completo usado pelo pipeline (Ciro brutos)
use "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta" in 1, clear
di "Fila1018 (Ciro brutos) — 1 obs; vars:"
ds
di "--- tipos das chaves ---"
foreach v in cd_aluno_sme cd_esc_encaminhamento an_letivo_encaminhamento cd_serie_ensino_encaminhamento tipo_prioridade_encaminhamento dt_solicitacao dt_encaminhamento {
    cap confirm variable `v'
    if !_rc { local ty : type `v'; di "  `v' : `ty'" }
    else di "  `v' : NAO EXISTE"
}
log close
