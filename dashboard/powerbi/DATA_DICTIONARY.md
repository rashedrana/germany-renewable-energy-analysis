# Data Dictionary — Germany Energy Transition (Power BI model)

Star-schema tables in `dashboard/powerbi/data/`. Two sizes of each fact and
country table exist: the paper's 4-country extract (Germany, France, Poland,
Denmark) and the full dataset (`*_Full.csv`, 213 countries). The 4-country
files are rounded extracts (shares and CO₂ per capita to 2 dp, carbon
intensity / generation / demand to 1 dp); the `_Full` files keep full
precision. See `PIPELINE.md` for how every file is built and validated.

Source: Our World in Data energy dataset (Ember Electricity Data Explorer;
Energy Institute Statistical Review) and OWID CO₂ dataset (Global Carbon
Project). Licence of the source data: CC BY.

## Model

```
DimCountry (CountryKey) ──> FactCountryYear <── DimYear (YearKey)
DimCountry (CountryKey) ──> FactGeneration  <── DimYear (YearKey)
DimSource  (SourceKey)  ──> FactGeneration
```

## DimCountry / DimCountry_Full — country dimension

| Column | Type | Description |
|---|---|---|
| CountryKey | integer, PK | Surrogate key. Full file: alphabetical by country name (Afghanistan = 1 … Zimbabwe = 213). 4-country file: Germany = 1, France = 2, Poland = 3, Denmark = 4. |
| Country | text | Country name as in the OWID dataset (e.g. "Democratic Republic of Congo"). |
| ISO_Code | text | ISO 3166-1 alpha-3 code (e.g. DEU). Aggregates such as "World" have no ISO code and are excluded. |

Rows: 4 (extract) / 213 (full).

## DimYear — year dimension

| Column | Type | Description |
|---|---|---|
| YearKey | integer, PK | The year itself (2000–2024). |
| Year | integer | Calendar year. |
| Decade | text | Decade band (`2000s`, `2010s`, `2020s`). |

Rows: 25.

## DimSource — electricity source dimension

| Column | Type | Description |
|---|---|---|
| SourceKey | integer, PK | 1 Coal, 2 Gas, 3 Nuclear, 4 Hydro, 5 Wind, 6 Solar, 7 Other Renewables. |
| Source | text | Source name. |
| Category | text | Fossil (Coal, Gas), Nuclear, Renewable (Hydro, Wind, Solar, Other Renewables). |
| IsRenewable | integer 0/1 | 1 for Hydro, Wind, Solar, Other Renewables. |

Rows: 7. "Other Renewables" = total renewables − (hydro + wind + solar),
i.e. mostly bioenergy and geothermal.

## FactCountryYear / FactCountryYear_Full — country-year indicators

Grain: one row per country × year, 2000–2024. A row exists only when
electricity generation is present and > 0 and the renewable share is known
(see `PIPELINE.md` — this excludes Niue entirely and Lesotho 2023–2024).

| Column | Type | Description |
|---|---|---|
| CountryKey | integer, FK → DimCountry | Country. |
| YearKey | integer, FK → DimYear | Year. |
| RenewableShare_Pct | float | Share of electricity from renewable sources, %. Germany 2024: 58.64. |
| CarbonIntensity_gCO2_kWh | float | CO₂ emitted per kWh of electricity, gCO₂/kWh. Germany 2024: 336.4. |
| CO2_PerCapita_t | float | Total CO₂ emissions per capita, tonnes. Empty for 183 of 5,271 rows where the CO₂ dataset has no value for that country-year. Germany 2024: 6.79. |
| TotalGeneration_TWh | float | Total electricity generation, TWh. Germany 2024: 496.0. |
| ElectricityDemand_TWh | float | Electricity demand, TWh. Germany 2024: 522.3. |
| Population | integer | Population. Full file only (the 4-country extract has no Population column). |

Rows: 100 (extract) / 5,271 (full).

## FactGeneration / FactGeneration_Full — generation by source

Grain: one row per country × year × source. Exactly 7 rows per
`FactCountryYear` row (5,271 × 7 = 36,897). Missing source values are stored
as 0.0 ("no generation from that source").

| Column | Type | Description |
|---|---|---|
| CountryKey | integer, FK → DimCountry | Country. |
| YearKey | integer, FK → DimYear | Year. |
| SourceKey | integer, FK → DimSource | Electricity source. |
| Generation_TWh | float | Electricity generated from this source, TWh (2 dp). |
| Share_Pct | float | Share of the country's total generation from this source, % (= 100 × Generation_TWh / TotalGeneration_TWh). |

Rows: 700 (extract) / 36,897 (full).

## Related files

| File | Contents |
|---|---|
| `data/analysis_subset.csv` | The same 4 countries × 25 years in OWID's wide format (the paper's working extract, 100 rows). |
| `data/owid-energy-data.csv`, `data/owid-co2-data.csv` | The full OWID source downloads. |
| `energy.db` | SQLite database built from `data/analysis_subset.csv` (`src/build_db.py`). |
| `sql/queries.sql` | 9 SQL queries answering the paper's questions over the `energy` table. |
| `dashboard/powerbi/queries.sql` | SQL queries answering the dashboard's business questions (Q7, Q8, Q11, Q15–Q17, Q19) over this star schema, with results in `sql_results.md`. |
| `dashboard/powerbi/QUESTIONS.md` | The 19 business questions and their verified answers. |
| `dashboard/powerbi/DAX_measures.md` | DAX measures for the Power BI report. |
| `dashboard/powerbi/model_diagram.md` | Star-schema diagram and relationships. |
