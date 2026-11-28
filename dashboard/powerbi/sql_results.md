# SQL results — Germany Energy Transition dashboard

Every query in `queries.sql`, run against the star-schema CSVs in
`powerbi/data/` with the repository venv Python (`sqlite3` module,
in-memory database, CSVs loaded as TEXT exactly as `sqlite3 .import`
loads them). Each query is followed by its real result table.
Expected values are from `QUESTIONS.md`; verification notes sit
under each table.

## 1. Q1 / Q7 — Top-10 large producers (>= 100 TWh in 2024) by renewable share, 2024

```sql
SELECT
    RANK() OVER (ORDER BY CAST(f.RenewableShare_Pct AS REAL) DESC) AS rank,
    c.Country AS country,
    ROUND(CAST(f.RenewableShare_Pct AS REAL), 1) AS renewable_share_pct_2024,
    ROUND(CAST(f.TotalGeneration_TWh AS REAL), 1) AS total_generation_TWh_2024
FROM FactCountryYear_Full AS f
JOIN DimCountry_Full AS c
    ON c.CountryKey = f.CountryKey
WHERE CAST(f.YearKey AS INTEGER) = 2024
  AND CAST(f.TotalGeneration_TWh AS REAL) >= 100
ORDER BY CAST(f.RenewableShare_Pct AS REAL) DESC
LIMIT 10;
```

| rank | country | renewable_share_pct_2024 | total_generation_TWh_2024 |
| --- | --- | --- | --- |
| 1 | Norway | 98.6 | 157.1 |
| 2 | Brazil | 87.3 | 745.7 |
| 3 | Sweden | 69.4 | 172.2 |
| 4 | Canada | 64.3 | 636.8 |
| 5 | Germany | 58.6 | 496.0 |
| 6 | Spain | 57.3 | 280.9 |
| 7 | Netherlands | 50.7 | 122.3 |
| 8 | United Kingdom | 50.6 | 284.2 |
| 9 | Italy | 50.2 | 267.6 |
| 10 | Turkey | 45.6 | 341.2 |

Rows returned: 10

Verified: matches QUESTIONS.md Q7 exactly -- top 5 Norway 98.6%, Brazil 87.3%, Sweden 69.4%, Canada 64.3%, Germany 58.6%, so Germany ranks #5.

## 2. Q2 / Q8 — Fastest transitioners: renewable-share change 2000 -> 2024, top 5

```sql
SELECT
    c.Country AS country,
    ROUND(CAST(f24.RenewableShare_Pct AS REAL) - CAST(f00.RenewableShare_Pct AS REAL), 1)
        AS renewable_share_change_pp_2000_2024
FROM FactCountryYear_Full AS f24
JOIN FactCountryYear_Full AS f00
    ON f00.CountryKey = f24.CountryKey
   AND CAST(f00.YearKey AS INTEGER) = 2000
JOIN DimCountry_Full AS c
    ON c.CountryKey = f24.CountryKey
WHERE CAST(f24.YearKey AS INTEGER) = 2024
  AND CAST(f24.TotalGeneration_TWh AS REAL) >= 100
ORDER BY CAST(f24.RenewableShare_Pct AS REAL) - CAST(f00.RenewableShare_Pct AS REAL) DESC
LIMIT 5;
```

| country | renewable_share_change_pp_2000_2024 |
| --- | --- |
| Germany | 52.4 |
| United Kingdom | 48.0 |
| Netherlands | 47.4 |
| Spain | 41.7 |
| Italy | 31.3 |

Rows returned: 5

Verified: matches QUESTIONS.md Q8 -- Germany first at +52.4 pp, then United Kingdom +48.0, Netherlands +47.4, Spain +41.7; Italy +31.3 is 5th.

## 3. Q2 / Q8 — Slowest transitioner: renewable-share change 2000 -> 2024, bottom 1

