# FINDING: Route A region plumbing works, but the data layer does not follow

Date: 2026-10-08

## 1. Route A itself is DONE and verified

`define_polygons(cfg, region_data, "IC1", "OFF3")` now returns **21 onshore**
polygons (8 BEC + 9 NLC + DE + DK + NO + UK) and **32 offshore**, each new
country's OFF3 zones attached to its own onshore region. FR/LU correctly absent.

Three edits were required, not one:
- `IC1` sheet 17 -> 21 rows (geometry copied from `PECD1`).
- `PECD1_IC1`: the DE/DK/NO/UK `target` cells held the *formula* `=A17` etc.
  pandas renders these as NaN, so a pandas-only check would have reported the
  identity rows as already present. openpyxl exposed them. Replaced with literals.
- `OFF3_map.IC1`: blank for all 26 offshore zones of the four countries.
  `define_polygons` L104/L110 does `.tolist()[0]` on that lookup, so a blank
  raises IndexError. Filled with the country code.

`userconfig.yaml` `countries` went 2 -> 6. **All codes must be quoted**:
unquoted `NO` is YAML 1.1 boolean false. This was observed live - the list
printed as `['BE','NL','DE','DK',False,'UK']` and only 20 polygons appeared.

Only `_ines-builder/region_transformation.xlsx` was edited. Three sibling
copies exist (all md5 59ef3fdbd13e); `ines_target.py` L1698 opens the bare
relative name and the Toolbox item sets `execute_in_work: false`, so cwd is
`_ines-builder` and the edited copy is the one read. `_industry-aidres` keeps
its own `_IC1` copy, untouched.

## 2. BLOCKER: regions exist, data does not

All 13 pipelines are IC1 -> IC1. At `ines_target.py` L228
`source_level == target_level`, so the builder takes the **direct lookup**
branch and never calls `ines_aggregrate`. A new region therefore gets data only
if the sector source store already carries that region code. Measured:

| store | DE | DK | NO | UK |
|---|---|---|---|---|
| transmission_db, cargo_db | yes | yes | yes | yes |
| gas_db | yes | - | - | yes |
| power_db, vre_db(onshore), heat_db, rdemand_db, biomass_db, transport_db, hydro_db, industry_db, other_industry_db | - | - | - | - |

So rebuilding now would create DE/DK/NO/UK as demand-free, generation-free
stubs that only extend the transmission graph. **Do not solve in this state.**

## 3. SEPARATE DEFECT found while investigating: Step 1 staging broke geolevel

`power_DB.py` L116 does `geomap[geomap["level"] == geolevel]`, where `geolevel`
comes from `data/Energy_Conversion/config.json` - NOT from the Excel workbook
and NOT from userconfig.yaml.

The Step 1 hybrid-dataset overlay **overwrote that file and flipped
`geolevel` from `IC1` to `PECD1`** (old md5 1989205330fd, staged 22ad0a3eefbb).
`geodata/IC1.geojson` contains only features with `level == "IC1"`, so the
filter would have matched **zero** regions and the power importer would have
produced an empty fleet. Reverted to `IC1` and verified.

The same staged file also added `bioST+CC` to `units_new` (16 -> 17 entries).
That change was left in place and needs a decision - it is a scope change, not
a defect.

Lesson: the Step 1 manifest verified that 53 files were *copied correctly*. It
did not verify that their *contents were compatible* with the existing run
configuration. Other staged config/scenario files should be diffed against
`backups/data-pre-mixedres/` on the same basis before any rebuild.

## 4. Relevant to the next step: IC_NWEU.geojson

`verification/IC_NWEU.geojson` has 21 features matching the 21 regions we now
want, but its `level` values are `IC1_NWEU` for 20 features and `IC_NWEU` for
UK. Since `power_DB.py` filters on exact equality with `geolevel`, adopting
this file requires normalising `level` to a single value and setting
`geolevel` to match - otherwise UK is silently dropped. The four country
features also have null `area_km2`.
