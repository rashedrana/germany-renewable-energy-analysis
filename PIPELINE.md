# ETL Pipeline — Germany's Renewable Electricity Transition

How the data behind this project (and its Power BI dashboard) gets from the
published sources to the files in this repository. The pipeline was
informal when the project was built — a download script, an analysis script
and a one-off build of the Power BI CSVs with no saved builder. This document
and `src/etl_pipeline.py` formalise it, so anyone can rebuild every derived
file from the two source downloads and check the result.

## Overview

```
SOURCE                     EXTRACT                  TRANSFORM                LOAD
OWID energy dataset  --->  download_data.py  --->   analysis.py        ---> data/analysis_subset.csv
(github.com/owid/                              build_db.py            outputs/results.json
 energy-data)                                                            energy.db
OWID CO2 dataset     --->  download_data.py  --->   etl_pipeline.py  ---> dashboard/powerbi/data/
(github.com/owid/                                                            DimCountry(_Full).csv
 co2-data)                                                                   DimYear.csv, DimSource.csv
                                                                            FactCountryYear(_Full).csv
                                                                            FactGeneration(_Full).csv
```

| Stage | Tool | Input | Output |
|---|---|---|---|
| Source | Our World in Data | Ember Electricity Data Explorer; Energy Institute Statistical Review; Global Carbon Project (CO₂) | `data/owid-energy-data.csv`, `data/owid-co2-data.csv` |
| Extract | `src/download_data.py` | The two OWID GitHub repositories | The two CSVs above, stored in `data/` |
| Transform (paper) | `src/analysis.py` | OWID energy + CO₂ CSVs | `data/analysis_subset.csv` (4 countries × 25 years, 100 rows), `outputs/results.json`, `outputs/germany_yearly.csv` |
| Transform (extended) | `src/analysis_extended.py` | `data/analysis_subset.csv` | `outputs/extended_results.json` (multivariate OLS, sub-period trends) |
| Transform (model) | `src/etl_pipeline.py` | OWID energy + CO₂ CSVs | Star-schema CSVs in `dashboard/powerbi/data/` (see below) |
| Load (SQL) | `src/build_db.py` | `data/analysis_subset.csv` | `energy.db` (SQLite, table `energy`), `outputs/sql_results.md` |
| Load (figures) | `src/figures.py`, `src/figures_extra.py` | `data/analysis_subset.csv`, `outputs/results.json` | `outputs/figures/fig1–fig8.png` |
| Load (dashboard) | `dashboard/` build (template + data) | `data/analysis_subset.csv`, star-schema CSVs, OWID full extract | `dashboard/index.html` (+ `dashboard/data.json`), `dashboard/powerbi/` |

## Rebuilding everything

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt        # pandas, numpy (openpyxl for the KPI workbook)
python src/download_data.py            # fetch the two OWID datasets into data/
python src/etl_pipeline.py             # rebuild the star-schema CSVs (validates against the committed files)
python src/analysis.py                 # headline statistics -> outputs/results.json
python src/analysis_extended.py        # extended statistics -> outputs/extended_results.json
python src/build_db.py                 # SQLite db + SQL results -> outputs/sql_results.md
python src/figures.py                  # figures 1-6 -> outputs/figures/
```

`python src/etl_pipeline.py --validate-only` rebuilds all nine derived
tables in memory and compares them with the committed files without writing
anything. Current result: **exact reproduction** (see the tolerances below).

## Transform rules (star schema)

These rules were reverse-engineered from the committed files and verified by
`etl_pipeline.py --validate-only` on 2026-11-28:

- **Grain.** `FactCountryYear`: one row per country × year, 2000–2024.
  `FactGeneration`: one row per country × year × source (7 sources).
- **Inclusion rule.** A country-year enters the facts only when electricity
  generation is present **and > 0** and the renewable share is known. That is
  why Niue (0.0 TWh, no share) is absent entirely and Lesotho 2023–2024
  (0.00 TWh, no share) are absent: **5,271** fact rows, not 5,273.
  `FactGeneration` is exactly 5,271 × 7 = **36,897** rows.
- **Countries.** 213 in `DimCountry_Full` (every ISO-coded country meeting the
  inclusion rule in at least one year); keys are alphabetical by country name.
  Aggregates such as "World" have no ISO code and are excluded.
- **Sources.** Coal 1, Gas 2, Nuclear 3, Hydro 4, Wind 5, Solar 6,
  Other Renewables 7. "Other Renewables" = total renewables − (hydro + wind
  + solar). Missing source values mean "no generation from that source" and
  are stored as 0.0 (e.g. Cambodia has no wind data, so its wind rows are 0.0
  and its "Other Renewables" still counts the residual).
- **Rounding.** `Generation_TWh` is stored to 2 decimals in both sizes.
  The 4-country extract files are rounded extracts: shares and CO₂ per capita
  to 2 dp, carbon intensity / total generation / demand to 1 dp; the `_Full`
  files keep full precision. `Share_Pct` = 100 × Generation_TWh /
  TotalGeneration_TWh.
- **CO₂ per capita** comes from the OWID CO₂ dataset (Global Carbon Project),
  joined on ISO code + year. 183 of the 5,271 fact rows have no CO₂ value
  (the CO₂ dataset does not cover every country-year); the column is left
  empty there rather than filled.

## Verified row counts

| Table | Rows | Grain |
|---|---|---|
| `data/analysis_subset.csv` | 100 | 4 countries × 25 years |
| `dashboard/powerbi/data/DimCountry_Full.csv` | 213 | country |
| `dashboard/powerbi/data/DimCountry.csv` | 4 | country (paper extract) |
| `dashboard/powerbi/data/DimYear.csv` | 25 | year, 2000–2024 |
| `dashboard/powerbi/data/DimSource.csv` | 7 | source |
| `dashboard/powerbi/data/FactCountryYear_Full.csv` | 5,271 | country × year |
| `dashboard/powerbi/data/FactCountryYear.csv` | 100 | country × year (paper extract) |
| `dashboard/powerbi/data/FactGeneration_Full.csv` | 36,897 | country × year × source |
| `dashboard/powerbi/data/FactGeneration.csv` | 700 | country × year × source (paper extract) |

## Known rounding notes (documented, not hidden)

- `FactGeneration_Full.Share_Pct` agrees with 100 × Generation / Total to
  within **0.002 pp** (133 of 36,897 rows differ by > 0.001 pp, all in
  "Other Renewables") — the original build's shares came from the OWID share
  columns, this rebuild computes them from generation. Immaterial.
- The 4-country extract files agree with the current OWID files to within
  **0.01 pp / 0.1 TWh** on a few rows where an exact `.x5` value rounds either
  way (7 of 100 share values, 3 of 100 carbon-intensity values). The
  full-precision `_Full` files reproduce exactly.
- The web dashboard's waterfall (Q17) splits "Bioenergy" (+46.75 TWh, the
  OWID `biofuel_electricity` column) and "Oil & other" (+2.56 TWh, oil plus
  other renewables excluding biofuel) out of the star schema's
  "Other Renewables" residual (+46.97 TWh). The 0.22 TWh difference is
  geothermal/other renewables; the bridge closes exactly either way
  (569.0 − 73.0 = 496.0 TWh).

## What this pipeline is not

There is no scheduled job, no incremental load and no data warehouse here:
the sources are two static annual datasets, and a full rebuild from the raw
files takes seconds. If the OWID datasets are re-downloaded in a later year,
re-run the pipeline and check `etl_pipeline.py --validate-only` — the
validation step exists precisely to catch silent source revisions.
