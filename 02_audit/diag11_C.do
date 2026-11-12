* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global fila "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
cap log close
log using "$aud\diag11_C.log", text replace

*==============================================================
di "########## Preparar eventos e niveis de capacidade (perfil) ##########"
import delimited "$aud\esc_sem_cap.csv", clear varnames(1) case(preserve)
destring codesc, replace force
* delta vs semestre anterior (por escola), so consecutivos
sort codesc sidx
by codesc: gen delta_berc = cap_berc - cap_berc[_n-1] if sidx==sidx[_n-1]+1
by codesc: gen delta_cre  = cap_creche - cap_creche[_n-1] if sidx==sidx[_n-1]+1
* data do evento = snapshot do semestre s1: sem1->30jun(ano), sem2->31dez(ano)
gen ano = floor(sidx/2)
gen sem = mod(sidx,2)+1
gen event_date = mdy(6,30,ano) if sem==1
replace event_date = mdy(12,31,ano) if sem==2
format event_date %td
* niveis (para cap_base): data de referencia do semestre
gen level_date = event_date
save "$aud\cap_full.dta", replace
* arquivo de eventos (mudancas >=7 na creche)
preserve
    keep if !missing(delta_cre) & abs(delta_cre)>=7
    keep codesc event_date delta_cre delta_berc
    rename codesc ceicode
    save "$aud\cap_events.dta", replace
    di "N eventos de capacidade (|delta|>=7) = " _N
restore
* niveis por escola-semestre (para cap_base)
keep codesc sidx cap_creche cap_berc level_date
rename codesc ceicode
save "$aud\cap_levels.dta", replace

*==============================================================
di ""
di "########## Universo: 1a solicitacao Bercario (idade<23m), coortes 2013-2018 ##########"
use cd_aluno_sme dt_solicitacao dt_encaminhamento dt_matricula cep_aluno ano_nasc mes_nasc ///
    cd_sexo_aluno tp_raca_cor cd_serie_ensino_solicitacao tipo_prioridade_encaminhamento ///
    using "$fila", clear
gen double dt_sol = date(dt_solicitacao,"DMY hms")
keep if !missing(dt_sol) & !missing(cep_aluno)
gsort cd_aluno_sme dt_sol
by cd_aluno_sme: keep if _n==1
gen double dt_enc = date(dt_encaminhamento,"DMY hms")
gen double dt_mat = date(dt_matricula,"DMY hms")
gen idade_sol = (year(dt_sol)-ano_nasc)*12 + (month(dt_sol)-mes_nasc)
keep if inrange(idade_sol,0,22)          /* Bercario I/II */
gen anosol = year(dt_sol)
keep if inrange(anosol,2013,2018)
keep if missing(tipo_prioridade_encaminhamento)
gen byte feminino = cd_sexo_aluno=="F"
gen byte branco = tp_raca_cor==1
* semestre da solicitacao
gen sol_sidx = year(dt_sol)*2 + (month(dt_sol)>6)
di "N criancas Bercario (1a sol, sem prioridade, 2013-2018) = " _N
* desfechos
gen espera = dt_enc - dt_sol if !missing(dt_enc)
gen byte enc180 = (!missing(dt_enc) & dt_enc<=dt_sol+180)
gen idade_entrada = (year(dt_mat)-ano_nasc)*12 + (month(dt_mat)-mes_nasc) if !missing(dt_mat)
replace idade_entrada=. if !inrange(idade_entrada,0,48)
gen byte mat365 = (!missing(dt_mat) & dt_mat<=dt_sol+365)
rename cep_aluno cep
compress
save "$aud\berc_child.dta", replace

*==============================================================
di ""
di "########## C1 — conjunto elegivel (CEIs <=2km) ##########"
joinby cep using "$aud\cep_cei_pairs_novo.dta", unmatched(master)
gen byte tem_par = !missing(dist_km)
* tamanho do conjunto elegivel por crianca
preserve
    keep if tem_par
    bysort cd_aluno_sme: gen nelig = _N
    by cd_aluno_sme: keep if _n==1
    di "--- tamanho do conjunto elegivel (CEIs <=2km) ---"
    sum nelig, detail
restore

*==============================================================
di ""
di "########## C2 — choques e cap_base no conjunto elegivel ##########"
* cap_base: nivel de capacidade Bercario dos CEIs elegiveis no semestre da solicitacao
rename ceicode ceicode_pair
gen ceicode = ceicode_pair
cap confirm variable sol_sidx
if _rc gen sol_sidx = year(dt_sol)*2 + (month(dt_sol)>6)
rename sol_sidx sidx
merge m:1 ceicode sidx using "$aud\cap_levels.dta", ///
    keep(master match) keepusing(cap_berc) nogen
gen capb = cap_berc
* eventos nos CEIs elegiveis: janelas
* juntar todos os eventos daquele CEI (m:m por ceicode)
* -> mais eficiente: para cada par crianca-CEI, somar deltas por janela via merge com eventos
* Faremos por reshape/collapse: primeiro guardar pares
keep cd_aluno_sme ceicode dt_sol capb
save "$aud\child_cei.dta", replace
* juntar eventos (um CEI pode ter varios eventos)
joinby ceicode using "$aud\cap_events.dta", unmatched(master)
gen rel = event_date - dt_sol
* janelas
gen neg180 = -delta_cre if !missing(delta_cre) & delta_cre<0 & inrange(rel,0,180)
gen pos180 =  delta_cre if !missing(delta_cre) & delta_cre>0 & inrange(rel,0,180)
gen neg_pre = -delta_cre if !missing(delta_cre) & delta_cre<0 & inrange(rel,-180,-1)   /* placebo pre */
gen neg_fut = -delta_cre if !missing(delta_cre) & delta_cre<0 & inrange(rel,366,545)   /* placebo futuro */
collapse (sum) choque_neg=neg180 choque_pos=pos180 choque_pre=neg_pre choque_fut=neg_fut (max) capb2=capb, by(cd_aluno_sme)
save "$aud\child_shock_cei.dta", replace
* cap_base por crianca = soma de capb dos CEIs elegiveis
use "$aud\child_cei.dta", clear
collapse (sum) cap_base=capb, by(cd_aluno_sme)
merge 1:1 cd_aluno_sme using "$aud\child_shock_cei.dta", nogen
foreach v in choque_neg choque_pos choque_pre choque_fut { replace `v'=0 if missing(`v') }
save "$aud\child_shock.dta", replace

* juntar aos desfechos
use "$aud\berc_child.dta", clear
merge 1:1 cd_aluno_sme using "$aud\child_shock.dta", keep(master match) nogen
foreach v in choque_neg choque_pos choque_pre choque_fut cap_base { replace `v'=0 if missing(`v') }
compress
save "$aud\berc_design.dta", replace
di "N final design = " _N
di "--- distribuicao dos choques ---"
sum choque_neg choque_pos choque_pre choque_fut cap_base, detail
di "--- fracao com choque_neg>0 / choque_pos>0 ---"
count if choque_neg>0
count if choque_pos>0
di "--- C3: excluir 2017 ---"
count if anosol==2017
di "  (criancas com solicitacao em 2017)"

di "=== FIM C ==="
log close