```sql
SELECT
    c.Country AS country,
    ROUND(CAST(f24.RenewableShare_Pct AS REAL) - CAST(f00.RenewableShare_Pct AS REAL), 1)
        AS renewable_share_change_pp_2000_2024
FROM FactCountryYear_Full AS f24
JOIN FactCountryYear_Full AS f00
    ON f00.CountryKey = f24.CountryKey
   AND CAST(f00.YearKey AS INTEGER) = 2000
JOIN DimCountry_Full AS c
    ON c.CountryKey = f24.CountryKey
WHERE CAST(f24.YearKey AS INTEGER) = 2024
  AND CAST(f24.TotalGeneration_TWh AS REAL) >= 100
ORDER BY CAST(f24.RenewableShare_Pct AS REAL) - CAST(f00.RenewableShare_Pct AS REAL) ASC
LIMIT 1;
```

| country | renewable_share_change_pp_2000_2024 |
| --- | --- |
| Philippines | -22.4 |

Rows returned: 1

Verified: matches QUESTIONS.md Q8 -- Philippines -22.4 pp, the only large producer down more than 20 pp.

## 4. Q3 / Q15 — Countries with >= 90% renewable share in 2024

```sql
SELECT
    COUNT(*) AS countries_at_least_90_pct_renewable_2024
FROM FactCountryYear_Full
WHERE CAST(YearKey AS INTEGER) = 2024
  AND CAST(RenewableShare_Pct AS REAL) >= 90;
```

| countries_at_least_90_pct_renewable_2024 |
| --- |
| 20 |

Rows returned: 1

Verified: matches QUESTIONS.md Q15 -- 20 countries at >= 90% renewable share in 2024.

## 5. Q3 / Q15 — Countries at (almost) 100% renewable share in 2024

```sql
SELECT
    c.Country AS country,
    ROUND(CAST(f.RenewableShare_Pct AS REAL), 1) AS renewable_share_pct_2024
FROM FactCountryYear_Full AS f
JOIN DimCountry_Full AS c
    ON c.CountryKey = f.CountryKey
WHERE CAST(f.YearKey AS INTEGER) = 2024
  AND CAST(f.RenewableShare_Pct AS REAL) >= 99.95
ORDER BY c.Country;
```

| country | renewable_share_pct_2024 |
| --- | --- |
| Albania | 100.0 |
| Bhutan | 100.0 |
| Democratic Republic of Congo | 100.0 |
| Ethiopia | 100.0 |
| Iceland | 100.0 |
| Nepal | 100.0 |
| Paraguay | 100.0 |

Rows returned: 7

Verified: matches QUESTIONS.md Q15 -- exactly the seven named countries at 100.0% (Costa Rica sits just below at 99.9% and is excluded by the >= 99.95 cutoff).

## 6. Q3 / Q15 — Germany's rank among all countries in 2024

```sql
WITH deu AS (
    SELECT CAST(RenewableShare_Pct AS REAL) AS share
    FROM FactCountryYear_Full
    WHERE CountryKey = (SELECT CountryKey FROM DimCountry_Full WHERE Country = 'Germany')
      AND CAST(YearKey AS INTEGER) = 2024
)
SELECT
    (SELECT COUNT(*) + 1
     FROM FactCountryYear_Full
     WHERE CAST(YearKey AS INTEGER) = 2024
       AND CAST(RenewableShare_Pct AS REAL) > (SELECT share FROM deu))
        AS germany_rank_world_2024,
    ROUND((SELECT share FROM deu), 1) AS germany_renewable_share_pct_2024,
    (SELECT COUNT(*) FROM FactCountryYear_Full WHERE CAST(YearKey AS INTEGER) = 2024)
        AS countries_with_2024_data;
```

| germany_rank_world_2024 | germany_renewable_share_pct_2024 | countries_with_2024_data |
| --- | --- | --- |
| 55 | 58.6 | 195 |

Rows returned: 1

Verified: matches QUESTIONS.md Q15 -- Germany ranks #55 of 195 countries with 2024 data.

## 7. Q4 / Q16 — Heatmap: renewable share (%) of the 12 largest producers, 2000-2024

