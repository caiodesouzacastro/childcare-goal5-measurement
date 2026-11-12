* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global rc  "$NE_ROOT\dados_restritos\Ciro\01_dados\brutos\rais_cpf"
cap log close
log using "$aud\diag09_build2.log", text replace

di "########## A1 — empem3112: quantos arquivos so tem empregados (rate=1)? ##########"
foreach spec in "cpf_fila_07 2007" "cpf_fila_081 2008" "cpf_fila_092 2009" "cpf_fila_101 2010" "cpf_fila_102 2010" "cpf_fila_11 2011" "cpf_fila_12 2012" "cpf_fila_13 2013" "cpf_fila_14 2014" {
    gettoken f yr : spec
    use "$rc/`f'.dta" in 1/1, clear
    * so contar a media de empem3112/vinc na base inteira
    cap use empem3112 using "$rc/`f'.dta", clear
    if !_rc {
        qui sum empem3112
        di "  `f' (`yr'): empem3112 media=" %5.3f r(mean) "  N=" r(N) "  (1.000 => so empregados)"
    }
    else {
        use vínculoativo3112 using "$rc/`f'.dta", clear
        qui sum vínculoativo3112
        di "  `f' (`yr'): vinc media=" %5.3f r(mean) "  N=" r(N)
    }
}

di ""
di "########## Painel corrigido (fem via string; salario em SM direto) ##########"
tempfile acc
clear
gen byte _x=.
save `acc', emptyok
foreach spec in "cpf_fila_07 2007" "cpf_fila_081 2008" "cpf_fila_092 2009" "cpf_fila_101 2010" "cpf_fila_102 2010" "cpf_fila_11 2011" "cpf_fila_12 2012" "cpf_fila_13 2013" "cpf_fila_14 2014" {
    gettoken f yr : spec
    use "$rc/`f'.dta", clear
    gen byte emp_raw = .
    cap replace emp_raw = empem3112
    cap replace emp_raw = vínculoativo3112
    * sexo
    gen byte fem = .
    cap replace fem = (genero=="FEMININO")
    cap replace fem = (sexotrabalhador==2)
    * salario em SM (direto)
    gen double wsm = .
    cap destring remmedia, gen(_r) force dpcomma
    cap replace wsm = _r
    cap drop _r
    cap destring vlremunmédiasm, gen(_s) force dpcomma
    cap replace wsm = _s
    cap drop _s
    * horas
    gen double hrs = .
    cap destring horascontr, gen(_h) force dpcomma
    cap replace hrs = _h
    cap drop _h
    cap replace hrs = qtdhoracontr
    * estab e natjur
    gen double estabsz = .
    cap replace estabsz = tamestab
    cap replace estabsz = tamanhoestabelecimento
    gen double njur = .
    cap replace njur = naturjur
    cap replace njur = natjuridica
    cap replace njur = naturezajurídica
    * nasc mae
    gen int maeb = .
    cap replace maeb = `yr' - idade
    cap replace maeb = floor(dtnasciment/10000) if missing(maeb) & dtnasciment>19000000 & dtnasciment<20200000
    gen int rais_year = `yr'
    keep cd_aluno_sme cpf emp_raw fem wsm hrs estabsz njur maeb rais_year ano_nasc mes_nasc
    append using `acc'
    save `acc', replace
}
use `acc', clear
drop _x
egen long respid = group(cpf)
drop cpf
gen byte emp = (emp_raw==1)
gen byte publico = inrange(njur,1000,1999) if !missing(njur)
* colapsar para (crianca, resp, ano): vinculo principal (maior salario)
gsort cd_aluno_sme respid rais_year -wsm
by cd_aluno_sme respid rais_year: gen byte _f=_n==1
collapse (max) emp (firstnm) fem maeb ano_nasc mes_nasc (max) wsm hrs publico (firstnm) estabsz, ///
    by(cd_aluno_sme respid rais_year)
compress
save "$aud\panel_es.dta", replace
di "N painel (crianca x resp x ano) = " _N
di "--- fem por ano (corrigido) ---"
table rais_year, stat(mean fem) stat(mean emp) stat(p50 wsm) stat(count wsm)

di "=== FIM build2 ==="
log close
