* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 240
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag02_descB.log", text replace

local files `" "$NE_ROOT/dados_restritos/Dados - SME/Atual (25.06)/corteescolaunique.dta" "$NE_ROOT/dados_restritos/Dados - SME/Atual (25.06)/escolas/escolassite.dta" "$NE_ROOT/dados_restritos/Dados - SME/Atual (25.06)/escolas/escolasPSP2.dta" "$NE_ROOT/dados_restritos/Dados - SME/Atual (25.06)/escolas/censo2018.dta" "$NE_ROOT/dados_restritos/Dados - SME/Atual (25.06)/matriculas/fila1018.dta" "$NE_ROOT/dados_restritos/Dados - SME/Atual (25.06)/matriculas/matriculas1018.dta" "$NE_ROOT/dados_restritos/Dados - SME/Atual (25.06)/matriculas/filamatriculasite.dta" "$NE_ROOT/dados_restritos/Dados - SME/Atual (25.06)/Microdados_Demanda_Infantil_Escola_Especifica_FGV/fila_preferencia.dta" "'

foreach f of local files {
    di ""
    di "=================================================================="
    di "FILE: `f'"
    di "=================================================================="
    cap use "`f'", clear
    if _rc {
        di "  ERRO rc=" _rc
        continue
    }
    di "  N obs = " _N "   N vars = " c(k)
    describe, fullnames
}
di "=== FIM DESC B ==="
log close
