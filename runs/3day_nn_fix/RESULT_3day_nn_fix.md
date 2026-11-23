# RESULT 3day_nn_fix - scenario filter + 2041->2040 restamp (2026-10-09)
Model `checkpoints/Final_SpineOpt_Model.tiny.3day.nn_fix.sqlite`; results `checkpoints/Investment_Results.3day_nn_fix.sqlite`; cache `run_logs/nn_fix.pkl`.
Solve 16:09-17:40 (90.9 min, Gurobi 596 s). OPTIMAL, **penalties 0 (PASS)**, objective **3,663,545** (-4.5% vs nodac_nuc 3,835,677).

| NL+BE | nodac_nuc (old) | nn_fix |
|---|---|---|
| CO2 storage 2040 | 9.0 Mt (2.5 + 6.5) | **27.2 Mt** (both sites at cap) |
| CO2 storage 2050 | 27.2 | 27.2 |
| Emissions (Mt) | 165.4 / 36.8 / 0 | 165.4 / 36.8 / 0 (budget binds) |
| Electricity excl. offshore (TWh) | 181.6 / 217.4 / 203.1 | 190.4 / 194.1 / 188.7 (incl. offshore 71/166/320: 262 / 364 / 514) |
| New nuclear NL 2040/50 (GW) | 4.0 / 4.85 | 3.4 / 4.43 (BE 6.0 at cap) |
| PEM H2 (TWh) | 0 / 55.7 / 54.5 | 0 / **0** / 66.0 |
| LNG (TWh) | 417 / 104 / 99.6 | 421 / **226** / 97.8 |
| Methanation | 0 / 65 / 28.8 | 0 / 9.7 / 44.5 |
| Cement 2030 | 96% oxy-MEA | **100% reference** (CCS from 2040) |
| Olefins 2040 | 33% MEA | 100% MEA |
| Ammonia 2050 | 56% bio / 44% H2 | 45% bio / 54% NG+CCS (no H2-NH3) |
| Steel | identical: MOE 57% / NG-DRI-MEA 43% from 2040 |

Interpretation: with the full 2040 storage cap and the fossil-CH4 limit gone, 2040 decarbonises by CCS on fossil gas instead of electrolysis. The unrealistic 2030 cement switch disappears.


**SUPERSEDED (2026-10-09):** biomass was understated (pipeline data loss) and older technology data was used. Replaced by run 3day_nb_v2.
