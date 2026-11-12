# -*- coding: utf-8 -*-
# f8_sem_titulo.py -- rodada noite-2026-11-09, Parte E3. Script NOVO, so de desenho, no scratchpad.
# Reproduz a Figura A3 (F8_serie_mensal.pdf) a partir do F8_data.csv, SEM o titulo dentro da imagem.
# Copia literal do desenho de 02_audit/build03_s7s8.py L189-L201 e das configuracoes de L17-L18, com uma unica
# diferenca: a linha ax.set_title(...) (L200, segunda instrucao) foi retirada. Nao le microdados, nao grava tabela,
# nao acrescenta nada ao facts.md, nao grava fora do scratchpad.
# Controle opcional (Parte E4): um terceiro argumento grava, na mesma execucao, a mesma figura COM o titulo, para
# separar o efeito de tirar o titulo do efeito da versao do matplotlib (o F8 atual foi gravado com a 3.11.0).
# Uso: python f8_sem_titulo.py <F8_data.csv> <pdf_sem_titulo> [<pdf_controle_com_titulo>]
import os, sys
import pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

CSV = sys.argv[1]
SAIDAS = [(os.path.abspath(sys.argv[2]), False)] + ([(os.path.abspath(sys.argv[3]), True)] if len(sys.argv) > 3 else [])
for s, _ in SAIDAS:
    if "dropbox" in s.lower():
        sys.exit("RECUSA: saida no Dropbox; este script so grava no scratchpad.")

plt.rcParams.update({"font.size": 11, "figure.dpi": 120, "axes.grid": True, "grid.alpha": .3})   # = L18
ser = pd.read_csv(CSV)                                                                            # ano, mes, idade_mediana

for SAIDA, com_titulo in SAIDAS:
    # ================= F8 (= L189-L201; sem o titulo, salvo no controle) =================
    fig, ax = plt.subplots(figsize=(8, 4.3))
    xser = ser["d"] if "d" in ser else pd.to_datetime(dict(year=ser.ano, month=ser.mes, day=1))
    ax.plot(xser, ser["idade_mediana"], "-", color="#1f3b73", lw=1.2)
    # marcos administrativos (linhas verticais)
    for dt, lab in [("2013-12-01", "Dec 2013"), ("2015-10-01", "Oct 2015"), ("2016-07-01", "Jul 2016")]:
        x = pd.Timestamp(dt)
        ax.axvline(x, color="#999999", ls="--", lw=0.9)
        ax.annotate(lab, xy=(x, ax.get_ylim()[1]), xytext=(2, -2), textcoords="offset points",
                    rotation=90, va="top", ha="left", fontsize=8, color="#666666")
    ax.set_xlabel("Month of application"); ax.set_ylabel("Median age at application (months)")
    if com_titulo:   # so no controle; na figura nova a linha L200 (set_title) esta retirada
        ax.set_title("Median age at first application, monthly series")
    fig.tight_layout(); fig.savefig(SAIDA); plt.close(fig)
    print("matplotlib", matplotlib.__version__, "->", SAIDA, "| titulo:", com_titulo, "|", len(ser), "pontos")
