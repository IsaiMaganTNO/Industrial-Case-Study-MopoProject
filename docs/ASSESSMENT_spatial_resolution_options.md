# Spatial-resolution alternatives: difficulty assessment

Question: how hard is it to run (A) NL+BE at **country** level (1 node each), and
(B) NL+BE at **IC1** resolution plus other NW-European countries at country level?

Scope note: no electricity-trade / cross-border component is modified by either
option as a *design choice*; but see the caveat in §5 -- option B unavoidably
touches the cross-border set, because that is literally what it adds.

> **SUPERSEDED IN PART (7 Oct 2026).** This document judged option B a 3-6 week
> effort dominated by *data acquisition*. A hybrid IC1 + country-level input set
> has since been supplied at `verification/Data - IC1 and PECD1` (~5 GB, 13 sector
> folders) and verified as near-complete. **Option B is revised to ~1.5-3 weeks**,
> and the dominant risk moves from data to build orchestration. See
> `docs/ASSESSMENT_mixed_resolution_data.md`. The analysis of *how resolution is
> wired* (§1-§2) and the option A estimates below remain valid.
>
> **FURTHER CORRECTION (7 Oct 2026).** §1 layer 3 and §3/§4 below claim *"there
> are no per-sector source DBs in the tree"* and treat a never-yet-executed
> pipeline as the dominant risk. **That claim is false.** It was based on
> searching only `data-pipelines/europe/**` and `EU_case/`. The **repo root is
> itself a Spine Toolbox project**, and `.spinetoolbox/items/` holds populated
> databases for every sector (`ines_db` 656 MB / 14,966 entities, `vre_db` 403 MB,
> `transport_db` 418 MB, `spineopt_target` 156 MB, plus power/gas/industry/
> biomass/heat/rdemand/transmission/hydro/cargo). **The pipeline has been run
> end-to-end on this machine.** This removes the largest risk in every estimate
> below. See `docs/PLAN_mixed_resolution_run.md` §0.
>
> Method note: the error was concluding absence from a search scoped to the
> directories I expected the artefacts to live in, rather than searching the
> whole tree. Same shape as the recurring blind-spot pattern - the evidence that
> would have settled it was one `Get-ChildItem` away.

## 1. How spatial resolution is actually wired

Three layers, and only the first is a config switch.

**Layer 1 - region definitions.** `data-pipelines/europe/_ines-builder/region_transformation.xlsx`
carries one sheet per *level* (`PECD1`, `PECD2`, `NUTS2`, `IC1`, `NUTS3`, `OFF1-3`)
plus one sheet per ordered *level pair* (`PECD1_IC1`, `IC1_PECD1`, `IC1_NUTS3`, ...)
holding `source,target,area,population` disaggregation weights.

Key structural finding: **`IC1` is not a pan-European level.** The `IC1` sheet has
exactly 17 rows, all BE or NL (`BEC1..BEC8`, `NLC1..NLC9`). The `PECD1_IC1` sheet
has 54 rows = 17 BE/NL split rows + **37 identity rows** (`AL->AL`, `DE->DE`, ...,
weight 1.0). So `IC1` is already defined as *"country level everywhere, except
BE and NL which are clustered"*. That matters a lot below.

**Layer 2 - country selection.** `ines_target.py::define_polygons` (L61-110) filters
against a hardcoded `countries` list (L65: BE, DK, FR, DE, NL, UK, NO enabled;
rest commented out) intersected with `userconfig.yaml::countries` (L96: `[BE, NL]`).
The `"Europe"` sentinel branch selects the complement.

**Layer 3 - source data.** Each sector pipeline (`_power`, `_vre`, `_industry-aidres`,
`_gas`, `_biomass`, ...) has its own `source_resolution`/`target_resolution` in
`userconfig.yaml` (all currently `IC1`, except VRE offshore = `OFF3`), and each
writes a per-sector Spine DB that `ines_target.py` then aggregates.

