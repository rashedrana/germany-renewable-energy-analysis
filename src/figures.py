"""Generate the six publication-quality figures (300 dpi PNG).

Every figure is drawn from data/analysis_subset.csv only, so the figures
always match the numbers in outputs/results.json.
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({
    "figure.dpi": 300, "savefig.dpi": 300, "font.size": 10,
    "axes.titlesize": 12, "axes.titleweight": "bold",
    "axes.grid": True, "grid.alpha": 0.3, "axes.spines.top": False,
    "axes.spines.right": False,
})
OUT = "outputs/figures"
sub = pd.read_csv("data/analysis_subset.csv")
de = sub[sub.iso_code == "DEU"].sort_values("year")
R = json.load(open("outputs/results.json"))

# --- Figure 1: renewable share trajectory -----------------------------------
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.plot(de.year, de.renewables_share_elec, color="#1a9850", lw=2.2, marker="o", ms=3.5)
ax.axhline(50, color="grey", ls="--", lw=1)
ax.annotate("50% crossed in 2023", xy=(2023, 54.69), xytext=(2011.5, 52),
            arrowprops=dict(arrowstyle="->", color="grey"), color="grey")
ax.annotate(f"2024: {R['renew_share_2024']:.1f}%", xy=(2024, 58.64),
            xytext=(2018.6, 63), fontweight="bold", color="#1a9850")
ax.set_ylim(0, 70)
ax.set_xlabel("Year"); ax.set_ylabel("Share of electricity (%)")
ax.set_title("Figure 1. Renewable share of Germany's electricity, 2000-2024")
fig.tight_layout(); fig.savefig(f"{OUT}/fig1_renewable_share.png"); plt.close(fig)

# --- Figure 2: electricity mix, stacked -------------------------------------
other = 100 - (de.renewables_share_elec + de.coal_share_elec
               + de.nuclear_share_elec + de.gas_share_elec)
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.fill_between(de.year, 0, de.renewables_share_elec, color="#1a9850", label="Renewables")
base = de.renewables_share_elec
for col, color, label in [("coal_share_elec", "#4d4d4d", "Coal"),
                          ("nuclear_share_elec", "#762a83", "Nuclear"),
                          ("gas_share_elec", "#fdae61", "Gas")]:
    ax.fill_between(de.year, base, base + de[col], color=color, label=label)
    base = base + de[col]
ax.fill_between(de.year, base, 100, color="#bdbdbd", label="Other")
ax.set_ylim(0, 100); ax.set_xlabel("Year"); ax.set_ylabel("Share of electricity (%)")
ax.set_title("Figure 2. Germany's electricity mix by source, 2000-2024")
ax.legend(loc="upper left", fontsize=8, framealpha=0.9)
fig.tight_layout(); fig.savefig(f"{OUT}/fig2_electricity_mix.png"); plt.close(fig)

# --- Figure 3: wind and solar growth -----------------------------------------
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.plot(de.year, de.wind_electricity, color="#4575b4", lw=2.2, marker="o", ms=3.5,
        label=f"Wind (CAGR {R['wind_cagr_pct']:.1f}%)")
ax.plot(de.year, de.solar_electricity, color="#fdae61", lw=2.2, marker="s", ms=3.5,
        label=f"Solar (CAGR {R['solar_cagr_pct']:.1f}% since 2001)")
ax.set_xlabel("Year"); ax.set_ylabel("Generation (TWh)")
ax.set_title("Figure 3. Wind and solar generation in Germany, 2000-2024")
ax.legend()
fig.tight_layout(); fig.savefig(f"{OUT}/fig3_wind_solar.png"); plt.close(fig)

# --- Figure 4: renewable share vs carbon intensity ---------------------------
x, y = de.renewables_share_elec, de.carbon_intensity_elec
slope, intercept = np.polyfit(x, y, 1)
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.scatter(x, y, c=de.year, cmap="viridis", s=45, edgecolors="k", linewidths=0.4)
xs = np.linspace(x.min(), x.max(), 50)
ax.plot(xs, slope * xs + intercept, color="crimson", lw=1.8,
        label=f"OLS fit (r = {R['corr_renew_vs_carbon_intensity_r']}, "
              f"R² = {R['reg_renew_vs_carbon_r2']})")
for yr in (2000, 2010, 2020, 2024):
    row = de[de.year == yr].iloc[0]
    ax.annotate(str(yr), (row.renewables_share_elec, row.carbon_intensity_elec),
                textcoords="offset points", xytext=(5, 5), fontsize=8)
ax.set_xlabel("Renewable share of electricity (%)")
ax.set_ylabel("Carbon intensity (gCO$_2$/kWh)")
ax.set_title("Figure 4. Renewable share vs carbon intensity of electricity,\nGermany 2000-2024")
ax.legend()
fig.tight_layout(); fig.savefig(f"{OUT}/fig4_renewables_vs_carbon.png"); plt.close(fig)

# --- Figure 5: four-country comparison, 2024 ---------------------------------
comp = sub[sub.year == 2024].set_index("country").loc[
    ["Germany", "France", "Poland", "Denmark"]]
fig, ax1 = plt.subplots(figsize=(7, 4.2))
bars = ax1.bar(comp.index, comp.renewables_share_elec, color="#1a9850", alpha=0.85,
               width=0.55, label="Renewable share (%)")
ax1.set_ylabel("Renewable share of electricity (%)")
ax1.set_ylim(0, 100)
ax2 = ax1.twinx()
ax2.plot(comp.index, comp.carbon_intensity_elec, color="crimson", marker="D",
         lw=0, ms=9, label="Carbon intensity (gCO$_2$/kWh)")
ax2.set_ylabel("Carbon intensity (gCO$_2$/kWh)")
ax2.set_ylim(0, 700); ax2.grid(False)
for b, v in zip(bars, comp.renewables_share_elec):
    ax1.annotate(f"{v:.1f}%", (b.get_x() + b.get_width() / 2, v),
                 textcoords="offset points", xytext=(0, 3), ha="center", fontsize=9)
ax1.set_title("Figure 5. Renewable share and carbon intensity, 2024")
fig.tight_layout(); fig.savefig(f"{OUT}/fig5_country_comparison.png"); plt.close(fig)

# --- Figure 6: CO2 per capita trajectories -----------------------------------
fig, ax = plt.subplots(figsize=(7, 4.2))
for iso, color in [("DEU", "#1a9850"), ("FRA", "#4575b4"),
                   ("POL", "#d73027"), ("DNK", "#984ea3")]:
    s = sub[sub.iso_code == iso]
    ax.plot(s.year, s.co2_per_capita, lw=2, marker="o", ms=3,
            color=color, label=s.country.iloc[0])
ax.set_xlabel("Year"); ax.set_ylabel("CO$_2$ per capita (tonnes)")
ax.set_title("Figure 6. CO$_2$ emissions per capita, 2000-2024")
ax.legend()
fig.tight_layout(); fig.savefig(f"{OUT}/fig6_co2_per_capita.png"); plt.close(fig)

print("6 figures written to", OUT)
