* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
global bruto "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera"
global amost "$NE_ROOT\dados_restritos\Ciro\01_dados\processados\amostra_rdd\Fila1018_amostraRDD.dta"

log using "$NE_ROOT\02_audit\_describe.log", text replace

di "==================== trat2011ber.dta (Ciro bruto) ===================="
use "$bruto\trat2011ber.dta", clear
di "N obs = " _N
di "N vars = " c(k)
ds
di "---- describe (short) ----"
describe, short

di "==================== varlist detail: esc / dt_corte / cd_esc / trat ===================="
foreach stub in esc dt_corte cd_esc trat trat_ber trat2011 dt_solic cd_aluno {
    di "---- vars matching *`stub'* ----"
    ds *`stub'*,
}

di "==================== D: copy trat2011ber.dta ===================="
use "$NE_ROOT\dados_restritos\Dados - SME\Atual (25.06)\trat2011ber.dta", clear
di "N obs = " _N
di "N vars = " c(k)
describe, short

di "==================== amostra RDD final ===================="
use "$amost", clear
di "N obs = " _N
di "N vars = " c(k)
describe, short

log close