**This is the binding constraint, not the config.** There are no per-sector source
DBs in the tree -- `Get-ChildItem data-pipelines\europe -Recurse -Filter *.sqlite`
returns exactly one file, a 0.3 MB near-empty `ines_target.sqlite`. We hold the
*built model*, not the *build inputs*. Any resolution change means re-running the
upstream pipelines from raw data, which we have never done end-to-end.

## 2. Current state of neighbour countries in the model

Measured on `checkpoints/Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite`:

- 1,594 nodes, 1,690 units.
- 1,675 of 1,690 units (99.1%) sit on a `*_BEC?`/`*_NLC?` region.
- DE/FR/UK/LU/NO/DK exist **only as bare stub nodes** (5-7 each:
  `elec_*`, `CH4_*`, `H2_*`, `HC_*`, `MeOH_*`, `bio_*`, `bunker-HC_*`).
- Those stubs carry **zero units**, zero demand -- the only parameters on e.g.
  `elec_DE` / `CH4_DE` are `storage_active` and `storage_longterm_active`.

This confirms and explains the earlier measurement that net exchange at
`CH4_DE/FR/UK/LU` is **exactly 0.0 TWh**: they have no feeders because they have
no generation, no demand, and no supply units. They are boundary placeholders
created by `coupling_spatial_resolutions` (L1377), not modelled countries.

## 3. Option A - NL+BE at country level (2 regions)

**Difficulty: moderate. The honest route is a pipeline re-run; a cheap
approximation is available and probably good enough.**

Why it is *not* trivial despite looking like a one-line change: setting the
sector `target_resolution` to `PECD1` would make the builder aggregate
IC1 -> PECD1 using the `IC1_PECD1` sheet (which exists, 54 rows, all weight 1).
Mechanically that is supported. But it requires the per-sector source DBs
(§1 layer 3), which we do not have.

Two sub-routes:

- **A1, honest re-run.** Re-run every sector pipeline with
  `target_resolution: PECD1`, then `ines_target.py`, then clustering and the
  SpineOpt conversion. Cost is dominated by *first-time* pipeline execution:
  undocumented raw-data dependencies, the AIDRES industry workbook, VRE
  potentials, and the ines->SpineOpt step. Estimate **1-2 weeks**, high variance,
  and it would re-expose every data defect we have already patched downstream
  (bidirectional CO2, gas availability, onshore VRE caps, 365x storage) --
  all our patches operate on the *built* DB and would need re-application or
  porting into the pipeline.
- **A2, post-hoc aggregation of the existing DB.** Rewrite region suffixes
  `*_BEC1..8 -> *_BE`, `*_NLC1..9 -> *_NL`, merge duplicate units by summing
  capacity, and drop now-internal connections. This stays inside the tooling we
  already trust (`DatabaseMapping` patches, the guard assertions). Estimate
  **2-4 days**. Risks: unit-name collisions, `investment_count_initial_cumulative`
  must be re-summed (the 1522.5048 guard changes meaning by construction), and
  VRE profiles must be capacity-weighted, not averaged.

**Expected payoff is real.** Model size drops roughly 8.5x on regional entities
(1,675 IC1 units -> order 200). Solve time should fall from ~90 min to a few
minutes, which turns the model into something colleagues can actually iterate on
-- directly serving goal (b). It also makes the fossil-CH4 budget and CO2 budget
comparisons against `verification/` exact rather than per-region approximations.

**Expected cost in realism:** loses intra-country congestion and the industrial
siting detail that is the entire point of IC1. Port-cluster vs inland distinctions
(LNG siting, CO2 pipeline routing, offshore landing points) vanish. Useful as a
*reference/debug* model, not as the deliverable.

## 4. Option B - IC1 for NL+BE + country level for NW Europe

**Difficulty: high. This is the expensive one, and the cost is data, not code.**

The *good* news is larger than expected: §1 shows `PECD1_IC1` already contains
37 country identity rows, and `define_polygons` already has DK/FR/DE/UK/NO
uncommented at L65. So the **region framework for a mixed-resolution model is
already in place** -- `IC1` was designed as exactly this hybrid. Enabling it is
plausibly a `userconfig.yaml::countries` edit from `[BE, NL]` to
`[BE, NL, DE, FR, UK, LU, DK, NO]` plus the `"Europe"` sentinel semantics.

