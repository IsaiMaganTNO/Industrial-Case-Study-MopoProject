# RESULT - INES_DB verification after mixed-resolution build (2026-10-08)

Build: `run_logs/_mr_build2.log`, `ines_builder` EXIT=0 at 23:02:51.
DB: `.spinetoolbox/items/ines_db/INES_DB.sqlite` (820 MB, 19,622 entities).
Script: `tools/verify_mixedres_inesdb.py` (read-only).

## Outcome vs predictions

| Prediction | Result |
|---|---|
| EU-merge P6: DE/DK/NO/UK get heat/transport/industry entities | PASS - heat 67, transport 115 each; industry DE 315 / UK 286 / NO 232 / DK 170 |
| Heat hourly `flow_profile` present for the 4 countries | PASS (same structure as BEC1) |
| Hydro: DE 7, NO 12, UK 7, DK 0 | PASS (DK has no hydro, as in EU case) |
| Biomass P1/P2: supply present for all 4 countries incl. NO | PASS - `biomass-stock_XX.storages_existing` (GWh): DE 519,690 (medium) = 1,871 PJ, NO 40,236 = 144.8 PJ - matches raw CSV |
| Constraints P5: atmosphere budget 1146.35 / 254.745 / 0 | PASS |
| CO2 storage injection for DE/DK/NO/UK | Present (NS/AS/AT storage sites) |

## Open before solve
- `fossil-CH4` limit: alternative `limited_fossil-CH4` is NOT in the active scenario (inert).
- 365x per-representative-period hazard on `limited_commodity` (P6 of biomass prediction) not yet verified.
- Per-country nuclear caps (workbook) not applied - needs schema change.
- Log has many `Repeated Entity region__commodity__region ... not added` messages (duplicate-skip, likely harmless).
- Next pipeline step: INES_DB -> SpineOpt conversion, scenario setup, clustering, test solve.
