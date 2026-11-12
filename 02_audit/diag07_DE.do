* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag07_DE.log", text replace

*==============================================================
di "########## PARTE D — desfechos de trabalho (RAIS e' SECAO TRANSVERSAL: 1 ano/crianca) ##########"
di "########## D1 — taxa de emp por ano sobre TODO B_novo (nao-RAIS=0) ##########"
use cd_aluno_sme using "$aud\B_novo.dta", clear
gen byte inbnovo=1
merge 1:m cd_aluno_sme using "$aud\rais_panel.dta", keep(master match) nogen
di "  N B_novo (total) = "
egen tag=tag(cd_aluno_sme)
count if tag==1
scalar NB = r(N)
di "  (denominador D1 = todo B_novo)"
forvalues t=2010/2018 {
    qui count if ano==`t' & emp==1
    di "  ano `t': emp_t medio (sobre B_novo) = " %6.4f r(N)/NB "   (N emp=`r(N)')"
}
di "  --- distribuicao do UNICO ano RAIS por crianca (entre com RAIS) ---"
tab ano if !missing(ano) & inrange(ano,2010,2018)

*==============================================================
di ""
di "########## D2 — event study cru: emp por tempo relativo (ano_rais - ano_nasc) ##########"
use "$aud\rais_panel.dta", clear
merge m:1 cd_aluno_sme using "$aud\B_novo.dta", keep(match) keepusing(mes_nasc) nogen
keep if inrange(ano_nasc,2009,2015)
gen reltime = ano - ano_nasc
di "--- range de reltime (min/max) — ha tempo negativo (pre-parto)? ---"
sum reltime
gen grp = cond(mes_nasc<=3,"marco",cond(mes_nasc>=4,"abril",""))
di "--- taxa de emp por reltime (marco) ---"
table reltime if mes_nasc==3 & inrange(reltime,-3,8), stat(mean emp) stat(count emp)
di "--- taxa de emp por reltime (abril) ---"
table reltime if mes_nasc==4 & inrange(reltime,-3,8), stat(mean emp) stat(count emp)

di ""
di "########## D3 — remuneracao (SM) por reltime, condicional a emp ##########"
di "--- marco ---"
table reltime if mes_nasc==3 & emp==1 & inrange(reltime,0,8), stat(mean remun) stat(p50 remun) stat(count remun)
di "--- abril ---"
table reltime if mes_nasc==4 & emp==1 & inrange(reltime,0,8), stat(mean remun) stat(p50 remun)

di ""
di "########## D4 — horas contratadas por reltime, condicional a emp ##########"
di "--- marco ---"
table reltime if mes_nasc==3 & emp==1 & inrange(reltime,0,8), stat(mean horas) stat(count horas)
di "--- abril ---"
table reltime if mes_nasc==4 & emp==1 & inrange(reltime,0,8), stat(mean horas)

di ""
di "########## D5 — N com emp em >=3 anos consecutivos incl >=1 antes do nascimento ##########"
use "$aud\rais_panel.dta", clear
gen byte pre = ano < ano_nasc
bysort cd_aluno_sme: egen npre = total(pre)
bysort cd_aluno_sme: egen nyears = total(1)
di "  criancas com >=1 ano RAIS antes do nascimento: "
egen tagc=tag(cd_aluno_sme)
count if tagc==1 & npre>=1
di "  criancas com >=3 anos RAIS observados: "
count if tagc==1 & nyears>=3
di "  --> N event-study (>=3 anos incl >=1 pre-nasc) = "
count if tagc==1 & nyears>=3 & npre>=1

*==============================================================
di ""
di "########## PARTE E — quebra de 2013 e balanco ##########"
di "########## E1 — ano de elegibilidade ao Bercario I vs 2013 ##########"
di "  (elegibilidade Berc I = ano_nasc se mes<=3, senao ano_nasc+1)"
use "$aud\B_novo.dta", clear
keep if inrange(ano_nasc,2009,2015)
gen elig_berc1 = ano_nasc + (mes_nasc>=4)
di "--- distribuicao ano elegibilidade Berc I por coorte (marco vs abril) ---"
gen grp = cond(mes_nasc==3,"mar",cond(mes_nasc==4,"abr",""))
table ano_nasc grp if inlist(mes_nasc,3,4), stat(min elig_berc1) stat(max elig_berc1)
di "  (>=2013 = apos a quebra de encaminhamentos)"

di ""
di "########## E2 — razao marco/abril de N por coorte ##########"
forvalues c=2009/2015 {
    qui count if ano_nasc==`c' & mes_nasc==3
    local n3=r(N)
    qui count if ano_nasc==`c' & mes_nasc==4
    local n4=r(N)
    di "  coorte `c': N marco=`n3'  N abril=`n4'  razao=" %5.3f `n3'/`n4'
}

di ""
di "########## E3 — balanco marco vs abril nas vars do responsavel ##########"
di "  (NOTA: remuneracao no ano ANTES do nascimento NAO existe -- RAIS sem pre-parto; uso ano observado)"
use "$aud\rais_panel.dta", clear
gen idade_no_nasc = idade - (ano - ano_nasc)
gen byte fem = sexo==2
merge m:1 cd_aluno_sme using "$aud\B_novo.dta", keep(match) keepusing(mes_nasc) nogen
keep if inrange(ano_nasc,2009,2015) & inlist(mes_nasc,3,4)
gen byte abril = mes_nasc==4
foreach v in fem idade_no_nasc escol remun {
    qui ttest `v', by(abril)
    di "  `v': marco=" %8.3f r(mu_1) "  abril=" %8.3f r(mu_2) "  dif=" %8.4f r(mu_1)-r(mu_2) "  se=" %8.4f r(se) "  p=" %6.4f r(p)
}

di "=== FIM DE ==="
log close