```sql
SELECT
    c.Country AS country,
    MAX(CASE WHEN CAST(f.YearKey AS INTEGER) = 2000 THEN ROUND(CAST(f.RenewableShare_Pct AS REAL), 1) END) AS share_2000,
    MAX(CASE WHEN CAST(f.YearKey AS INTEGER) = 2005 THEN ROUND(CAST(f.RenewableShare_Pct AS REAL), 1) END) AS share_2005,
    MAX(CASE WHEN CAST(f.YearKey AS INTEGER) = 2010 THEN ROUND(CAST(f.RenewableShare_Pct AS REAL), 1) END) AS share_2010,
    MAX(CASE WHEN CAST(f.YearKey AS INTEGER) = 2015 THEN ROUND(CAST(f.RenewableShare_Pct AS REAL), 1) END) AS share_2015,
    MAX(CASE WHEN CAST(f.YearKey AS INTEGER) = 2020 THEN ROUND(CAST(f.RenewableShare_Pct AS REAL), 1) END) AS share_2020,
    MAX(CASE WHEN CAST(f.YearKey AS INTEGER) = 2024 THEN ROUND(CAST(f.RenewableShare_Pct AS REAL), 1) END) AS share_2024,
    ROUND(MAX(CASE WHEN CAST(f.YearKey AS INTEGER) = 2024 THEN CAST(f.TotalGeneration_TWh AS REAL) END), 1)
        AS total_generation_TWh_2024
FROM FactCountryYear_Full AS f
JOIN DimCountry_Full AS c
    ON c.CountryKey = f.CountryKey
WHERE CAST(f.YearKey AS INTEGER) IN (2000, 2005, 2010, 2015, 2020, 2024)
  AND f.CountryKey IN (
      SELECT CountryKey
      FROM FactCountryYear_Full
      WHERE CAST(YearKey AS INTEGER) = 2024
      ORDER BY CAST(TotalGeneration_TWh AS REAL) DESC
      LIMIT 12
  )
GROUP BY c.Country
ORDER BY MAX(CASE WHEN CAST(f.YearKey AS INTEGER) = 2024 THEN CAST(f.TotalGeneration_TWh AS REAL) END) DESC;
```

| country | share_2000 | share_2005 | share_2010 | share_2015 | share_2020 | share_2024 | total_generation_TWh_2024 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| China | 16.6 | 16.2 | 18.7 | 24.0 | 28.1 | 33.7 | 10086.9 |
| United States | 9.2 | 8.7 | 10.3 | 13.6 | 20.3 | 24.1 | 4391.0 |
| India | 14.0 | 15.3 | 15.1 | 14.6 | 19.0 | 19.8 | 2036.5 |
| Russia | 18.7 | 18.1 | 16.1 | 15.8 | 19.9 | 18.1 | 1209.3 |
| Japan | 9.2 | 8.9 | 10.2 | 15.0 | 19.1 | 22.9 | 1016.4 |
| Brazil | 89.5 | 87.1 | 84.8 | 74.2 | 83.2 | 87.3 | 745.7 |
| Canada | 60.6 | 60.1 | 61.1 | 63.8 | 66.6 | 64.3 | 636.8 |
| South Korea | 1.4 | 1.0 | 1.1 | 2.8 | 7.0 | 9.7 | 625.4 |
| France | 12.7 | 9.7 | 13.6 | 16.0 | 23.7 | 27.2 | 561.8 |
| Germany | 6.2 | 10.3 | 16.9 | 29.4 | 44.4 | 58.6 | 496.0 |
| Saudi Arabia | 0.0 | 0.0 | 0.0 | 0.0 | 0.2 | 2.2 | 454.6 |
| Iran | 3.2 | 8.2 | 4.4 | 4.8 | 7.4 | 5.3 | 395.8 |

Rows returned: 12

Verified: matches QUESTIONS.md Q16 -- row order by 2024 generation, Germany 6.2% -> 58.6%, Brazil the greenest big system at 87.3%, Saudi Arabia the coldest row at 2.2%, Iran next at 5.3%, China +17.1 pp. One rounding note: the USA cells read 9.2% -> 24.1% (+14.9 pp from the rounded cells) while Q16 states +14.8 pp -- the unrounded change is +14.83 pp, so the 0.1 gap is a rounding artefact of the 1-decimal cells, not a data disagreement.

## 8. Q5 / Q17 — Germany generation bridge 2000 -> 2024 by source

