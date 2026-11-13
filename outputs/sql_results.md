# SQL query results

Produced by `src/build_db.py` running `sql/queries.sql` against `energy.db`.

## Q1. Germany's renewable share of electricity, every year 2000-2024

```sql
SELECT year, ROUND(renewables_share_elec, 2) AS renewables_share_pct
FROM energy
WHERE iso_code = 'DEU'
ORDER BY year;
```

|   year |   renewables_share_pct |
|-------:|-----------------------:|
|   2000 |                   6.22 |
|   2001 |                   6.54 |
|   2002 |                   7.62 |
|   2003 |                   7.75 |
|   2004 |                   9.51 |
|   2005 |                  10.34 |
|   2006 |                  11.51 |
|   2007 |                  14.17 |
|   2008 |                  14.93 |
|   2009 |                  16.34 |
|   2010 |                  16.89 |
|   2011 |                  20.57 |
|   2012 |                  23.14 |
|   2013 |                  24.13 |
|   2014 |                  26.17 |
|   2015 |                  29.43 |
|   2016 |                  29.48 |
|   2017 |                  33.47 |
|   2018 |                  35.26 |
|   2019 |                  40.19 |
|   2020 |                  44.37 |
|   2021 |                  40.17 |
|   2022 |                  44.37 |
|   2023 |                  54.69 |
|   2024 |                  58.64 |

## Q2. First year each country passed 50% renewable electricity

```sql
SELECT country, MIN(year) AS first_year_over_50pct
FROM energy
WHERE renewables_share_elec >= 50
GROUP BY country
ORDER BY first_year_over_50pct;
```

| country   |   first_year_over_50pct |
|:----------|------------------------:|
| Denmark   |                    2014 |
| Germany   |                    2023 |

## Q3. Germany's electricity mix in 2000 vs 2024 (share of generation, %)

```sql
SELECT year,
       ROUND(renewables_share_elec, 2) AS renewables,
       ROUND(coal_share_elec, 2)       AS coal,
       ROUND(nuclear_share_elec, 2)    AS nuclear,
       ROUND(gas_share_elec, 2)        AS gas
FROM energy
WHERE iso_code = 'DEU' AND year IN (2000, 2024)
ORDER BY year;
```

|   year |   renewables |   coal |   nuclear |   gas |
|-------:|-------------:|-------:|----------:|------:|
|   2000 |         6.22 |  52.15 |     29.81 |  8.65 |
|   2024 |        58.64 |  21.44 |      0    | 15.81 |

## Q4. Average annual growth of the renewable share, in percentage points,

```sql
SELECT CASE WHEN year < 2010 THEN '2000s'
            WHEN year < 2020 THEN '2010s'
            ELSE '2020s' END AS decade,
       ROUND(AVG(renewables_share_elec), 2) AS avg_share_pct,
       ROUND(MAX(renewables_share_elec) - MIN(renewables_share_elec), 2)
           AS growth_within_decade_points
FROM energy
WHERE iso_code = 'DEU'
GROUP BY decade
ORDER BY decade;
```

| decade   |   avg_share_pct |   growth_within_decade_points |
|:---------|----------------:|------------------------------:|
| 2000s    |           10.49 |                         10.12 |
| 2010s    |           27.87 |                         23.3  |
| 2020s    |           48.45 |                         18.48 |

## Q5. Wind and solar generation (TWh) in Germany at five-year intervals

```sql
SELECT year,
       ROUND(wind_electricity, 2)  AS wind_twh,
       ROUND(solar_electricity, 2) AS solar_twh,
       ROUND(wind_electricity + solar_electricity, 2) AS wind_plus_solar_twh
FROM energy
WHERE iso_code = 'DEU' AND year % 5 = 0
ORDER BY year;
```

