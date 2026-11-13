-- =====================================================================
-- Germany's renewable electricity transition, 2000-2024 - SQL analysis
-- Database: energy.db, table `energy` (built from data/analysis_subset.csv
-- by src/build_db.py). One row per country-year for Germany, France,
-- Poland and Denmark.
-- =====================================================================

-- Q1. Germany's renewable share of electricity, every year 2000-2024
SELECT year, ROUND(renewables_share_elec, 2) AS renewables_share_pct
FROM energy
WHERE iso_code = 'DEU'
ORDER BY year;

-- Q2. First year each country passed 50% renewable electricity
SELECT country, MIN(year) AS first_year_over_50pct
FROM energy
WHERE renewables_share_elec >= 50
GROUP BY country
ORDER BY first_year_over_50pct;

-- Q3. Germany's electricity mix in 2000 vs 2024 (share of generation, %)
SELECT year,
       ROUND(renewables_share_elec, 2) AS renewables,
       ROUND(coal_share_elec, 2)       AS coal,
       ROUND(nuclear_share_elec, 2)    AS nuclear,
       ROUND(gas_share_elec, 2)        AS gas
FROM energy
WHERE iso_code = 'DEU' AND year IN (2000, 2024)
ORDER BY year;

-- Q4. Average annual growth of the renewable share, in percentage points,
--     per decade, Germany
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

-- Q5. Wind and solar generation (TWh) in Germany at five-year intervals
SELECT year,
       ROUND(wind_electricity, 2)  AS wind_twh,
       ROUND(solar_electricity, 2) AS solar_twh,
       ROUND(wind_electricity + solar_electricity, 2) AS wind_plus_solar_twh
FROM energy
WHERE iso_code = 'DEU' AND year % 5 = 0
ORDER BY year;

-- Q6. The year coal stopped being Germany's largest single source:
--     first year renewables generation exceeded coal generation
SELECT MIN(year) AS first_year_renewables_beat_coal
FROM energy
WHERE iso_code = 'DEU' AND renewables_electricity > coal_electricity;

-- Q7. Carbon intensity of electricity in 2024, ranked across the four
--     countries, with each country's dominant low-carbon strategy visible
SELECT country,
       ROUND(renewables_share_elec, 2) AS renewables_pct,
       ROUND(nuclear_share_elec, 2)    AS nuclear_pct,
       ROUND(carbon_intensity_elec, 1) AS gco2_per_kwh
FROM energy
WHERE year = 2024
ORDER BY gco2_per_kwh;

-- Q8. Germany's electricity demand around the two shocks:
--     COVID-19 (2020) and the 2022 European energy crisis
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

-- Q9. Which country cut its CO2 per capita the most between 2000 and 2024?
SELECT a.country,
       ROUND(a.co2_per_capita, 2) AS co2_per_capita_2000,
       ROUND(b.co2_per_capita, 2) AS co2_per_capita_2024,
       ROUND(100.0 * (a.co2_per_capita - b.co2_per_capita)
             / a.co2_per_capita, 1) AS reduction_pct
FROM energy a
JOIN energy b ON a.iso_code = b.iso_code AND b.year = 2024
WHERE a.year = 2000
ORDER BY reduction_pct DESC;
