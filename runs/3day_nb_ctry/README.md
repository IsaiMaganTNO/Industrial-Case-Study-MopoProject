# 3day_nb_ctry - "Country-level" (NL+BE at country resolution)

Purpose: isolate the effect of spatial resolution. Same model as Standalone (`3day_nb_v2`, 17 zones),
but the zone network nodes are merged into one node per country and carrier.

## Build
- Tool: `tools/merge_zones_to_country.py SRC DST`, source `runs/3day_nb_v2/input/...nb_v2.sqlite`.
- 119 zone network nodes (elec, CH4, H2, CO2, HC, MeOH, bio x 17 zones) -> 14 country nodes (`elec_BE`, `CO2_NL`, ...).
- 596 connections inside a country deleted. NL-BE and border connections re-pointed to the country nodes; their parameters are unchanged (883 connections checked).
- Electricity demand summed per country for each weather year (8 BE zones, 9 NL zones). Total unchanged (80,120,284.90).
- 60 duplicate CO2 temporal-block links removed (identical settings).
- Units, storage nodes, transport/heat demand nodes and VRE profiles keep their zone names.
- Unit relationships and unit parameter counts and sums: unchanged. Preflight: PASS.
- Foreign-key check: 8,514 violations, identical to the source model (DB storage of unit-flow-to-unit-flow links), so not caused by the merge.

## Solve
- Scenario `baseline_blended_representative_periods`, Gurobi, 8 threads.
- OPTIMAL, 66.3 min, peak RAM 46.7 GB. Log: `3day_nb_ctry_solve.out`.
- **Penalties: 0 (PASS).**
- Objective 3,602,610 vs Standalone 3,644,339 (-1.1%).

## Key differences vs Standalone (NL+BE)
| | Standalone | Country-level |
|---|---|---|
| Electricity 2040 / 2050 (TWh) | 355 / 502 | 373 / 474 |
| Hydrogen supply 2030 / 2050 (TWh) | 12.7 / 106.5 | 19.2 / 68.1 |
| Methane supply 2050 (TWh) | 133 | 119 |
| CO2 stored 2030/40/50 (Mt) | 2.5 / 27.2 / 27.2 | same (cap binding in both) |
| Industry output | 46.2 | 46.2 (same) |
| Nuclear investment (cost units) | 104 | 59 |
| Biomass 2050 BE / NL (TWh) | 3.5 / 39.6 | 11.6 / 31.5 (same total) |

Emissions follow the same path (2050 net about 0 in both).

## Files
- `input/`, `output/`: model and results DBs (moved, not copied).
- `plots/compare_standalone/`: C01-C10 comparison plots and CSVs (labels "Standalone (17 zones)" and "Country-level (NL, BE)").
- Caches: `run_logs/nb_ctry.pkl`, `nb_ctry_NLBE.pkl`, `nb_ctry_xbbio.pkl`.

## Tool changes made for this run
- `tools/postprocess.py`: the `REGION` pattern also accepts plain `_BE` / `_NL` (country nodes). Zone names are read the same as before.
- `tools/extract_xb_bio.py`: same change for biomass nodes.
- `tools/plot_compare_nlbe.py`: run names and DB paths come from `CMP_NAME_A/B` (previously hardcoded to nb_v2/mr_fix).

## Presentation
- `SLIDES_Standalone_vs_CountryLevel.pdf`: 18-slide deck (`python tools/make_slides_ctry.py <out.pdf>`). Display names: **Standalone** = 3day_nb_v2 (17 zones), **Country-level** = 3day_nb_ctry.
- Shareable plots: `plots/compare_standalone/`, `plots/summary_named_standalone/`, `plots/summary_named_countrylevel/`. Slide previews: `plots/slides_png/`.
- Analysis: `ANALYSIS_standalone_vs_countrylevel.md`.
