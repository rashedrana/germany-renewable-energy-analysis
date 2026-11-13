"""Germany's renewable electricity transition, 2000-2024.

Main analysis for the project *germany-renewable-energy-analysis*.
Data: Our World in Data energy dataset (owid-energy-data.csv), which is
compiled from Ember's Electricity Data Explorer and the Energy Institute
Statistical Review.

The script:
  1. extracts Germany + three comparator countries (France, Poland, Denmark)
     for 2000-2024 into data/analysis_subset.csv,
  2. computes every headline finding used in the README and the paper draft,
  3. writes the numbers to outputs/results.json so that no number in any
     document is typed by hand.
"""
import json
import numpy as np
import pandas as pd

RAW = "data/owid-energy-data.csv"
COUNTRIES = ["DEU", "FRA", "POL", "DNK"]
YEARS = range(2000, 2025)

COLS = [
    "country", "iso_code", "year", "population",
    "electricity_generation", "renewables_electricity", "wind_electricity",
    "solar_electricity", "hydro_electricity", "coal_electricity",
    "gas_electricity", "nuclear_electricity",
    "renewables_share_elec", "wind_share_elec", "solar_share_elec",
    "hydro_share_elec", "coal_share_elec", "gas_share_elec",
    "nuclear_share_elec", "carbon_intensity_elec", "co2_per_capita",
    "energy_per_capita", "electricity_demand",
]


def cagr(first, last, n_years):
    return (last / first) ** (1 / n_years) - 1


