# PREDICTION - merge EU country rows into IC1 sector DBs

Registered BEFORE building the merge tool.

## Plan
Copy ONLY DE/DK/NO/UK rows from the EU_case DBs into our sector DBs:
  heat_db, transport_db, industry_db, other_industry_db, hydro_db
Leave all 17 IC1 rows untouched so BE/NL stays identical across both runs.

## Verified pre-conditions (all PASS)
- units GW/Meuro identical; planning_years identical incl. 2041
- entity_class and parameter_definition sets identical for all four sectors
- EU regions stored as plain 'DE'/'UK'; composites '<x>__DE' -> matches the
  direct-lookup branch at ines_target.py L228 (source_level == target_level),
  so NO aggregation path is involved
- heat: 'current' alt present, 6 end-uses x 4 countries, flow_profile 26280 h
  over 1995/2008/2009, index_name 't' -> wy2009 resolves
- transport: GA_flex0 present (64 values); 4-country subset is 800 values
  / 148 MB out of 6112 / 1.14 GB
- hydro: DE 7, NO 14 (incl. inflow + storage), UK 7, DK 0 (correct - DK has
  no hydro in the EU case either)
- industry: technology 80/80 and commodity 21/21 EXACT match, no EU-only names

## DEFECT FOUND - must handle in the tool
other_industry: EU uses `wood-and-wood-products-production-{alternative,reference}`
(all hyphens); IC1 config AND IC1 DB use
`wood-and-wood-products_production-{alternative,reference}` (underscore before
"production"). These are the ONLY two mismatched names across all four sectors.
If copied verbatim, user_entity_condition looks up
config["technology"]["wood-and-wood-products-production-reference"] -> missing
-> entity_dict falsy -> status defaults True -> entity IS created but under a
name the rest of the config never references. Silent divergence.
ACTION: rename EU -> IC1 convention on copy.

## Predictions
P1. After merge, all five DBs report 21 regions (hydro: 9 = 6 IC1 + DE/NO/UK).
P2. BE/NL rows byte-identical before vs after merge (hash per parameter_value).
P3. No new entity_class or parameter_definition is created in any target DB.
P4. transport gains ~800 values; heat ~124; industry ~? ; other_ind ~?
P5. After renaming, 0 technology names in the merged DBs are absent from
    userconfig["technology"].
P6. ines_builder will then emit heat/transport/industry entities suffixed _DE
    etc. Specifically `res-space_DE` flow_profile and `cement_DE` demand.

## Blind spots being guarded
- Instance #16 (biomass): inferred coverage from output DB not source. Here:
  verify against the EU SOURCE DB counts, and re-check the TARGET DB after.
- The wood naming defect was found only because I enumerated names rather than
  trusting "schemas are identical". Apply the same enumeration to alternatives
  and parameter_definitions during the merge, not just entity classes.
