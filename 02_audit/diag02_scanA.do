* REPLICATION PACKAGE NOTE: this do-file does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
* pacote de replicacao (R3): raiz unica; defina a variavel de ambiente NE_ROOT antes de rodar
global NE_ROOT : env NE_ROOT
clear all
set more off
set linesize 240
global aud "$NE_ROOT\02_audit"
cap log close
log using "$aud\diag02_scanA.log", text replace

* Diretórios a varrer
local dirs `" "$NE_ROOT/dados_restritos/Dados - SME/Atual (25.06)" "$NE_ROOT/dados_restritos/Dados - SME/Atual (25.06)/ceps" "$NE_ROOT/dados_restritos/Dados - SME/Atual (25.06)/escolas" "$NE_ROOT/dados_restritos/Dados - SME/Atual (25.06)/matriculas" "$NE_ROOT/dados_restritos/Dados - SME/Atual (25.06)/Microdados_Demanda_Infantil_Escola_Especifica_FGV" "$NE_ROOT/dados_restritos/Dados - SME/01.07" "$NE_ROOT/dados_restritos/Dados - SME/01.07/matriculas" "'

* palavras-chave
local kw corte vaga capac limite class posic ordem rank fila prior chamada convoc sorteio data_lim

foreach d of local dirs {
    local fl : dir "`d'" files "*.dta"
    foreach f of local fl {
        local path "`d'/`f'"
        cap use "`path'" in 1, clear
        if _rc {
            di "ERRO ao abrir `path' : rc=" _rc
            continue
        }
        foreach v of varlist _all {
            local vl : variable label `v'
            local vlow = lower("`v'")
            local llow = lower(`"`vl'"')
            local hit 0
            foreach k of local kw {
                if strpos("`vlow'","`k'")>0 | strpos(`"`llow'"',"`k'")>0 local hit 1
            }
            if `hit' {
                local ty : type `v'
                di "MATCH | `f' | `v' | `ty' | `vl'"
            }
        }
    }
}
di "=== FIM SCAN A ==="
log close
