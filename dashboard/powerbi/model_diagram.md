# Star Schema — Germany Energy Transition (Power BI model)

```
                    DimCountry                      DimYear
                 (CountryKey PK)                 (YearKey PK)
                  Country, ISO_Code               Year, Decade
                        |                              |
          +-------------+--------------+---------------+
          |                            |
  FactCountryYear              FactGeneration
  (CountryKey FK,              (CountryKey FK,
   YearKey FK,                  YearKey FK,
   RenewableShare_Pct,          SourceKey FK,
   CarbonIntensity_gCO2_kWh,    Generation_TWh,
   CO2_PerCapita_t,             Share_Pct)
   TotalGeneration_TWh,               |
   ElectricityDemand_TWh)             |
                                 DimSource
                              (SourceKey PK)
                               Source, Category,
                               IsRenewable
```

## Tables (CSVs in `data/`)
| Table | Grain | Rows | Contents |
|---|---|---|---|
| FactGeneration | country × year × source | 700 | Generation (TWh) and share (%) per source |
| FactCountryYear | country × year | 100 | Renewable share, carbon intensity, CO₂ per capita, total generation, demand |
| DimCountry | country | 4 | Germany, France, Poland, Denmark |
| DimYear | year | 25 | 2000–2024, with decade band |
| DimSource | source | 7 | Coal, Gas, Nuclear, Hydro, Wind, Solar, Other Renewables (with Category + IsRenewable flag) |

## Design notes
- Two fact tables share the conformed DimCountry and DimYear dimensions — the
  standard way to combine source-level detail (FactGeneration) with country-year
  indicators that have no source dimension (carbon intensity, CO₂ per capita).
- "Other Renewables" = total renewables − (hydro + wind + solar), i.e. mostly
  bioenergy and geothermal, computed during data prep so the mix stacks to the
  published totals.
- Source data: `data/analysis_subset.csv` of this repository (Our World in Data
  energy + CO₂ datasets), the same dataset used in the research paper — the
  dashboard and the paper therefore always agree number for number.