def linfit(x, y):
    """Simple OLS: returns slope, intercept, Pearson r, R^2."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    slope, intercept = np.polyfit(x, y, 1)
    r = np.corrcoef(x, y)[0, 1]
    return slope, intercept, r, r ** 2


def main():
    df = pd.read_csv(RAW, usecols=lambda c: c in COLS and c != "co2_per_capita")
    co2 = pd.read_csv("data/owid-co2-data.csv",
                      usecols=["iso_code", "year", "co2_per_capita"])
    df = df.merge(co2, on=["iso_code", "year"], how="left")
    sub = df[df.iso_code.isin(COUNTRIES) & df.year.isin(YEARS)].copy()
    sub = sub.sort_values(["iso_code", "year"])
    sub.to_csv("data/analysis_subset.csv", index=False)

    de = sub[sub.iso_code == "DEU"].set_index("year")
    R = {"data_rows_germany": int(len(de))}

    # --- Finding 1: renewable share trajectory -------------------------------
    r00, r24 = de.loc[2000, "renewables_share_elec"], de.loc[2024, "renewables_share_elec"]
    R["renew_share_2000"] = round(float(r00), 2)
    R["renew_share_2024"] = round(float(r24), 2)
    R["renew_share_multiple"] = round(float(r24 / r00), 2)
    for yr in range(2000, 2025):  # first year renewables passed 50%
        if de.loc[yr, "renewables_share_elec"] >= 50:
            R["first_year_renew_over_50"] = int(yr)
            break
    slope, intercept, r, r2 = linfit(de.index, de["renewables_share_elec"])
    R["renew_share_trend_per_year"] = round(float(slope), 3)
    R["renew_share_trend_r2"] = round(float(r2), 3)
    # naive linear projection of the 80%-by-2030 target year
    R["projected_year_80pct_linear"] = int(np.ceil((80 - intercept) / slope))

    # --- Finding 2: wind and solar drove the growth --------------------------
    for src, col in [("wind", "wind_electricity"), ("solar", "solar_electricity")]:
        series = de[col]
        base_year = int(series[series > 0].index.min())  # solar is 0.0 in 2000
        a, b = series.loc[base_year], series.loc[2024]
        R[f"{src}_base_year"] = base_year
        R[f"{src}_twh_base"] = round(float(a), 2)
        R[f"{src}_twh_2000"] = round(float(series.loc[2000]), 2)
        R[f"{src}_twh_2024"] = round(float(b), 2)
        R[f"{src}_cagr_pct"] = round(float(cagr(a, b, 2024 - base_year)) * 100, 2)
        R[f"{src}_share_2024"] = round(float(de.loc[2024, f"{src}_share_elec"]), 2)
    wind_add = de.loc[2024, "wind_electricity"] - de.loc[2000, "wind_electricity"]
    solar_add = de.loc[2024, "solar_electricity"] - de.loc[2000, "solar_electricity"]
    total_add = de.loc[2024, "renewables_electricity"] - de.loc[2000, "renewables_electricity"]
    R["wind_plus_solar_share_of_renewable_growth_pct"] = round(
        float((wind_add + solar_add) / total_add) * 100, 1)
    R["renewables_twh_2000"] = round(float(de.loc[2000, "renewables_electricity"]), 2)
    R["renewables_twh_2024"] = round(float(de.loc[2024, "renewables_electricity"]), 2)

    # --- Finding 3: coal decline and nuclear exit ----------------------------
    R["coal_share_2000"] = round(float(de.loc[2000, "coal_share_elec"]), 2)
    R["coal_share_2024"] = round(float(de.loc[2024, "coal_share_elec"]), 2)
    R["coal_twh_2000"] = round(float(de.loc[2000, "coal_electricity"]), 2)
    R["coal_twh_2024"] = round(float(de.loc[2024, "coal_electricity"]), 2)
    R["nuclear_share_2000"] = round(float(de.loc[2000, "nuclear_share_elec"]), 2)
    R["nuclear_share_2022"] = round(float(de.loc[2022, "nuclear_share_elec"]), 2)
    R["nuclear_share_2024"] = round(float(de.loc[2024, "nuclear_share_elec"]), 3)
    R["nuclear_twh_2000"] = round(float(de.loc[2000, "nuclear_electricity"]), 2)

    # --- Finding 4: emissions ------------------------------------------------
    ci00, ci24 = de.loc[2000, "carbon_intensity_elec"], de.loc[2024, "carbon_intensity_elec"]
    R["carbon_intensity_2000"] = round(float(ci00), 1)
    R["carbon_intensity_2024"] = round(float(ci24), 1)
    R["carbon_intensity_drop_pct"] = round(float((ci00 - ci24) / ci00) * 100, 1)
    slope, intercept, r, r2 = linfit(de["renewables_share_elec"], de["carbon_intensity_elec"])
    R["corr_renew_vs_carbon_intensity_r"] = round(float(r), 3)
    R["reg_carbon_per_renew_point"] = round(float(slope), 2)
    R["reg_renew_vs_carbon_r2"] = round(float(r2), 3)
    c00, c24 = de.loc[2000, "co2_per_capita"], de.loc[2024, "co2_per_capita"]
    R["co2_per_capita_2000"] = round(float(c00), 2)
    R["co2_per_capita_2024"] = round(float(c24), 2)
    R["co2_per_capita_drop_pct"] = round(float((c00 - c24) / c00) * 100, 1)

    # --- Finding 5: shocks - COVID-19 (2020) and the 2022 energy crisis ------
    dem = de["electricity_demand"]
    R["demand_2019"] = round(float(dem.loc[2019]), 1)
    R["demand_2020"] = round(float(dem.loc[2020]), 1)
    R["demand_change_2020_pct"] = round(float((dem.loc[2020] / dem.loc[2019] - 1)) * 100, 1)
    R["demand_2021"] = round(float(dem.loc[2021]), 1)
    R["demand_2022"] = round(float(dem.loc[2022]), 1)
    R["demand_2024"] = round(float(dem.loc[2024]), 1)
    R["gas_share_2021"] = round(float(de.loc[2021, "gas_share_elec"]), 2)
    R["gas_share_2022"] = round(float(de.loc[2022, "gas_share_elec"]), 2)
    R["gas_share_2024"] = round(float(de.loc[2024, "gas_share_elec"]), 2)
    R["coal_share_2021"] = round(float(de.loc[2021, "coal_share_elec"]), 2)
    R["coal_share_2022"] = round(float(de.loc[2022, "coal_share_elec"]), 2)

    # --- Finding 6: cross-country comparison, 2024 ---------------------------
    comp = {}
    for iso in COUNTRIES:
        row = sub[(sub.iso_code == iso) & (sub.year == 2024)].iloc[0]
        comp[iso] = {
            "country": row["country"],
            "renewables_share_elec": round(float(row["renewables_share_elec"]), 2),
            "coal_share_elec": round(float(row["coal_share_elec"]), 2),
            "nuclear_share_elec": round(float(row["nuclear_share_elec"]), 2),
            "carbon_intensity_elec": round(float(row["carbon_intensity_elec"]), 1),
            "co2_per_capita": round(float(row["co2_per_capita"]), 2),
        }
    R["comparison_2024"] = comp
    # growth since 2000 for each comparator
    for iso in COUNTRIES:
        s = sub[sub.iso_code == iso].set_index("year")["renewables_share_elec"]
        comp[iso]["renewables_share_2000"] = round(float(s.loc[2000]), 2)
        comp[iso]["renewables_growth_points"] = round(
            float(s.loc[2024] - s.loc[2000]), 2)

    with open("outputs/results.json", "w") as f:
        json.dump(R, f, indent=2)
    de.reset_index().to_csv("outputs/germany_yearly.csv", index=False)
    print(json.dumps(R, indent=2))


if __name__ == "__main__":
    main()
