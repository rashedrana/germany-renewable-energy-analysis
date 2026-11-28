-- ============================================================================
-- queries.sql -- Business-question SQL for the Germany Energy Transition
-- dashboard (powerbi/QUESTIONS.md, Q1-Q19)
--
-- Dataset: Our World in Data energy + CO2, full extract, 213 countries,
-- 2000-2024, 36,897 fact rows. Star schema, one CSV per table in
-- powerbi/data/ :
--   FactCountryYear_Full  (country x year: renewable share, carbon
--                          intensity, CO2 per capita, total generation)
--   FactGeneration_Full   (country x year x source: generation TWh,
--                          share of that country-year total)
--   DimCountry_Full       (213 countries, CountryKey 1-213)
--   DimSource             (7 sources: Coal, Gas, Nuclear, Hydro, Wind,
--                          Solar, Other Renewables)
--   DimYear               (2000-2024, not needed by the queries below)
--
-- PORTABILITY: standard SQL only, runs unchanged in DuckDB and SQLite.
--   * Every numeric CSV column is wrapped in CAST(... AS REAL). SQLite
--     .import stores CSV values as TEXT, DuckDB read_csv_auto infers
--     DOUBLE, and the CAST is a no-op there, so the same file works in
--     both engines. YearKey is compared as CAST(... AS INTEGER) for the
--     same reason.
--   * No engine-only functions are used (no sqrt, no corr, no
--     DuckDB-only or SQLite-only helpers). RANK, CTEs, CASE pivots and
--     UNION ALL are standard SQL.
--
-- LOADING THE CSVs
--   DuckDB (from the repo root):
--     CREATE TABLE FactCountryYear_Full AS
--       SELECT * FROM read_csv_auto('dashboard/powerbi/data/FactCountryYear_Full.csv');
--     ... and the same for FactGeneration_Full, DimCountry_Full,
--     DimSource and DimYear.
--   SQLite (sqlite3 CLI, from the repo root):
--     .mode csv
--     .import --skip 1 dashboard/powerbi/data/FactCountryYear_Full.csv FactCountryYear_Full
--     ... and the same for the other four files. (Without --skip 1 the
--     header row is imported as data, so delete it afterwards.)
--
-- VERIFIED NUMBERS: every expected value is stated in a comment above its
-- query and comes from powerbi/QUESTIONS.md. The results were run against
-- the CSVs in SQLite and recorded in powerbi/sql_results.md.
-- ============================================================================


-- Q1 / Q7 -- Top-10 large producers (>= 100 TWh generation in 2024) by
-- renewable share, 2024, with rank.
-- Expected (QUESTIONS.md Q7): 36 large producers in total. Top 5 are
-- Norway 98.6%, Brazil 87.3%, Sweden 69.4%, Canada 64.3%, Germany 58.6%,
-- so Germany ranks #5.
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


-- Q2 / Q8 -- Renewable-share change 2000 -> 2024 among large producers,
-- fastest first.
-- Expected (QUESTIONS.md Q8): Germany first at +52.4 pp, then the United
-- Kingdom +48.0, the Netherlands +47.4, Spain +41.7 and Italy +31.3.
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


-- Q2 / Q8 (continued) -- The large producer that went backwards fastest.
-- Expected (QUESTIONS.md Q8): the Philippines, -22.4 pp, the only large
-- producer with a fall of more than 20 pp.
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


-- Q3 / Q15 -- How many countries ran on >= 90% renewable electricity
-- in 2024?
-- Expected (QUESTIONS.md Q15): 20 of the 195 countries with 2024 data.
SELECT
    COUNT(*) AS countries_at_least_90_pct_renewable_2024
FROM FactCountryYear_Full
WHERE CAST(YearKey AS INTEGER) = 2024
  AND CAST(RenewableShare_Pct AS REAL) >= 90;


-- Q3 / Q15 (continued) -- The countries at (almost) 100% renewable
-- electricity in 2024.
-- Expected (QUESTIONS.md Q15): seven countries at exactly 100% --
-- Albania, Bhutan, Democratic Republic of Congo, Ethiopia, Iceland,
-- Nepal and Paraguay. Costa Rica sits just below at 99.9% and is
-- therefore not listed here.
SELECT
    c.Country AS country,
    ROUND(CAST(f.RenewableShare_Pct AS REAL), 1) AS renewable_share_pct_2024