```sql
WITH deu AS (
    SELECT CountryKey
    FROM DimCountry_Full
    WHERE Country = 'Germany'
),
src AS (
    SELECT
        s.Source AS source,
        ROUND(CAST(g00.Generation_TWh AS REAL), 1) AS generation_2000_TWh,
        ROUND(CAST(g24.Generation_TWh AS REAL), 1) AS generation_2024_TWh,
        ROUND(CAST(g24.Generation_TWh AS REAL), 1) - ROUND(CAST(g00.Generation_TWh AS REAL), 1) AS change_TWh
    FROM DimSource AS s
    JOIN FactGeneration_Full AS g00
        ON g00.SourceKey = s.SourceKey
       AND g00.CountryKey = (SELECT CountryKey FROM deu)
       AND CAST(g00.YearKey AS INTEGER) = 2000
    JOIN FactGeneration_Full AS g24
        ON g24.SourceKey = s.SourceKey
       AND g24.CountryKey = (SELECT CountryKey FROM deu)
       AND CAST(g24.YearKey AS INTEGER) = 2024
),
tot AS (
    SELECT
        ROUND(MAX(CASE WHEN CAST(YearKey AS INTEGER) = 2000 THEN CAST(TotalGeneration_TWh AS REAL) END), 1) AS tot2000,
        ROUND(MAX(CASE WHEN CAST(YearKey AS INTEGER) = 2024 THEN CAST(TotalGeneration_TWh AS REAL) END), 1) AS tot2024
    FROM FactCountryYear_Full
    WHERE CountryKey = (SELECT CountryKey FROM deu)
      AND CAST(YearKey AS INTEGER) IN (2000, 2024)
)
SELECT
    0 AS seq,
    'Total generation, 2000' AS item,
    tot2000 AS generation_2000_TWh,
    NULL AS generation_2024_TWh,
    NULL AS change_TWh
FROM tot
UNION ALL
SELECT
    1 AS seq,
    source AS item,
    generation_2000_TWh,
    generation_2024_TWh,
    change_TWh
FROM src
UNION ALL
SELECT
    2 AS seq,
    'Oil (residual -- not a source in the 7-source star schema)' AS item,
    NULL AS generation_2000_TWh,
    NULL AS generation_2024_TWh,
    (SELECT tot2024 - tot2000 FROM tot) - (SELECT SUM(change_TWh) FROM src) AS change_TWh
FROM tot
UNION ALL
SELECT
    3 AS seq,
    'Total generation, 2024' AS item,
    NULL AS generation_2000_TWh,
    tot2024 AS generation_2024_TWh,
    tot2024 - tot2000 AS change_TWh
FROM tot
ORDER BY seq, change_TWh;
```

| seq | item | generation_2000_TWh | generation_2024_TWh | change_TWh |
| --- | --- | --- | --- | --- |
| 0 | Total generation, 2000 | 569.0 |  |  |
| 1 | Coal | 296.7 | 106.3 | -190.4 |
| 1 | Nuclear | 169.6 | 0.0 | -169.6 |
| 1 | Hydro | 21.7 | 23.8 | 2.1 |
| 1 | Gas | 49.2 | 78.4 | 29.2 |
| 1 | Other Renewables | 4.3 | 51.3 | 47.0 |
| 1 | Solar | 0.0 | 74.1 | 74.1 |
| 1 | Wind | 9.3 | 141.6 | 132.3 |
| 2 | Oil (residual -- not a source in the 7-source star schema) |  |  | 2.3 |
| 3 | Total generation, 2024 |  | 496.0 | -73.0 |

Rows returned: 10

Verified: the bridge closes exactly, 569.0 -> 496.0 TWh (net -73.0). Source deltas match QUESTIONS.md Q17 (coal -190.4, nuclear -169.6, wind +132.3, solar +74.1, gas +29.2, hydro +2.1). Other Renewables is +47.0 here vs bioenergy +46.75 in the dashboard waterfall -- the 0.22 TWh definitional difference documented in queries.sql. The oil residual is +2.3 TWh (unrounded +2.34, OWID oil_electricity 18.05 -> 20.39 TWh).

## 9. Q6 / Q19 — Germany 2024 mix shares by source

