# 3day_nb_ctry_ccslow - "Country-level, pessimistic CCS" (NL+BE, 1 node per country)

Country-level model (`3day_nb_ctry`) with the same pessimistic CCS changes as `3day_nb_ccslow`:
- CO2 storage caps `low_CO2` instead of `high_CO2` (NL 2.5 / 10.5 / 10.5 Mt/yr).
- High-cost CO2 tariffs (`verification/CO2_data_IC1_high_cost.xlsx`):
  - 16 transport costs (only the NL-BE links remain at country level);
  - 6 injection costs.
Built with `tools/make_ccs_pessimistic.py`.

## Verification
- vs `3day_nb_ctry`: 22 values changed, 0 added/removed, entities identical, only scenario difference `high_CO2` -> `low_CO2`.
- All 22 new values are identical to the IC1 pessimistic model. Preflight: PASS.

## Solve
- OPTIMAL, 71.2 min, peak RAM 51.1 GB. **Penalties: 0 (PASS).**
- Objective 3,777,356: +4.9% vs Country-level 3,602,609; -1.4% vs Standalone pessimistic 3,829,096.
- Net CO2 165 / 37 / 0 Mt. Stored 2.5 / 10.5 / 10.5 Mt (at cap).

## Files
- `input/`, `output/` (moved), solve log. Cache `run_logs/nb_ctry_ccslow.pkl`.
