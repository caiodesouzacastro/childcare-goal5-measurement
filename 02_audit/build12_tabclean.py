# -*- coding: utf-8 -*-
# Limpeza tipografica dos tabulars (revisao pos-EE): nao altera nenhum valor numerico.
import re
LABELS=[(" (S2d)",""),(" (S5a)",""),(" (S5b)",""),(" (S5c)",""),(" (S5e)",""),(" (S5f)",""),
        ("CIF mat","CIF enr"),("RMST mat","RMST enr"),("Enrolled only (paper)","Enrolled only"),
        ("Total (todos)","Total"),("VAGOFER (offered places)","Offered places"),
        ("Mat.\\ rate \\%","Enrollment rate \\%"),("Med.\\ age at mat.","Median age at enr.")]
def clean(b):
    # faixas malformadas da P4_dist (antes do sinal de menos): (-60---36 -> $(-60,-36]$ ; (-6--0 -> $(-6,0]$ ; (0--6 -> $(0,6]$
    b=re.sub(r"(?m)^\(-(\d+)---(\d+)", r"$(-\1,-\2]$", b)
    b=re.sub(r"(?m)^\(-(\d+)--(\d+)", r"$(-\1,\2]$", b)
    b=re.sub(r"(?m)^\((\d+)--(\d+)", r"$(\1,\2]$", b)
    # sinal de menos: hifen isolado antes de digito em celula -> $-$
    b=re.sub(r"(?<=[\s&])-(?=\d)", r"$-$", b)
    # anos com separador de milhar (T4d_never)
    b=b.replace("2,013.34","2013.34").replace("2,014.16","2014.16")
    # diacriticos e rotulos internos/portugueses (texto, nao valores)
    b=b.replace("Bercario","Ber\\c{c}\\'ario")
    for a,c in LABELS: b=b.replace(a,c)
    return b
