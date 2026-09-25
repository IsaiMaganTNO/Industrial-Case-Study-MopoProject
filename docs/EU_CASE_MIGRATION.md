# Industrial Case Study (IC1) — migration onto the validated EU case workflow

Branch: `eu-case-migration` · Base: `upstream/main` (f0ece41) · Last updated: 2026-09-25

This document records what was changed, why, what was found, and what is still open.
It is written so that someone else — or ourselves in three months — can pick the work up
without re-deriving any of it.

---

## 1. Background and decision

The Industrial Case Study (IC1, Belgium + Netherlands at sub-national resolution) had never
produced a feasible SpineOpt solve. A colleague's pan-European case study, built on the same
toolchain, solves reliably. Two options were considered:

1. Cherry-pick individual fixes from the EU case into the IC1 repository.
2. Rebase the IC1 case onto the EU case workflow wholesale.

**Option 2 was chosen.** The EU case is a known-good baseline; cherry-picking risked carrying
across half of an interdependent set of fixes. The work is isolated on `eu-case-migration`
so the original IC1 branch is untouched.

The EU workflow has two optimisation stages (`Run_Model_Planning` → `fix_investments` →
`Operational_Model` → `Run_Dispatch`). **Only stage 1 (investment planning) is in scope.**
The colleague has advised that stage 2 currently has bugs.

---

## 2. Environment

| Component | Version / location |
|---|---|
| SpineOpt | v1.0.0 |
| SpineInterface | v0.18.0 |
| Julia | 1.12.6, env `…\spinetools\environments\jenv` |
| Python | env `…\spinetools\environments\penv` |
| Solver | HiGHS.jl (open source, mandated over Gurobi) |
| Spine Toolbox | workflow DAG; `Run SpineOpt` / `Load template` come from the SpineOpt plugin |

Repositories on disk:

