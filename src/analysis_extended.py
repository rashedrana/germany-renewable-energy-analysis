"""Extended statistics for the full paper version.

Adds, on top of src/analysis.py:
  * a multivariate OLS of carbon intensity on the renewable, coal and gas
    shares and electricity demand (full inferential statistics),
  * sub-period trend analysis of the renewable share
    (2000-2010 EEG build-up, 2011-2019 post-Fukushima, 2020-2024 crisis era),
  * a correlation matrix of the main variables,
  * an electricity-demand trend check.
All output -> outputs/extended_results.json. Requires statsmodels.
"""
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm

sub = pd.read_csv("data/analysis_subset.csv")
de = sub[sub.iso_code == "DEU"].sort_values("year").reset_index(drop=True)
R = {}

# --- Multivariate OLS: carbon intensity -------------------------------------
X = de[["renewables_share_elec", "coal_share_elec", "gas_share_elec",
        "electricity_demand"]]
X = sm.add_constant(X)
y = de["carbon_intensity_elec"]
model = sm.OLS(y, X).fit()
R["multivariate_ols"] = {
    "n": int(model.nobs),
    "r_squared": round(float(model.rsquared), 4),
    "adj_r_squared": round(float(model.rsquared_adj), 4),
    "f_statistic": round(float(model.fvalue), 2),
    "f_pvalue": float(model.f_pvalue),
    "coefficients": {
        name: {
            "coef": round(float(model.params[name]), 3),
            "std_err": round(float(model.bse[name]), 3),
            "t": round(float(model.tvalues[name]), 2),
            "p": float(model.pvalues[name]),
        } for name in model.params.index
    },
}

# --- Simple OLS with inferential stats (renewable share only) ----------------
X1 = sm.add_constant(de["renewables_share_elec"])
m1 = sm.OLS(y, X1).fit()
R["simple_ols"] = {
    "slope": round(float(m1.params["renewables_share_elec"]), 3),
    "slope_std_err": round(float(m1.bse["renewables_share_elec"]), 3),
    "slope_t": round(float(m1.tvalues["renewables_share_elec"]), 2),
    "slope_p": float(m1.pvalues["renewables_share_elec"]),
    "intercept": round(float(m1.params["const"]), 2),
    "r_squared": round(float(m1.rsquared), 4),
}

# --- Sub-period trends of the renewable share --------------------------------
periods = {"2000-2010": (2000, 2010), "2011-2019": (2011, 2019),
           "2020-2024": (2020, 2024)}
R["subperiods"] = {}
for name, (a, b) in periods.items():
    s = de[(de.year >= a) & (de.year <= b)]
    slope, intercept = np.polyfit(s.year, s.renewables_share_elec, 1)
    R["subperiods"][name] = {
        "share_start": round(float(s.renewables_share_elec.iloc[0]), 2),
        "share_end": round(float(s.renewables_share_elec.iloc[-1]), 2),
        "change_points": round(float(s.renewables_share_elec.iloc[-1]
                                     - s.renewables_share_elec.iloc[0]), 2),
        "trend_per_year": round(float(slope), 3),
    }

# --- Correlation matrix (Germany) --------------------------------------------
cols = ["renewables_share_elec", "coal_share_elec", "nuclear_share_elec",
        "gas_share_elec", "carbon_intensity_elec", "co2_per_capita",
        "electricity_demand"]
corr = de[cols].corr().round(3)
R["correlation_matrix"] = corr.to_dict()
corr.to_csv("outputs/correlation_matrix.csv")

# --- Demand trend --------------------------------------------------------------
slope, intercept = np.polyfit(de.year, de.electricity_demand, 1)
R["demand_trend_per_year_twh"] = round(float(slope), 2)
R["demand_peak_year"] = int(de.loc[de.electricity_demand.idxmax(), "year"])
R["demand_peak_twh"] = round(float(de.electricity_demand.max()), 1)

with open("outputs/extended_results.json", "w") as f:
    json.dump(R, f, indent=2)
print(json.dumps(R, indent=2))
print("\n--- OLS summary ---\n", model.summary())
