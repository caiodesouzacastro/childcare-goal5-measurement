* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global rc  "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\rais_cpf"
cap log close
log using "$aud\diag09_build.log", text replace

* programa de harmonizacao: cria `tgt' a partir do 1o candidato existente
capture program drop pick
program define pick
    args tgt
    gettoken tgt cands : 0
    cap confirm variable `tgt'
    if !_rc exit
    gen `tgt' = .
    foreach c of local cands {
        cap confirm variable `c'
        if !_rc {
            cap replace `tgt' = `c'
            if _rc {
                cap destring `c', gen(_tmp) force dpcomma
                cap replace `tgt' = _tmp
                cap drop _tmp
            }
            continue, break
        }
    }
end

tempfile acc
clear
gen byte _x=.
save `acc', emptyok

foreach spec in "cpf_fila_07 2007" "cpf_fila_081 2008" "cpf_fila_092 2009" "cpf_fila_101 2010" "cpf_fila_102 2010" "cpf_fila_11 2011" "cpf_fila_12 2012" "cpf_fila_13 2013" "cpf_fila_14 2014" {
    gettoken f yr : spec
    use "$rc/`f'.dta", clear
    * harmonizar (nomes numericos)
    gen byte emp_raw = .
    cap replace emp_raw = empem3112
    cap replace emp_raw = vínculoativo3112
    gen byte sex_raw = .
    cap replace sex_raw = genero
    cap replace sex_raw = sexotrabalhador
    gen byte estabsz = .
    cap replace estabsz = tamestab
    cap replace estabsz = tamanhoestabelecimento
    gen double njur = .
    cap replace njur = naturjur
    cap replace njur = natjuridica
    cap replace njur = naturezajurídica
    * strings -> destring
    gen double wnom = .
    cap destring remmedia, gen(_w1) force dpcomma
    cap replace wnom = _w1
    cap destring vlremunmédianom, gen(_w2) force dpcomma
    cap replace wnom = _w2
    cap drop _w1 _w2
    gen double hrs = .
    cap destring horascontr, gen(_h1) force dpcomma
    cap replace hrs = _h1
    cap confirm variable qtdhoracontr
    if !_rc cap replace hrs = qtdhoracontr
    cap drop _h1
    * nascimento da mae
    gen int maeb = .
    cap replace maeb = `yr' - idade
    cap replace maeb = floor(dtnasciment/10000) if missing(maeb) & dtnasciment>19000000 & dtnasciment<20200000
    gen int rais_year = `yr'
    keep cd_aluno_sme cpf emp_raw sex_raw estabsz njur wnom hrs maeb rais_year ano_nasc mes_nasc
    append using `acc'
    save `acc', replace
    di "  `f' (`yr') carregado"
}

use `acc', clear
drop _x
egen long respid = group(cpf)
drop cpf
gen byte emp = (emp_raw==1)
gen byte fem = (sex_raw==2)
gen minw = .
replace minw = 380 if rais_year==2007
replace minw = 415 if rais_year==2008
replace minw = 465 if rais_year==2009
replace minw = 510 if rais_year==2010
replace minw = 545 if rais_year==2011
replace minw = 622 if rais_year==2012
replace minw = 678 if rais_year==2013
replace minw = 724 if rais_year==2014
gen double wage_sm = wnom/minw if !missing(wnom) & wnom>0
gen byte publico = inrange(njur,1000,1999) if !missing(njur)
keep cd_aluno_sme respid rais_year ano_nasc mes_nasc emp fem wage_sm hrs estabsz publico maeb
compress
save "$aud\panel_es.dta", replace
di "N painel rico = " _N

di "--- sexo (fem=1 se codigo 2) ---"
tab fem, miss
di "--- publico (natjur 1xxx) ---"
tab publico, miss
di "--- wage_sm ---"
sum wage_sm, detail
di "--- maeb (ano nasc mae) nao-missing ---"
count if !missing(maeb)
di "=== FIM build ==="
log close
