# 6 – Mixed resolution, optimistic CCS (sensitivity S3)

Baseline = run 3 (`mr_ccslow_ccu_cap16_dac0`). The only change is CCS back to optimistic:
- Scenario alternative `low_CO2` → `high_CO2` (storage caps as in the original model).
- 132 CO2 tariffs (112 transport, 20 injection) back to `verification/CO2_data_IC1_low_cost.xlsx`.
- Kept: DAC `existing_units = 0`, methanation CCU fix. The NL 16 Mt cap is not active (it is defined in `low_CO2`).
- Build/check: `run_logs/_ccsopt_build.py`, `_ccsopt_diff.py` (the 15 values that differ from `mr_fix` differ only by float rounding).

Solve 28-10-2026 14:11–16:56 (2 h 45 min), OPTIMAL, objective **7.190e6** (−5.5% vs baseline 7.607e6), **penalties 0**.

## Key results (NL+BE unless stated), 2050: optimistic vs pessimistic
- CO2 stored (whole model) 356 vs 135 Mt: UK 164, NO 69, DE 60, DK 36.5, NL 27.2 (all sites at their caps).
- CO2 captured: BE 54.5 (16), DE 142.5 (55), UK 95 (14), NL 42 (34) Mt.
- CO2 exports from NL+BE to the UK 69 vs 35 Mt (BE→UK 54).
- Heat: bioenergy 87 → 5 TWh; unabated fossil heat 6 → 102 TWh (its emissions are offset by storage instead).
- Offshore wind 246 → 169 TWh; electrolysis 28 → 9 TWh; methane net export 316 → 60 TWh.
- Industry: ammonia moves to (NG)NH3-MVR-DEA; cement fully CEM2 oxyfuel with capture; primary steel in 2040 is 50% BF-BOF; container and fibre glass move from H2/electric to NG with capture.
- No CCU: all CO2 is injected.

Details: `comparison_vs_baseline.txt` (from `run_logs/_ccsopt_all.py`). Caches: `run_logs/mr_ccsopt_ccu_dac0{,_NLBE,_xbbio}.pkl`.