```sql
WITH deu AS (
    SELECT CountryKey
    FROM DimCountry_Full
    WHERE Country = 'Germany'
),
tot AS (
    SELECT CAST(TotalGeneration_TWh AS REAL) AS total
    FROM FactCountryYear_Full
    WHERE CountryKey = (SELECT CountryKey FROM deu)
      AND CAST(YearKey AS INTEGER) = 2024
),
mix AS (
    SELECT
        s.Source AS source,
        CAST(g.Generation_TWh AS REAL) AS generation_raw_TWh,
        ROUND(CAST(g.Generation_TWh AS REAL), 1) AS generation_TWh,
        ROUND(100.0 * CAST(g.Generation_TWh AS REAL) / (SELECT total FROM tot), 1) AS share_pct
    FROM FactGeneration_Full AS g
    JOIN DimSource AS s
        ON s.SourceKey = g.SourceKey
    WHERE g.CountryKey = (SELECT CountryKey FROM deu)
      AND CAST(g.YearKey AS INTEGER) = 2024
)
SELECT 0 AS seq, source, generation_TWh, share_pct FROM mix
UNION ALL
SELECT
    1 AS seq,
    'Oil (residual -- not a source in the 7-source star schema)' AS source,
    ROUND((SELECT total FROM tot) - (SELECT SUM(generation_raw_TWh) FROM mix), 1) AS generation_TWh,
    ROUND(100.0 * ((SELECT total FROM tot) - (SELECT SUM(generation_raw_TWh) FROM mix)) / (SELECT total FROM tot), 1) AS share_pct
FROM tot
ORDER BY seq, share_pct DESC;
```

| seq | source | generation_TWh | share_pct |
| --- | --- | --- | --- |
| 0 | Wind | 141.6 | 28.5 |
| 0 | Coal | 106.3 | 21.4 |
| 0 | Gas | 78.4 | 15.8 |
| 0 | Solar | 74.1 | 14.9 |
| 0 | Other Renewables | 51.3 | 10.3 |
| 0 | Hydro | 23.8 | 4.8 |
| 0 | Nuclear | 0.0 | 0.0 |
| 1 | Oil (residual -- not a source in the 7-source star schema) | 20.4 | 4.1 |

Rows returned: 8

Verified: matches QUESTIONS.md Q9 exactly -- Wind 28.5%, Coal 21.4%, Gas 15.8%, Solar 14.9%, Other Renewables 10.3%, Hydro 4.8%, Nuclear 0%. The residual is oil, 20.4 TWh / 4.1% of total generation. (The 1-decimal shares sum to 99.8% with the residual, a 0.2 pp rounding effect; unrounded they sum to 100%.)

## 10. Q7 / Q11 — Germany 2000-2024: OLS aggregates, renewable share vs carbon intensity

```sql
SELECT
    COUNT(*) AS n_years,
    ROUND(SUM(x), 2) AS sum_renewable_share,
    ROUND(SUM(y), 2) AS sum_carbon_intensity,
    ROUND(SUM(x * x), 2) AS sum_x_squared,
    ROUND(SUM(y * y), 2) AS sum_y_squared,
    ROUND(SUM(x * y), 2) AS sum_x_times_y,
    ROUND(
        (1.0 * COUNT(*) * SUM(x * y) - SUM(x) * SUM(y))
        / (1.0 * COUNT(*) * SUM(x * x) - SUM(x) * SUM(x)),
        2
    ) AS ols_slope_gCO2_per_kWh_per_pp
FROM (
    SELECT
        CAST(RenewableShare_Pct AS REAL) AS x,
        CAST(CarbonIntensity_gCO2_kWh AS REAL) AS y
    FROM FactCountryYear_Full
    WHERE CountryKey = (SELECT CountryKey FROM DimCountry_Full WHERE Country = 'Germany')
      AND CAST(YearKey AS INTEGER) BETWEEN 2000 AND 2024
);
```

| n_years | sum_renewable_share | sum_carbon_intensity | sum_x_squared | sum_y_squared | sum_x_times_y | ols_slope_gCO2_per_kWh_per_pp |
| --- | --- | --- | --- | --- | --- | --- |
| 25 | 625.91 | 12342.41 | 21425.66 | 6224788.61 | 282787.5 | -4.56 |

Rows returned: 1

Verified: slope -4.56 gCO2/kWh per pp, i.e. -4.6 as stated in QUESTIONS.md Q11 and the paper; n = 25 years. The correlation r = -0.954 (stated as -0.95) was checked in Python, not in SQL, because r needs a square root, which is not standard SQL.
