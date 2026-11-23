# PREDICTION - Route A mixed-resolution region enablement

Date: 2026-10-08
Run: ines_builder rebuild after adding DE/DK/NO/UK to the IC1 sheet.

## Changes made
1. `data-pipelines/europe/_ines-builder/region_transformation.xlsx`
   - `IC1` sheet: 17 -> 21 rows. Added DE/DK/NO/UK with `level=IC1`,
     `per_km2`/`area_km2` copied verbatim from the `PECD1` sheet.
   - `PECD1_IC1` sheet: 4 rows for DE/DK/NO/UK had `target` stored as the
     *formula* `=A17` etc., which pandas reads as NaN. Replaced with literal
     identity strings. (openpyxl `data_only=False` exposed this; pandas hid it.)
   - `OFF3_map` sheet: `IC1` column was blank for all 26 offshore zones of
     DE/DK/NO/UK. Filled with the country code so `define_polygons` can attach
     them. Without this the dict comprehension at L104/L110 raises IndexError.
2. `data-pipelines/europe/userconfig.yaml`: `countries` 2 -> 6 entries,
   ALL QUOTED. Unquoted `NO` parses as boolean false under YAML 1.1; this was
   observed live (countries list printed as `['BE','NL','DE','DK',False,'UK']`
   and onshore polygons came back 20 not 21).

Note: only `_ines-builder/region_transformation.xlsx` was edited. Three other
copies of the workbook exist (`europe/region_transformation.xlsx`,
`europe/region_transformation_IC1.xlsx`,
`_industry-aidres/region_transformation_IC1.xlsx`, all md5 59ef3fdbd13e).
`ines_target.py` L1698 opens the bare relative name and the Toolbox item has
`execute_in_work: false`, so cwd is `_ines-builder` and the edited file is the
one read. The industry pipeline reads its own `_IC1` copy and was NOT touched.

## Verified already (not predictions)
- `define_polygons(cfg, rd, "IC1", "OFF3")` returns 21 onshore polygons
  (8 BEC + 9 NLC + DE/DK/NO/UK) and 32 offshore, with each new country's
  OFF3 zones attached to its own onshore region. FR/LU absent as intended.

## PREDICTIONS (register before running)

P1. `ines_builder` exits 0.

P2. `INES_DB` region/node count rises above the 14,966-entity baseline.
    DIRECTION only; no magnitude claimed.

P3. **The four new regions will be largely EMPTY of sector data.**
    Rationale: all 13 pipelines run IC1->IC1, so `source_level == target_level`
    and `ines_target.py` L228 takes the *direct lookup* branch, NOT
    `ines_aggregrate`. Data therefore appears only if the sector source store
    already carries that region code. Measured today:
      - have DE/DK/NO/UK : cargo_db, transmission_db
      - have DE/UK only  : gas_db
      - have NEITHER     : power_db, heat_db, biomass_db, transport_db,
                           hydro_db, industry_db, other_industry_db,
                           rdemand_db, vre_db(onshore)
    So I expect DE/DK/NO/UK to receive transmission + cargo (+ partial gas)
    and essentially no generation, demand, heat, industry or VRE.

P4. Consequently the solve, if attempted now, would be **infeasible or
    absurd**: the new regions would be demand-free, generation-free stubs
    that merely extend the transmission graph.

## Blind spot of this check
I have confirmed region *existence* and the polygon plumbing. I have NOT
confirmed region *data*. P3/P4 state explicitly that I expect the data layer
to be the next blocker. Specifically unexamined: whether any pipeline
back-fills a country-level region from PECD1/PECD2 sources at import time
(i.e. whether re-running the sector importers with the new userconfig would
populate power_db/vre_db/rdemand_db with DE/DK/NO/UK rows). That is the
decisive open question and must be tested before any solve.
