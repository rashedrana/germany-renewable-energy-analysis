# Germany's Renewable Electricity Transition, 2000–2024

A data-analysis project (Python + SQL) on how Germany rebuilt its electricity
system in one generation — and what the transition did to emissions. Germany is
compared with France, Poland and Denmark to show that *how* a country
decarbonises matters as much as *how fast*.

**Data (100% real, published sources):** Our World in Data energy dataset
(compiled from Ember's Electricity Data Explorer and the Energy Institute
Statistical Review) and the OWID CO₂ dataset — see `src/download_data.py`.
Every number below is produced by `src/analysis.py` / `sql/queries.sql` and
stored in `outputs/results.json` / `outputs/sql_results.md`; nothing is typed
by hand.

## Key findings

1. **Renewables grew nine-fold.** Their share of Germany's electricity rose
   from **6.2% in 2000 to 58.6% in 2024** (+2.05 percentage points per year,
   R² = 0.95), crossing 50% for the first time in **2023**. A naive linear
   projection reaches the 80% policy target only in **2039** — nine years
   late — so the historical trend alone is not enough.
2. **Wind and solar did the work.** They supplied **80.8%** of all renewable
   growth: wind rose from 9.4 to 141.6 TWh (CAGR 12.0%), solar from 0.1 TWh
   (2001) to 74.1 TWh (CAGR 33.3%).
3. **Coal collapsed and nuclear ended.** Coal's share fell from 52.2% to
   21.4%; renewable generation overtook coal in **2019**. Nuclear went from
   29.8% of generation in 2000 to **0% in 2024**, completing the phase-out.
4. **Emissions followed.** The carbon intensity of electricity fell **41.3%**
   (573 → 336 gCO₂/kWh). Across 2000–2024 it is strongly associated with the
   renewable share (Pearson r = −0.95; each additional percentage point of
   renewables ≈ 4.6 gCO₂/kWh less). CO₂ per capita fell 38.2% (11.0 → 6.8 t).
5. **Two shocks are visible in the data.** COVID-19 cut electricity demand
   3.5% in 2020. In the 2022 energy crisis gas's share fell (15.6% → 14.0%)
   while coal temporarily rebounded (28.5% → 31.7%) — a one-year step back
   inside a 24-year trend.
6. **Strategy matters (2024 comparison).** Denmark leads on renewables
   (89.2%) and cut CO₂ per capita most (−55.5%). France has the cleanest
   electricity (41 gCO₂/kWh) through nuclear (67.7%), not renewables (27.2%).
   Poland, still 54.3% coal, has the dirtiest electricity (608 gCO₂/kWh) and
   cut CO₂ per capita least (−12.9%).

## Figures

| Figure | Content |
|---|---|
| `outputs/figures/fig1_renewable_share.png` | Renewable share trajectory, 2000–2024 |
| `outputs/figures/fig2_electricity_mix.png` | Electricity mix by source (stacked) |
| `outputs/figures/fig3_wind_solar.png` | Wind and solar generation growth |
| `outputs/figures/fig4_renewables_vs_carbon.png` | Renewable share vs carbon intensity (OLS fit) |
| `outputs/figures/fig5_country_comparison.png` | Four-country comparison, 2024 |
| `outputs/figures/fig6_co2_per_capita.png` | CO₂ per capita trajectories |

## Repository layout

```
data/analysis_subset.csv   Germany, France, Poland, Denmark, 2000-2024 (extract)
src/download_data.py       downloads the two full OWID source datasets
src/analysis.py            all headline statistics -> outputs/results.json
src/build_db.py            builds energy.db (SQLite) and runs the SQL queries
src/figures.py             the six figures -> outputs/figures/
sql/queries.sql            9 documented SQL queries (shares, milestones, shocks)
outputs/sql_results.md     the queries with their actual output tables
paper/paper_draft.md       scientific paper draft based on these results
```

## How to run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/download_data.py   # fetch the full OWID datasets into data/
python src/analysis.py        # statistics -> outputs/results.json
python src/build_db.py        # SQLite db + SQL results -> outputs/sql_results.md
python src/figures.py         # figures -> outputs/figures/
```

## Methods in brief

Descriptive statistics, compound annual growth rates, and ordinary
least-squares regression (renewable share → carbon intensity) over annual
observations, 2000–2024 (n = 25). The regression is an association, not a
causal estimate; the paper draft (`paper/paper_draft.md`) discusses
limitations, including the 2022 coal rebound and demand effects.

## Data sources

- Ritchie, H. & Roser, M. — *Energy*, Our World in Data.
  Energy dataset: https://github.com/owid/energy-data
  (sources: Ember Electricity Data Explorer; Energy Institute Statistical
  Review of World Energy).
- Our World in Data CO₂ dataset: https://github.com/owid/co2-data
  (source: Global Carbon Project).

Licence of the source data: CC BY. This project's code: MIT.
