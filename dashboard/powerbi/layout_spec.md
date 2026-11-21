# Power BI Layout Spec — Germany Energy Transition Dashboard

Design language follows modern end-to-end Power BI project style (cf. "The Developer"
YouTube channel's end-to-end dashboard projects): a clean canvas, a slicer header,
rounded KPI cards, bookmark-driven metric switching and page-navigation buttons.
The web edition in `dashboard/index.html` is the visual reference — build the PBIX
to match it page for page.

## Global formatting
- Page size: 16:9 (1280 × 720)
- Background: #F7F6FA · Cards: white, subtle shadow, rounded-corner shape underlay
- Accent: purple #7C3AED · Secondary blue #0078D4
- Font: Segoe UI (titles bold 14–16 pt, KPI values bold 20–24 pt, body 10–11 pt)
- Source colors (use everywhere): Coal #57534E · Gas #D97706 · Nuclear #9333EA ·
  Hydro #0284C7 · Wind #059669 · Solar #EAB308 · Other Renewables #84CC16
- Country colors: Germany #7C3AED · France #0078D4 · Poland #DC2626 · Denmark #059669

## Data model (Get Data → the CSVs in `powerbi/data/`)
Build on the **full dataset** (`FactGeneration_Full.csv`, `FactCountryYear_Full.csv`,
`DimCountry_Full.csv` + shared `DimYear.csv`, `DimSource.csv`): 213 countries,
36,897 fact rows. The 4-country files are the paper's extract — same model,
numbers agree. Default the country slicer to Germany.
Relationships (single direction, from dims to facts):
- DimCountry[CountryKey] → FactGeneration[CountryKey], FactCountryYear[CountryKey]
- DimYear[YearKey] → FactGeneration[YearKey], FactCountryYear[YearKey]
- DimSource[SourceKey] → FactGeneration[SourceKey]
Hide all key columns; mark DimYear[Year] as the date table's year column.
Paste all measures from `DAX_measures.md` into a `_Measures` table.

## Page 1 — Overview (the page from the video-style template)
Slicer header (top band, synced to all pages):
- Country: chiclet slicer (DimCountry[Country]), single select, Germany default
- Year: slider slicer (DimYear[Year]) + a card showing [Selected Year Label]
- Metric switch: three buttons (Renewable share / Carbon intensity / CO₂ per capita)
  wired to bookmarks that swap the main trend visual's measure
  (field parameter is the modern alternative — either is fine)

KPI card row (6 cards, each with its vs-2000 delta underneath):
1. Renewable Share % · 2. Avg Carbon Intensity · 3. Avg CO2 per Capita ·
4. Total Generation (TWh) · 5. Coal Share % · 6. Wind + Solar Share %

Visuals:
- Main trend: line chart, axis DimYear[Year], values = bookmark-switched measure,
  legend DimCountry[Country] (small multiples off; all 4 countries shown)
- Right: clustered bar — Renewable Share % by DimCountry[Country] for the selected
  year, country colors, drill-through enabled to Page 3
- Bottom left: 100%-stacked + absolute stacked column (two visuals or a toggle
  bookmark) — Total Generation by DimSource[Source] per year
- Bottom right: horizontal bar — Total Generation (TWh) by source, selected year, sorted desc

## Page 2 — Electricity Mix Deep-Dive
- Stacked column: generation (TWh) by source and year (absolute)
- Stacked 100% column: same, as shares — bookmark toggle between the two
- Matrix: sources × years with Share_Pct, conditional color scales
- Decomposition tree: Total Generation → Category → Source (selected year)

## Page 3 — Country Comparison (drill-through target)
- Bar: Renewable Share % by country (selected year), rank measure as tooltip
- Line: carbon intensity by country, 2000–2024
- Scatter: renewable share (x) vs carbon intensity (y), bubble = total generation,
  play axis = year
- Drill-through filter: DimCountry[Country]

## Page 4 — About & Method
- Text box: research question, headline findings (renewables 6.2% → 58.6%;
  carbon intensity −41%; coal 52% → 21%; nuclear exit complete 2023)
- Data source: Our World in Data (energy + CO₂ datasets)
- Links (buttons with web URL actions): GitHub project, portfolio site
- Note: companion research paper by Rashed Rana

## Navigation
Left vertical button bar on every page (home icon style): Overview · Mix ·
Countries · About — page navigator or buttons with "Page navigation" actions,
selected page highlighted in the accent color.

## Publish checklist
- [ ] All slicers synced across pages 1–3
- [ ] Bookmarks tested (metric switch, absolute/share toggle)
- [ ] Drill-through from Page 1 comparison bar to Page 3 works
- [ ] Mobile layout: KPI cards 2 × 3, trend chart full width
- [ ] File saved as `Germany_Energy_Transition.pbix` next to this spec
