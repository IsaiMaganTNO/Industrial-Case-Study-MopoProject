# RESEARCH STATE - SpineOpt industrial decarbonisation (snapshot 2026-10-13 18:00 CEST)

Purpose: restart point if the session or workspace is lost. Repo: `Industrial-Case-Study-MopoProject`.
Environment: Windows, pwsh, venv `.\.venv\Scripts\python.exe`, Julia SpineOpt + Gurobi (`tools/run_solve_live.ps1`, `tools/solve_tiny_gurobi.jl`).

## 1. Model setup (common to all runs)
- Pipeline: data-pipelines -> INES_DB (`.spinetoolbox/items/ines_db/INES_DB.sqlite`) -> SpineOpt conversion -> scenario setup -> clustering -> `checkpoints/Final_SpineOpt_Model.tiny.3day.*.sqlite`.
- Temporal: "3day" = 3 representative days per milestone year 2030 / 2040 / 2050 (investment years).
- CO2 budget (atmosphere node, shared by all modelled countries): 1146.35 / 254.745 / 0 Mt (2030/2040/2050) for 6 countries; NL+BE-only runs use their own NL+BE budget (165.4 / 36.8 / 0).
- Spatial NL+BE "IC1": 17 zones (NLC1..NLC9, BEC1..BEC8).
  - CH4 inter-zone links: 70, fixed, not expandable.
  - H2 links: 70, all expandable (investment cost, 40-yr lifetime).
  - Electricity links: 60 (38 expandable, 50-yr; 22 fixed).
  - Salt caverns: storage investment cost 2.65 / 1.45 / 0.69 (2030/40/50), ~0 FOM, charge/discharge links free, efficiency 1.0.
- CO2 transport and storage data: `verification/CO2_data_IC1_{low,high}_cost.xlsx`.
  - Sheets: `network` (171 rows), `network_to_storage` (28), `storage` (low/medium/high caps; same in both files).
  - The pipeline default `CO2_data_IC1.xlsx` = low-cost file.
  - High-cost file: pipeline tariffs x6, storage-link (injection) tariffs x1.2-4.7, shipping unchanged.
- Penalty check after every solve: `run_logs/_mfpen.py` template (replace DB path). All runs below: penalties = 0.

## 2. Runs (all OPTIMAL, penalties 0)
Folder convention: `runs/3day_<name>/{input,output}/`, solve log, README, `plots/`. Caches: `run_logs/<name>.pkl`, `<name>_NLBE.pkl`, `<name>_xbbio.pkl`.

| Run | Display name | Scope | CCS assumption | Objective | Solve |
|---|---|---|---|---|---|
| `3day_nb_v2` | Standalone (IC1) | NL+BE, 17 zones | base: `high_CO2` caps + low-cost tariffs | 3,644,339 | - |
| `3day_nb_ctry` | Country-level | NL+BE merged to 1 node/country | base | 3,602,609 (-1.1%) | - |
| `3day_mr_fix` | Interconnected / mixed resolution | NL+BE IC1 + DE/DK/NO/UK 1 node each | base | 7,073,666 | - |
| `3day_nb_ccslow` | IC1 pessimistic | as nb_v2 | `low_CO2` caps + high-cost tariffs | 3,829,096 (+5.1%) | 90.2 min |
| `3day_nb_ctry_ccslow` | Country pessimistic | as nb_ctry | pessimistic | 3,777,356 (+4.9%) | 71.2 min |
| `3day_mr_ccslow` | Mixed-res pessimistic | as mr_fix | pessimistic | 7,618,824 (+7.7%) | 150.2 min |

(`3day_nn_fix` is an older run, not part of this comparison set.)

### How variants were built
- Country-level: `tools/merge_zones_to_country.py` (user-edited; recursive `delete_entities`). Merges 119 zonal network nodes into 14 country nodes, deletes 596 intra-country connections, sums demand. Unit nodes stay zonal.
- Pessimistic CCS: `tools/make_ccs_pessimistic.py SRC DST LOW.xlsx HIGH.xlsx`.
  - Swaps scenario alternative `high_CO2` -> `low_CO2` (same rank).
  - Sets CO2 `connection_flow_cost` = high `network` tariff / 1000, and CO2-injection `vom_cost` = high `network_to_storage` tariff / 1000.
  - Asserts every old value equals the low-cost file first.
  - Changes: nb_ccslow 76 (70+6); nb_ctry_ccslow 22 (16+6); mr_ccslow 132 (112+20). No entities added or removed.
- mr_ccslow preflight needs `tools/preflight_check.py --cap-below 5` (the 6-country budget also fails the default on mr_fix).
- Low caps for the 14 non-NL sites are NOT yet cross-checked against the spreadsheet low column (open).

## 3. Key results (whole model; Mt CO2 for 2030/2040/2050)
| Run | Net CO2 | Stored CO2 |
|---|---|---|
| nb_v2 | 165 / 37 / 0 | 2.5 / 27.2 / 27.2 |
| nb_ctry | 165 / 37 / 0 | 2.5 / 27.2 / 27.2 |
| nb_ccslow | 165 / 37 / 0 | 2.5 / 10.5 / 10.5 (cap) |
| nb_ctry_ccslow | 165 / 37 / 0 | 2.5 / 10.5 / 10.5 (cap) |
| mr_fix | 795 / 255 / 0 | 5 / 296 / 356 |
| mr_ccslow | 797 / 255 / 0 | 8 / 111 / 130 |

Details: `docs/ANALYSIS_standalone_vs_countrylevel.md`, `docs/ANALYSIS_pessimistic_ccs.md`.

