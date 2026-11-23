# 3day_nb_ctry_ccslow_ccu_cap16_dac0 — Country-level (NL+BE), pessimistic CCS, CCU-fixed

Status: OPTIMAL, penalties = 0 (checked 2026-10-16). Solve 66.5 min (Gurobi, 8 threads).
Objective: 3,774,840 (old Country-level nb_ctry_ccslow: 3,777,356).

## Input = runs/3day_nb_ctry_ccslow/input/...nb_ctry_ccslow.sqlite + same three patches as IC1
1. CCU fix (tools/patch_ccu_co2.py): 17 methanation units, 0.2 t CO2/MWh CH4 output.
2. CO2 storage cap (tools/patch_co2cap_set.py 13.5): 2050 total 16.0 Mt/yr; 2030/2040 unchanged.
3. DAC off (tools/patch_dac_existing0.py): existing_units = 0 on all 17 DAC units.

## Key results (weighted)
- DAC = 0, methanation = 0 in all years. Storage binding: 2.5 / 10.5 / 16.0 Mt.
- Captured CO2 2050: 27.5 Mt (REF-SMR-MEA 15.4, (LN)O-MEA 8.9, LC3-(Afm)Oxy-CaL 2.5, ((COEL)MeOH)O-MEA 0.5, (MeOH)O-MEA 0.2).