| Path | Role |
|---|---|
| `Documents\github-repos\Industrial-Case-Study-MopoProject` | **migration repo**, branch `eu-case-migration` |
| `Documents\Industrial-Case-Study-MopoProject` | original IC1 repo, branch `path-b-time-resolution` (untouched) |
| `…\github-repos\…\EU_case\` | colleague's reference case incl. solved databases (15.2 GB, git-excluded) |

Remotes: `origin` = personal fork, `upstream` = `spine-tools/Industrial-Case-Study-MopoProject`.

---

## 3. Committed work (11 commits)

```
98e1cae Disable the onshore VRE potential limitation for IC1
485271b Align the scenario alternative list with the IC1 pipeline output
7d57368 Add the unsuffixed maritime vehicles to userconfig
c849840 Restore the IC1 region transformation workbooks
eef64dc Also repoint the tool command-line arguments at the IC1 datasets
8b329b5 Use HiGHS instead of Gurobi
26b11c5 Point the EU visualization at IC1 regions and merge mappings
be5fdd7 Point Spine Toolbox data connections at the IC1 datasets
34032a1 Merge IC1 support into the EU ines_builder
17bdc63 Restore IC1 sector importers over the EU baseline
5917e57 Scaffold: rebase Industrial Case Study onto validated EU case workflow
```

### 3.1 The INES builder (`data-pipelines/europe/_ines-builder/ines_target.py`)

EU base plus exactly ten IC1-specific hunks:

- country list scoped to BE/NL plus neighbours
- `mopo_resolutions = ["PECD1", "IC1", "NUTS3"]`
- investment method read from the userconfig block
- defensive `units_existing` lookup in `add_heat_sector`
- defensive `user_section` lookup

**Adopted from the EU case** (these are the fixes we wanted):

- `node_type storage` together with `storage_state_binding_method leap_over_within_period` (3 sites)
- `efficiency = 1.0` on `node__link__node`
- `atmosphere` modelled as a storage node carrying the CO₂ budget

**Deliberately not ported:** our old `entity_exists()` guard. It was broken —
`get_entity_items()` returns a list and never raises, so the guard returned `True`
unconditionally and silently suppressed *all* cross-resolution links.

### 3.2 Issues encountered during migration, in order

| # | Symptom | Cause and fix |
|---|---|---|
| 1 | missing `region_transformation_IC1.xlsx` | EU workbook lacks all IC1 mapping sheets; restored to 4 paths |
| 2 | importers reading EU filenames | 5 substitutions needed in **both** `file_references` and `cmd_line_args` (the latter initially missed; 57 resource paths audited) |
| 3 | `KeyError: 'maritime'` | our transport pipeline emits `maritime`, the EU one emits `maritime-HC/-NH3/-MeOH`; added the unsuffixed forms |
| 4 | `no alternative matching 'GA_flex5'` | our transport pipeline emits flex 0/10/20, EU emits 0/5/10; switched to `GA_flex0` |
| 5 | `KeyError: 'BEC1'` in `onshore_potentials` | `max_capacity_history` is keyed by 39 country codes, the model has 17 IC1 polygons; function disabled |
| 6 | `Package SpineOpt not found` | colleague's Julia path baked into local settings |
| 7 | `INES_DB` not cleared between runs | **standing rule: purge `INES_DB` before every `ines_builder` re-run** |

### 3.3 Latent bugs found in the *old* IC1 code

- `entity_exists()` always returned `True` (see above).
- `countries: "-NL -BE"` was a YAML *string*; it selected BE/NL only by substring accident.
  Now a proper list.
- `sysconfig.yaml` read `node_type` from `commodity__vehicle__region`, where the pipeline
  never writes it.

---

## 4. Build and solve results to date

`INES_DB`: 24 classes, 14,738 entities, 20,253 values, all 17 IC1 regions.
`Final_SpineOpt_Model`: 58 classes, 25,978 entities, 32,965 values.

The model build completed in roughly 2.5 hours and **`constraint_cyclic_node_state` passed in
30.7 s** — this was the historical blocker for the IC1 case and it is resolved.

The solve was **infeasible**, detected in presolve after about 6 seconds.

### 4.1 Model inventory

| Dimension | IC1 (ours) | EU reference |
|---|---|---|
| Units | 1,654 | 333 |
| Nodes | 1,592 | 286 |
| Connections | 1,409 | 125 |
| Representative days per year | 5 → **2** | 10 |
| Planning years | 2030 / 2040 / 2050 | same |

Geography: BE (`BEC1`–`BEC8`) + NL (`NLC1`–`NLC9`) at IC1 = 1,031 nodes; neighbours
DE/FR/UK/NO/DK/LU = 37 nodes; global = 524.

Units by sector: industry 769, buildings/heat 340, power 153, other 149, gas/H₂ 111,
VRE 81, transport 51.

Build-time hotspots: `constraint_node_injection` 1211 s, `variable_unit_flow` 1099 s,
`constraint_unit_flow_capacity` 959 s, `node_state_longterm_trajectory` 840 s,
`node_state_capacity` 778 s, `variable_units_on` 567 s.

### 4.2 The server crash (2026-09-18) and the protection now in place

After infeasibility was detected, two expensive steps exhausted the remote machine's RAM:

1. HiGHS re-solving the un-presolved LP with an interior-point method to obtain a dual ray
   (`ComputeInfeasibilityCertificate`, default `true`).
2. SpineOpt's `_compute_and_print_conflict!` → `MOI.compute_conflict!` → `MathOptIIS` IIS search.

Both are now disabled in the **SpineOpt plugin**, not in this repository:

`~\.spinetoolbox\plugins\SpineOpt\specifications\Tool\run_spineopt.jl`

```julia
using SpineOpt
const JuMP = SpineOpt.JuMP
const HiGHS = SpineOpt.HiGHS
@eval SpineOpt _compute_and_print_conflict!(m) = @info "IIS computation disabled (local testing configuration)"
solver = JuMP.optimizer_with_attributes(
    HiGHS.Optimizer,
    HiGHS.ComputeInfeasibilityCertificate() => false,
    "presolve" => "on",
    "time_limit" => 3600.01,
)
m = run_spineopt(ARGS...; mip_solver=solver, lp_solver=solver)
```

Verified applied: `ComputeInfeasibilityCertificate = false`, `time_limit = 3600.01`, IIS override active.
Original backed up to `Documents\_migration-snapshots\run_spineopt.jl.ORIGINAL.20260925_142054.bak`.

Note: `skip_failed_windows` is **not** reachable — `run_spineopt!` and `solve_model!` have
closed keyword lists.

---

## 5. Root cause of the infeasibility

| | IC1 (ours) | EU (solves) |
|---|---|---|
| Emitting flows into `atmosphere` | 318 | 76 |
| Removal flows out of `atmosphere` | **0** | 2 |
| CO₂ storage nodes | **none** | `CO2-storage_FR`, `CO2-storage-WMES06_ES` |
| Injection units | **none** | `CO2-injection-FR`, `CO2-injection-WMES06` |
| 2050 cumulative cap | 0.0 | 0.0 |

The atmosphere node carries `storage_investment_count_max_cumulative = {2030: 170, 2041: 40, 2050: 0, 2060: 0}`,
forcing cumulative CO₂ to zero by 2050 **with no sink anywhere in the model**.

### Why CCS was missing — the actual mechanism

Not because CO₂ was disabled: `commodity.CO2.status` is `True` in both cases. The gas-sector
branch of `add_policy_constraints` iterates `polygons["onshore_polygons"]` and looks these up in
`CO2_data.xlsx`, which is keyed by **country codes and offshore site codes**. Our polygons are
IC1 ids (`BEC1`…`NLC9`), which appear nowhere in that workbook, so `nodes` came back empty and
no storage was ever created. In the EU case the polygons *are* country codes, so it matched.

---

## 6. Uncommitted work (2026-09-25)

```
 M .spinetoolbox/project.json
 M Pan-European-Framework-Energy-System-Planning/src/_clustering/tulipa_call.jl
 M Pan-European-Framework-Energy-System-Planning/src/_planning-input-processsing/scenario_config.yml
 M Pan-European-Framework-Energy-System-Planning/src/_planning-input-processsing/scenario_run.py
 M data-pipelines/europe/_ines-builder/ines_target.py
 M data-pipelines/europe/userconfig.yaml
