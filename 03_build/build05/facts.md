# BUILD05 -- facts.md (analise de irmaos: aprendizado sobre a fila)

Descritivo (associacao/diferenca/variacao). Irmaos ligados por cpf\_resp\_aluno (Fila1018); variaveis de child\_master. Nao modifica build01/02/03/04.

## Numeros

- **S1a** [build05_irmaos.py]: 1,175,658 responsaveis (cpf); 256,984 familias com 2+ filhos; 78.1\% dos responsaveis tem 1 filho no painel.

- **S1c** [build05_irmaos.py]: 79,893 pares de irmaos com ambos os filhos nascidos 2010-2016 (plenamente observaveis 0-24m) e espacamento >=1 mes.

- **S2ab** [build05_irmaos.py]: o filho mais novo e inscrito, em media, 11.4 meses mais cedo que o mais velho (idade na 1a solicitacao); em 78\% dos pares o filho mais novo e inscrito mais cedo.

- **S2d** [build05_irmaos.py]: com efeito fixo de familia, o filho mais novo (ordem 2) e inscrito 7.09 meses mais cedo que o mais velho (EP 0.11); acrescentando FE distrito x ano de nascimento, 7.15 (EP 0.11).

- **S3bc** [build05_irmaos.py]: no bruto, mais espera do 1o filho associa-se a inscricao mais precoce do 2o (2.72 meses/100d). Porem idade de inscricao e espera do 1o sao negativamente correlacionadas (r=-0.43: quem inscreve cedo espera mais); como a diferenca inclui a idade do 1o, o gradiente e mecanico: controlando a idade de inscricao do proprio 1o filho, o coeficiente cai a 0.14 meses/100d (~0). Nao ha gradiente de aprendizado liquido.

- **S3d** [build05_irmaos.py]: familias cujo 1o filho nunca foi matriculado antecipam o 2o em 14.9 meses, vs 21.6 nas de 1o filho atendido rapido (diferenca 6.7).

- **S4ab** [build05_irmaos.py]: o PLACEBO (espera do 1o filho realizada APOS a inscricao do 2o, logo nao-observavel pela familia no ato) preve tao forte quanto a espera observada: 2.35 meses/100d (placebo) vs 2.53 (observada). Como o placebo nao morre, a associacao nao vem de a familia observar a espera -- consistente com o confound mecanico de S3, nao com aprendizado.

- **S4c** [build05_irmaos.py]: 17\% dos pares tem os dois filhos matriculados na mesma escola -- possivel prioridade de irmao (ver grep no relatorio).


- **S5 (robustez de S2d)** [build05_S5.py]: substituindo a tendencia linear de coorte por DUMMIES de ano de nascimento (padrao da literatura de ordem de nascimento), o coeficiente de ordem de nascimento passa de -7.09 (linear) para -7.20 meses (EP 0.11); com dummies de ano-mes e com distrito x ano permanece proximo. A estimativa linear nao estava materialmente contaminada. Placebos (sexo, raca) por ordem de nascimento ~0. O filho mais novo e inscrito mais cedo dentro da familia.

- **S5 (robustez de S2d)** [build05_S5.py]: substituindo a tendencia linear de coorte por DUMMIES de ano de nascimento (padrao da literatura de ordem de nascimento), o coeficiente de ordem de nascimento passa de -7.09 (linear) para -7.20 meses (EP 0.11); com dummies de ano-mes e com distrito x ano permanece proximo. A estimativa linear nao estava materialmente contaminada. Placebos (sexo, raca) por ordem de nascimento ~0. O filho mais novo e inscrito mais cedo dentro da familia.
