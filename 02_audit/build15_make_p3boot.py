# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# FASE 2, etapa 1.2: gera build15_p3boot_clean.py a partir do build_p3boot.py ORIGINAL, trocando so:
# caminhos (maquina atual), coortes (2013, 2016; alvo continua 2013), base do Delta (2013) e pasta de saida.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import re, os
A = (NE_ROOT + r"\02_audit")
s = open(os.path.join(A, "build_p3boot.py"), encoding="utf-8").read()
rep = [
 (r'ROOT = NE_ROOT + r""', r'ROOT = os.environ.get("NE_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))'),
 (r'OUT  = os.path.join(ROOT, r"03_build\build11\tables")', r'OUT  = os.path.join(ROOT, r"03_build\build15"); os.makedirs(OUT, exist_ok=True)'),
 (r'CEPRENDA = NE_ROOT + r"\dados_restritos\Ciro\01_dados\processados\bases_analise\cep_renda_pop_2010.dta"',
  r'CEPRENDA = os.path.join(os.environ.get("NE_DADOS_SME", os.path.join(ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")), r"processados\bases_analise\cep_renda_pop_2010.dta")'),
 ("COH    = [2010, 2013, 2016]", "COH    = [2013, 2016]\nBASE   = 2013"),
 ("for c in (2010, 2016):", "for c in (BASE, 2016):"),
 ("return vals[2016] - vals[2010], vals", "return vals[2016] - vals[BASE], vals"),
 ("v = {c: cif365_w(CO[c], counts[c].astype(float)) for c in (2010, 2016)}", "v = {c: cif365_w(CO[c], counts[c].astype(float)) for c in (BASE, 2016)}"),
 ("return v[2016] - v[2010], v", "return v[2016] - v[BASE], v"),
 ('S(f"  Raw           : 2010={v_raw[2010]:.3f} 2016={v_raw[2016]:.3f}  Delta={d_raw:+.4f}  (esperado +0.313)")',
  'S(f"  Raw           : 2013={v_raw[BASE]:.3f} 2016={v_raw[2016]:.3f}  Delta={d_raw:+.4f}  (esperado +0.123 = 0.876-0.753, tab:P3series)")'),
 ('S(f"  Applicant std : 2010={v_std[2010]:.3f} 2016={v_std[2016]:.3f}  Delta={d_std:+.4f}  (esperado +0.387)")',
  'S(f"  Applicant std : 2013={v_std[BASE]:.3f} 2016={v_std[2016]:.3f}  Delta={d_std:+.4f}  (esperado +0.132 = 0.885-0.753, tab:P3series)")'),
 ("if abs(d_std - 0.387) > 0.002 or abs(d_raw - 0.313) > 0.002:", "if abs(d_std - 0.132) > 0.002 or abs(d_raw - 0.123) > 0.002:"),
 ('os.path.join(OUT, "P3_boot_reps.csv")', 'os.path.join(OUT, "P3_boot_reps_2013_2016.csv")'),
 ('open(os.path.join(OUT, "P3_boot.tex"), "w", encoding="utf-8")', 'open(os.path.join(OUT, "P3_boot_2013_2016.tex"), "w", encoding="utf-8")'),
 (r'os.path.join(ROOT, r"03_build\build11", "p3boot.log")', r'os.path.join(OUT, "p3boot_2013_2016.log")'),
]
for a, b in rep:
    assert a in s, "nao achei: " + a[:60]
    s = s.replace(a, b)
s = s.replace("2010--2016 change", "2013--2016 change").replace("(2016$-$2010)", "(2016$-$2013)").replace("each of the 2010 and 2016 cohorts and within the 2013 cohort, the last included because it supplies the target composition",
              "each of the 2013 and 2016 cohorts; the 2013 cohort also supplies the target composition")
s = "# GERADO por build15_make_p3boot.py a partir de build_p3boot.py (25/10/2026). Nao editar a mao.\n" + s
open(os.path.join(A, "build15_p3boot_clean.py"), "w", encoding="utf-8").write(s)
print("ok: build15_p3boot_clean.py,", len(rep), "substituicoes")
