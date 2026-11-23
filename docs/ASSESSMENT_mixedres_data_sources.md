# ASSESSMENT: what it actually takes to populate DE/DK/NO/UK

Date: 2026-10-08
Follows `FINDING_routeA_region_vs_data.md` (region plumbing done, data missing).

## The mechanism, confirmed

Each sector importer decides its own region set from its OWN input, not from
`userconfig.yaml` and not from `region_transformation.xlsx`:

- **power**: `power_DB.py` L115-117 reads a geojson, filters
  `level == geolevel` (from `data/Energy_Conversion/config.json`), then
  assigns each plant by point-in-polygon (`get_region`, L1313-1335).
  => region set is controlled by **which geojson is wired in**.
- **rdemand**: reads whichever CSV the Toolbox passes; the column headers
  are the region set.
- `ines_builder` then does a **direct lookup** (IC1 -> IC1, so no
  aggregation). It can only surface what the sector store already holds.

So "enabling" a country is per-importer input swapping, not a config flag.

## Good news: the source data already supports the hybrid shape

**Power.** `data/Energy_Conversion/powerplants.csv` is pan-European
(158,548 rows, 36 countries; DE 141,411 / UK 2,436 / NO 1,022 / DK 236).
I built `geodata/IC1_NWEU.geojson` (21 features) from the supplied
`verification/IC_NWEU.geojson` and dry-ran the spatial join:

| | plants | GW |
|---|---|---|
| BE+NL 17 IC1 clusters | 706 | 56.9 |
| DE | 139,439 | 313.9 |
| UK | 2,379 | 137.9 |
| NO | 996 | 40.3 |
| DK | 208 | 12.7 |
| **assigned total** | 143,728 | **561.6** |

Mix is credible (DE: 90.9 GW wind, 49.7 solar, 45.5 gas, 27.4 nuclear;
NO: 33.3 hydro; UK: 38.2 gas, 19.1 nuclear). The 17 IC1 polygons in that
file are **geometrically identical** to the active `geodata/IC1.geojson`
(0 mismatches), so it is a safe superset drop-in.

**Residual demand.** `data/Rdemand/other_electricity_demand.csv` (202 MB)
already has **exactly the hybrid shape**: 30 country columns *including*
DE, DK, NO, UK **plus** the 17 BEC/NLC clusters. The Toolbox currently
wires the restricted `other_electricity_demand_IC1.csv` (17 clusters plus
15 trailing empty columns - which is where `rdemand_db`'s 15 `Unnamed: 18..32`
junk regions come from).

So for the two biggest sectors the hybrid dataset exists already; it is a
matter of repointing inputs, not of generating data.

## Normalisation applied to the geojson

`geodata/IC1_NWEU.geojson` (new, 2,109,983 B) differs from the supplied file:
- `level` normalised to `IC1` for all 21 features. The source had the UK
  feature at `IC_NWEU` and the other 20 at `IC1_NWEU`; since `power_DB.py`
  filters on exact string equality, the typo would have **silently dropped
  the UK** (137.9 GW).
- `area_km2` filled for DE/DK/NO/UK (was null) from the `PECD1` sheet.
- dropped the extra `layer`/`path` columns.
This file is NOT yet wired into the project.

## Defect already fixed

`data/Energy_Conversion/config.json` had `geolevel` flipped `IC1` -> `PECD1`
by the Step 1 overlay. With the active `IC1.geojson` that filter matches
**zero** regions and would have emptied the power fleet. Reverted to `IC1`
and verified. A sweep of all config-like files under `data/` against
`backups/data-pre-mixedres/` found this was the ONLY semantic regression.
The same staged file also added `bioST+CC` to `units_new` (16 -> 17); left
in place, flagged as a scope change needing a decision.

## Still unresolved - needs your decision

Sectors with NO data for the four countries: heat, biomass, transport,
hydro, industry, other_industry, VRE(onshore), and gas for DK/NO.
Options per sector: (a) leave absent, (b) find a pan-EU source variant like
the two above, (c) synthesise a country-level proxy.

A country with 314 GW of plant but no demand and no VRE profile is worse
than no country at all - it becomes an unconstrained export source. So
**power and rdemand must be switched together**, and VRE matters because
90.9 GW of the German fleet is wind that needs a capacity factor profile.

## Blind spot of this assessment

I have verified source-data *availability and shape* for power and rdemand
only. I have NOT verified that `demand_DB.py` can parse the pan-European
file (its delimiter is `;` and its dates are `1-1-1982 00:00`, whereas the
IC1 file uses `,` and `1/1/1982 0:00` - a known delimiter/format hazard in
this repo). Nor have I checked whether VRE onshore profiles for DE/DK/NO/UK
can be produced: the staged PECD2 timeseries have DE01-DE07, UK01-UK05+UKNI,
NOM1/NON1/NOS1-3, DKE1/DKW1, i.e. **sub-country zones that would need
aggregating to one country region** - and `VRE_DB.py` writes the source
store while `ines_builder` aggregates, so the aggregation path there is
genuinely untested. No run has been launched.