## 4. Documents, decks, plots
- `docs/ANALYSIS_standalone_vs_countrylevel.md` + `runs/3day_nb_ctry/SLIDES_Standalone_vs_CountryLevel.pdf` (`tools/make_slides_ctry.py`).
- `runs/3day_mr_fix/SLIDES_Standalone_vs_Interconnected.pdf` (`tools/make_slides.py`).
- `docs/ANALYSIS_pessimistic_ccs.md` (this round). Plots from `tools/plot_compare_nlbe.py` (env `CMP_NAME_A/B`, `CMP_LABEL_A/B`):
  - `runs/3day_nb_ccslow/plots/cmp_vs_base/`
  - `runs/3day_nb_ctry_ccslow/plots/cmp_vs_base/`
  - `runs/3day_mr_ccslow/plots/cmp_vs_base/`
  - `runs/3day_nb_ctry_ccslow/plots/cmp_vs_ic1_pess/`
  - `runs/3day_mr_ccslow/plots/cmp_vs_ic1_pess/`
- Metrics: `run_logs/ccs_metrics_NLBE.csv` (`run_logs/_ccsmetrics.py`); whole-model diffs in `run_logs/_ccsdiff.out`.

## 5. Tools (tools/)
- `make_ccs_pessimistic.py`, `merge_zones_to_country.py`, `preflight_check.py` (`--db`, `--cap-below`).
- `postprocess.py` (PP.load / load_weights; REGION regex accepts `_BE`/`_NL`), `filter_pkl_countries.py`, `extract_xb_bio.py`.
- `plot_run_summary.py` (route labels), `plot_compare_nlbe.py`, `make_slides.py`, `make_slides_ctry.py`.

## 6. Open items
- Low caps for non-NL sites vs spreadsheet low column: unverified.
- mr_fix: BE biomass 158 TWh unexplained.
- mr runs: NL+BE-attributed net CO2 is not 0 in 2050 (106 / 90 Mt); the 6-country total is 0. Removals (DAC/BECCS) and storage sit partly outside NL+BE, so NL+BE net is an accounting view, not a constraint.
- Possible cavern-cost sensitivity; disk cleanup of old checkpoints awaits approval.
- From `docs/RESULT_mixedres_inesdb_verify.md`: `limited_fossil-CH4` not in the active scenario; per-country nuclear caps not applied.

## CORRECTION 2026-10-13 ~18:40 - DAC is NOT fully disabled (free default unit)
- `patch_nodac_lng.py` set `investment_count_max_cumulative = 0` for all DAC_* units (no *new* DAC). That is in place in all six runs.
- But no unit has an explicit `existing_units`, and the SpineOpt default is **1.0**. Each DAC_* unit has `capacity_per_unit = 1.0` on its CO2 output, so every region gets **one free existing DAC unit**. Up to 1 CO2 unit/h, about 8.76 Mt/yr per region, with no investment cost.
- Evidence (`run_logs/_free1.py`-`_free3.py`): units_invested = 0 for all DAC, yet DAC_NLC1 in mr_fix runs at max 1.0, mean 0.60 per hour.

DAC capture (Mt) per run:

| Run | 2030 | 2040 | 2050 |
|---|---|---|---|
| nb_v2 | 0.10 | 0 | 0 |
| nb_ctry | 0.36 | 0 | 0 |
| nb_ccslow | 0.33 | 0 | 0 |
| nb_ctry_ccslow | 0.25 | 0 | 0 |
| mr_fix | 0 | 142.9 | 172.6 (21 regions, ~8 Mt each) |
| mr_ccslow | 0 | 26.6 | 14.9 |

- Consequence: the NL+BE-only runs are essentially unaffected (DAC <0.4 Mt, 2030 only). **mr_fix and mr_ccslow are contaminated.** DAC is a large free negative-emission source there, which inflates storage use (356 Mt) and the mr pessimistic-vs-base deltas. The mr conclusions in this document should not be shared until the runs are redone with DAC `existing_units = 0`.

## UPDATE 2026-10-14 - Mixed resolution re-run with DAC fixed (`3day_mr_ccslow_dac0`)
- This run supersedes `3day_mr_ccslow`. OPTIMAL, 138 min, objective 7,623,391 (+0.06% vs the free-DAC run), penalties 0, DAC = 0.
- NL+BE 2050 numbers barely change vs the free-DAC run:
  - Net CO2 93 Mt; 10.5 Mt stored; 40 Mt CO2 exported (NL->UK 24, BE->UK 15).
  - Electrolysis 29 TWh; offshore wind 249 TWh; methane 475 TWh.
  - Heat: pumps 37, bio 87, gas 6 TWh. Nuclear 8.4 GW.
  - Industry: steel 100% gas DRI+CCS; ammonia 100% gas SMR+CCS; cement 58% biomass oxy-fuel (BECCS).
- Section 3b conclusions stand. Metrics for the three pessimistic runs: `run_logs/ccs_metrics_pess_NLBE.csv`.
- Decks (`tools/make_slides_pess.py {ctry|mr|combined} out.pdf`):
  - `runs/3day_nb_ctry_ccslow/SLIDES_Pess_IC1_vs_CountryLevel.pdf` (16 p.)
  - `runs/3day_mr_ccslow_dac0/SLIDES_Pess_IC1_vs_MixedRes.pdf` (16 p.)
  - `reports/pessimistic_ccs/SLIDES_Pess_Resolution_vs_Scope.pdf` (10 p.)
