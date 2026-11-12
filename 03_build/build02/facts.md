# BUILD02 -- facts.md (robustez de T3)

Descritivo (associacao/diferenca/variacao/composicao). Reaproveita B\_novo e child\_master (BUILD01) + primeira data de encaminhamento de Fila1018. Nada modificado em Dropbox\\ (fora de \_audit\\) ou <D>\\.

## R1a -- fim do painel

- Ultima data observada: dt\_solicitacao **2018-12-17**; dt\_encaminhamento **2019-11-28**; dt\_matricula **2019-11-27**. Solicitacoes so vao ate dez/2018; encaminhamentos/matriculas seguem ate nov/2019. Ultimo ano com acompanhamento de 730 dias completo: **2016**.

## Numeros por tabela

- **R2a** [build02_build.py]: com janela fixa de 180 dias, a fracao encaminhada em 180d varia de 47\% (2010) a 72\% (2018); a espera\_180 media fica entre 96 e 134 dias.

- **R2b** [build02_build.py]: mediana KM do tempo ate encaminhamento cai de 220 dias (2010) para 163 (2017); $S(180)$ passa de 0.53 a 0.47. A coorte 2018 (mediana 96) esta parcialmente truncada.

- **R2c** [build02_build.py]: em 2010--2016 (acompanhamento completo), a idade media de entrada cai -15.11 meses; idade na solicitacao -14.92; espera -0.21. A queda da espera quase desaparece quando se removem as coortes truncadas.

- **R3a** [build02_build.py]: a idade media na 1a solicitacao cai de 39.3 meses na coorte 2008 para 9.4 na coorte 2016 --- tendencia por coorte de nascimento (transicao estoque$\to$fluxo).

- **R3b** [build02_build.py]: a fracao inscrita antes dos 12 meses sobe de 5.6\% (coorte 2008) para 65.3\% (2016); antes dos 24 meses, de 20.1\% a 92.5\%.

- **R3c** [build02_build.py]: a variacao liquida da idade media na solicitacao (2010--2018, -18.9 meses) e o residuo de dois componentes grandes e opostos --- composicao por coorte -88.8 (entrada de coortes jovens) e dentro de coorte +69.9 (envelhecimento do estoque nao inscrito). A queda e um fenomeno de composicao/maturacao do painel, nao uma mudanca limpa dentro de coorte.

- **R3d** [build02_build.py]: a fracao de solicitacoes por criancas com mais de 24 meses cai de 62\% (2010) para 25\% (2018) --- o estoque de demanda represada e absorvido ao longo do painel.

## R5 -- BUILD01 vs corrigido (lado a lado)

| Quantidade | BUILD01 (2010--2018) | Corrigido (2010--2016, 730d) |
|---|---|---|
| Queda total da idade de entrada | -19.09 meses | -15.11 meses |
| Fracao vinda da solicitacao | 80\% | 99\% |
| Fracao vinda da espera | 20\% | 1\% |

**A conclusao qualitativa se mantem e se fortalece.** A queda da idade de entrada continua dominada pela solicitacao mais precoce, nao pela menor espera. A parcela de ~20\% atribuida a espera no BUILD01 era, em grande parte, **artefato de truncamento a direita**: a forte queda da espera concentrava-se nas coortes 2017--2018, ainda sem acompanhamento completo (Tabela R2c). Restrito a coortes completas (2010--2016), a espera responde por ~1\% e a solicitacao por ~99\%.

**Ressalva de interpretacao (R3).** A propria queda da idade na solicitacao e majoritariamente **composicional**: reflete a transicao de um estoque (demanda represada de criancas mais velhas: 62\% das solicitacoes de 2010 eram de $>$24 meses) para um fluxo (recem-nascidos: 25\% em 2018), com as coortes de nascimento sucessivas se inscrevendo cada vez mais cedo (idade media por coorte 39,3 $\to$ 9,4 meses de 2008 a 2016). Nao e uma mudanca de comportamento medida limpa dentro de uma mesma coorte --- coortes de 2010 e 2018 quase nao se sobrepoem.

## O que nao saiu

- Coortes de nascimento 2017+ nao entram (sem tempo de painel suficiente).
- $S(730)$ das coortes 2017--2018 (R2b) e pouco informativo por censura.
