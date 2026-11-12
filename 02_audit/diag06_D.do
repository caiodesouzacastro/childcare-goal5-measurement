* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global dsme "$NE_ROOT\dados_restritos\Dados - SME\Atual (25.06)"
global fila "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
cap log close
log using "$aud\diag06_D.log", text replace

*==============================================================
di "########## Base: crianca -> (cep, mes_sol, escola atribuida) 1o encaminhamento ##########"
use cd_aluno_sme dt_solicitacao dt_encaminhamento cd_esc_encaminhamento cep_aluno ///
    cd_sexo_aluno tp_raca_cor mes_nasc using "$fila", clear
gen double dt_sol = date(dt_solicitacao,"DMY hms")
gen double dt_enc = date(dt_encaminhamento,"DMY hms")
keep if !missing(dt_enc) & !missing(cd_esc_encaminhamento) & !missing(cep_aluno)
gsort cd_aluno_sme dt_enc
by cd_aluno_sme: keep if _n==1
gen ym_sol = ym(year(dt_sol),month(dt_sol))
rename cep_aluno cep
rename cd_esc_encaminhamento escola
* atributos da escola atribuida
merge m:1 escola using "$aud\escolas_parsed.dta", keepusing(tipoesc codinep) ///
    keep(master match) nogen
rename escola esc_atrib
save "$aud\d_assign.dta", replace
di "N criancas com encaminhamento = " _N

*==============================================================
di ""
di "########## D1 — rank de distancia da escola atribuida (entre CEIs <=2km) ##########"
use "$aud\d_assign.dta", clear
keep cd_aluno_sme cep esc_atrib
joinby cep using "$aud\cep_cei_pairs_novo.dta", unmatched(master)
gen byte is_assigned = (ceicode==esc_atrib)
* dist da atribuida (se estiver nos pares)
bysort cd_aluno_sme: egen dist_assigned = max(cond(is_assigned,dist_km,.))
gen byte closer = dist_km < dist_assigned
bysort cd_aluno_sme: egen rank_assigned = total(closer) if !missing(dist_assigned)
replace rank_assigned = rank_assigned + 1
bysort cd_aluno_sme: egen has_assigned = max(is_assigned)
bysort cd_aluno_sme: keep if _n==1
di "--- crianca cuja escola atribuida esta entre CEIs<=2km ---"
count if has_assigned==1
di "--- crianca cuja escola atribuida NAO esta nos pares (>2km ou sem dt_abertura) ---"
count if has_assigned==0
di "--- distribuicao do RANK de distancia da escola atribuida (1=mais proxima) ---"
gen rc = rank_assigned
replace rc = 6 if rank_assigned>=6 & !missing(rank_assigned)
tab rc

*==============================================================
di ""
di "########## D2 — celulas CEP x mes_sol com >=2 criancas: variacao de escola ##########"
use "$aud\d_assign.dta", clear
bysort cep ym_sol: gen ncel = _N
egen cellid = group(cep ym_sol)
di "--- celulas com >=2 criancas ---"
preserve
    keep if ncel>=2
    * distintas escolas por celula
    bysort cellid esc_atrib: gen firstesc = _n==1
    bysort cellid: egen nescolas = total(firstesc)
    bysort cellid: keep if _n==1
    di "  N celulas (>=2 criancas) = " _N
    gen byte variou = nescolas>=2
    di "  celulas com >=2 escolas distintas: "
    count if variou==1
    di "  % com variacao: "
    sum variou
restore

*==============================================================
di ""
di "########## D4 — desvio-padrao within-celula da qualidade da escola atribuida ##########"
use "$aud\d_assign.dta", clear
* qualidade: modalidade (tipoesc), infra do censo (in_bercario, qt_salas)
merge m:1 codinep using "$dsme\escolas\censo2018.dta", keepusing(in_bercario qt_salas_existentes) ///
    keep(master match) nogen
encode tipoesc, gen(modal)
bysort cep ym_sol: gen ncel=_N
keep if ncel>=2
egen cellid = group(cep ym_sol)
foreach v in modal in_bercario qt_salas_existentes {
    bysort cellid: egen sd_`v' = sd(`v')
    qui sum sd_`v'
    di "  SD within-celula de `v': media = " r(mean) "  (N celulas-obs)"
}
* fracao de celulas com SD>0 (variacao) em modalidade
bysort cellid: keep if _n==1
gen byte var_modal = sd_modal>0 & !missing(sd_modal)
sum var_modal

di "=== FIM D ==="
log close
