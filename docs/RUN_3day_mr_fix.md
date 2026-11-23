# RUN 3day_mr_fix - mixed resolution, same assumptions as nn_fix (2026-10-09)
Source: `checkpoints/Final_SpineOpt_Model.tiny.3day.mixedres.sqlite` (unchanged; serves as backup).
Patches in order:
1. `patch_co2_storage_div365.py`: 48 rows, 16 sites incl. DE/DK/NO/UK
2. `patch_nodac_lng.py`: DAC 21 -> 0; LNG 1.0; NL extraction 0
3. `patch_nuclear_country_caps.py`: BE 0/6/6, NL 0/4/5, UK 6/11/13, DE/DK/NO 0
4. `patch_restamp_2041.py`: 2040-01-01 points added
Guard 377 / 2532.8882 unchanged; preflight PASSED.
Model `checkpoints/Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite`; results `checkpoints/Investment_Results.3day_mr_fix.sqlite`; log `run_logs/3day_mr_fix_solve.out`.
Solver: Gurobi, 8 threads, scenario filter baseline_blended_representative_periods. Started 18:39; expected about 2.3 h, 51 GB RAM.

CANCELLED 2026-10-09 by user decision (NL+BE first with corrected biomass). Model kept for later reuse.

## SOLVE OUTCOME (re-run 2026-10-09)
Started 21:08, finished 23:29 (141.6 min). RAM 31.4 -> 52.7 GB. OPTIMAL, **penalties 0 (PASS)**, objective **7,073,666**.
Split: fixed O&M 3,857,637; investment 2,557,379; taxes 460,354; variable O&M 113,467; connection flow 43,662; storage investment 38,984; connection investment 2,184.
Results: checkpoints/Investment_Results.3day_mr_fix.sqlite (171 MB).
