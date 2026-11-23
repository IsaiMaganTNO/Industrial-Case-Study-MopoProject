# RUN (build only): 3day_mixedres - NL+BE at IC1 + DE/DK/NO/UK at country level

Date: 2026-10-09. **Model built, patched, preflight PASSED. Not yet solved.**

Model DB: `checkpoints/Final_SpineOpt_Model.tiny.3day.mixedres.sqlite` (198 MB)
Upstream: `INES_DB` verified in `docs/RESULT_mixedres_inesdb_verify.md`.

## Pipeline
1. `ines_to_spinetop` - EXIT 0 (`run_logs/_mr_convert.log`, ~9 min)
2. `make_cluster_seed.py --days 134 253 358` (14 May / 10 Sep / 24 Dec = 3-day baseline days)
3. `run_pipeline.py --from merge_spineopt` -> **failed at run_clustering**: clustering input now
   has **8** profiles (new `reservoir`, from NO/DE/UK hydro); seed had 7. Re-ran the seed tool,
   resumed `--from run_clustering` -> EXIT 0. Final_SpineOpt_Model entities 26,705 -> 31,375.
4. `make_tiny_model.py` -> 219 timesteps (3 + 3x24x3). Weights 104.62/146.26/114.12.

## Patches (all on the 21-region build, in standard order)

| # | patch | result | 21-region change made to the tool |
|---|---|---|---|
| 1 | route_emissions | 197 targets, +312 route rows, -197 fuel rows, 115 new atmosphere links | **`base()` regex was IC1-only** -> DE/DK/NO/UK skipped silently ("no route data"). Fixed. |
| 2 | co2_cap_div365 | max series 1146.35/254.745/0 -> 3.1407/0.6979/0 | readback hard-coded to 165.4/36.8 -> now checks computed values. **Also divides `initial_cumulative`** (was done upstream by old `patch_co2_caps.py` in the 17-region chain; preflight caught 1146.35). |
| 3 | biomass_cap_div365 | 252 rows; medium_bio 516,382 -> 1,414.7 | none |
| 4 | screen_retirement + retire_industry | 292 RETIRE-SAFE (priced 74, scaffold 218), 16 BLOCKED sole producer | **screen regex was IC1-only** - fixed. Fresh screen `run_logs/retire_screen_mixedres.csv`. |
| 5 | hc_co2 | 57 units | none (name-based) |
| 6 | co2_bidirectional | 62 -> **124** CO2 connections, integrity ok | ids now resolved by name |
| 7 | gas_availability | LNG 0.50 on **19** terminals (17 IC1 + 2 country-level, incl. `LNG-terminal_UK`); extraction 0.0 on **NL only** (9). DE/DK/NO extraction untouched. UK has no extraction unit in the data. | NL-only extraction; ids by name; fixed guard only with `--expect-guard` |
| 8 | onshore_vre_potential | 42 groups; table below | history table extended to DE/DK/UK from `scenario_config.yml`; NO has no history -> 0.15 only; caps never raised |

Onshore result (GW): BE wind 3.60 / solar 12.77, NL 7.20 / 33.50 (**identical to vre15**),
DE 65.50 (history) / 139.30, DK 5.67 / 22.69, NO 38.17 / 152.68, UK 25.42 / 101.67.

Regression: patches 6/7/8 dry-run on the 17-region checkpoints reproduce the old row counts
and BE/NL values exactly.

## New baseline guard values (21 regions)
Cross-border `investment_count_initial_cumulative` on `connection`: **377 rows, sum 2532.8882**
(was 327 / 1522.5048). Unchanged through all 8 patches.

## Decisions recorded
- `limited_fossil-CH4` left **inert** (user, 2026-10-09): keeps gas treatment identical to the
  BE/NL baseline; likely carries the same 365x issue. Candidate follow-up sensitivity.
- Per-country nuclear caps: not applied.
- **UK gas extraction: absent - known gap, accepted (user, 2026-10-09).** Checked
  `EU_case/data/Gas/Gas_Sectors_Dataset.xlsx!CH4_Production`: 16 countries have
  `gas-extraction` (NO 3,931, DK 105.6, DE 77.0, NL 284.6 GWh/d) but **not UK** - identical
  to our dataset. UK has only `LNG-terminal_UK` (1,616.45 GWh/d, af 0.5). UK can import
  Norwegian gas via the network. Revisit with ENTSOG TYNDP if UK gas proves material.

## Preflight
`preflight_check.py --expect-days 134 253 358 --cap-below 10` -> **all checks PASSED**.
(`--cap-below` added: the default 1.0 threshold assumed the BE+NL budget.)

## Solve risks
- 17-region 3-day solve took ~88 min / 40 GB RAM. 21 regions with full sectors in 4 large
  countries: expect substantially longer.
- DE wind-on and BE/NL caps sit on the history floor -> binding; check `penalties == 0` first.

## SOLVE OUTCOME (2026-10-09)
Gurobi (`tools/solve_tiny_gurobi.jl`, 8 threads). Start 00:33, end 02:51 = **138.6 min**.
RAM 30.3 -> 51.5 GB. **OPTIMAL**, primal FEASIBLE_POINT, **penalties 0.000000 (PASS)**.
Objective **7,198,010** (17-region vre15: 3,510,170). Results:
`checkpoints/Investment_Results.3day_mixedres.sqlite`. Log: `run_logs/3day_mixedres_solve.out`.

Split: fixed_om 3,913,624; unit_investment 2,606,220; taxes 477,518; variable_om 122,228;
connection_flow 55,993; storage_investment 19,798; connection_investment 2,627; fuel 0; penalties 0.

Next: compare NL+BE (IC1) results against vre15 - capacity mix, cross-border flows, CO2.

## Results & plots (2026-10-09)
Analysis: `docs/RESULT_3day_mixedres.md`. Plots: `reports_v2_mixedres/` via `tools/plot_mixedres_compare.py`
(01-05 NL+BE vs vre15 incl. IC1 maps; 06 21-region maps of emissions/CO2 storage+pipelines/electricity/capture; 07 country mixes; 08 objective).
