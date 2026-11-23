# 10day_mr_ccslow_ccu_cap16_dac0 - sensitivity: 10 representative days (EU case)
Same as `final_runs_pessimistic_ccs/3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK`, only the temporal blocks differ.

## Build (`run_logs/_rp10_build.py`)
- Copied the 3-day MR input DB.
- Copied EU case `representative_periods.csv` + `weights_wy2009.csv` (TulipaClustering, convex hull, weather year 2009 = same as ours) into `results/`.
- Ran our `clustering_output.py` (removes old blocks, writes 10 blocks/year + blended `representative_blocks_by_period`).

## Checks (`run_logs/_rp10_check.py`)
- 30 blocks, indexes 1..30 contiguous; weights sum to 365 per year; map has 365 rows, each summing to 1.
- Days (day-of-year): 11, 119, 147, 176, 182, 199, 222, 262, 348, 359.
- Weights (days): 60.8 (11 Jan), 62.2 (19 Sep), 56.7 (29 Apr), 47.2 (14 Dec), 28.1, 27.9, 27.5, 27.0, 14.0, 13.6.

## Solve
```
pwsh tools\run_solve_live.ps1 -Db runs\rp10_mr\Final_SpineOpt_Model.tiny.10day.mr_ccslow_ccu_cap16_dac0.sqlite `
  -Out runs\rp10_mr\output\Investment_Results.10day_mr_ccslow_ccu_cap16_dac0.sqlite `
  -Script tools\solve_tiny_gurobi.jl -LogPath runs\rp10_mr\10day_mr_ccslow_ccu_cap16_dac0_solve.out
```
3-day reference: 3.56 M rows, 2 h 23 min total. Expect roughly 3x the model size.
