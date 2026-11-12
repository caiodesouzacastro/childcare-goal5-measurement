* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud  "$NE_ROOT\02_audit"
global fila "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
cap log close
log using "$aud\diag02_partC.log", text replace

*==============================================================
di "########## Construindo universo de ENCAMINHADOS 2011 Ber I ##########"
di "Filtros (replicando dataencaminhamentopico_0607_2.do, EXCETO exclusao de escola especifica):"
di "  tipo_prioridade_encaminhamento==. ; serie_aluno==1 (cod 1/2/3) ;"
di "  an_letivo_encaminhamento==2011 ; dt_encaminhamento<=31dec2010"
use "$fila", clear
di "N total Fila1018 = " _N
gen serie_aluno = .
replace serie_aluno = 1 if inlist(cd_serie_ensino_encaminhamento,1,2,3)
gen double dt_sol = date(dt_solicitacao, "DMY hms")
gen double dt_enc = date(dt_encaminhamento, "DMY hms")
keep if tipo_prioridade_encaminhamento==.
keep if serie_aluno==1
keep if an_letivo_encaminhamento==2011
keep if !missing(dt_enc) & dt_enc <= mdy(12,31,2010)
keep if !missing(cd_esc_encaminhamento) & !missing(dt_sol)
di "N linhas no universo = " _N
di "N criancas distintas = "
codebook cd_aluno_sme, compact

* por (escola, crianca): ultima solicitacao
collapse (max) dt_sol_child = dt_sol, by(cd_esc_encaminhamento cd_aluno_sme)
* estatisticas por escola: n, max1, argmax, max2
gsort cd_esc_encaminhamento -dt_sol_child
by cd_esc_encaminhamento: gen long nchild = _N
by cd_esc_encaminhamento: gen double s_max1 = dt_sol_child[1]
by cd_esc_encaminhamento: gen long   s_alu1 = cd_aluno_sme[1]
by cd_esc_encaminhamento: gen double s_max2 = dt_sol_child[2]
by cd_esc_encaminhamento: keep if _n==1
keep cd_esc_encaminhamento nchild s_max1 s_alu1 s_max2
format s_max1 s_max2 %td
save "$aud\school_stats_2011ber.dta", replace

*==============================================================
di ""
di "########## C1 — nº de encaminhados por escola (2011 Ber I) ##########"
use "$aud\school_stats_2011ber.dta", clear
di "N escolas com >=1 encaminhado = " _N
sum nchild, detail
di "--- percentis via tabstat ---"
tabstat nchild, stat(n min p25 p50 p75 max mean sd) col(stat)
count if nchild>=2
di "  escolas com >=2: " r(N)
count if nchild>=5
di "  escolas com >=5: " r(N)
count if nchild>=10
di "  escolas com >=10: " r(N)

*==============================================================
di ""
di "########## C2 — pares crianca-escola com corte_LOO definido ##########"
use "$aud\b1_2011_audit.dta", clear
keep cd_aluno_sme dt_sol esc_trat dt_matricula an_letivo_matricula ///
     cd_esc_encaminhamento1-cd_esc_encaminhamento31 dt_corte_escola1-dt_corte_escola31
* reshape long sobre as 31 escolas vinculadas por distancia
reshape long cd_esc_encaminhamento dt_corte_escola, i(cd_aluno_sme) j(k)
rename cd_esc_encaminhamento cd_esc_link
* merge estatisticas da escola
rename cd_esc_link cd_esc_encaminhamento
merge m:1 cd_esc_encaminhamento using "$aud\school_stats_2011ber.dta", keep(master match) gen(mrg)
* corte_LOO = max entre encaminhados != i
gen double corte_loo = .
replace corte_loo = s_max1 if mrg==3 & s_alu1 != cd_aluno_sme
replace corte_loo = s_max2 if mrg==3 & s_alu1 == cd_aluno_sme
format corte_loo %td
di "--- pares (i, escola vinculada) totais (k=1..31, escola nao-missing) ---"
count if !missing(cd_esc_encaminhamento)
di "--- pares com escola no universo de encaminhados (merge==3) ---"
count if mrg==3
di "--- pares com corte_LOO definido ---"
count if !missing(corte_loo)
* validacao: stored dt_corte_escola vs meu s_max1 (quando i nao e o argmax)
gen difcorte = dt_corte_escola - s_max1 if mrg==3
di "--- validacao stored dt_corte_escola == s_max1 (dias de diferenca) ---"
sum difcorte, detail
save "$aud\loo_long.dta", replace

