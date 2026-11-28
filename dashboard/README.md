# Germany Energy Transition — Interactive Dashboard

The interactive companion to this repository's research paper
(*Germany's Renewable Energy Transition, 2000–2024*). Same data, same numbers —
the paper explains the transition, this dashboard lets you explore it.

## Web edition (live, no install)
Open `index.html` in a browser (or via GitHub Pages). Features:

- **Country buttons** — Germany, France, Poland, Denmark as the main view
- **Focus-year slider (2000–2024)** — every KPI card, the source breakdown and the
  country comparison update to the selected year
- **Metric switch** — the trend chart flips between renewable share, carbon
  intensity and CO₂ per capita; per-country show/hide toggles
- **6 KPI cards** with change vs 2000, a stacked electricity-mix chart, a
  by-source bar for the focus year, and a carbon-intensity vs renewable-share
  dual-axis chart
- Clicking a bar in the country comparison switches the whole dashboard to
  that country

## Slicer honesty

Every panel either follows the slicers or says so. The KPI cards, country
comparison, mix chart, source breakdown and carbon-intensity chart all follow
the country and focus-year slicers; the trend chart follows the country
toggles and metric switch and always shows the full 2000–2024 series. The
five fixed exhibits (world map, heatmap, slope chart, generation bridge,
waffle) are comparisons fixed to 2024 or to 2000→2024 and carry a visible
**"Fixed comparison — ignores slicers by design"** label. Every panel also
carries a statistics line (trend slope and R², rank, correlation, bridge
closure…) with a one-line takeaway, computed from the project data — see
`../notebooks/energy_key_numbers.ipynb` for the reproduction.

## Behind the dashboard

- `powerbi/queries.sql` — SQL over the star-schema CSVs answering the
  dashboard's business questions (Q7, Q8, Q11, Q15–Q17, Q19), with results
  in `powerbi/sql_results.md`
- `powerbi/DATA_DICTIONARY.md` — column-level dictionary for all five
  star-schema tables
- `../PIPELINE.md` + `../src/etl_pipeline.py` — the extract → transform →
  load pipeline that rebuilds every derived file from the OWID sources
  (validates exactly against the committed files)
- `../notebooks/energy_key_numbers.ipynb` — reproduces every headline number
  and panel statistic from the data
- `../outputs/Energy_KPI_Workbook.xlsx` — KPI workbook (KPI cards, yearly
  series, country comparison, panel statistics)

## Power BI edition (build guide)
Everything needed to rebuild this as a native Power BI report sits in `powerbi/`:

- `powerbi/data/` — star-schema CSVs (2 fact tables, 3 dimensions; see
  `powerbi/model_diagram.md`). Two sizes: the paper's 4-country extract, and the
  **full dataset — 213 countries, 36,897 fact rows** (`*_Full.csv`), which the
  report is built on (default view: Germany)
- `powerbi/DAX_measures.md` — all measures, copy-paste ready (totals, shares,
  YoY and vs-2000 deltas, ranks)
- `powerbi/QUESTIONS.md` — 19 business questions, each solved with a different
  Power BI visual type (KPI cards, gauge, waterfall, scatter, map, ribbon,
  decomposition tree…), with the verified answers
- `powerbi/queries.sql` + `powerbi/sql_results.md` — SQL over the star-schema
  CSVs answering the dashboard questions, with the actual results
- `powerbi/DATA_DICTIONARY.md` — column-level dictionary for the five
  star-schema tables
- `powerbi/layout_spec.md` — page-by-page layout in modern end-to-end project
  style: slicer header, KPI row, bookmark metric switching, drill-through
  country page, navigation buttons, exact color palette

On a Windows PC with Power BI Desktop: load the 5 CSVs, set the 5 relationships
in `model_diagram.md`, paste the DAX, and place the visuals per the layout spec.

## Data
Our World in Data energy and CO₂ datasets, via `data/analysis_subset.csv` in
this repository — 4 countries × 25 years, no gaps in the series used.