|   year |   wind_twh |   solar_twh |   wind_plus_solar_twh |
|-------:|-----------:|------------:|----------------------:|
|   2000 |       9.35 |        0    |                  9.35 |
|   2005 |      27.77 |        1.31 |                 29.08 |
|   2010 |      38.55 |       11.96 |                 50.51 |
|   2015 |      80.62 |       38.08 |                118.7  |
|   2020 |     132.11 |       49.5  |                181.61 |

## Q6. The year coal stopped being Germany's largest single source:

```sql
SELECT MIN(year) AS first_year_renewables_beat_coal
FROM energy
WHERE iso_code = 'DEU' AND renewables_electricity > coal_electricity;
```

|   first_year_renewables_beat_coal |
|----------------------------------:|
|                              2019 |

## Q7. Carbon intensity of electricity in 2024, ranked across the four

```sql
SELECT country,
       ROUND(renewables_share_elec, 2) AS renewables_pct,
       ROUND(nuclear_share_elec, 2)    AS nuclear_pct,
       ROUND(carbon_intensity_elec, 1) AS gco2_per_kwh
FROM energy
WHERE year = 2024
ORDER BY gco2_per_kwh;
```

| country   |   renewables_pct |   nuclear_pct |   gco2_per_kwh |
|:----------|-----------------:|--------------:|---------------:|
| France    |            27.18 |         67.72 |           40.5 |
| Denmark   |            89.19 |          0    |          131.8 |
| Germany   |            58.64 |          0    |          336.4 |
| Poland    |            31.15 |          0    |          608.2 |

## Q8. Germany's electricity demand around the two shocks:

```sql
WITH deu AS (
    SELECT year, electricity_demand, coal_share_elec, gas_share_elec,
           LAG(electricity_demand) OVER (ORDER BY year) AS prev_demand
    FROM energy
    WHERE iso_code = 'DEU'
)
SELECT year,
       ROUND(electricity_demand, 1) AS demand_twh,
       ROUND(100.0 * (electricity_demand - prev_demand) / prev_demand, 1)
           AS change_vs_prev_year_pct,
       ROUND(coal_share_elec, 2) AS coal_share_pct,
       ROUND(gas_share_elec, 2)  AS gas_share_pct
FROM deu
WHERE year BETWEEN 2018 AND 2024
ORDER BY year;
```

|   year |   demand_twh |   change_vs_prev_year_pct |   coal_share_pct |   gas_share_pct |
|-------:|-------------:|--------------------------:|-----------------:|----------------:|
|   2018 |        583.5 |                      -1.4 |            36.09 |           12.9  |
|   2019 |        567.4 |                      -2.8 |            28.57 |           15    |
|   2020 |        547.7 |                      -3.5 |            23.75 |           16.76 |
|   2021 |        560.3 |                       2.3 |            28.45 |           15.6  |
|   2022 |        539.6 |                      -3.7 |            31.74 |           13.95 |
|   2023 |        515.9 |                      -4.4 |            24.63 |           15.13 |
|   2024 |        522.3 |                       1.2 |            21.44 |           15.81 |

## Q9. Which country cut its CO2 per capita the most between 2000 and 2024?

```sql
SELECT a.country,
       ROUND(a.co2_per_capita, 2) AS co2_per_capita_2000,
       ROUND(b.co2_per_capita, 2) AS co2_per_capita_2024,
       ROUND(100.0 * (a.co2_per_capita - b.co2_per_capita)
             / a.co2_per_capita, 1) AS reduction_pct
FROM energy a
JOIN energy b ON a.iso_code = b.iso_code AND b.year = 2024
WHERE a.year = 2000
ORDER BY reduction_pct DESC;
```

| country   |   co2_per_capita_2000 |   co2_per_capita_2024 |   reduction_pct |
|:----------|----------------------:|----------------------:|----------------:|
| Denmark   |                 10.17 |                  4.52 |            55.5 |
| France    |                  6.86 |                  3.93 |            42.8 |
| Germany   |                 10.99 |                  6.79 |            38.2 |
| Poland    |                  8.29 |                  7.23 |            12.9 |