*==============================================================
di ""
di "########## C3 — rvar_loo fixando a escola mais proxima (esc1, k==1) ##########"
use "$aud\loo_long.dta", clear
keep if k==1
gen double rvar_loo = corte_loo - dt_sol
di "N rvar_loo nao-missing = "
count if !missing(rvar_loo)
sum rvar_loo, detail
gen rvar_loo_int = round(rvar_loo)
di "--- contagem por inteiro em [-10,10] ---"
tab rvar_loo_int if inrange(rvar_loo_int,-10,10), miss
di "--- quantas em rvar_loo == 0 ---"
count if rvar_loo_int==0 & !missing(rvar_loo)
* preparar base child-level para C4/C5/C6
gen esc_trat_nm = !missing(esc_trat)
gen double dt_mat = date(dt_matricula,"DMY hms")
gen mat_nm = !missing(dt_mat)
keep cd_aluno_sme rvar_loo esc_trat_nm mat_nm
save "$aud\loo_child.dta", replace

*==============================================================
di ""
di "########## C4 — primeiro estagio bruto por faixas de rvar_loo ##########"
use "$aud\loo_child.dta", clear
gen faixa = .
replace faixa = 1 if inrange(rvar_loo,-60,-31)
replace faixa = 2 if inrange(rvar_loo,-30,-11)
replace faixa = 3 if inrange(rvar_loo,-10,-1)
replace faixa = 4 if inrange(rvar_loo,0,10)
replace faixa = 5 if inrange(rvar_loo,11,30)
replace faixa = 6 if inrange(rvar_loo,31,60)
label define fx 1 "[-60,-31]" 2 "[-30,-11]" 3 "[-10,-1]" 4 "[0,10]" 5 "[11,30]" 6 "[31,60]"
label values faixa fx
di "--- N e taxa de esc_trat (encaminhamento observado) por faixa ---"
table faixa, stat(count esc_trat_nm) stat(mean esc_trat_nm)
di "--- N e taxa de matricula (dt_matricula nao-missing) por faixa ---"
table faixa, stat(count mat_nm) stat(mean mat_nm)

*==============================================================
di ""
di "########## C5 — rdrobust primeiro estagio com rvar_loo ##########"
di "--- DEP: esc_trat_nm ---"
cap rdrobust esc_trat_nm rvar_loo, c(0) kernel(triangular) bwselect(mserd)
if !_rc di "esc_trat_nm: tau_cl=" e(tau_cl) " se_rb=" e(se_tau_rb) " p_rb=" e(pv_rb) " h=" e(h_l) " Nl=" e(N_h_l) " Nr=" e(N_h_r)
else di "  ERRO rc=`=_rc'"
di "--- DEP: mat_nm ---"
cap rdrobust mat_nm rvar_loo, c(0) kernel(triangular) bwselect(mserd)
if !_rc di "mat_nm: tau_cl=" e(tau_cl) " se_rb=" e(se_tau_rb) " p_rb=" e(pv_rb) " h=" e(h_l) " Nl=" e(N_h_l) " Nr=" e(N_h_r)
else di "  ERRO rc=`=_rc'"

*==============================================================
di ""
di "########## C6 — rddensity rvar_loo ##########"
cap rddensity rvar_loo, c(0)
if !_rc di "rddensity: T=" e(T_q) "  p=" e(pv_q)
else di "  ERRO rc=`=_rc'"

di "=== FIM diag02_partC ==="
log close
