* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global dsme "$NE_ROOT\dados_restritos\Dados - SME\Atual (25.06)"
cap log close
log using "$aud\diag07_build.log", text replace

*==============================================================
di "########## A1 — cada cpf_fila: N e cobertura de 'ano' ##########"
foreach f in cpf_fila_101 cpf_fila_102 cpf_fila_11 cpf_fila_12 cpf_fila_13 cpf_fila_14 {
    use ano cd_aluno_sme using "$dsme/`f'.dta", clear
    di ""
    di "==== `f' : N=`=_N' ===="
    tab ano
}

*==============================================================
di ""
di "########## Painel RAIS a partir de cpf_fila_11..14 (esquema completo) ##########"
di "  (cpf_fila_101/102 tem esquema antigo diferente, sem idade/SM -> EXCLUIDOS do painel)"
tempfile acc
clear
gen byte _x=.
save `acc', emptyok
foreach f in cpf_fila_11 cpf_fila_12 cpf_fila_13 cpf_fila_14 {
    use cd_aluno_sme ano ano_nasc mes_nasc sexotrabalhador idade ///
        vínculoativo3112 vlremunmédiasm qtdhoracontr escolaridadeapós2005 cpf ///
        using "$dsme/`f'.dta", clear
    rename vínculoativo3112 vinc
    rename vlremunmédiasm remun_s
    rename qtdhoracontr horas
    rename escolaridadeapós2005 escol
    rename sexotrabalhador sexo
    append using `acc'
    save `acc', replace
}
use `acc', clear
drop _x
egen long respid = group(cpf)
drop cpf
di "N linhas empilhadas (11-14) = " _N
destring remun_s, gen(remun) force dpcomma
gen byte emp = (vinc==1)
collapse (max) emp (max) remun (max) horas (firstnm) sexo idade escol ano_nasc mes_nasc, ///
    by(cd_aluno_sme respid ano)
compress
save "$aud\rais_panel.dta", replace
di "N (crianca x responsavel x ano) = " _N

*==============================================================
di ""
di "########## A2 — nº de ANOS RAIS distintos por crianca ##########"
preserve
    keep cd_aluno_sme ano
    duplicates drop
    bysort cd_aluno_sme: gen nanos = _N
    by cd_aluno_sme: keep if _n==1
    gen nc = nanos
    replace nc = 5 if nanos>=5
    tab nc
    sum nanos, detail
restore

*==============================================================
di ""
di "########## A3 — criancas de B_novo com vinculo do responsavel por ano ##########"
preserve
    keep cd_aluno_sme ano
    duplicates drop
    merge m:1 cd_aluno_sme using "$aud\B_novo.dta", keep(match) keepusing(cd_aluno_sme) nogen
    di "--- N criancas de B_novo com >=1 registro RAIS por ano ---"
    tab ano if inrange(ano,2009,2018)
restore

*==============================================================
di ""
di "########## A4 — vinculo em ano ANTES do nascimento (pre-parto) ##########"
gen byte pre = ano < ano_nasc
count if pre==1
di "  (linhas crianca-resp-ano com ano<ano_nasc acima)"
preserve
    keep if pre==1
    keep cd_aluno_sme
    duplicates drop
    di "  criancas distintas com vinculo pre-nascimento = " _N
restore

di "=== FIM build ==="
log close
