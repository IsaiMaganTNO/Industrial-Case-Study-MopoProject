# FINDING - EU-case merge supplies the four countries' missing sectors

## Problem
DE/DK/NO/UK had power, VRE, demand, gas, transmission and (after the biomass
fix) biomass -- but no heat, transport, industry or hydro. Their load was
understated against their capacity, which would have made them artificial net
exporters and biased exactly the BE/NL quantity the resolution comparison is
meant to measure.

## Resolution
`EU_case/.spinetoolbox/items/` already contains these sectors built at COUNTRY
resolution. `tools/merge_eu_country_rows.py` copies only DE/DK/NO/UK rows into
our sector DBs, leaving all 17 IC1 rows untouched.

## Why a direct SQL merge is safe
`ines_target.spatial_transformation` takes the DIRECT-LOOKUP branch (L228) when
`source_level == target_level`, querying `get_parameter_value_items(
entity_byname=...)`. The EU DBs store regions as plain `DE`/`UK` and composites
as `<x>__DE` -- exactly the names `define_polygons` emits for our country-level
polygons. No aggregation path is involved. Had the EU DBs used PECD1-style
codes this would have failed silently.

## Pre-conditions verified (all PASS)
- units GW/Meuro identical; planning_years identical incl. the 2041 quirk
- entity_class and parameter_definition sets identical across all four sectors
- heat: `current` alt present; 6 end-uses x 4 countries; flow_profile 26,280 h
  over 1995/2008/2009, index_name `t` -> `wy2009` resolves
- transport: `GA_flex0` (our scenario's alt) present, 64 values
- hydro: DE 7, NO 14 (incl. inflow + storage), UK 7, DK 0 -- DK is 0 in the EU
  case too; Denmark genuinely has no hydro. Not a gap.
- industry: technology 80/80 and commodity 21/21 EXACT match

## Two defects found and handled

### 1. Name divergence between the two pipelines
EU uses `wood-and-wood-products-production-{alternative,reference}` (hyphen);
IC1 config AND IC1 DB use `wood-and-wood-products_production-*` (underscore).
Copied verbatim, `user_entity_condition` would look up a config key that does
not exist -> `entity_dict` falsy -> `status` defaults True -> entity created
under a name nothing else references. `NAME_FIXUPS` renames on copy.
VERIFIED: only the underscore form exists post-merge.

### 2. Composite parents are not country-suffixed  (caught by the P-guard)
First apply emitted 72 warnings: `vehicle` entities `van*`, `maritime-*` and
`commodity` `MeOH`, `NH3` exist ONLY in the EU DB and carry no country suffix,
so `is_target()` skipped them. Result: **52 composites written with 2 of 3
entity_element rows and 228 dangling parameter values**, while the tool still
reported success.
Rolled back from `backups/sector-dbs-pre-eumerge/` and added a transitive
closure over `entity_element` so any missing parent is pulled in.
Second apply: 0 warnings, 0 malformed composites.

NOTE on the audit that nearly missed this: my first malformed-composite query
reused one sqlite3 cursor inside its own iteration, which silently truncated
the scan to 1 row and reported "0 malformed". Materialise with `.fetchall()`
before looping. The clean result was the tell -- 646 entities cannot yield a
1-entry histogram.

## Result (all predictions P1-P5 PASS)
    DB                 regions  malformed  new_class  new_pdef  BE/NL changed
    heat_db               21        0          -         -           0
    transport_db          21        0          -         -           0
    industry_db           19        0          -         -           0
    other_industry_db     21        0          -         -           0
    hydro_db               9        0          -         -           0

`industry_db` 19 and `hydro_db` 9 are correct: industry covers 15 of 17 IC1
regions (2 have no industry) and hydro 6 (+DE/NO/UK, no DK).
BE/NL parameter values are byte-identical before vs after (md5 per value),
so BE/NL input remains identical between the 17- and 21-region runs.

Two new alternatives appear in transport (`GA_flex5`, `DE_flex5`); they are
inert -- the active scenario uses `GA_flex0`.

`CO2_emitted` looked IC1-only but has 0 values in our DB too: an empty
definition, not data. No loss.
