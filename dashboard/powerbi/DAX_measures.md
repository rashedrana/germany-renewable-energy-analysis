# DAX Measures — Germany Energy Transition (Power BI)

Model tables: `FactGeneration`, `FactCountryYear`, `DimCountry`, `DimYear`, `DimSource`.
Create a dedicated measure table (`_Measures`) in Power BI and paste these in one by one.
All measures respond to the Year and Country slicers unless stated otherwise.

---

## Core generation measures

```dax
Total Generation (TWh) =
SUM ( FactGeneration[Generation_TWh] )
```

```dax
Renewable Generation (TWh) =
CALCULATE (
    [Total Generation (TWh)],
    DimSource[IsRenewable] = TRUE
)
```

```dax
Renewable Share % =
DIVIDE ( [Renewable Generation (TWh)], [Total Generation (TWh)] ) * 100
```

```dax
Fossil Generation (TWh) =
CALCULATE (
    [Total Generation (TWh)],
    DimSource[Category] = "Fossil"
)
```

```dax
Coal Share % =
DIVIDE (
    CALCULATE ( [Total Generation (TWh)], DimSource[Source] = "Coal" ),
    [Total Generation (TWh)]
) * 100
```

```dax
Wind + Solar Share % =
DIVIDE (
    CALCULATE (
        [Total Generation (TWh)],
        DimSource[Source] IN { "Wind", "Solar" }
    ),
    [Total Generation (TWh)]
) * 100
```

## KPI / time-intelligence measures

```dax
Renewable Share % (2000) =
CALCULATE ( [Renewable Share %], DimYear[Year] = 2000 )
```

```dax
Renewable Share Change vs 2000 (pp) =
[Renewable Share %] - [Renewable Share % (2000)]
```

```dax
Renewable Share YoY Change (pp) =
VAR ThisYear = [Renewable Share %]
VAR PrevYear =
    CALCULATE (
        [Renewable Share %],
        DimYear[Year] = MAX ( DimYear[Year] ) - 1
    )
RETURN
    ThisYear - PrevYear
```

```dax
Total Generation YoY % =
VAR ThisYear = [Total Generation (TWh)]
VAR PrevYear =
    CALCULATE (
        [Total Generation (TWh)],
        DimYear[Year] = MAX ( DimYear[Year] ) - 1
    )
RETURN
    DIVIDE ( ThisYear - PrevYear, PrevYear ) * 100
```

## Country-year metric measures (FactCountryYear)

```dax
Avg Carbon Intensity =
AVERAGE ( FactCountryYear[CarbonIntensity_gCO2_kWh] )
```

```dax
Avg CO2 per Capita =
AVERAGE ( FactCountryYear[CO2_PerCapita_t] )
```

```dax
Carbon Intensity Change vs 2000 =
[Avg Carbon Intensity]
    - CALCULATE ( [Avg Carbon Intensity], DimYear[Year] = 2000 )
```

```dax
Country Rank by Renewable Share =
RANKX (
    ALL ( DimCountry[Country] ),
    [Renewable Share %],
    ,
    DESC,
    DENSE
)
```

## Display helpers

```dax
Selected Country =
SELECTEDVALUE ( DimCountry[Country], "All countries" )
```

```dax
Selected Year Label =
"Focus year: " & SELECTEDVALUE ( DimYear[Year], 2024 )
```

---

## Additional measures — retrofit visuals (Q15–Q19)

For the choropleth map (Q15) and heatmap (Q16) — the map colours by the
existing `Renewable Share %`; this companion counts how many countries clear
a threshold in the selected year:

```dax
Countries Above Renewable Threshold =
VAR Threshold = 90
RETURN
    CALCULATE (
        DISTINCTCOUNT ( DimCountry[Country] ),
        FILTER (
            ALL ( DimCountry[Country] ),
            [Renewable Share %] >= Threshold
        )
    )
```
(2024, threshold 90 → 20 countries; threshold 100 → 7 countries.)

For the waterfall bridge (Q17) — change in generation per source between two
slicer-independent anchor years:

```dax
Generation Change 2000-2024 (TWh) =
CALCULATE ( [Total Generation (TWh)], DimYear[Year] = 2024 )
    - CALCULATE ( [Total Generation (TWh)], DimYear[Year] = 2000 )
```
Note: the star model's `Other Renewables` source combines bioenergy with
other renewables, and oil is not a separate source in `FactGeneration`; the
web edition's bridge splits bioenergy out and adds oil & other from the raw
OWID columns (`biofuel_electricity`, `oil_electricity`), so its start/end
totals (569.0 / 496.0 TWh) tie to `FactCountryYear`, not to the
`FactGeneration` source sum.

For the slope chart (Q18):

```dax
Renewable Share Change 2000-2024 (pp) =
CALCULATE ( [Renewable Share %], DimYear[Year] = 2024 )
    - CALCULATE ( [Renewable Share %], DimYear[Year] = 2000 )
```

For the waffle chart (Q19) — source share of the selected country-year:

```dax
Source Share % =
DIVIDE (
    [Total Generation (TWh)],
    CALCULATE ( [Total Generation (TWh)], ALL ( DimSource[Source] ) )
) * 100
```
Feed it to a 100-cell waffle visual; the web edition rounds by largest
remainder so the cells sum to exactly 100.

---

Notes
- `DimSource[IsRenewable]` is stored as 1/0 in the CSV; in Power Query convert it to True/False (or use `= 1` in the CALCULATE filters above).
- KPI cards on Page 1 use: Renewable Share %, Avg Carbon Intensity, Avg CO2 per Capita, Total Generation (TWh), Coal Share %, Wind + Solar Share % — each with its "vs 2000" companion measure as the delta visual.