The *bad* news: that only creates the regions. Every neighbour country needs a
full sector build -- demand profiles, generation fleet, VRE potentials and
profiles, industry, gas, biomass, heat, transport. §2 shows we currently have
**zero** of this: 0 units across all six neighbours. The upstream data largely
exists in country coding (`data/Gas/Gas_Sectors_Dataset.xlsx` carries BE/NL/DE/
UK/FR; AIDRES is nuts0/nuts3; PECD covers Europe), so it is a *pipeline-run*
problem rather than a *data-acquisition* problem -- but it is the same
never-yet-executed pipeline run as A1, over 4x the countries.

Size estimate: 17 IC1 regions + ~6 country regions = 23 regions, but the
neighbours are large, so unit count plausibly 2-3x current, and the cross-border
connection set grows substantially. **Solve time is the real risk**: at 3
representative days we are already at ~90 min; 2-3x the entities on a barrier
solve is superlinear. Expect multi-hour, possibly requiring more representative
days to be dropped -- which degrades exactly the temporal resolution we need for
the VRE conclusions.

Estimate **3-6 weeks**, and it should not be attempted before the pipeline has
been successfully re-run once for the current scope (i.e. A1 is a prerequisite
de-risking step for B).

## 5. Interaction with the "do not touch cross-border" instruction

Option A is safe: aggregating BE/NL internally does not alter the external
interface, though it does collapse 17 regions' worth of connection endpoints.

Option B **necessarily** modifies the cross-border set -- today's exports to
DE/FR/UK/LU terminate at dead stubs with zero net flow, and option B's entire
purpose is to give them real counterparties. This is the opposite of a
side-effect; it is the deliverable. Worth flagging explicitly to whoever issued
the constraint, because it means option B cannot be done under it as literally
written.

## 6. Recommendation

1. **Do A2 (post-hoc 2-region aggregate) next**, as a fast *companion* model, not
   a replacement. It is the cheapest way to get a model colleagues can run in
   minutes, and it gives a clean sanity check against the national totals in
   `verification/`.
2. Treat **A1 as the real prerequisite**: before promising anyone option B, prove
   the upstream pipeline can be re-run end-to-end at current scope. Until that is
   demonstrated, every resolution estimate above is uncertain on the high side.
3. **Defer B.** Its value is real (it would make the trade/transit question
   answerable rather than degenerate) but the cost is weeks and it conflicts with
   the current no-cross-border-changes instruction.

## 7. Confidence and blind spots

Measured, not assumed: sheet contents and row counts of
`region_transformation.xlsx`; the 37 identity rows; node/unit counts and the
zero-unit neighbour finding; the absence of per-sector source DBs.

Not verified, and these drive the estimates:
- Whether the sector pipelines actually run to completion today. **Untested.**
  This is the single largest uncertainty in both options; all day/week figures
  collapse or balloon on it.
- Whether `ines_to_spineopt.py` and the clustering step are resolution-agnostic.
  Assumed, not checked.

Checked after first draft:
- `EU_case/` holds **no** prebuilt multi-country artefact. It is an empty Spine
  Toolbox project skeleton: every `.spinetoolbox/items/*` directory (`power_db`,
  `gas_db`, `industry_db`, `ines_db`, `investment_results`, ...) is 0 KB and
  there is no `.sqlite` anywhere. Option B is not short-circuited.
- That skeleton does, however, change the picture of *how* a re-run happens.
  The 20-odd item directories mirror the sector pipelines one-for-one, and
  `.spinetoolbox/project.json` is 96 KB -- i.e. **the pipeline is orchestrated as
  a Spine Toolbox DAG, not as standalone Python scripts.** A re-run (A1 or B)
  therefore most likely means driving Toolbox, not calling `*_DB.py` by hand.
  This cuts both ways: the wiring and execution order are already encoded
  (good), but it is a toolchain we have not used in this engagement at all, and
  our entire working practice to date is direct `DatabaseMapping` patching of
  built artefacts. **This raises confidence in A2 relative to A1/B**, and is an
  argument for treating the §6 ordering as firm.
