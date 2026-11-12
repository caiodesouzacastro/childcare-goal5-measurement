* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 200
global aud "$NE_ROOT\02_audit"
global ba  "$NE_ROOT\dados_restritos\Ciro\01_dados\processados\bases_analise"
cap log close
log using "$aud\diag09_BCDE.log", text replace

*==============================================================
di "########## PARTE B — amostra do event study (maes) ##########"
use "$aud\panel_es.dta", clear
* primeira crianca (menor ano_nasc) por responsavel
bysort respid: egen firstbirth = min(ano_nasc)
* manter responsaveis femininos
keep if fem==1

di "--- B1: criancas e maes distintas (responsavel feminino) ---"
egen tagcm = tag(cd_aluno_sme)
count if tagcm==1
di "  criancas com responsavel feminino = " r(N)
egen tagm = tag(respid)
count if tagm==1
di "  maes distintas = " r(N)

di ""
di "--- B2: maes com 1o filho nascido 2009-2013 ---"
preserve
    keep respid firstbirth
    duplicates drop
    count if inrange(firstbirth,2009,2013)
    di "  maes com 1o filho 2009-2013 = " r(N)
restore

di ""
di "--- B3: anos RAIS pre/pos primeiro nascimento (por mae) ---"
preserve
    keep respid rais_year firstbirth
    duplicates drop
    gen byte pre = rais_year < firstbirth
    gen byte pos = rais_year >= firstbirth
    bysort respid: egen npre = total(pre)
    bysort respid: egen npos = total(pos)
    by respid: keep if _n==1
    keep if inrange(firstbirth,2009,2013)
    di "  --- tab npre x npos ---"
    tab npre npos
    count if npre>=2 & npos>=3
    di "  N maes com >=2 pre E >=3 pos = " r(N)
restore

di ""
di "--- B4: idade da mae no 1o nascimento (firstbirth - maeb) ---"
preserve
    keep respid firstbirth maeb
    duplicates drop
    gen idade_mae = firstbirth - maeb
    keep if inrange(firstbirth,2009,2013)
    sum idade_mae, detail
    count if idade_mae<18 & !missing(idade_mae)
    di "  <18 anos: " r(N)
    count if idade_mae>40 & !missing(idade_mae)
    di "  >40 anos: " r(N)
    count if missing(idade_mae)
    di "  missing: " r(N)
restore
di "--- B5: escolaridade NAO foi retida no painel (grinstrucao vs escolaridadeapos2005 = escalas diferentes) ---"

*==============================================================
di ""
di "########## PARTE C — desfechos por tempo relativo (maes, 1o filho 2009-2013) ##########"
di "  ATENCAO: 2008/2009 sao arquivos so-empregados -> emp inflado nesses anos (artefato)"
* painel mae-ano em torno do 1o filho
keep if inrange(firstbirth,2009,2013)
gen rel = rais_year - firstbirth
collapse (max) emp wsm hrs publico (firstnm) estabsz, by(respid rel firstbirth)

di "--- C1: emp (incondicional; mae-ano presente) ---"
table rel if inrange(rel,-5,6), stat(mean emp) stat(count emp)
di "--- C2: salario SM incondicional (sem vinculo=0) ---"
gen wsm0 = wsm
replace wsm0 = 0 if emp==0 | missing(wsm)
table rel if inrange(rel,-5,6), stat(mean wsm0)
di "--- C3: salario SM condicional a emprego ---"
table rel if inrange(rel,-5,6) & emp==1, stat(mean wsm) stat(p50 wsm)
di "--- C4: horas condicional a emprego ---"
table rel if inrange(rel,-5,6) & emp==1, stat(mean hrs)
di "--- C5: setor publico (natjur 1xxx) condicional a emprego ---"
table rel if inrange(rel,-5,6) & emp==1, stat(mean publico)

di "=== FIM BCDE ==="
log close
