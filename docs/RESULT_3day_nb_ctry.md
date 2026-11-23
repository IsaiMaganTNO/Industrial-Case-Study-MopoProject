# RUN/RESULT: 3day_nb_ctry - NL+BE at country resolution ("Country-level")
Date: 2026-10-10/11. Display name: **Country-level** (vs **Standalone** = 3day_nb_v2, 17 IC1 zones).
Purpose: isolate the effect of spatial resolution (same data, scenario, years, rep. days).

## Build
- Source: `runs/3day_nb_v2/input/Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite`.
- Tool: `tools/merge_zones_to_country.py SRC DST` (raw SQL, FK on).
- The 119 zone network nodes `<carrier>_(BE|NL)C<k>` (carriers elec, CH4, H2, CO2, HC, MeOH, bio) were merged into 14 country nodes `<carrier>_BE` / `<carrier>_NL`.
  - The lowest-numbered zone node was kept and renamed; all relationships were re-pointed to it.
- The 596 intra-country connections were deleted.
- Electricity `demand` was summed per country and weather year (BE 8 zones, NL 9 zones).
  - The total of 80,120,284.90 is unchanged.
- The other node parameters (CO2 `storage_active` / `storage_longterm_active`, `cyclic_condition*`) were asserted identical across the merged zone nodes before merging.
  - 60 duplicate CO2 `node__temporal_block` entries were dropped; their parameters were identical.
- Units, storage nodes, transport/heat demand nodes and VRE profiles keep their zone names.

## Verification (vs Standalone)
- Entity count changes:
  - connection 596
  - connection relationships 980 per class
  - node 105
  - node__temporal_block 60
- No other class changed.
- All unit relationships and unit parameter counts and sums are unchanged. The 883 kept connections have byte-identical parameters.
- No zone network nodes remain. Scenarios and alternatives are unchanged.
- `foreign_key_check`: 8,514 violations, identical to the source DB. They are pre-existing, from the `unit_flow__unit_flow` superclass encoding.
- `tools/preflight_check.py`: all checks passed.

## Solve
- Scenario `baseline_blended_representative_periods`, Gurobi with 8 threads.
- Status: OPTIMAL, 66.3 min, peak RAM 46.7 GB.
- Objective **3,602,610**, vs 3,644,339 Standalone (41.7k, 1.1%).
- **Penalties = 0 (PASS).**
- Log: `3day_nb_ctry_solve.out`. DBs are in `input/` and `output/`.

## Key results (NL+BE)
| | 2030 | 2040 | 2050 |
|---|---|---|---|
| Electricity TWh (Std / Ctry) | 256 / 258 | 355 / 373 | 502 / 474 |
| Hydrogen TWh | 12.7 / 19.2 | 42.5 / 42.5 | 106.5 / 68.1 |
| Methane TWh | 412 / 412 | 223 / 223 | 133 / 119 |
| Emissions Mt | 165.4 / 165.4 | 36.8 / 36.8 | 0 / 0 |
| CO2 stored Mt (cap) | 2.5 / 2.5 | 27.2 / 27.2 | 27.2 / 27.2 |
| Industry output | identical | identical | identical |

- **Industry routes and output are unchanged.**
  - 2050 fuel split is nearly the same: NG 17.1  16.4, electricity 9.5  10.1, H2 1.4  0.8, biomass 3.1  3.8.
  - This confirms that the industry results are not driven by intra-country grid limits.
- **The 2050 difference is in hydrogen and power.**
  - PEM output falls 64  26 TWh.
  - H2 use falls in `(H2)PEA` (57.9  33.0) and methanation (44.3  31.3).
  - Nuclear output falls 80  53 TWh (investment costs 104  59).
  - Battery output is spread across more zones.
  - Interpretation, not verified: with the zonal grid limits removed, there is no need for locally produced H2/e-CH4 and firm nuclear at specific zones.
- **The CO2 storage cap binds in both runs**, so the CO2 budget/storage outcome is the same.
- BE biomass use in 2050 is 3.5  11.6 TWh and NL 39.6  31.5 TWh; the total is about the same.

## Plots
`plots/compare_standalone/` C01C10, made with `tools/plot_compare_nlbe.py` and these environment variables:
- `CMP_NAME_A=nb_v2`, `CMP_NAME_B=nb_ctry`
- `CMP_LABEL_A=Standalone (17 zones)`, `CMP_LABEL_B=Country-level (NL, BE)`

Caches: `run_logs/nb_ctry.pkl`, `nb_ctry_NLBE.pkl`, `nb_ctry_xbbio.pkl`.

## Tool changes made for this run
- `tools/postprocess.py` `REGION`: added `BE|NL` (country nodes). Without it, half of the supply rows and all CO2-network rows were dropped. Zone names are unaffected.
- `tools/extract_xb_bio.py`: the same regex fix.
- `tools/plot_compare_nlbe.py`: the run keys and DB paths now come from `CMP_NAME_A/B`.
