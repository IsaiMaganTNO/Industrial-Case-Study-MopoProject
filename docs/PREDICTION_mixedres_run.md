# PREDICTION - mixed-resolution run (IC1 BE/NL + country DE/DK/NO/UK)

Date: 2026-10-08. Register BEFORE running. Check `penalties == 0` FIRST.

## What changed
1. `region_transformation.xlsx`: IC1 sheet 17->21; PECD1_IC1 formula->literal
   identity for the 4; OFF3_map.IC1 filled for 26 offshore zones.
2. `userconfig.yaml`: countries 2->6, all quoted (unquoted NO == false).
3. `data/Energy_Conversion/config.json`: geolevel PECD1 -> IC1 (staging regression).
4. `geodata/IC1_NWEU.geojson` (new): 21 features, level normalised to IC1,
   area_km2 filled. 17 IC1 polygons geometrically identical to the old file.
5. `data/Rdemand/other_electricity_demand_IC1_NWEU.csv` (new): 21 cols,
   comma-delimited (importer uses default sep).
6. Gas repointed to the full pan-EU workbook.
7. `data/VRE_NWEU/` (new): onshore aggregated PECD2->country by
   capacity-weighted mean (profiles) / sum (GW). Offshore copied verbatim.

## Verified pre-run (facts, not predictions)
- define_polygons -> 21 onshore, 32 offshore.
- geojson passes the exact `level=="IC1"` filter -> 21 regions.
- spatial join: 561.6 GW over 21 regions (DE 313.9, UK 137.9, NO 40.3, DK 12.7).
- aggregated CF within member range AND equal to independent recompute
  (delta < 1e-6) for all 4 countries, both wind and solar.
- potentials/capacities sum exactly; BE/NL byte-equal passthrough.
- 2009 demand TWh: DE 400.8, UK 265.7, NO 91.8, DK 29.2.

## PREDICTIONS

P1. All four importers exit 0.
P2. `power_db` region count 17 -> 21.
P3. `vre_db` onshore regions 17 -> 21; offshore stays 77 (OFF3, untouched).
    Total region entities 94 -> 98.
P4. `rdemand_db` 32 -> 21 regions. **This is a DECREASE** because the old
    store carried 15 `Unnamed: 18..32` junk columns from the trailing commas
    in the old IC1 csv. Their disappearance is a FIX, not data loss.
P5. `gas_db` regions 21 -> 23ish (gains DK/NO; already had DE/UK).
P6. `ines_builder` exits 0 and INES_DB entity count rises well above 14,966.
P7. Sectors still IC1-only (heat, transport road/non-road, hydro RoR,
    industry, biomass) will contribute NOTHING to the 4 countries. The new
    regions will therefore have electricity demand + power fleet + VRE + gas
    + transmission, but no heat/transport/industry demand.
P8. Because of P7 the 4 countries are **net exporters by construction** -
    they carry ~505 GW of plant and ~788 TWh of electricity demand but none
    of the heat/transport/industry load that would otherwise consume it.
    Expect heavy imports into BE/NL. Treat first results as a structural
    check, not a scenario.

## Blind spot
Biggest unknown is `ines_to_spinetop` + `run_clustering` at 21 regions: the
transmission graph gains 4 nodes and the cross-border guard
(`investment_count_initial_cumulative`, 327 rows / sum 1522.5048 on class
`connection`) may no longer hold. I have NOT checked whether the transmission
importer creates lines to the new regions - `transmission_db` already had 6
two-letter stubs (DE DK FR LU NO UK), so the lines may already exist, but
whether they now resolve to real regions instead of dangling is untested.
Second unknown: whether 21 regions blows up solve time or memory.
