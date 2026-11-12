# Replication notes

Written from scratch on 11 Nov 2026 for the package assembled that day. It replaces the earlier `04_paper/REPLICATION_NOTES.md`, which is not distributed.

## 1. Inputs

**Public, included:**
- SME class profiles (`01_dados_publicos/perfil_*.csv`) and class modules (`turmas_modulo_2016_2017.csv`);
- SME partner-organisation lists (`01_dados_publicos/parc_*.csv`, `parcerias_mar2023.csv`; 29 files);
- the SME school registry as parsed for this project (`02_audit/escolas_parsed.dta`; see below);
- SINASC live births by district (`01_dados_publicos/ceinfo/`);
- SEADE population files (`03_build/build13_coverage/seade_raw/`);
- SME published demand and enrolment series (`04_paper/referee_EE_2026-10/fontes_saidaC/serie_SME/`, `03_build/build19/`);
- SIDRA table 9514 (`fontes_saidaC/censo2022/`);
- SME demand by district (`03_build/build04/_ext/`).

**`02_audit/escolas_parsed.dta`: origin and content.**
- **Origin:** built by `02_audit/diag04_A.do` (lines 33–56) from the school registry published on the SME website (`escolassite.dta`).
- **Rows:** one per school or educational unit, 4,753 in all, of 16 types: municipal centres, partner centres, private schools, adult-literacy units and others.
- **Columns:**
  - the unit's code, Inep code, type, name and former name;
  - regional directorate, sub-prefecture, district and census sector;
  - the unit's street address, number, neighbourhood and CEP (3,790 distinct);
  - the unit's telephone and fax;
  - creation, authorisation, agreement and start-of-operation dates and acts;
  - the unit's latitude and longitude.
- Every address, CEP and coordinate is that of the educational unit. No child or guardian information is included.

**Public, not redistributed:**
- The Inep School Census microdata: see section "External data".
- Third-party documents (laws, reports, news) in `fontes_saidaC/`. Their redistribution licence is not stated; cite them by URL.

**Restricted, not included:** SME individual application records (Fila) and EOL enrolment records, and every file derived from them at the level of a child:
- `spine.parquet`, `child_master.feather`, `child_dtenc.feather`, `_panel_criancas.parquet`, `eol_creche.parquet`;
- the `.dta` files with `cd_aluno_sme`;
- `03_build/build01/_staging/t4d_dist_far.csv` (one distance per enrolled child).

They are expected under `$NE_ROOT/dados_restritos/`.

**Left out under the individual-data rule because the origin of their postcodes cannot be determined:**
- **The files:** `02_audit/cep_cei_pairs.dta`, `02_audit/cep_cei_pairs_novo.dta`, `02_audit/cep_setor.dta` and `03_build/build01/_staging/cep_covars.csv`.
- **Their postcodes are street-level, not those of educational units:** 44,558, 44,667, 45,362 and 43,495 distinct CEPs respectively.
- **Where they come from:** the first three come from a CEP-centroid file in the restricted SME folder (`cepcentroide.dta`, 46,258 CEPs; `diag04_Cprep.do`, `diag05_Bprep.do`, `diag05_D1D2.do`), and the fourth from a CEP–income base in a restricted folder (`build01_cepcovars.py`).
- **Why they stay out:** whether those CEP lists were derived from children's or guardians' residences cannot be established.

## External data (not redistributed; download from Inep)

