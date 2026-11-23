# 3day_mr_ccslow_ccu_cap16_dac0 - Mixed resolution, pessimistic CCS, FINAL

NL+BE in 17 IC1 zones + DE, DK, NO, UK as one node each. Shared 6-country CO2 cap.

## Changes vs `3day_mr_ccslow_dac0`
- CCU leak closed: `tools/patch_ccu_co2.py` on 21 methanation units (synthetic CH4 carries 0.2 t CO2/MWh to atmosphere).
- NL storage NSNL012 2050 = 13.5 Mt (`tools/patch_co2cap_set.py`) -> NL total 16 Mt/yr. Other countries' low_CO2 caps unchanged.
- DAC `existing_units = 0` (already in the source DB).

## Solve (16-10-2026, 19:19 -> 21:43)
- Gurobi barrier + crossover, OPTIMAL. Model 3.56 M rows x 3.97 M cols. Solve 983 s.
- Objective 7,606,649 (old 7,623,391; -0.2%).
- Penalties 0 (PASS). DAC 0. Methanation 0.

## Key results 2050 (NL+BE)
- NL storage 2.5 / 10.5 / 16.0 Mt (2030/40/50), binding.
- CO2 exported to UK 34.7 Mt (old 39.7). Captured 50.7 Mt. NL+BE net emissions 89.7 Mt (6-country cap is the binding one).
- Offshore wind 246 TWh, electrolysis 28 TWh, methane (gross LNG landed) 488 TWh, heat pumps 36 TWh.

## Files
- `input/Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite`
- `output/Investment_Results.3day_mr_ccslow_ccu_cap16_dac0.sqlite`
- `3day_mr_ccslow_ccu_cap16_dac0_solve.out`
- Caches: `run_logs/mr_ccslow_ccu_cap16_dac0{,_NLBE,_xbbio}.pkl`
