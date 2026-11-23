# RUN 3day_nodac - NL+BE IC1, no DAC, LNG 1.0, CO2 storage /365 (2026-10-09)
Model : `checkpoints/Final_SpineOpt_Model.tiny.3day.nodac.sqlite`, built from `...gascap.vre15.sqlite` plus:
  1. `patch_co2_storage_div365.py`: 6 rows (NSNL012 21 -> 0.0575, NSNL031 6.2 -> 0.017 high)
  2. `patch_nodac_lng.py`: 17 DAC max 1000 -> 0; 17 LNG 0.5 -> 1.0; NL extraction stays 0
  Guard 327 / 1522.5048 unchanged; integrity ok; preflight PASSED.
Results: `checkpoints/Investment_Results.3day_nodac.sqlite`. Log: `run_logs/3day_nodac_solve.out`.
Started 12:12, Gurobi, 8 threads.
Risk: 2050 net-zero without DAC and with NL+BE storage of only 27.2 Mt/yr -> check penalties first.

## Follow-up: 3day_nodac_nuc (2026-10-09)
Model `checkpoints/Final_SpineOpt_Model.tiny.3day.nodac_nuc.sqlite` = nodac + `patch_nuclear_country_caps.py`
(BE 0/6/6, NL 0/4/5 GW; 8+9 unit links). Preflight PASSED, integrity ok, guard 327/1522.5048.
Results -> `checkpoints/Investment_Results.3day_nodac_nuc.sqlite`, log `run_logs/3day_nodac_nuc_solve.out`.
Outcome (finished 15:30): OPTIMAL, penalties 0 (PASS), objective 3,835,677 (+0.6% vs nodac), Gurobi 712 s, RAM 47.5 GB.
Details: `docs/RESULT_3day_nodac_nuc.md`.