The Inep School Census microdata are not redistributed (Inep's terms). Download them from Inep into `$NE_ROOT/03_build/build20/_inep/`. Check the SHA-256 below to confirm that the file is the one used here. On 11 Nov 2026, each URL answered HTTP 200 with the byte size shown.

| Year | File | Official URL | Bytes | SHA-256 |
|---|---|---|---|---|
| 2019 | `microdados_censo_escolar_2019.zip` | https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2019.zip | 26,219,731 | `ff023a2fccab4402772a1e1d87426cf5d35e10fcf2d13749a8bcb862d86894e7` |
| 2020 | `microdados_censo_escolar_2020.zip` | https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2020.zip | 26,033,386 | `1e4bd258c08906908438bbc0fbcf7e6a378919c467f11afb4785e3fd4b098f04` |
| 2021 | `microdados_censo_escolar_2021.zip` | https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2021.zip | 25,942,916 | `b4083b55058ba19d7e45982239e5d6f3e843786da210b657e77c653e5558b1f2` |
| 2022 | `microdados_censo_escolar_2022.zip` | https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2022.zip | 26,394,408 | `450d6f60d3447a8ca926b58d64eb5a0c4da823da07f045e129c3c8f154253a39` |
| 2023 | `microdados_censo_escolar_2023.zip` | https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2023.zip | 32,094,587 | `8ed0db8c557137593727b0574d5c99d0abb52491cd7c5769f8cefa98e1fa9e66` |
| 2024 | `microdados_censo_escolar_2024.zip` | https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2024.zip | 33,829,396 | `ae29d81d45ddecef59e11eda39788cbfd30dfa1cc71be9d29f23051fc2d640db` |

Each zip contains the school-level file `microdados_ed_basica_<year>.csv`.

How `02_audit/build20_censo.py` reads them (series 2007–2024):
- It reads `microdados_ed_basica_<year>.csv` from a local folder when that file exists. On the build machine this was the case for 2007–2019, from a shared folder outside the project.
- Otherwise it reads the zip above.
- To reproduce 2007–2018, download the zip of the same name and pattern for each year from the same Inep address. Those files were not hashed here, because the build used extracted CSVs.

## Corrections and redactions made for this package (11 Nov 2026)

- **The disclosure rule on CNPJ was wrong and has been corrected.** The first version of the scan treated any CNPJ as a stop. A CNPJ identifies a legal entity, not a person. Lists of partner agreements with the organisations' CNPJ are public under transparency law, so the 29 partner-organisation lists are included.
- **Stata licence header removed from 6 logs.** In `02_audit/desc.log`, `desc2.log`, `desc3.log`, `desc4.log`, `probe_do.log` and `vn.log`, the four opening lines with the licence type, the serial number and the licensee were deleted (original lines 13–16). The rest of each log is unchanged.
- **Two child identifiers redacted.** In `00_diagnosticos/DIAG02_reconstruido.md` (line 269) and `02_audit/diag02_partC.log` (line 62), the minimum and maximum of `cd_aluno_sme` printed by `codebook` are replaced by `[REDACTED: individual identifier]`. Nothing else changes.
- **Machine paths.** In every copied text file, machine-specific paths and user names were replaced by `NE_ROOT`-relative paths or placeholders.

## 2. Code

- Every hard-coded machine path was replaced by the root `NE_ROOT` (environment variable; for Python the default is the folder above the script's folder). Restricted inputs point to `$NE_ROOT/dados_restritos/...`.
- 134 of the 209 scripts read restricted inputs. Each one has a first-line note: `REPLICATION PACKAGE NOTE: this script does not run without the restricted SME microdata`.
- The 8 scripts that build the child-level base used by most exhibits are `build01_cepcovars.py`, `build01_child.py`, `build03_cohort.py`, `build03_demog.py`, `build03_s7s8.py`, `build05_panel.py`, `build09.py` and `build10_spine.py` (all in `02_audit/`). None of them runs without restricted data.
- `build03_cohort.py` originally read the SINASC file from a download folder. The package copy reads `$NE_ROOT/dados_externos/sinasc_nv_distrito_2006_2026.csv`. The file in `01_dados_publicos/ceinfo/` has the same name. The originally downloaded copy could not be compared: when checked on 12 Nov 2026, it was no longer in any download folder of the machine whose path the script used. The three copies that remain are byte-identical (11,551 bytes; sha256 `59f997098eca2dd940fb6e68ebab6eab696c1a50aafbf5912612895a37efe834`): `01_dados_publicos/ceinfo/`, `02_audit/` and the copy in the SME folder read by `utilitarios_nao_necessarios/build13_rates.py`. Every other script that uses SINASC reads one of them.
- `utilitarios_nao_necessarios/` holds one-off utilities (checks, renumbering, downloads). None of them writes an exhibit.

## 3. Exhibit by exhibit

"Regenerable" means that the listed script rewrites the file from inputs in this repository. "Needs restricted data" means that some step upstream of the generator reads child-level records. "By hand" lists edits made after generation, which the generator does not reproduce.

| Exhibit (label) | File in `04_paper/` | Generator | Regenerable from this repository? | By hand after generation |
|---|---|---|---|---|
| Table 1 (`tab:series`) | `assets/tables/v3w/V3w_series.tex` + `c/C_series_body.tex` | `build20_tables.py` (body) | Body: yes (public SME series). Wrapper: author source, no generator | caption/notes wrapper written by the author |
| Table 2 (`tab:arms`) | `v3w/V3w_arms.tex` + `c/C_arms_v3_body.tex` | `build23_denominador.py` | Body: yes. Wrapper: author source | wrapper |
| Table 3 (`tab:indet`) | `v3w/V3w_indet.tex` + `c/C_indet_body.tex` | `build25_indeterminacia.py` | Numbers: yes. Layout: no | wrapper; panel separator changed to vertical space (11 Nov) |
| Table 4 (`tab:coverage`) | `assets/tables/v2/V2_coverage.tex` | `build15_tables.py` | No: needs restricted data | caption sentence (9 Nov); inner panel rules removed, panels kept as separate tabulars (11 Nov); spelling (OQ-223) |
| Figure 1 (`fig:goal`) | `assets/figures/C_fig_goal.pdf` via `v3w/V3w_fig_goal.tex` | `build19_fig_meta.py`; copied by `build20_tables.py` | Yes | wrapper |
| Figure 2 (`fig:coverage`) | `figures/V3_fig_coverage.pdf` via `v3w/V3w_fig_coverage.tex` | `build18_figs.py` | Plot step: yes, from the staged aggregates in `03_build/build18/`. Aggregates: need restricted data | wrapper |
| A1 (`tab:T6a_modulo`) | `appx/A_T6a.tex` | `build01_tex.py` → copy → `build12_appendix.py` | Numbers: yes (public class profiles). Byte for byte: no | column labels and titles; the copy from `03_build/build01/tables/` is manual |
| A2 (`tab:T6b_ratio`) | `appx/A_T6b.tex` | same chain | Numbers: yes. Byte for byte: no | labels; manual copy |
| A3 (`tab:calendar`) | `appx/A_calendar.tex` | `build15_appx.py` | No: needs restricted data | separator (11 Nov); spelling (OQ-223) |
| A4 (`tab:T2a_capacidade`) | `appx/A_T2.tex` | `build01_tex.py` → copy → `build12_appendix.py` | Numbers: yes. Byte for byte: no | labels; inner panel rules removed (11 Nov); manual copy |
| A5 (`tab:R_capcheck`) | `appx/A_Rcap.tex` | `build04_capcheck.py` → copy → `build12_appendix.py` | Numbers: yes. Byte for byte: no | labels; separator (11 Nov) |
| A6 (`tab:T7a_ceis`) | `appx/A_T7a.tex` | `build01_tex.py` → copy → `build12_appendix.py` | Numbers: yes. Byte for byte: no | labels |
| A7 (`tab:S6c_cobertura`) | `appx/A_S6cd.tex` | `build03_tex.py` (inputs from `build03_demog.py`) → copy → `build12_appendix.py` | No: needs restricted data | labels; inner panel rules removed and separator replaced by vertical space (11 Nov) |
| A8 (`tab:T5c_modal`) | `appx/A_T5c.tex` | `build01_tex.py` → copy → `build12_appendix.py` | No: its CSV input comes from the request record | manual copy |
| A9 (`tab:T1_fila`) | `appx/A_T1.tex` | `build01_tex.py` → copy → `build12_appendix.py` | No: needs restricted data | labels; manual copy |
| A10 (`tab:N1`) | `appx/A_N1lotes.tex` | `build09.py` → copy → `build12_appendix.py` | No: needs restricted data | separator (11 Nov); manual copy |
| A11 (`tab:armArob`) | `v3w/V3w_armArob.tex` + `c/C_armA_rob_body.tex` | `build22_robustez.py` | No: the script mixes public and restricted inputs | wrapper |
| A12 (`tab:indetfull`) | `v3w/V3w_indet_full.tex` + `c/C_indet_full_body.tex` | `build25_indeterminacia.py` | Numbers: yes. Layout: no | wrapper; one separator removed (11 Nov) |
| A13 (`tab:recon`) | `v3w/V3w_recon.tex` + `c/C_recon_body.tex` | `build20_tables.py` | Body: yes | wrapper |
| A14 (`tab:decomp`) | `v3w/V3w_decomp.tex` + `c/C_decomp_body.tex` | `build22_robustez.py` | No: mixes public and restricted inputs | wrapper |
| A15 (`tab:dates`) | `v3w/V3w_dates.tex` + `c/C_dates_body.tex` | `build20_tables.py` | Body: yes | wrapper |
| A16 (`tab:covtype`) | `appx/A_covtype.tex` | `build15_appx.py` | No: needs restricted data | spelling (OQ-223) |
| A17 (`tab:completeness`) | `v3/V3_completeness.tex` | `build18_tables.py` | No: needs restricted data | inner panel rules removed (11 Nov) |
| A18 (`tab:prospect`) | `appx/A_prospect.tex` | `build18_appx.py` | Table step: yes, from staged aggregates. Aggregates: need restricted data | inner panel rules removed (11 Nov); spelling (OQ-223) |
| A19 (`tab:enrolledbyage`) | `appx/A_full_N4.tex` | `build12_tables.py` + `build12_spelling.py` (`N4_enrolled.tex`) | No: needs restricted data | built from a copy of `N4_enrolled.tex` |
| A20 (`tab:level`) | `v3/V3_level.tex` | `build18_tables.py` | No: needs restricted data | inner panel rules removed and separators replaced by vertical space (11 Nov); spelling (OQ-223) |
| A21 (`tab:timing`) | `v3/V3_timing.tex` | `build18_tables.py` | No: needs restricted data | none recorded |
| A22 (`tab:C4`) | `appx/A_C4v2.tex` | `build15_appx.py` | No: needs restricted data | spelling (OQ-223) |
| A23 (`tab:service`) | `v3/V3_service.tex` | `build18_tables.py` | No: needs restricted data | inner panel rules removed (11 Nov) |
| A24 (`tab:specs`) | `v3/V3_specs.tex` | `build18_tables.py` | No: needs restricted data | panel title row added (11 Nov); spelling (OQ-223) |
| A25 (`tab:T4d_never`) | `appx/A_T4dv2.tex` | `build15_appx.py` | No: needs restricted data | none recorded |
| A26 (`tab:stab`) | `v3w/V3w_stab.tex` + `c/C_stab_body.tex` | `build20_tables.py` | Body: yes | wrapper |
| A27 (`tab:cohortcov`) | `v3/V3_cohortcov.tex` | `build18_tables.py` | No: needs restricted data | spelling (OQ-223) |
| Figure A1 (`fig:F7`) | `figures/F7_capacidade_pool.pdf` | `build16_figfix.py` | Plot step: yes. Pool input: needs restricted data | wrapper |
| Figure A2 (`fig:level`) | `figures/V3_fig_level.pdf` | `build18_figs.py` | Plot step: yes, from staged aggregates | wrapper |
| Figure A3 (`fig:F8`) | `figures/F8_serie_mensal.pdf` | `02_audit/f8_sem_titulo.py`, from `03_build/build03/figures/F8_data.csv` (`build03_s7s8.py`) | Plot step: yes. CSV: needs restricted data | the PDF was installed by a copy step that is outside the repository |
| B1 (`tab:designs`) | `appendix_V3_designs.tex` | **none**: typed by hand from the reports in `00_diagnosticos/` | No | the whole table |

Notes on the table:
- The 14 `assets/tables/v3w/V3w_*.tex` wrappers have no generator. They hold the caption, label, notes and alt text, and input the generated body or the PDF.
- The copies from `03_build/*/tables/` to `04_paper/assets/tables/` were made without a script. Of the 62 root-level `.tex` files, 59 are byte-identical to the build output.
- **11 Nov 2026 layout edits.** Internal rules were replaced by vertical space, by hand, in 13 files: `C_indet_body`, `C_indet_full_body`, `A_calendar`, `A_Rcap`, `A_S6cd`, `A_N1lotes`, `A_T2`, `V2_coverage`, `V3_completeness`, `A_prospect`, `V3_level`, `V3_service` and `V3_specs`; also `appendix_V3_designs.tex`. No panel tabulars were merged: in `A_S6cd`, `A_T2`, `V2_coverage`, `V3_completeness`, `A_prospect`, `V3_level` and `V3_service`, the panels remain separate tabulars, and only the top and bottom rules of the inner panels were removed. No number changed.

## 4. Compiling the manuscript

From `04_paper/`: `pdflatex paper_v4`, `bibtex paper_v4`, `pdflatex paper_v4`, `pdflatex paper_v4`. The compiled `04_paper/paper_v4.pdf` is included.

## 5. Files left out and why

| What | Rule |
|---|---|
| Child-level files (38 classified as not publishable, plus `t4d_dist_far.csv` and 2 files with child identifier columns) | R1: no individual records |
| 7 Stata logs with `list` output | R1/R4: row-by-row output cannot be shown not to be individuals |
| The 4 CEP files listed in section 1 | individual-data rule: residential origin cannot be excluded |
| Inep School Census zips (6) | not redistributable; see "External data" |
| Process records (word counts, appendix ordering, number checks) | not data or code of the chain |
| Third-party documents in `fontes_saidaC/` (144) | redistribution licence not stated |
| Compilation by-products, the obsolete title page, the old `REPLICATION_NOTES.md` | not needed or superseded |
| 7 inputs outside the project folder (restricted SME folders and a download folder) | restricted or external |
