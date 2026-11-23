# ASSESSMENT: NL+BE at country resolution (for comparison with Standalone IC1)

Date: 2026-10-10. Read-only investigation, nothing built.

## Goal
Run NL+BE alone with one node per country. Compare it with Standalone (`runs/3day_nb_v2`, 17 IC1 zones) so that the ONLY difference is spatial resolution.

## Route A - pipeline rebuild at country level (PECD1)
`userconfig.yaml` has `source_resolution` / `target_resolution` per sector, and `region_transformation_IC1.xlsx` has `IC1_PECD1` (zone to country). But:
- `ines_target.py` aggregates only the "dynamic" (regional) parameters via the transformer sheets (`spatial_transformation` / `ines_aggregrate`).
- Power transmission and gas pipelines print "Source DB must be in the user-defined target resolution". They take links as-is from the source DB, which holds IC1 zone-to-zone links. Country-level link data would have to be supplied separately (not consistent with the IC1 data).
- The biomass and industry importers convert natively to IC1 (`DEFAULT_TARGET_RESOLUTION = "ic1"`, `TARGET_RESOLUTION = "ic1"`) and would need re-running at PECD1.
- Aggregation weights (sysconfig) are area/population shares. Summing back from zones to a country returns the original totals only if the zone data were themselves split from country data with the same weights. Not guaranteed (industry is plant-located, power is point-in-polygon).
- All our patches/tools (route_emissions, onshore caps, gas availability, CO2 storage, postprocess) use IC1 regexes and would need a country variant.
=> High effort (~1 day + verification), and the totals are NOT guaranteed identical to Standalone. Not recommended.

## Route B - "copper-plate" the Standalone model (recommended)
Start from the solved-ready Standalone input DB and change ONLY the network:
1. Create one node per country and commodity (e.g. `elec_NL`, `CH4_BE`) replacing the 17 zone nodes `<commodity>_<zone>`.
2. Re-point every `unit__to_node` / `node__to_unit` / storage link to the country node. **Units are kept, not merged**: every zone's plants, VRE units (own availability profile), investment caps, costs and storage stay exactly as they are.
3. Delete the 596 zone-to-zone connections inside the same country (980 relationships each in from/to/node__node). Keep NL<->BE and border-stub connections, re-pointed to country nodes; parallel links become summed capacity.
4. Demand: sum the zone `demand` time series per country node (exact). `demand_fraction` / node-group structures need checking.
5. Leave temporal blocks, CO2 budget, storage caps and scenarios untouched.

Why this is the cleanest comparison:
- Totals are identical by construction (demand, capacities, potentials, biomass, industry output, storage caps).
- Weather detail per zone is retained (units keep own profiles). The run isolates **internal network constraints** (transmission, pipelines, CO2 transport inside NL/BE), which is the main thing IC1 adds.
- Same patch chain and checks as before. The verification guard compares totals with Standalone.

Scope in the Standalone DB (zonal items): 1,565 nodes, 1,692 units, 1,473 connections (596 internal), 52 distinct zonal parameter types (time series 7,589, floats 14,793).

Risks to check:
- Name-based logic in our tools (`(BE|NL)C\d` regex): node names change, so postprocess needs a country regex.
- Per-zone user constraints / investment groups (17 / 34): stay valid for units, but check any that reference zone nodes.
- Node-level parameters that cannot be summed (`storage_state_max`, `demand_fraction`, `balance_type`): need explicit rules.
- Solve time: much smaller network. Expected well under the 85 min of Standalone.

Variant (optional, later): also merge identical units per country (fewer variables). That changes VRE profiles (capacity-weighted average) and is not needed for the comparison.

## Recommendation
Route B. Steps:
(1) write `tools/copperplate_country.py SRC DST`;
(2) verification: every sum (demand, existing capacity, max investment, storage caps, biomass, CO2 budget) identical to Standalone, 0 zone nodes left, 0 internal connections;
(3) preflight;
(4) solve;
(5) comparison plots with the existing compare tooling.

## Update 2026-10-10 - implemented differently (simpler)
Instead of merging nodes, the intra-country zone links were made unconstrained and free (`tools/copperplate_country.py`). Same effect (each country acts as one node), but zero data changes elsewhere and no tool/regex changes needed. See `docs/RUN_3day_nb_cp.md`.
