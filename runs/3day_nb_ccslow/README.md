# 3day_nb_ccslow - "Standalone, pessimistic CCS" (NL+BE, 17 zones)

Same as Standalone (`3day_nb_v2`) except two CCS assumptions:
- CO2 storage caps: `low_CO2` instead of `high_CO2` (NL: 2.5 / 10.5 / 10.5 Mt/yr in 2030/40/50, vs 2.5 / 27.2 / 27.2).
- CO2 tariffs from `verification/CO2_data_IC1_high_cost.xlsx` instead of the low-cost file:
  - 70 transport costs (`connection_flow_cost`), 6x higher;
  - 6 injection costs (`vom_cost` on CO2-injection units), 1.2-4.7x higher.
Built with `tools/make_ccs_pessimistic.py SRC DST LOW.xlsx HIGH.xlsx`. The tool checks every old value equals the low-cost file before replacing it.

## Verification
- vs Standalone: 76 parameter values changed (all of the above), 0 added/removed, entities identical.
- Only scenario difference: rank 7 `high_CO2` -> `low_CO2`. Preflight: PASS.

## Solve
- OPTIMAL, 90.2 min, peak RAM 54.3 GB. **Penalties: 0 (PASS).**
- Objective 3,829,100 vs Standalone 3,644,339 (+5.1%).
- Net CO2 165 / 37 / 0 Mt (same as Standalone). Stored 2.5 / 10.5 / 10.5 Mt (at the new cap).

## Files
- `input/`, `output/`: model and results DBs (moved, not copied); `3day_nb_ccslow_solve.out`.
- Cache: `run_logs/nb_ccslow.pkl`.
