# Business Questions & Chart Problem-Solving
## Germany Energy Transition Dashboard — 14 questions, 14 visual types

Dataset: Our World in Data energy + CO₂ (full extract in `powerbi/data/`):
**213 countries · 2000–2024 · 36,897 fact rows** (country × year × source).
"Large producers" below = the 36 countries generating ≥ 100 TWh in 2024.
Every answer was computed from the project data and cross-checked against the
research paper's 4-country subset (Germany 2024 renewable share 58.6% in both).

---

**Q1. How clean is Germany's electricity in the selected year — at a glance?**
Visual: **KPI cards** (Renewable Share %, Carbon Intensity, CO₂ per Capita,
Total Generation, Coal Share %, Wind + Solar Share %) with vs-2000 deltas.
Answer (2024): 58.6% renewable · 336 gCO₂/kWh (−41% vs 2000) · 6.79 t CO₂ per
capita · 496 TWh generated · coal down to 21.4%.

**Q2. Is Germany on track for its 80%-renewables-by-2030 target?**
Visual: **Gauge** — Renewable Share % vs target line 80, with the 2000–2024
trend slope (+2.2 pp/yr since 2015) as the tooltip story.
Answer: At the recent pace Germany lands near ~72–75% by 2030 — close, but the
target needs acceleration; the paper's full-period trend reaches 80% only in 2039.

**Q3. How did the renewable share evolve, and which metric tells the story best?**
Visual: **Line chart** with bookmark metric switch (renewable share / carbon
intensity / CO₂ per capita), 4 paper countries + any country via slicer.
Answer: Germany 6.2% → 58.6% (2000→2024); the world's share rose 18.7% → 31.9%.

**Q4. What does Germany's electricity mix look like, year by year?**
Visual: **Stacked column chart** (TWh by source, 2000–2024).
Answer: Coal collapses (297 → 106 TWh), nuclear exits to zero (2023),
wind becomes the largest single source (142 TWh in 2024).

**Q5. How does the mix *composition* shift, independent of total size?**
Visual: **100% stacked column chart** (share % by source per year).
Answer: Fossil + nuclear fall from ~90% of the mix (2000) to ~37% (2024).

**Q6. Which sources gained and lost most between 2000 and 2024?**
Visual: **Waterfall chart** (Δ TWh by source, Germany).
Answer: Wind +132 TWh and solar +74 TWh gained; coal −190 TWh and
nuclear −170 TWh lost — the transition is a substitution story.

**Q7. Where does Germany rank among large producers in 2024?**
Visual: **Clustered bar chart** (renewable share, top-10 of the 36 large
producers) using the `Country Rank by Renewable Share` DAX measure.
Answer: **#5** — Norway 98.6%, Brazil 87.3%, Sweden 69.4%, Canada 64.3%,
Germany 58.6%.

**Q8. Which country transitioned fastest since 2000?**
Visual: **Bar chart** of renewable-share change in percentage points
(large producers), sorted descending.
Answer: **Germany itself: +52.4 pp** — ahead of the UK (+48.0), the
Netherlands (+47.4) and Spain (+41.7). The Philippines (−22.4 pp) went backwards.

**Q9. What is each source's slice of the 2024 mix?**
Visual: **Donut chart** (share by source, selected country + year).
Answer (Germany 2024): Wind 28.5%, coal 21.4%, gas 15.8%, solar 14.9%,
other renewables 10.3%, hydro 4.8%, nuclear 0%.

**Q10. How is global generation distributed across sources and regions?**
Visual: **Treemap** (generation TWh → country grouped in the model by source
category: Fossil / Nuclear / Renewable).
Answer: Renewables are 31.9% of world electricity (2024), up from 18.7% (2000);
coal is still the world's largest single source at 34.1%.

**Q11. Do countries with more renewables really emit less per kWh?**
Visual: **Scatter chart** — renewable share (x) vs carbon intensity (y),
bubble size = total generation, play axis = year.
Answer: Yes — a clear negative relationship (paper: r = −0.95 for Germany's
time series). 2024's cleanest large systems: Norway 30, Sweden 35,
France 40 gCO₂/kWh.

**Q12. Where in the world is electricity cleanest / dirtiest?**
Visual: **Filled map** (carbon intensity by country, selected year).
Answer: Hydro- and nuclear-heavy systems (Norway, Sweden, France) are darkest
green; coal-heavy systems (Poland, India, Australia) remain the most intense.

**Q13. Who still depends on nuclear — and who exited?**
Visual: **Ribbon chart** (nuclear share rank by country across years) +
matrix callout for Germany's exit.
Answer: France still leads at 67.7% nuclear (2024); Germany went from
29.8% (2000) to 0% — the only large producer to fully exit in this period.

**Q14. What drives carbon intensity down — the detail view?**
Visual: **Matrix with conditional formatting** (sources × years, share %,
data bars) + **decomposition tree** (carbon intensity → country → source
category) on the deep-dive page.
Answer: Coal displacement, not renewables growth alone — intensity fell
fastest in the years coal share dropped most (paper's regression analysis).

---

Coverage checklist (Power BI visual palette): KPI card ✓ · gauge ✓ · line ✓ ·
stacked column ✓ · 100% stacked column ✓ · waterfall ✓ · clustered bar ✓ ·
donut ✓ · treemap ✓ · scatter ✓ · filled map ✓ · ribbon ✓ · matrix ✓ ·
decomposition tree ✓ — plus slicers, bookmarks and drill-through (layout spec).
