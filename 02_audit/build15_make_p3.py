# -*- coding: utf-8 -*-
# REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata (not distributed; see REPLICATION_NOTES.md).
# FASE 2, etapa 1.2: gera build15_p3_clean.py a partir do build_p3.py ORIGINAL, trocando so caminhos, a base do Delta
# (2013 em vez de 2010) e a pasta de saida. As series por coorte (2010-2016) sao as mesmas; muda so a diferenca.
# Caminhos portateis (27/10/2026, retomada no PC <usuario>): raiz do projeto e microdados da SME por variavel de
# ambiente, com padrao relativo a este arquivo (02_audit/ -> raiz; raiz/../../Compartilhado -> microdados).
import os as _os_ne
NE_ROOT = _os_ne.environ.get("NE_ROOT", _os_ne.path.dirname(_os_ne.path.dirname(_os_ne.path.abspath(__file__))))
import os
A = (NE_ROOT + r"\02_audit")
s = open(os.path.join(A, "build_p3.py"), encoding="utf-8").read()
rep = [
 (r'ROOT=NE_ROOT + r""', r'ROOT=os.environ.get("NE_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))'),
 (r'OUT=os.path.join(ROOT,r"03_build\build11\tables")', r'OUT=os.path.join(ROOT,r"03_build\build15"); os.makedirs(OUT,exist_ok=True)'),
 (r'CEPRENDA=NE_ROOT + r"\dados_restritos\Ciro\01_dados\processados\bases_analise\cep_renda_pop_2010.dta"',
  r'CEPRENDA=os.path.join(os.environ.get("NE_DADOS_SME", os.path.join(ROOT, "..", "..", "Compartilhado", "Microdados_Creches_SME")), r"processados\bases_analise\cep_renda_pop_2010.dta")'),
 ("dcif=vals[2016]-vals[2010]", "dcif=vals[2016]-vals[2013]"),
 ('CIF365 2010={v1[2010]:.3f}', 'CIF365 2013={v1[2013]:.3f}'), ('CIF365 2010={v2[2010]:.3f}', 'CIF365 2013={v2[2013]:.3f}'),
 ('CIF365 2010={v3[2010]:.3f}', 'CIF365 2013={v3[2013]:.3f}'),
 ('f"{v[2016]-v[2010]:+.3f}"', 'f"{v[2016]-v[2013]:+.3f}"'),
 (r'with open(os.path.join(ROOT,r"03_build\build11","p3.log"),"w",encoding="utf-8")', r'with open(os.path.join(OUT,"p3_2013_2016.log"),"w",encoding="utf-8")'),
]
for a, b in rep:
    assert a in s, "nao achei: " + a[:70]
    s = s.replace(a, b)
s = "# GERADO por build15_make_p3.py a partir de build_p3.py (25/10/2026): Delta com base 2013. Nao editar a mao.\n" + s
open(os.path.join(A, "build15_p3_clean.py"), "w", encoding="utf-8").write(s)
print("ok:", len(rep), "substituicoes")
