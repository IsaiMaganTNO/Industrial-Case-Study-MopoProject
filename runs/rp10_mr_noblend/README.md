# Sensitivity run: mixed resolution (MR) with 10 representative days, not blended

Scenario `mr_ccslow_ccu_cap16_dac0`, pessimistic CCS. This is the same model as the 3-day MR run in
`final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK`, except that it uses 10 representative days instead of 3.

## Set-up
- The input is a fresh copy of the 3-day MR input database, built by `run_logs\_rp10_noblend_build.py`.
- The 9 representative blocks (3 per year) were replaced with 30 blocks (10 per year). Each block has 1 h resolution and `representative_block_index` 1–30.
- The days are the EU case's TulipaClustering result for weather year 2009. Day of year and weight (days represented):

  | Day of year | 182 | 11 | 147 | 262 | 119 | 199 | 359 | 348 | 222 | 176 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | Weight | 13.6 | 60.8 | 28.1 | 62.2 | 56.7 | 14.0 | 27.0 | 47.2 | 27.9 | 27.5 |

  Sources: `EU_case\...\src\_clustering\results\representative_periods.csv` and `weights_wy2009.csv`.
- **Not blended.** Like the 3-day run, each year's map is a single row, with weight/365 per block. Year 2040 uses calendar 2041 dates.
- Storage, cyclic conditions (copied per block), the `all_rps` group, alternatives (Base / wy2009) and scenarios are the same as in the 3-day run.
- Checked with `_rp10_noblend_check.py` and `_cyc_chk.py`: all 27,994 non-temporal entities and 37,098 parameter values are identical to the 3-day database.

## Solve
- Run with `tools\run_solve_live.ps1` and Gurobi (`tools\solve_tiny_gurobi.jl`). Started 22-10-2026 10:44, finished 23-10-2026 23:26 (36 h 42 min).
- Building the model took 9 h 02 min. The model has 11.8 M rows × 13.0 M columns (1.59 M × 2.31 M after presolve). Peak RAM was about 102 GB.
- Barrier converged in 126 iterations (about 9 h) and crossover took about 18 h. Termination: OPTIMAL. Objective 8.418e6, which is 10.7% above the 3-day run's 7.607e6.
- The atmosphere balance penalty is 0.

## Files
- Input: `Final_SpineOpt_Model.tiny.10day_noblend.mr_ccslow_ccu_cap16_dac0.sqlite`
- Output: `output\Investment_Results.10day_noblend_mr_ccslow_ccu_cap16_dac0.sqlite`
- Log: `10day_noblend_mr_ccslow_ccu_cap16_dac0_solve.out`
- Caches: `run_logs\rp10nb_mr_ccslow_ccu_cap16_dac0{,_NLBE,_xbbio}.pkl`
- Comparison scripts and outputs: `run_logs\_rp10nb_cmp.py/.out` and `run_logs\_rp10nb_routes.py/.out`

## Results: NL+BE in 2050, 3 days vs 10 days
| | 3-day | 10-day |
|---|---|---|
| Offshore wind (TWh) | 246 | 311 |
| Onshore wind / solar (TWh) | 37 / 53 | 29 / 66 |
| Electrolysis H2 (TWh) | 28 | 46 |
| Heat from heat pumps (TWh) | 36 | 139 |
| Heat from bioenergy (TWh) | 87 | 21 |
| CO2 captured (Mt) | 50.7 | 35.6 |
| CO2 exported to UK (Mt) | 34.7 | 15.3 |
| CO2 stored in NL / DK / NO / UK (Mt) | 16 / 11 / 56 / 52.5 | same |
| Net export of electricity / H2 / CH4 (TWh) | 41 / 33.5 / 316 | 31 / 40 / 393 |

Industry routes, as shares of each sector's output in NL+BE (output volumes are the same in both runs):
- Cement in 2040 and 2050: 100% LC3 with oxyfuel capture (3-day: 78% CEM2 with oxyfuel capture).
- Primary steel in 2040: 100% NG-DRI-EAF with capture (3-day: 21.5% BF-BOF).
- Container glass in 2050: 100% NG with capture (3-day: 38% electric, 5% H2).
- Pulp in 2040 and paper in 2030 differ by 2–5 percentage points. All other sectors and years are the same.

## Interpretation
With more representative days, NL+BE building heat moves from biomass to heat pumps. This brings more offshore wind, solar and electrolysis.

Capture in NL+BE falls, and the CO2 export to the UK more than halves. The storage used per country does not change.

The overall pattern holds: NL+BE remain net exporters of electricity, H2 and CO2, and a CH4 transit hub.