?? data-pipelines/europe/_ines-builder/CCS_data/
?? data-pipelines/europe/_ines-builder/CO2_data_IC1.xlsx
?? geodata/IC1.geojson
```

### 6.1 CCS enabled

New input data supplied in `_ines-builder/CCS_data/`:

| File | Role |
|---|---|
| `CO2_data_IC1.xlsx` | **the input the builder now reads** — IC1-keyed |
| `CO2_data_pan_EU.xlsx` | country-keyed equivalent; a *revision* of the existing `CO2_data.xlsx` (209 vs 507 network rows) — do not assume they are interchangeable |
| `CCS_storage_scenarios_mopo.xlsx` | provenance: JRC 2024 storage potentials, `OFF3 → country` map. Not read by the builder |
| `processing_fee_co2_storage.xlsx` | provenance: PBL cost derivation (shipping, pipeline €0.04431/km/t, storage 8.5/18 USD/t). Not read by the builder |

Consistency check: the IC1 workbook's `network` (171 rows) + `network_to_storage` (28 rows)
= 199 = exactly the row count of `CO2_netw_links_and_costs_IC1` in the cost workbook.

Verified properties of `CO2_data_IC1.xlsx`:

- `network`: all 17 IC1 regions, 35 intra-IC1 links
- `network_to_storage`: `NLC1`/`NLC5`/`NLC6` → `NSNL012`, `NSNL031`
- `storage`: byte-identical to the pan-EU sheet — correct, because storage sites are physical
  and not region-resolved
- Belgium has **no** `network_to_storage` entry, which is realistic. A graph traversal confirms
  **all 17 regions reach an offshore entry point** (Belgium via `BEC1/BEC4 → NLC7`,
  `BEC5 → NLC8/NLC9`, `BEC1 → NLC6`); nothing is stranded.

Changes made:

1. **Workbook is now selectable.** The builder previously hardcoded `CO2_data.xlsx`; it now reads
   `global_constraints.co2_data_file`, defaulting to the old name so the EU case is unaffected.
2. **Tariff lookup bug fixed.** The lookup matched on `to` only, so with the IC1 workbook all
   three NL regions inherited `NLC1`'s tariff. Now filters on `from` as well —
   `NLC5 → NSNL031` is 19.09 instead of 28.00.
3. **Duplicate-entity crash fixed.** `add_entity` raises on duplicates and the injection unit was
   named by site only (`CO2-injection-NSNL012`). In the pan-EU data each site had exactly one
   accessing country so this never fired; with IC1, `NSNL012` is reached from three regions and
   the builder would have died on the second. The storage node had the mirror problem — named
   per region, it would have created `NSNL012` three times, each with the full 21,000 kt
   potential, inventing 42 Mt of storage that does not exist.

   Restructured to match physical reality: **one storage node per reservoir, one injection unit
   per (region, site)**, each paying its own tariff.

   ```
   CO2-storage-NSNL012   <- CO2-injection-NSNL012_NLC1  (23.88)
                         <- CO2-injection-NSNL012_NLC5  (23.98)
                         <- CO2-injection-NSNL012_NLC6  (25.50)
   CO2-storage-NSNL031   <- CO2-injection-NSNL031_NLC1  (28.00)
                         <- CO2-injection-NSNL031_NLC5  (19.09)
                         <- CO2-injection-NSNL031_NLC6  (19.70)
   ```

   Dry-run against both workbooks: IC1 → 2 storage nodes / 6 injection units; pan-EU → 24 / 24
   with a clean 1:1 mapping, so EU behaviour is unchanged apart from entity names. Those names
   are not referenced downstream (the hits in `scenario_run.py` and the visualization mappings
   target the *global* `CO2-storage` node from the non-regionalised branch).

4. **`high_CO2` restored** to the scenario list. `storages_fix_cumulative` is written *only*
   under the `low_CO2`/`medium_CO2`/`high_CO2` alternatives. It had been dropped during
   migration because `scenario_setup` reported it did not exist — which was itself a symptom:
   no storage nodes were built, so the alternative was never created. Without it the storage
   nodes get `storage_investment_method: no_limits` and **no cumulative cap**, i.e. unlimited
   free sequestration.

**Capacity obtained:** 27.2 Mt cumulative by 2050 under `high_CO2` (21.0 `NSNL012` + 6.2 `NSNL031`).
Proportionality check against the case that solves:

| | IC1 | EU | share |
|---|---|---|---|
| 2050 storage potential | 27.2 Mt | 373.5 Mt | 7.3 % |
| 2030 CO₂ budget | 165.4 Mt | 2600 Mt | 6.4 % |

Storage share slightly exceeds budget share, so we are not structurally worse off than the EU case.

`network.CO2.interconnection_out_model` is `False` and **must stay that way** — an out-of-model
CO₂ node is created as an uncapped storage node, i.e. a free unlimited sink abroad.

### 6.2 Missing existing thermal fleet — root-caused and fixed

31 `-existing` units (CCGT, SCPC, wasteST, oil-eng, nuclear-3, bioST) present in the old model
were absent from the new one. Static analysis of the builder was exhausted first and found
nothing: `add_power_sector`, `spatial_transformation`, `ines_aggregrate`, `user_entity_condition`
and all nine sector functions are byte-identical between old and new, as are `power_DB.py`,
`powerplants.csv` and the `power_sector` configuration (`source_resolution: IC1` in both).

The divergence was in the **Power databases**, which are *not* identical:

| | `region` entities in `Power_DB` |
|---|---|
| OLD (worked) | `BEC1`…`BEC8`, `NLC1`…`NLC9` |
| NEW (broken) | `BEALB`, `BEANT`, `BEBRU`, `BECHA`, `BEFLA`, `BEGHE`, `BEHAI`, `BELIE`, `NLCHE`, `NLEAS`, `NLEEM`, `NLNOO`, `NLNOR`, `NLROT`, `NLSOU`, `NLWES`, `NLZEE` |

Identical payload — 42 `units_existing` values, same counts per technology. Only the region keys
differ, and the cause is a single tool argument:

| | geodata file given to `power_importer` |
|---|---|
| OLD | `data/geodata/IC1.geojson` — 17 features, ids `BEC1…NLC9` |
| NEW | `geodata/onshore_plus_ic.geojson` — 1,993 features, IC1-level ids `BEALB…NLZEE` |

The superset file contains the same 17 polygons (`per_km2` matches them 1:1) but names them with
5-letter cluster codes. Everything else in the pipeline speaks `BEC1…NLC9`, so the importer wrote
capacities against a vocabulary nothing else recognised, the builder's polygon lookup missed, and
the fleet was silently dropped.

**Fix:** `IC1.geojson` copied into the migration repo at `geodata/IC1.geojson`; both the
`power_input` file reference and the `power_importer` argument repointed. An audit of every
tool's geodata argument confirms `power_importer` was the **only** one affected.

### 6.3 Reduced temporal size

`number_of_representatives` in `_clustering/tulipa_call.jl`: **5 → 2**.
Representative blocks drop from 15 to 6 across the three planning years.

Note that the temporal side was never the main driver of model size — the EU case uses *10*
representative days. Size is driven by spatial and technological detail (1,654 units vs 333).

### 6.4 CO₂ budget aligned to the BE+NL trajectory

| Year | Old | New | Source |
|---|---|---|---|
| 2030 | 170 Mt | **165.4 Mt** | BE 65.6 + NL 99.8 |
| 2040 | 40 Mt | **36.8 Mt** | BE 14.6 + NL 22.2 |
| 2050 | 0.0 | 0.0 | — |

### 6.5 Elastic carbon budget (slack)

So that an unreachable target reports a *cost* rather than an infeasible model, slack is applied
to the `atmosphere` node in `scenario_run.py`:

```python
add_or_update_parameter_value(sopt_db, "node", "balance_penalty", "Base", ("atmosphere", ), 10000.0)
```

Controlled by `co2_overshoot_penalty` in `scenario_config.yml`; set to `null` to disable.

This replaced a first attempt that built a custom priced sink (`CO2-overshoot` node plus
`CO2-overshoot-sink` unit) inside the INES builder. That approach was rejected because:

- it added 6 entities and 7 parameter values to the INES schema, each a chance to fail translation;
- it relied on `storage_investment_method: no_limits` **without** `storages_fix_cumulative`, a path
  nothing in the model currently exercises (every CO₂ storage node has its count pinned by the
  `*_CO2` alternatives);
- its failure mode was a **model build error**.

`balance_penalty` is SpineOpt's built-in slack, already used in this codebase at this version
(`fix_investments.py`, identical `1e4`). Its failure mode is "no effect", it adds no entities, and
because it lives downstream of the builder, toggling it costs seconds rather than an INES rebuild.
`update_parameters(config)` is confirmed called (line 669).

Residual caveat: `balance_penalty` relaxes the node *balance*, whereas the budget is enforced as a
bound on the atmosphere's storage state. Slack should let emissions be absorbed rather than
accumulate, but the mechanism is indirect and only a run will confirm it. Direct fallback: raise
`storage_investment_count_max_cumulative` for 2050 in the SpineOpt DB (a seconds-long edit).

---

## 7. Verified non-issues

Things investigated and cleared — recorded so they are not re-investigated:

- **DAC is not wired backwards.** Both cases wire DAC as energy in → `CO2_<R>` out with *no*
  atmosphere link. The negative-emissions accounting happens at the injection unit, which draws
  from `atmosphere` at an equality ratio of 1. An earlier claim to the contrary was wrong.
  Two genuine differences remain, neither affecting feasibility: our DAC runs on **CH₄**, the EU's
  on **heat**; and the EU builds DAC in 2 of 39 regions while we build it in all 17.
- **Capture-capable unit types:** 36, *identical* to the EU case.
- **Flow ratios:** 2,060 `connection__node__node`, 2,060 flow ratios, 0 unconstrained.
- **Cargo connections:** 651 of 1,409 are cargo bio/HC/MeOH — normal for IC1; the old model had
  the identical 651.
- **`constraint_cyclic_node_state`** passes (30.7 s).

---

## 8. Open items

| Priority | Item | Notes |
|---|---|---|
| 1 | **Run stage 1 and check feasibility** | full rebuild required (the power fix changes `Power_DB`) |
| 2 | Wind turbine class review | `SP199` → `SP277` (×17); different specific power means different capacity factors |
| 3 | `oil-boiler` ×17 removed | consequence of userconfig status flips; confirm intended |
| 4 | ~190 `FOM cost not found` warnings | unreviewed |
| 5 | `EU_historical_inflation_ECB.csv` differs | different checksum between the two projects, feeds `power_importer`; may shift costs |
| 6 | DAC methane emission factor | does the CH₄ it burns carry an emission charge? |
| 7 | Phantom-connection root cause | still unresolved; both old and new models have 100 % flow-ratio coverage, so the earlier `link_parameters_to_directions` hypothesis was wrong |
| 8 | Mixed spatial resolution | adding NO/DE/DK/UK at country resolution alongside BE/NL at IC1. **Not currently implemented** — today's neighbour nodes are exogenous boundary nodes only |
| 9 | Stage 2 (dispatch) | skipped on the colleague's advice |

### Remaining infeasibility suspects, if the run still fails

1. **`no_investable_2030`** — `nuclear-3`, `SCPC`, `waste-ST`, `SMR`, `(BM)MeOH`, `(H2)MeOH-DC`,
   `DAC`, H2/elec connections, `salt-cavern` cannot be built by 2030.
2. **Another broken data link.** The thermal fleet bug was a silent keying mismatch from a
   repointed data connection; the migration repointed many.
3. **Biomass limits** — `biomass_potential_realistic: 0.5` with limitations enabled.
4. **CO₂ capture with no route to storage** — `CO2_<R>` nodes use `fix_start_and_horizon_end`, so
   captured CO₂ must net to zero over the horizon. Only 3 of 17 regions touch storage directly.

The `atmosphere` slack covers (4) and the budget itself. It does **not** cover 1–3.

---

## 9. Things that do not live in this repository

These will **not** travel with the branch and must be reproduced manually:

| Item | Location | Notes |
|---|---|---|
| `run_spineopt.jl` | `~\.spinetoolbox\plugins\SpineOpt\specifications\Tool\` | crash protection + HiGHS options. **Should not be upstreamed as-is** — suppressing IIS is a local testing hack |
| `specification_local_data.json` | `.spinetoolbox/local/` (git-ignored) | machine-specific Julia/Python paths; each user sets their own |
| `EU_case/` | repo root | 15.2 GB reference; excluded via `.git/info/exclude`, which is **local-only** — move to `.gitignore` if the convention stays |

---

## 10. Notes for an eventual upstream pull request

The branch currently does two separable jobs:

1. **IC1-specific configuration** — `countries: [BE, NL]`, `co2_data_file`, HiGHS over Gurobi,
   onshore potential limits disabled, IC1 region transformation workbooks. Arguably not for
   `upstream/main` at all.
2. **Wholesale adoption of the EU case's shared tooling** — the source of
   `93 files changed, +6405 / −10061`, including 1,891 changed lines in `ines_to_spineopt.py`.
   This is the part a reviewer will contest.

Cleanly separable and uncontroversial — both improve the EU case too:

- the `network_to_storage` tariff lookup ignoring `from`;
- the injection unit named by site only, which crashes whenever one reservoir is reachable from
  more than one region.

Those two would make a tight standalone PR independent of the migration.

---

## 11. Standing rules

- **Purge `INES_DB` before every `ines_builder` re-run.** It does not clear itself.
- **Only stage 1.** Do not run `fix_investments`, `merge_operations`, `Operational_Model` or
  `Run_Dispatch`.
- **Keep `network.CO2.interconnection_out_model: False`** — otherwise CO₂ leaks to uncapped
  foreign sinks.
- Comparing against the colleague's solved databases under `EU_case\…\.spinetoolbox\items\` has
  been by far the most productive diagnostic technique. Use it first.
