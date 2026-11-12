# childcare-goal5-measurement

Replication material for the paper *Measuring Compliance with Statutory Targets: Childcare Access in São Paulo*.

Repository: https://github.com/caiodesouzacastro/childcare-goal5-measurement

## What is here

| Folder | Content |
|---|---|
| `04_paper/` | LaTeX sources of the manuscript (`paper_v4.tex`, the ten `secV*.tex` sections, `tables_V3.tex`, `tables_V3_appendix.tex`, `appendix_V3_designs.tex`, the two `.bib` files), every table and figure file under `04_paper/assets/`, and the compiled `paper_v4.pdf`. |
| `02_audit/` | Analysis code (Python and Stata do-files) and the small intermediate files that do not contain individual records. |
| `03_build/` | Aggregated outputs of the build scripts (tables, CSV summaries, logs, figures). |
| `01_dados_publicos/` | Public source data: SME class profiles (`perfil_*.csv`), the class-module file, SME partner-organisation (`parc_*`) lists, and SINASC births by district (`ceinfo/`). |
| `00_diagnosticos/` | The diagnostic reports cited as the source of Table B1. |
| `utilitarios_nao_necessarios/` | One-off utilities kept for transparency. **Not needed** to reproduce any exhibit. |

`REPLICATION_NOTES.md` lists, exhibit by exhibit, the generating script and whether the exhibit can be regenerated from this repository. It also lists the external files to download, with checksums.

## What is not here

- **Individual-level records.** No file whose rows are children, guardians or applications is distributed, from any SME source, including the Escola On-Line (EOL) enrolment system. Scripts that read those records are included and are marked in their first lines as not runnable without them. See the paper's Data availability statement for how to request access from SME.
- **Inep School Census microdata (2019–2024).** Download them from Inep; URLs and SHA-256 checksums are in `REPLICATION_NOTES.md`, section "External data".

## Running the code

All scripts read one root folder from the environment variable `NE_ROOT`. For Python scripts, the default is the folder above the script's own folder. Restricted inputs are expected under `$NE_ROOT/dados_restritos/`, and downloaded external files under `$NE_ROOT/dados_externos/`.

```
export NE_ROOT=/path/to/this/repository      # Windows: set NE_ROOT=C:\path\to\repository
```

**Environment on the machine that assembled this package:**
- Python 3.13 with pandas 3.1, numpy 2.5, matplotlib 3.11 and pyarrow 26. A few scripts also import statsmodels, linearmodels and pyhdfe.
- Stata 17 MP for the do-files.
- pdflatex and BibTeX for the manuscript, with four passes.

## Licence

- **Code:** MIT (`LICENSE`), Copyright (c) 2026 Caio Castro.
- **Data:** CC BY 4.0 (`LICENSE-DATA.md`), same holder. Third-party public data keep their producers' terms, and the Inep microdata are not redistributed.

## Citation

Castro, C. *Measuring Compliance with Statutory Targets: Childcare Access in São Paulo.* Code and data: https://github.com/caiodesouzacastro/childcare-goal5-measurement.
