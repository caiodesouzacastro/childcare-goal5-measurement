# -*- coding: utf-8 -*-
# Substituicao segura (M8): grava com retentativas e CONFIRMA relendo o arquivo. Uso:
#   python safe_replace.py ARQUIVO pares.json        (lista de [antigo, novo]; antigo deve ocorrer exatamente 1 vez)
# Sai com codigo 1 se algum par nao for encontrado, ocorrer mais de uma vez, ou se a releitura nao confirmar.
import sys, json, time, io
def load(p):
    for i in range(6):
        try: return io.open(p, encoding="utf-8", newline="").read()
        except OSError: time.sleep(1)
    raise SystemExit(f"FALHA: nao consegui ler {p}")
def main(path, pairs):
    s = load(path); nl = "\r\n" if "\r\n" in s else "\n"; s2 = s.replace("\r\n", "\n"); bad = 0
    for a, b in pairs:
        a = a.replace("\r\n", "\n"); b = b.replace("\r\n", "\n"); k = s2.count(a)
        if k != 1: print(f"ERRO: ocorrencias={k}: {a[:70]!r}"); bad += 1; continue
        s2 = s2.replace(a, b)
    if bad: raise SystemExit(1)
    out = s2.replace("\n", nl)
    for i in range(6):
        try:
            io.open(path, "w", encoding="utf-8", newline="").write(out); time.sleep(0.3)
            if load(path) == out: print(f"OK ({len(pairs)} pares) confirmado na releitura: {path}"); return
        except OSError: pass
        time.sleep(1.5)
    raise SystemExit(f"FALHA: gravacao nao confirmada em {path}")
if __name__ == "__main__":
    main(sys.argv[1], json.load(io.open(sys.argv[2], encoding="utf-8")))
