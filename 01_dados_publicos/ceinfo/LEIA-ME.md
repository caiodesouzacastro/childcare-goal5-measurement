# CEInfo — nascidos vivos por distrito

## Arquivo
`sinasc_nv_distrito_2006_2026.csv` — nascidos vivos por distrito administrativo de
residência, município de São Paulo, 2006–2026 (colunas = anos; linhas = 96 distritos +
"Ignorado" + "Total").

## Fonte
TabNet CEInfo — Coordenação de Epidemiologia e Informação (CEInfo), **Secretaria Municipal
da Saúde de São Paulo**. Tabulação do Sistema de Informações sobre Nascidos Vivos (SINASC),
arquivo de definição **`nascido.def`** (nascidos vivos), agregado por Distrito Administrativo
de residência da mãe.

## Acesso
- **Data de acesso:** 2026-07-23 (data do arquivo local; confirmar a data exata da tabulação).
- **URL da tabulação:** URL a registrar.
- **Extração manual:** o host do TabNet **não responde a requisições por script** (o download
  foi feito manualmente pela interface de tabulação do TabNet). Registrar o passo como manual
  no pacote de replicação.

## Observações de uso
- Excluir a linha **"Ignorado"** (residual, distrito não informado) — registrada como excluída.
- Descartar o ano **2026** (parcial).
- Usado como denominador (nascidos vivos por coorte/ano) em BUILD03 (`build03_cohort.py`,
  `build03_demog.py`). A ponte distrito↔renda (cep_renda_pop_2010) casa 96/96.
