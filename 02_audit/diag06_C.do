* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global ba  "$NE_ROOT\dados_restritos\Ciro\01_dados\processados\bases_analise"
global fila "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\fila_espera\Fila1018.dta"
cap log close
log using "$aud\diag06_C.log", text replace

use "$aud\child_expo.dta", clear
gen idade_entrada = (year(dt_mat_first)-ano_nasc)*12 + (month(dt_mat_first)-mes_nasc) if ever_mat==1
replace idade_entrada=. if !inrange(idade_entrada,0,72)
gen espera_dias = dt_mat_first - dt_sol if ever_mat==1
gen byte mat12 = (ever_mat==1 & dt_mat_first<=dt_sol+365)
gen anomat = year(dt_mat_first)
gen mesmat = month(dt_mat_first)
rename cep_aluno cep
merge m:1 cep using "$ba\cep_renda_pop_2010.dta", keepusing(renda) keep(master match) nogen

*==============================================================
di "########## C1 — idade de entrada por ANO de matricula ##########"
table anomat if inrange(anomat,2010,2018), stat(count idade_entrada) stat(mean idade_entrada) stat(p50 idade_entrada)
di "--- MENSAL 2012-2014 (localizar o degrau): mediana idade ---"
gen ym = ym(anomat,mesmat)
format ym %tm
table ym if inrange(anomat,2012,2014), stat(p50 idade_entrada) stat(count idade_entrada) nototals

*==============================================================
di ""
di "########## C2 — espera / solic / mat12 por ANO de solicitacao ##########"
table ano_sol if inrange(ano_sol,2010,2018), stat(count cd_aluno_sme) stat(p50 espera_dias) stat(mean mat12)

di ""
di "########## C3 — idade de entrada por ano de matricula x quartil renda / estoque ##########"
xtile rq = renda if !missing(renda), nq(4)
xtile eq = estoque_1km, nq(4)
di "--- mediana idade por anomat x quartil de RENDA ---"
table anomat rq if inrange(anomat,2010,2018), stat(p50 idade_entrada) nototals
di "--- mediana idade por anomat x quartil de ESTOQUE_1km ---"
table anomat eq if inrange(anomat,2010,2018), stat(p50 idade_entrada) nototals

*==============================================================
di ""
di "########## C2b/C5 — encaminhamentos e prioridade por ano (Fila) ##########"
use an_letivo_encaminhamento dt_encaminhamento tipo_prioridade_encaminhamento using "$fila", clear
gen double dt_enc = date(dt_encaminhamento,"DMY hms")
di "--- N encaminhamentos por ano (an_letivo_encaminhamento) ---"
tab an_letivo_encaminhamento if inrange(an_letivo_encaminhamento,2010,2018)
di "--- tipo_prioridade_encaminhamento por ano (so encaminhados) ---"
gen byte prior = !missing(tipo_prioridade_encaminhamento)
table an_letivo_encaminhamento if inrange(an_letivo_encaminhamento,2010,2018), stat(count dt_enc) stat(mean prior)
di "--- composicao tipo_prioridade por ano ---"
tab an_letivo_encaminhamento tipo_prioridade_encaminhamento if inrange(an_letivo_encaminhamento,2010,2018), row

di "=== FIM C ==="
log close
