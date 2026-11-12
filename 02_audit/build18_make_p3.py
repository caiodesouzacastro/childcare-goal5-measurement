# -*- coding: utf-8 -*-
# MANHA, etapa 1.1 (26/10/2026): gera build18_p3_2012.py e build18_p3boot_2012.py a partir das versoes de base 2013
# (build15_p3_clean.py, build15_p3boot_clean.py), trocando so a base do Delta e a coorte-alvo da reponderacao (2013 -> 2012)
# e a pasta de saida (03_build/build18). Uso: python build18_make_p3.py p3   |   python build18_make_p3.py boot <d_raw> <d_std>
# (o boot confere a estimativa pontual contra os valores do p3, como o original fazia contra a tabela publicada).
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import os, sys
A = (NE_ROOT + r"\02_audit")
def gen(src, dst, rep, head):
    s = open(os.path.join(A, src), encoding="utf-8").read()
    for a, b in rep:
        assert a in s, "nao achei: " + a[:70]
        s = s.replace(a, b)
    open(os.path.join(A, dst), "w", encoding="utf-8").write(head + s); print("ok:", dst, len(rep), "substituicoes")
OUT15, OUT18 = r'r"03_build\build15"', r'r"03_build\build18"'
if sys.argv[1] == "p3":
    gen("build15_p3_clean.py", "build18_p3_2012.py", [
        (OUT15, OUT18),
        ("tgt=dd[dd.ano_nasc==2013][cellcol]", "tgt=dd[dd.ano_nasc==2012][cellcol]"),
        ("dcif=vals[2016]-vals[2013]", "dcif=vals[2016]-vals[2012]"),
        ("CIF365 2013={v1[2013]:.3f}", "CIF365 2012={v1[2012]:.3f}"), ("CIF365 2013={v2[2013]:.3f}", "CIF365 2012={v2[2012]:.3f}"),
        ("CIF365 2013={v3[2013]:.3f}", "CIF365 2012={v3[2012]:.3f}"),
        ('f"{v[2016]-v[2013]:+.3f}"', 'f"{v[2016]-v[2012]:+.3f}"'),
        ('"p3_2013_2016.log"', '"p3_2012_2016.log"'),
    ], "# GERADO por build18_make_p3.py a partir de build15_p3_clean.py (26/10/2026): base e alvo 2012. Nao editar a mao.\n"
       "# As tabelas .tex que este script grava em 03_build/build18 mantem textos da versao 2013 e NAO entram no paper; o paper le o log.\n")
else:
    d_raw, d_std = sys.argv[2], sys.argv[3]
    gen("build15_p3boot_clean.py", "build18_p3boot_2012.py", [
        (r'OUT  = os.path.join(ROOT, r"03_build\build15")', r'OUT  = os.path.join(ROOT, r"03_build\build18")'),
        ("COH    = [2013, 2016]\nBASE   = 2013\nTARGET = 2013", "COH    = [2012, 2016]\nBASE   = 2012\nTARGET = 2012"),
        ('S(f"  Raw           : 2013={v_raw[BASE]:.3f} 2016={v_raw[2016]:.3f}  Delta={d_raw:+.4f}  (esperado +0.123 = 0.876-0.753, tab:P3series)")',
         f'S(f"  Raw           : 2012={{v_raw[BASE]:.3f}} 2016={{v_raw[2016]:.3f}}  Delta={{d_raw:+.4f}}  (esperado {d_raw}, p3_2012_2016.log)")'),
        ('S(f"  Applicant std : 2013={v_std[BASE]:.3f} 2016={v_std[2016]:.3f}  Delta={d_std:+.4f}  (esperado +0.132 = 0.885-0.753, tab:P3series)")',
         f'S(f"  Applicant std : 2012={{v_std[BASE]:.3f}} 2016={{v_std[2016]:.3f}}  Delta={{d_std:+.4f}}  (esperado {d_std}, p3_2012_2016.log)")'),
        ("if abs(d_std - 0.132) > 0.002 or abs(d_raw - 0.123) > 0.002:", f"if abs(d_std - ({d_std})) > 0.002 or abs(d_raw - ({d_raw})) > 0.002:"),
        ('"P3_boot_reps_2013_2016.csv"', '"P3_boot_reps_2012_2016.csv"'),
        ('"P3_boot_2013_2016.tex"', '"P3_boot_2012_2016.tex"'),
        ('"p3boot_2013_2016.log"', '"p3boot_2012_2016.log"'),
    ], "# GERADO por build18_make_p3.py a partir de build15_p3boot_clean.py (26/10/2026): base e alvo 2012. Nao editar a mao.\n")
