# Run 4: mixed resolution with per-country CO2 caps, storage credit to the host (option A)

This run is identical to run 3 (`3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK`, 3 representative days, scenario `mr_ccslow_ccu_cap16_dac0`), except for one change: the CO2 cap is set per country instead of jointly for all six countries.

## Change compared with run 3
- The single `atmosphere` node is split into `atmosphere_{NL,BE,DE,DK,NO,UK}`. All parameters are copied, including `balance_penalty` = 10000.
- Each emitter is linked to its own country's node: NL 387 links, BE 326, DE 94, UK 85, NO 70, DK 56.
- Each of the 20 CO2-injection credit links (1 t removed from the atmosphere node per tonne stored) goes to the country where the storage site is: NL 6, UK 8, NO 3, DK 2, DE 1. BE has none.
- Each country's cap is its share of the original cap, based on 1990 emissions. Source: `verification\global_constraints_industry_case_study.xlsx`; 2030 is 45%, 2040 is 10%, and 2050 is 0.

  | Mt | NL | BE | NO | DE | DK | UK |
  |---|---|---|---|---|---|---|
  | 2030 | 99.8 | 65.6 | 22.8 | 563.0 | 32.3 | 362.8 |
  | 2040 | 22.2 | 14.6 | 5.1 | 125.1 | 7.2 | 80.6 |

- Built by `run_logs\_ctryco2_build.py` and checked by `run_logs\_ctryco2_check.py`. Apart from the atmosphere nodes, all entities, parameter values and scenarios are identical to run 3.

## Solve
- Gurobi. Total time 2 h 42 min. Termination: OPTIMAL. Objective 8.965e7 (run 3: 7.607e6).
- **Penalty: 8.10e7, from 8.1 Mt over the cap in 2050: BE 2.0 Mt and DE 6.1 Mt.**
  - BE has no storage, so it can never earn a credit.
  - DE's CO2 is stored in NO and the UK, so those countries receive the credit.
- Excluding the penalty, costs are about 12% higher than run 3, mainly from more unit investment (4.01e6 vs 3.05e6).
- The country caps bind in 2030 and 2040 for NL, BE and NO, and in 2040 also for DK and the UK.
- Analysis scripts: `run_logs\_ctryco2_pen2.py` and `_ctryco2_pen3.py`.

## Interpretation
Under national caps where only the storage host gets the credit, countries without their own storage (BE) or without the credit for it (DE) cannot reach net zero in 2050. Option B, where the credit goes to the exporting country, is run separately in `runs\ctryco2B_mr`.

## Files
- `input\Final_SpineOpt_Model.tiny.3day.ctryco2_mr_ccslow_ccu_cap16_dac0.sqlite`
- `output\Investment_Results.ctryco2_mr_ccslow_ccu_cap16_dac0.sqlite`
- `ctryco2_mr_ccslow_ccu_cap16_dac0_solve.out`
