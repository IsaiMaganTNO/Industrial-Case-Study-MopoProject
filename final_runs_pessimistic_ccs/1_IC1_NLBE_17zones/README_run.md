# 3day_nb_ccslow_ccu_cap16_dac0  IC1 (17 zones, NL+BE), pessimistic CCS, CCU-fixed

Status: OPTIMAL, penalties = 0 (checked 2026-10-16). Solve 85.3 min (Gurobi, 8 threads).
Objective: 3,941,040 (old IC1 nb_ccslow: 3,829,096; +2.9%).

## Input = runs/3day_nb_ccslow/input/...nb_ccslow.sqlite + three patches
1. CCU fix (tools/patch_ccu_co2.py): 17 methanation units emit 0.2 t CO2/MWh CH4 output to atmosphere
   (synthetic CH4 previously burned carbon-free -> captured CO2 counted as removed).
2. CO2 storage cap (tools/patch_co2cap_set.py): low_CO2 NSNL012 2050/2060 = 13.5 Mt/yr
   -> total 2050 = 16.0 Mt/yr (NSNL031 2.5). 2030 (2.5) and 2040 (10.5) unchanged.
3. DAC off (tools/patch_dac_existing0.py): existing_units = 0 on all 17 DAC units
   (SpineOpt default existing_units=1 gave free DAC capacity despite investment being blocked).

## Why 16 Mt
- CCU fix only, 10.5 Mt: 2050 excess 1.33 Mt (penalty 13.25 M).
- CCU + 12.5 Mt, free DAC: 0 penalties but DAC 26.3 Mt (2050) feeding (H2)MeOH-DC -> invalid.
- CCU + 12.5 Mt, DAC off: 2050 excess 2.29 Mt (penalty 22.87 M).
- CCU + 16 Mt, DAC off: 0 penalties. Storage binding in all years (2.5 / 10.5 / 16.0 Mt).

## Key results (weighted)
- DAC = 0, methanation = 0 in all years.
- Captured CO2 2050: 31.8 Mt (REF-SMR-MEA 14.7, bio-diges-up+CC 6.5, (LN)O-MEA 6.4, LC3-(Afm)Oxy-CaL 2.5, (NG)DRI-EAF-MEA 1.0).

## Files
- input/Final_SpineOpt_Model.tiny.3day.nb_ccslow_ccu_cap16_dac0.sqlite
- output/Investment_Results.3day_nb_ccslow_ccu_cap16_dac0.sqlite
- 3day_nb_ccslow_ccu_cap16_dac0_solve.out
