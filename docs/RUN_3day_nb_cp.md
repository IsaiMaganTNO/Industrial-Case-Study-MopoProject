> **SUPERSEDED (2026-10-10):** the copper-plate solve was stopped and abandoned in favour of merging the nodes; see `docs/RUN_3day_nb_ctry.md`.

> **SUPERSEDED (2026-10-11):** the copper-plate run was stopped and never finished. Replaced by node merging, see `docs/RESULT_3day_nb_ctry.md`.

# RUN: 3day_nb_cp - NL+BE at country resolution ("copper plate")

Date: 2026-10-10. Display name for slides: **Country-level** (vs Standalone = 3day_nb_v2).

## Build
- Source: `runs/3day_nb_v2/input/Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite` (Standalone).
- Tool: `tools/copperplate_country.py SRC DST`.
- DB: `checkpoints/Final_SpineOpt_Model.tiny.3day.nb_cp.sqlite`.

What changed: the limits and costs on the 596 zone-to-zone connections inside the same country (BE-BE, NL-NL; carriers elec, CH4, H2, CO2, HC, MeOH, bio) were removed.
- Removed: `capacity_per_connection`, `connection_flow_cost`, investment parameters, lifetimes.
- The connections become lossless (ratio 1.0), uncapacitated and free, so all zones of a country behave as one node.
- Every network is strongly connected (checked for all 14 country/carrier pairs), so every zone can reach every other.

Method choice: zones are KEPT as nodes, not merged. Every demand, unit, profile, potential, storage cap and the CO2 budget is untouched. The run differs from Standalone ONLY in internal network constraints. NL-BE and border links are unchanged.

## Verification (`run_logs/_cp_verify.py`)
- Entity counts identical to Standalone; scenarios identical.
- Parameter values: 0 added, 0 changed, 1,844 removed - all on intra-country connections (0 elsewhere).
- Preflight: all checks PASSED (weights 100.81 / 159.38 / 104.81).

## Solve
Started 22:03, Gurobi, 8 threads, scenario filter `baseline_blended_representative_periods`.
Out: `checkpoints/Investment_Results.3day_nb_cp.sqlite`. Log: `run_logs/3day_nb_cp_solve.out`.


