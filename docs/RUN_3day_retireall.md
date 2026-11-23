# RUN: 3-day Group 1 + biocap365 + full industry retirement (`retireall`)

Launched 2026-10-04 15:48. Input
`checkpoints/Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.sqlite`,
results -> `checkpoints/Investment_Results.3day_retireall.sqlite`,
log `run_logs/3day_retireall_solve.out`.

Baselines for comparison:
| run | objective |
|---|---:|
| `group1` (baseline) | 3,250,651 |
| `biocap365` (corrected biomass) | 3,334,510 |
| `retireall` | TBD |

## What changed vs `biocap365`

199 `investment_count_max_cumulative` rows, float -> declining time_series
`{2030: X, 2041: X/2, 2050: 0, 2060: 0}` where X = endowment. Nothing else.
Verified by full row-level diff (199 rows, one parameter, 31,470 rows both
sides) and BLOB type assertion.

## Predictions registered BEFORE the result

Writing these down so the run can falsify them.

1. **Status OPTIMAL.** The screen cleared every patched unit for per-region
   capacity adequacy. If INFEASIBLE, the screen is insufficient - most likely a
   regional energy balance (H2/elec) rather than sector capacity - and the
   `--tier priced` run bisects it.
2. **Objective rises** vs 3,334,510. Removing free incumbents can only remove
   options, never add them. A FALL would mean I have misunderstood the shape.
3. **The six flat sectors move.** Glass (container/float/fibre), pulp, paper,
   aluminium currently sit at 100% single route in all years. They should shift
   toward the priced alternatives by 2050.
4. **Chlorine stays flat at 100% `Diaphragm`** - deliberately excluded, sole
   producer. This is the control: if chlorine moves, something is wrong.
5. **Steel-secondary stays 100% scrap** - also excluded, same reason.
6. **Electricity demand rises**, since most alternatives
   (`pulp/paper/aluminium-production-alternative`, `(EL)_g*`) are
   electricity-fed. Possible knock-on: more VRE or more gas+CCS.

## The honest caveat

A clean OPTIMAL would NOT prove the scaffolding tier is the right modelling
choice. 175 of the 199 units have no capex and no FOM and rail to a 1000.0
bound - they look like scaffolding, not plant. If the result swings hard on
those, the finding is "the endowment convention drives the industry result",
which is a statement about the DATA, not about decarbonisation economics.
