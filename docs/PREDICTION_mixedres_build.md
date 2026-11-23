# PREDICTION - mixed-resolution build (21 regions)

Date: 2026-10-08. Registered BEFORE ines_builder completes.

## What changed vs the vre15 baseline

Inputs rewired (`backups/project.json.pre-mixedres` holds the old wiring):
| item | was | now |
|---|---|---|
| power_importer | `geodata/IC1.geojson` | `geodata/IC1_NWEU.geojson` (21 polys) |
| rdemand_importer | `other_electricity_demand_IC1.csv` | `..._IC1_NWEU.csv` (21 cols) |
| gas_import | `Gas_Sectors_Dataset_IC1_placeholder.xlsx` | `Gas_Sectors_Dataset.xlsx` |
| VRE_importer | `data/VRE/*` | `data/VRE_NWEU/*` (aggregated) |

Config: `userconfig.yaml` countries 2 -> 6 (quoted); `config.json` geolevel
restored IC1; `region_transformation.xlsx` IC1 sheet 17 -> 21 rows,
`PECD1_IC1` identity rows literalised, `OFF3_map.IC1` filled.

## Already MEASURED (not predictions)

- power_db 21 regions, vre_db 98 (21 onshore + 77 OFF3), rdemand_db 21,
  gas_db 52 (21 + 31 inert).
- The 31 extra gas regions carry 0 parameter values but DO appear in 322
  multi-dim entities (158 pipeline, 63 technology__region, ...). Verified
  `define_polygons` returns 21 onshore and **none** of the 31, and
  `ines_builder` iterates `for target_poly in polygons[...]`, so they cannot
  leak. This is the one thing I would most expect to be wrong.
- Power fleet pinned: 42 shared BE/NL series restored to vre15 values
  (28 updated), 17 new target-country series passed through untouched.
  `--check` now reports DIFFERING 0.

## PREDICTIONS

P1. `ines_builder` exits 0.
P2. `INES_DB` entity count rises well above the 14,966 baseline.
P3. BE/NL-only quantities are UNCHANGED vs baseline where they should be -
    specifically the 42 pinned `units_existing` series must reappear with
    identical values. If BE/NL drifts, something coupled the regions that
    should not have.
P4. The 31 inert gas countries do NOT appear in `INES_DB`.
P5. `ines_to_spinetop` exits 0 and `SpineOpt_target` gains the 4 countries.

## What I am NOT predicting

I will not predict solve feasibility or any economic quantity. The four new
countries have power, demand, gas, VRE and transmission but **no heat, no
road/non-road transport, no run-of-river hydro, no industry**. Their demand
is electricity-only, so their load is understated relative to their capacity.
Expect them to look like net exporters. That is a known artefact of this
build, not a result.

## Blind spot

The weighted-mean VRE aggregation was validated on capacity factors and sums,
and the reconstructed time index was cross-checked against 223,032
unambiguous timestamps. But I have NOT verified that `ines_builder` picks up
`profile_limit_upper` for the 4 new country regions - that parameter is
written per-region by `VRE_DB.add_technology_relationship`, and if the
builder's direct-lookup branch misses it the countries would get VRE capacity
with no profile. Check this explicitly in INES_DB before solving.
