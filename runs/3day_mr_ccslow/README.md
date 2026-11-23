# 3day_mr_ccslow  Mixed resolution, pessimistic CCS

Base: `runs/3day_mr_fix` (NL+BE IC1 zones + DE/DK/NO/UK single nodes).
Changes (tools/make_ccs_pessimistic.py): scenario alternative `high_CO2` -> `low_CO2` (storage caps, 16 sites);
132 CO2 tariffs replaced with `verification/CO2_data_IC1_high_cost.xlsx` (112 transport, 20 injection; 12 NO shipping routes unchanged = equal tariffs).
Entities identical to mr_fix. Preflight PASS (`--cap-below 5`).

## Solve
Gurobi, 8 threads, 150.2 min, RAM peak 59.2 GB. OPTIMAL. Penalties = 0 (PASS).
Objective 7,618,824 (mr_fix 7,073,666, +7.7%).

## CO2 (Mt/yr)
| | 2030 | 2040 | 2050 |
|---|---|---|---|
| Net, system (mr_fix) | 794.8 | 254.7 | 0.0 |
| Net, system (ccslow) | 797.0 | 254.7 | 0.0 |
| Stored, system (mr_fix) | 5.3 | 296.4 | 356.4 |
| Stored, system (ccslow) | 7.8 | 111.4 | 129.9 |
| Net NL+BE (mr_fix / ccslow) | 241.7 / 238.7 | 138.0 / 135.5 | 106.0 / 90.3 |
| Stored NL+BE (mr_fix / ccslow) | 0.6 / 2.5 | 27.2 / 10.5 | 27.2 / 10.5 |

Storage 2050 by site region (ccslow): UK 52.5, NO 55.9, DK 11.0, NLC1 8.0, NLC5 2.5, DE 0 (mr_fix: UK 164, NO 68.7, DE 60, DK 36.5, NL 27.2).

Files: `input/Final_SpineOpt_Model.tiny.3day.mr_ccslow.sqlite`, `output/Investment_Results.3day_mr_ccslow.sqlite`, `3day_mr_ccslow_solve.out`.
Caches: `run_logs/mr_ccslow.pkl`, `run_logs/mr_ccslow_NLBE.pkl`.
