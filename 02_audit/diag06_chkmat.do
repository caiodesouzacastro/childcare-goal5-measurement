* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global ba "$NE_ROOT\dados_restritos\Ciro\01_dados\processados\bases_analise"
cap log close
log using "$NE_ROOT\02_audit\diag06_chkmat.log", text replace
di "===== matriculas_2018.dta (1 obs) ====="
use "$ba\matriculas_2018.dta" in 1, clear
di "N vars = " c(k)
ds
di "--- describe (procurar serie/ano/aluno) ---"
ds *serie* *aluno* *ano* *nasc* *nivel* *etapa* cd_*
log close