FROM FactCountryYear_Full AS f
JOIN DimCountry_Full AS c
    ON c.CountryKey = f.CountryKey
WHERE CAST(f.YearKey AS INTEGER) = 2024
  AND CAST(f.RenewableShare_Pct AS REAL) >= 99.95
ORDER BY c.Country;


-- Q3 / Q15 (continued) -- Where Germany ranks among ALL countries in 2024.
-- Expected (QUESTIONS.md Q15): Germany's 58.6% ranks #55 of 195 countries
-- worldwide, but #5 among the 36 large producers (Q1 above). Small hydro
-- states dominate the global list.
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


-- Q4 / Q16 -- Heatmap values: renewable share (%) for the 12 largest
-- producers (by 2024 generation) in 2000 / 2005 / 2010 / 2015 / 2020 / 2024.
-- Expected (QUESTIONS.md Q16): rows ordered by 2024 generation -- China,
-- United States, India, Russia, Japan, Brazil, Canada, South Korea, France,
-- Germany, Saudi Arabia, Iran. Germany improved most of the twelve,
-- 6.2% -> 58.6% (+52.4 pp). Brazil is the greenest big system (87.3%),
-- Saudi Arabia the coldest row at 2.2%, Iran next at 5.3%.
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


-- Q5 / Q17 -- Germany generation bridge 2000 -> 2024 by source, from the
-- 7-source star schema. The bridge closes exactly: 569.0 -> 496.0 TWh
-- (net -73.0 TWh).
-- Deltas are computed from the 1-decimal TWh values the dashboard shows,
-- so the bridge reproduces the published Q17 figures exactly: coal -190.4,
-- nuclear -169.6, wind +132.3, solar +74.1, gas +29.2, hydro +2.1 and
-- Other Renewables +47.0. Unrounded, the source deltas sum to -75.30 TWh.
-- DEFINITIONAL NOTES (do not change the dashboard numbers):
--   * The star schema has only 7 sources, so oil is not a source row.
--     The residual row below (+2.3 TWh) is the oil change, computed as
--     the total change minus the 7-source deltas. In the raw OWID data
--     (data/owid-energy-data.csv) oil_electricity is 18.05 TWh in 2000
--     and 20.39 TWh in 2024, a change of +2.34 TWh.
--   * The dashboard's Q17 waterfall splits bioenergy out of
--     Other Renewables using the raw OWID biofuel column: bioenergy
--     +46.75 TWh and oil and other +2.56 TWh. The star schema instead
--     carries Other Renewables as one line (+46.97 TWh), which is the
--     OWID other_renewable_electricity column: bioenergy 46.75 plus
--     other-renewable-excluding-biofuel 0.22. The dashboard's
--     oil-and-other +2.56 is oil +2.34 plus that same 0.22, so the two
--     bridges agree apart from this 0.22 TWh definitional difference
--     and both close exactly.
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


-- Q6 / Q19 -- Germany 2024 mix shares by source, as a share of total
-- generation (496.0 TWh from FactCountryYear_Full, not of the 7-source
-- subtotal).
-- Expected (QUESTIONS.md Q9): Wind 28.5%, Coal 21.4%, Gas 15.8%,
-- Solar 14.9%, Other Renewables 10.3%, Hydro 4.8%, Nuclear 0%.
-- The 7 sources cover 95.9% of total generation. The remaining 4.1%
-- (20.4 TWh) is oil, which is not a source in the star schema -- the
-- dashboard's Q19 waffle chart shows it as 4 squares of oil and other.
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


-- Q7 / Q11 -- Germany 2000-2024: the aggregates for the renewable-share
-- (x) vs carbon-intensity (y) relationship, plus the OLS slope.
-- The slope is cov/var, computed from the aggregates with no square root,
-- so it is standard SQL. The correlation r needs a square root, which is
-- not standard SQL, so it is NOT computed here. Verified result, stated
-- for the record: r = -0.95 (r = -0.954 over the 25 years) and the OLS
-- slope is -4.6 gCO2/kWh per percentage point of renewable share, i.e.
-- each extra point of renewable share is associated with about
-- 4.6 gCO2/kWh lower carbon intensity.
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
