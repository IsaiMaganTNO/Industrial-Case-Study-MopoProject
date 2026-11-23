# 3day_mr_ccslow_dac0 - Mixed resolution, pessimistic CCS, DAC disabled (FIXED)

Snapshot written 2026-10-14. This run **supersedes `3day_mr_ccslow`** (free default DAC unit).

## Model
- Source: `runs/3day_mr_ccslow/input/...mr_ccslow.sqlite` (mr_fix + pessimistic CCS: `low_CO2` caps, high-cost CO2 tariffs).
- Patch: `tools/patch_dac_existing0.py` adds `existing_units = 0` (Base) to all 21 DAC_* units. The SpineOpt default is 1.0, which gave each region one free DAC unit.
- Verify (`run_logs/_dac0_verify.py`): 21 values added, 0 removed; entities and scenario identical. Preflight `--cap-below 5`: all PASS.

## Solve
- Gurobi, 8 threads, 18:36-20:54 on 2026-10-13 (138.0 min). OPTIMAL. Objective **7,623,390**. Penalties 0 (`run_logs/_dac0_pen.py`).
- DAC unit_flow = 0 in all years (verified).

## Results (whole model, Mt CO2)
- Net: 788.5 / 254.7 / 0 (2030/40/50).
- Stored: 7.4 / 111.4 / 129.9.

## Files
- `input/`, `output/`, `3day_mr_ccslow_dac0_solve.out`.
- Caches: `run_logs/mr_ccslow_dac0{,_NLBE,_xbbio}.pkl`.
