"""Figures 7-8 for the full paper version."""
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

# --- Figure 7: the coal-renewables crossover ---------------------------------
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.plot(de.year, de.renewables_electricity, color="#1a9850", lw=2.2,
        marker="o", ms=3.5, label="Renewables")
ax.plot(de.year, de.coal_electricity, color="#4d4d4d", lw=2.2,
        marker="s", ms=3.5, label="Coal")
cross = de[de.renewables_electricity > de.coal_electricity].year.min()
row = de[de.year == cross].iloc[0]
ax.annotate(f"Crossover in {cross}", xy=(cross, row.renewables_electricity),
            xytext=(2006.5, 265),
            arrowprops=dict(arrowstyle="->", color="grey"), color="grey")
ax.set_xlabel("Year"); ax.set_ylabel("Generation (TWh)")
ax.set_title("Figure 7. Renewable vs coal generation in Germany, 2000-2024")
ax.legend()
fig.tight_layout(); fig.savefig(f"{OUT}/fig7_coal_crossover.png"); plt.close(fig)

# --- Figure 8: carbon intensity path ------------------------------------------
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.plot(de.year, de.carbon_intensity_elec, color="#d73027", lw=2.2,
        marker="o", ms=3.5)
ci21 = float(de.loc[de.year == 2021, "carbon_intensity_elec"].iloc[0])
ci22 = float(de.loc[de.year == 2022, "carbon_intensity_elec"].iloc[0])
ax.annotate(f"2022 crisis uptick:\n{ci21:.0f} → {ci22:.0f} gCO$_2$/kWh",
            xy=(2022, ci22), xytext=(2013.2, 505),
            arrowprops=dict(arrowstyle="->", color="grey"), color="grey")
ax.set_xlabel("Year"); ax.set_ylabel("Carbon intensity (gCO$_2$/kWh)")
ax.set_title("Figure 8. Carbon intensity of Germany's electricity, 2000-2024")
fig.tight_layout(); fig.savefig(f"{OUT}/fig8_carbon_intensity.png"); plt.close(fig)

print("figures 7-8 written; 2021 CI =", ci21, "| 2022 CI =", ci22)
