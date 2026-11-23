# FINDING: Stage A is smaller than hoped - two sectors are code-gated

Date: 2026-10-08. Follows `SURVEY_sector_coverage_mixedres.md`, which was
too optimistic in calling the repoints "pure input swaps".

Smoke-tested each candidate repoint using the **importer's own call
signature**, per the rule in `FINDING_rdemand_delimiter_repoint.md`.

## Verdict per sector

| sector | verdict | evidence |
|---|---|---|
| **rdemand** | **GO** - needs converted file (done) | `;`-delimited pan-EU file parses to 0 cols under the importer's default-comma `read_csv`. Converted + validated file built. |
| **power** | **GO** - needs geojson swap | `geodata/IC1_NWEU.geojson` built and dry-run joined: 561.6 GW over 21 regions. |
| **gas** | **GO** - plain swap, 2 caveats | `gas_import.py` reads `sheet_name=None` (dict) and indexes rows **positionally** via `.iloc[]`, so the full workbook's extra `Original WP2` sheet and its string-vs-int year column labels are both harmless. |
| **transport** | PARTIAL | `fleets_per_scenario.csv` is hybrid and has all 4 countries, but the wired `fleet.csv` is IC1-only and `non-road/` has 17 IC1 files only. |
| **heat** | **NO-GO** | code-gated, see below |
| **VRE** | **NO-GO** | needs pre-aggregation, see `SURVEY_...md` |
| **hydro** | PARTIAL | reservoir params exist for NO only; RoR profiles IC1-only. |

## Heat is code-gated, not data-gated

I previously listed heat as a GO because
`scenario_total_yearly_demands_GWh.csv` and
`peak_to_yearly_demand_ratios_MW_GWh.csv` both carry DE/DK/NO/UK columns.
That was the wrong file to look at. `heat_DB.py` L258:

    for country in map_demand[dem].columns:

The region loop is driven by the **hourly demand timeseries**, not the yearly
scenario table. Those live in `data/Buildings/demand-timeseries/` (30 files)
and `cop-timeseries/` - all **18 columns = timestamp + 17 IC1 regions only**.
Each region additionally needs a COP series (L293-296) for
`A2AHP-cooling`, `A2WHP-radiators`, `G2WHP-radiators`.

So heat cannot reach the new countries no matter which yearly file is wired.
It would need synthesised hourly heat-demand and COP profiles for DE/DK/NO/UK
- a modelling task, not a plumbing one.

## Gas caveats to watch

1. `Technology_Conversion` in the full workbook has **two all-NaN rows**
   (`bio-gasif-metha+CC` -> CH4 and -> CO2). The placeholder has 20 rows vs
   the full 22. These NaNs will flow into conversion-rate parameters unless
   the importer skips them - **not yet verified**.
2. `H2_Network` in the full workbook has a trailing `Unnamed: 9` column.
   Harmless given positional indexing, but it signals a ragged source range.

## Consequence for the plan

Stage A as originally scoped (power + rdemand + heat + gas + transport) is
really **power + rdemand + gas**. The four new countries would get:

- a thermal/hydro power fleet (504.7 GW)
- hourly electricity demand (DE 400.8 / UK 265.7 / NO 91.8 / DK 29.2 TWh)
- gas production, storage and network
- transmission + cargo (already present)

and would have **no VRE, no heat, no road/non-road transport, no RoR hydro**.

That is still a coherent feasibility test, but the economic distortion is now
larger than I estimated: a Germany with 45.5 GW of gas and 27.4 GW of nuclear
but **zero** of its 90.9 GW of wind and 49.7 GW of solar will look far too
expensive, and NO without run-of-river loses most of its 33.3 GW hydro value.
BE/NL would under-import and over-build domestically.

**Therefore Stage A must be treated strictly as a build/feasibility gate.**
Its numbers must not be reported. The first interpretable run is Stage B
(VRE pre-aggregation included).

## Blind spot

I verified region-loop drivers for rdemand, heat and VRE by reading the loop
line itself. I have NOT done that for gas, transport or biomass - for those I
inferred coverage from source-file contents, which is exactly the mistake I
made with heat. Before wiring gas I should locate its region loop and confirm
it is driven by the sheet rows rather than by some other constrained list.
