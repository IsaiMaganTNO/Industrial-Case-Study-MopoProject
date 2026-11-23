# IC1 slide deck - run `3day_vre15`

Sixteen 16:9 slides plus a combined PDF, built straight from the two SQLite
databases. 2132x1200 px, drops into PowerPoint or Google Slides at full bleed.

- **Deck:** `IC1_vre15_deck.pdf`
- **Slides:** `P01`-`P16` as individual PNGs

## Build command

```powershell
cd plot_scripts
..\.venv\Scripts\python.exe presentation\build_deck.py `
  --results ..\checkpoints\Investment_Results.3day_vre15.sqlite `
  --input   ..\checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite `
  --out presentation\out_vre15 --pdf IC1_vre15_deck.pdf `
  --title "A power system that finally adds up" `
  --label "three representative days per milestone (14 May, 10 Sep, 24 Dec), weighted to 365"
```

The `--input` database is **required**, not optional: it supplies the
representative-day weights. Verified on build - 9 modelled days, weights
100.81 / 159.38 / 104.81 per milestone, summing to **365.0**, correctly keyed to
the 2041 calendar year for the 2040 milestone.

## Slides

| file | message |
|---|---|
| `P01_cover.png` | Headline KPIs: scope, emissions, storage, solve status |
| `P02_co2_pathway.png` | Net CO2 against the budget, with the driver for each year |
| `P03_emission_sources.png` | Gross emissions by part of the system |
| `P04_ccs_chain.png` | Sankey: capture source -> regional hub -> North Sea storage |
| `P05_co2_geography.png` | Real IC1 NUTS3 geometry: emissions, capture, pipeline flows |
| `P06_industry_routes.png` | Route mix per sector, 2030 vs 2050 |
| `P07_industry_capture.png` | Capture penetration by sector against sector size |
| `P08_industry_detail.png` | Per-sector production detail |
| `P09_energy_carriers.png` | Electricity, methane and hydrogen across the three years |
| `P10_supply_mix_electricity.png` | **The headline slide.** Electricity mix by milestone |
| `P11_fuel_supply.png` | Fuel supply by source |
| `P12_transmission_network.png` | Transmission network utilisation |
| `P13_capacity_change.png` | What is added and retired between 2030 and 2050 |
| `P14_capacity_vintage.png` | 2050 fleet split between legacy plant and new build |
| `P15_regions_ranked.png` | Regions ranked by emissions, with capture alongside |
| `P16_scope_and_method.png` | Conventions and open items, in neutral language |

**Keep `P16` in the deck.** It is the honest answer to the first question a
reviewer will ask.

## Numbers verification

The deck is built by a **different reader stack** (`plot_scripts/analysis_v2/`)
than the analysis report (`tools/postprocess.py`). The two were cross-checked on
this run and agree exactly:

| 2050 | analysis | deck |
|---|---:|---:|
| Total electricity | 347.7 TWh | 347.7 TWh |
| Nuclear | 51.4 | 51.4 |
| Onshore wind | 37.3 | 37.3 |
| Solar PV | 54.1 | 54.1 |

## What to say when presenting

The story is a chain of three corrections, each of which only became visible once
the previous one was fixed:

1. CO2 pipelines were one-directional -> fixed.
2. Gas supply ran at **100% load factor, every hour of every year** -> capped.
   Gas-with-capture collapsed from 131 TWh to zero; offshore wind appeared.
3. Onshore wind and solar had **no land constraint** -> limited. Offshore wind
   doubled to 193 TWh and nuclear entered at 51 TWh.

Cost of respecting land availability: **+2.9%** on total system cost. Carbon
outcomes are unchanged, because the CO2 budget binds in every case - so this is a
*how we decarbonise* result, not a *how much* result.

## Caveats to state out loud

1. **Three representative days.** Good enough for investment conclusions, but it
   **cannot resolve extended low-wind periods** - exactly what determines how much
   firm capacity is needed. The 51 TWh nuclear figure is **indicative only**.
2. **The Belgian nuclear result is not validation of Belgian policy.** It lands at
   ~5.9 GW against an external expectation of 6 GW, but that is coincidence:
   Belgium builds nuclear because it has **one** offshore zone and exhausts it,
   while the Netherlands has five and never runs out. See
   `docs/FINDING_nuclear_BE_vs_NL_asymmetry.md`.
3. **No electricity trade.** DE/FR/UK/LU are boundary placeholders with no
   generation or demand; NL+BE are solved as an island.
4. **Gas is capped at a flat 50% availability**, whereas the project's own IC1 gas
   budget implies a declining trajectory. Next correction.
5. **CO2 transport uses the low-cost variant**; a 4.8x high-cost variant exists.
6. Known open items: a 2030 switch to existing coal; a 2050 gas-boiler rebuild;
   floating and bottom-fixed offshore wind each receiving a full allocation of the
   *same* seabed.

## Taxonomy gaps

The build prints technologies falling through to the catch-all "Other" emission
group. On this run, 12 did, including `gas-extraction`, `coal-boiler-existing`,
`oil-boiler-existing`, `oil-eng`, `Scraps_EAF` and `REF(H2)`. They are **not
dropped** - they appear under "Other" - but if any becomes material to the story,
extend the maps in `plot_scripts/presentation/taxonomy.py`.

## Companion analysis plots

`reports_v2_vre15/` holds the analytical figure set, including three custom
comparison charts (`COMPARE_01/02/03`) that show the before/after and the
binding-limits diagnostic.
