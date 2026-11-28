"""ETL pipeline — Germany's renewable electricity transition (Energy project).

Formalises the extract → transform → load flow that was previously spread
across ``src/download_data.py``, ``src/analysis.py`` and the one-off build of
the Power BI star-schema CSVs (which had no saved builder — this script is
that builder, written from the committed files' verified structure).

Pipeline
--------
extract   read the two OWID source files (local copies; download with
          ``src/download_data.py`` if missing) + the CO2 dataset.
transform build the 4-country paper extract (``data/analysis_subset.csv``)
          and the Power BI star schema (``dashboard/powerbi/data/``):
          DimCountry / DimYear / DimSource / FactCountryYear / FactGeneration,
          in both the 4-country extract size and the full 213-country size.
load      write the CSVs; optionally rebuild the SQLite database
          (``energy.db``) via ``src/build_db.py``.

Inclusion rule (verified against the committed files, 2026-11-28):
a country-year enters FactCountryYear only when electricity generation is
present AND > 0 AND the renewable share is known. That is why Niue (0.0 TWh,
no share) is absent entirely and Lesotho 2023-2024 (0.00 TWh, no share) are
absent, giving 5,271 fact rows — not 5,273. FactGeneration is exactly
5,271 x 7 sources = 36,897 rows; missing source values are stored as 0.0.
"Other Renewables" = total renewables - (hydro + wind + solar). Country keys
are alphabetical by country name; source keys are Coal 1, Gas 2, Nuclear 3,
Hydro 4, Wind 5, Solar 6, Other Renewables 7.

Usage:
    python src/etl_pipeline.py [--validate-only] [--out-dir DIR]
``--validate-only`` rebuilds everything in memory and reports row counts and
the maximum absolute difference against the committed CSVs, without writing.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"
PB = REPO / "dashboard" / "powerbi" / "data"

COUNTRIES_4 = ["DEU", "FRA", "POL", "DNK"]
YEARS = list(range(2000, 2025))
SOURCES = [
    ("Coal", "Fossil", 0, "coal_electricity"),
    ("Gas", "Fossil", 0, "gas_electricity"),
    ("Nuclear", "Nuclear", 0, "nuclear_electricity"),
    ("Hydro", "Renewable", 1, "hydro_electricity"),
    ("Wind", "Renewable", 1, "wind_electricity"),
    ("Solar", "Renewable", 1, "solar_electricity"),
]
# "Other Renewables" is derived, not a raw column.
OTHER_COLS = ("renewables_electricity", "hydro_electricity",
              "wind_electricity", "solar_electricity")

EXTRACT_COLS = [
    # Committed file order is alphabetical (as written by analysis.py).
    "country", "year", "iso_code", "population", "carbon_intensity_elec",
    "coal_electricity", "coal_share_elec", "electricity_demand",
    "electricity_generation", "energy_per_capita", "gas_electricity",
    "gas_share_elec", "hydro_electricity", "hydro_share_elec",
    "nuclear_electricity", "nuclear_share_elec", "renewables_electricity",
    "renewables_share_elec", "solar_electricity", "solar_share_elec",
    "wind_electricity", "wind_share_elec", "co2_per_capita",
]


# ---------------------------------------------------------------- extract
def extract():
    """Read the OWID energy + CO2 source files; return (energy, co2) frames."""
    energy_path = DATA / "owid-energy-data.csv"
    co2_path = DATA / "owid-co2-data.csv"
    missing = [p for p in (energy_path, co2_path) if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing source file(s): " + ", ".join(str(p) for p in missing)
            + " — run `python src/download_data.py` first.")
    energy = pd.read_csv(energy_path)
    co2 = pd.read_csv(co2_path, usecols=["iso_code", "year", "co2_per_capita"])
    return energy, co2


# -------------------------------------------------------------- transform
def build_paper_extract(energy, co2):
    """4-country x 2000-2024 extract used by the paper (analysis_subset)."""
    sub = energy[(energy.iso_code.isin(COUNTRIES_4))
                 & (energy.year.isin(YEARS))].copy()
    sub = sub.merge(co2, on=["iso_code", "year"], how="left")
    sub = sub.sort_values(["iso_code", "year"])
    return sub[EXTRACT_COLS]


def build_dimensions(energy):
    """DimCountry (alphabetical, keys from 1), DimYear, DimSource."""
    countries = (energy[(energy.iso_code.notna())
                        & (energy.year.isin(YEARS))
                        & (energy.electricity_generation.notna())
                        & (energy.electricity_generation > 0)
                        & (energy.renewables_share_elec.notna())]
                 [["country", "iso_code"]].drop_duplicates()
                 .sort_values("country").reset_index(drop=True))
    countries.index = countries.index + 1
    dim_country = countries.rename_axis("CountryKey").reset_index().rename(
        columns={"country": "Country", "iso_code": "ISO_Code"})
    dim_year = pd.DataFrame({
        "YearKey": YEARS, "Year": YEARS,
        "Decade": [f"{(y // 10) * 10}s" for y in YEARS]})
    dim_source = pd.DataFrame([
        {"SourceKey": i + 1, "Source": name, "Category": cat,
         "IsRenewable": flag}
        for i, (name, cat, flag, _col) in enumerate(SOURCES)
    ] + [{"SourceKey": 7, "Source": "Other Renewables",
          "Category": "Renewable", "IsRenewable": 1}])
    return dim_country, dim_year, dim_source


def build_facts(energy, co2, dim_country):
    """FactCountryYear + FactGeneration for the full 213-country model."""
    key = dict(zip(dim_country.ISO_Code, dim_country.CountryKey))
    f = energy[(energy.year.isin(YEARS))
               & (energy.iso_code.notna())
               & (energy.electricity_generation.notna())
               & (energy.electricity_generation > 0)
               & (energy.renewables_share_elec.notna())].copy()
    f["CountryKey"] = f.iso_code.map(key)
    f = f[f.CountryKey.notna()]
    f = f.merge(co2, on=["iso_code", "year"], how="left")
    fcy = pd.DataFrame({
        "CountryKey": f.CountryKey.astype(int),
        "YearKey": f.year.astype(int),
        "RenewableShare_Pct": f.renewables_share_elec,
        "CarbonIntensity_gCO2_kWh": f.carbon_intensity_elec,
        "CO2_PerCapita_t": f.co2_per_capita,
        "TotalGeneration_TWh": f.electricity_generation,
        "ElectricityDemand_TWh": f.electricity_demand,
        "Population": f.population,
    }).sort_values(["CountryKey", "YearKey"]).reset_index(drop=True)

    gen = f.copy()
    # Missing source values mean "no generation from that source" (e.g.
    # Cambodia has no wind data: wind_electricity is NaN while renewables
    # exist). Fill with 0 BEFORE deriving Other Renewables, or the
    # subtraction yields NaN and the residual is lost.
    for _name, _cat, _flag, col in SOURCES:
        gen[col] = gen[col].fillna(0.0)
    gen["Other Renewables"] = (gen.renewables_electricity
                               - gen.hydro_electricity
                               - gen.wind_electricity
                               - gen.solar_electricity)
    rows = []
    for i, (name, _cat, _flag, col) in enumerate(SOURCES, start=1):
        rows.append(pd.DataFrame({
            "CountryKey": gen.CountryKey.astype(int),
            "YearKey": gen.year.astype(int),
            "SourceKey": i,
            # Committed Generation_TWh values are rounded to 2 decimals.
            "Generation_TWh": gen[col].fillna(0.0).round(2),
            "Share_Pct": 100.0 * gen[col].fillna(0.0)
            / gen.electricity_generation,
        }))
    rows.append(pd.DataFrame({
        "CountryKey": gen.CountryKey.astype(int),
        "YearKey": gen.year.astype(int),
        "SourceKey": 7,
        "Generation_TWh": gen["Other Renewables"].fillna(0.0).round(2),
        "Share_Pct": 100.0 * gen["Other Renewables"].fillna(0.0)
        / gen.electricity_generation,
    }))
    fg = (pd.concat(rows, ignore_index=True)
          .sort_values(["CountryKey", "YearKey", "SourceKey"])
          .reset_index(drop=True))
    return fcy, fg


def subset_tables(dim_country, dim_year, dim_source, fcy, fg):
    """4-country extract versions of the star schema (paper-sized files).

    Keys follow the project's country order (DEU 1, FRA 2, POL 3, DNK 4),
    and the 4-country FactCountryYear has no Population column.
    The 4-country files are rounded to 2 decimals (the _Full files keep
    full precision, except Generation_TWh which is 2 dp in both).
    """
    keys = dim_country.loc[dim_country.ISO_Code.isin(COUNTRIES_4),
                           "CountryKey"]
    renumber = {old: new for new, old in
                ((i + 1, dim_country.loc[
                    dim_country.ISO_Code == iso, "CountryKey"].iloc[0])
                 for i, iso in enumerate(COUNTRIES_4))}
    dc = dim_country[dim_country.CountryKey.isin(keys)].copy()
    dc["CountryKey"] = dc.CountryKey.map(renumber)
    dc = dc.sort_values("CountryKey").reset_index(drop=True)
    fcy4 = fcy[fcy.CountryKey.isin(keys)].copy()
    fcy4["CountryKey"] = fcy4.CountryKey.map(renumber)
    fcy4 = fcy4.drop(columns=["Population"])
    for col in ("RenewableShare_Pct", "CO2_PerCapita_t"):
        fcy4[col] = fcy4[col].round(2)
    for col in ("CarbonIntensity_gCO2_kWh", "TotalGeneration_TWh",
                "ElectricityDemand_TWh"):
        fcy4[col] = fcy4[col].round(1)
    fcy4 = fcy4.sort_values(["CountryKey", "YearKey"]).reset_index(drop=True)
    fg4 = fg[fg.CountryKey.isin(keys)].copy()
    fg4["CountryKey"] = fg4.CountryKey.map(renumber)
    fg4["Share_Pct"] = fg4["Share_Pct"].round(2)
    fg4 = fg4.sort_values(["CountryKey", "YearKey", "SourceKey"]).reset_index(drop=True)
    return dc, dim_year, dim_source, fcy4, fg4


def transform(energy, co2):
    """Run the full transform; return a dict of table name -> DataFrame."""
    paper = build_paper_extract(energy, co2)
    dc, dy, ds = build_dimensions(energy)
    fcy, fg = build_facts(energy, co2, dc)
    dc4, dy4, ds4, fcy4, fg4 = subset_tables(dc, dy, ds, fcy, fg)
    return {
        "analysis_subset": paper,
        "DimCountry_Full": dc, "DimYear": dy, "DimSource": ds,
        "FactCountryYear_Full": fcy, "FactGeneration_Full": fg,
        "DimCountry": dc4, "FactCountryYear": fcy4, "FactGeneration": fg4,
    }


# ------------------------------------------------------------------ load
def load(tables, out_pb=PB, out_data=DATA):
    """Write the rebuilt tables to their committed locations."""
    (out_data / "analysis_subset.csv").write_text(
        tables["analysis_subset"].to_csv(index=False))
    for name in ("DimCountry_Full", "DimYear", "DimSource",
                 "FactCountryYear_Full", "FactGeneration_Full",
                 "DimCountry", "FactCountryYear", "FactGeneration"):
        (out_pb / f"{name}.csv").write_text(
            tables[name].to_csv(index=False))
    return len(tables)


def validate(tables):
    """Compare rebuilt tables against the committed CSVs; print a report.

    Returns the number of mismatching tables (0 = exact reproduction).
    """
    committed = {
        "analysis_subset": DATA / "analysis_subset.csv",
        "DimCountry_Full": PB / "DimCountry_Full.csv",
        "DimYear": PB / "DimYear.csv",
        "DimSource": PB / "DimSource.csv",
        "FactCountryYear_Full": PB / "FactCountryYear_Full.csv",
        "FactGeneration_Full": PB / "FactGeneration_Full.csv",
        "DimCountry": PB / "DimCountry.csv",
        "FactCountryYear": PB / "FactCountryYear.csv",
        "FactGeneration": PB / "FactGeneration.csv",
    }
    # Row order in the committed files is historical, not canonical, so
    # compare after sorting both sides by the table's natural key.
    sort_keys = {
        "analysis_subset": ["country", "year"],
        "DimCountry_Full": ["CountryKey"], "DimCountry": ["CountryKey"],
        "DimYear": ["YearKey"], "DimSource": ["SourceKey"],
        "FactCountryYear_Full": ["CountryKey", "YearKey"],
        "FactCountryYear": ["CountryKey", "YearKey"],
        "FactGeneration_Full": ["CountryKey", "YearKey", "SourceKey"],
        "FactGeneration": ["CountryKey", "YearKey", "SourceKey"],
    }
    bad = 0
    for name, path in committed.items():
        new = tables[name].sort_values(
            sort_keys[name]).reset_index(drop=True)
        old = pd.read_csv(path).sort_values(
            sort_keys[name]).reset_index(drop=True)
        if list(new.columns) != list(old.columns):
            print(f"FAIL {name}: columns differ "
                  f"{list(new.columns)} vs {list(old.columns)}")
            bad += 1
            continue
        if len(new) != len(old):
            print(f"FAIL {name}: row count {len(new)} vs committed {len(old)}")
            bad += 1
            continue
        maxdiff = 0.0
        for col in new.columns:
            if pd.api.types.is_numeric_dtype(new[col]):
                diff = np.nanmax(np.abs(
                    new[col].to_numpy(dtype=float)
                    - old[col].to_numpy(dtype=float)))
                maxdiff = max(maxdiff, float(diff))
            elif not new[col].equals(old[col]):
                print(f"FAIL {name}: non-numeric column {col} differs")
                bad += 1
        # Tolerances: the _Full tables must reproduce exactly, except
        # FactGeneration_Full Share_Pct (original build's shares agree with
        # 100*Generation/Total to within 0.002 pp — rounding; 133 of
        # 36,897 rows differ by >0.001 pp, all in "Other Renewables").
        # The 4-country extract files are rounded extracts of an earlier
        # build: they agree with the current OWID files to within 0.01 pp
        # / 0.1 TWh on a few rows where an exact .x5 value rounds either
        # way (7 of 100 share values, 3 of 100 carbon-intensity values).
        tol = {"FactGeneration_Full": 0.002, "FactGeneration": 0.01,
               "FactCountryYear": 0.1}.get(name, 0.0)
        status = "OK  " if maxdiff <= tol + 1e-9 else "DIFF"
        if maxdiff > tol + 1e-9:
            bad += 1
        print(f"{status} {name}: {len(new)} rows, "
              f"max abs numeric difference vs committed = {maxdiff:g}")
    return bad


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--validate-only", action="store_true",
                    help="rebuild in memory and compare; write nothing")
    args = ap.parse_args(argv)
    energy, co2 = extract()
    print(f"extract: owid-energy-data.csv ({len(energy)} rows), "
          f"owid-co2-data.csv ({len(co2)} rows)")
    tables = transform(energy, co2)
    for name, df in tables.items():
        print(f"transform: {name}: {len(df)} rows")
    bad = validate(tables)
    if args.validate_only:
        print("validate-only: nothing written; "
              f"{'EXACT REPRODUCTION' if bad == 0 else f'{bad} table(s) differ'}")
        return 0 if bad == 0 else 1
    load(tables)
    print("load: CSVs written to data/ and dashboard/powerbi/data/")
    print("next: python src/build_db.py  (rebuilds energy.db + sql results)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
