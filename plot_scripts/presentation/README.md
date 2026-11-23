# presentation — slide deck for the IC1 summer run

Twelve 16:9 slides plus a combined PDF, built straight from the two SQLite
databases in the parent directory. Writes only to `presentation/out/`.

```powershell
python presentation\build_deck.py
```

Needs `pandas`, `numpy`, `matplotlib`. Reuses the readers in `../analysis_v2/`.

## Slides

| file | message |
|---|---|
| `P01_cover.png` | Headline KPIs: scope, emissions, storage, solve status |
| `P02_co2_pathway.png` | Net CO₂ against the budget, with the driver for each year |
| `P03_emission_sources.png` | Gross emissions by part of the system, with a value table |
| `P04_ccs_chain.png` | Sankey: capture source → regional hub → North Sea storage |
| `P05_industry_routes.png` | Route mix per sector, 2030 vs 2050 — fossil, CCS, biomass, electric |
| `P06_industry_capture.png` | Capture penetration by sector against sector size |
| `P07_energy_carriers.png` | Electricity, methane and hydrogen mix across the three years |
| `P08_capacity_change.png` | What is added and what is retired between 2030 and 2050 |
| `P09_capacity_vintage.png` | 2050 fleet split between legacy plant and new build |
| `P10_regional_map.png` | Schematic map: emissions, capture and pipeline flows by region |
| `P11_regions_ranked.png` | Regions ranked by emissions, with capture alongside |
| `P12_scope_and_method.png` | Conventions and open items, in neutral language |
| `IC1_summer_run_deck.pdf` | All twelve, in order |

## Files

- `theme.py` — palette, type scale, KPI tiles and a bezier-ribbon Sankey. No
  scenario knowledge.
- `taxonomy.py` — maps raw unit names onto the groups shown on the slides, plus
  the route classifier and the region layout. The build prints any technology
  that falls through to a catch-all so the lists can be extended.
- `build_deck.py` — one `slide_*` function per slide.

## Geography

Neither database has any `entity_location` rows, and there is no latitude or
longitude parameter anywhere in the input. `P10` therefore uses a **schematic**
layout: Dutch regions in the upper band, Belgian in the lower, offshore storage
to the west. Positions live in one place:

```python
# taxonomy.py
REGION_XY = {"NLC1": (0.17, 0.90), ...}
STORAGE_XY = {"CO2-storage-NSNL031": (0.06, 0.70), ...}
```

Drop real coordinates in there — normalised to a unit square, or swap the axis
limits for a projected extent — and the slide becomes a true map with no other
change. Everything else on it (circle areas, rings, arrow widths) is already
driven by the results.

## Route classification

`P05` classifies each production route from what it actually consumed in the
results, not from its name:

| category | rule |
|---|---|
| Fossil, unabated | fossil carbon > 50 % of carbon input, no CO₂ to the network |
| Fossil + CCS | as above, but sends CO₂ to the network |
| Biomass | biomass-dominant carbon input |
| Biomass + hydrogen | biomass-dominant and also consumes H₂ |
| Biomass + CCS | biomass-dominant and sends CO₂ to the network |
| Electrified | no carbon input at all |

Waste counts as fossil, which is the conservative reading for the EU clinker
mix. Change `FOSSIL_IN` / `BIO_IN` in `taxonomy.py` to adjust.

## Editing

Changing a grouping or a colour is a one-line edit in `taxonomy.py`. Changing the
house style is a one-line edit in `theme.py`. Slide copy — headline, standfirst
and side notes — sits inline in each `slide_*` function.

Slides are 13.33 × 7.5 in at 160 dpi, which drops straight into a 16:9 PowerPoint
or Google Slides page at full bleed.

## A note on the numbers

These are the model's own outputs, presented as the run produced them. `P12`
records the conventions behind them, including the emission-accounting items
still being reconciled in `../analysis_v2/`. Keep that slide in the deck — it is
the honest answer to the first question a reviewer will ask, and it is written to
inform rather than to alarm.
