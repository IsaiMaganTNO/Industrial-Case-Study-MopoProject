# Plan: mixed-resolution run - NL+BE at IC1 + NO/DE/DK/UK at country level

Scope as requested: **21 onshore regions** (17 IC1 clusters + NO, DE, DK, UK).
No FR, no LU - noted as a deliberate decision, with consequences in §6.

## 0. A correction that changes the plan

My earlier assessments (`ASSESSMENT_spatial_resolution_options.md`,
`ASSESSMENT_mixed_resolution_data.md`) both said *"there are no per-sector source
DBs in the tree"* and treated a never-yet-run pipeline as the dominant risk.
**That was wrong.** I had looked only at `data-pipelines/europe/**` and
`EU_case/`, and concluded from their absence there.

The repo root is itself a Spine Toolbox project, and `.spinetoolbox/items/`
contains **populated databases for every sector**:

| store | size | entities | params |
|---|---:|---:|---:|
| `ines_db` | 656 MB | 14,966 | 20,984 |
| `vre_db` | 403 MB | 900 | 807 |
| `transport_db` | 418 MB | 490 | 2,438 |
| `spineopt_target` | 156 MB | 21,016 | 24,848 |
| `heat_db` | 152 MB | 443 | 603 |
| `rdemand_db` | 25 MB | 65 | 32 |
| `power_db`, `gas_db`, `industry_db`, `biomass_db`, `cargo_db`, `transmission_db`, `hydro_db`, `commodity_db`, `other_industry_db` | <5 MB each | populated | populated |

**The pipeline has been run end-to-end on this machine.** That removes the single
largest risk in both previous estimates and makes this a *re-run with different
inputs*, not a first-ever run.

Resolution check on those stores confirms they are the current IC1-only build:
`vre_db` 17 IC1 + 50 offshore + **0** country regions; `rdemand_db`, `biomass_db`
17 IC1 + 0; `transmission_db` 17 IC1 + 7 country stubs (DE/DK/FR/LU/NO/UK/HV).
So the sector DBs must be rebuilt from the new inputs - but the machinery is
proven.

**Revised estimate: 1-2 weeks**, risk concentrated in VRE aggregation and solve
time rather than in orchestration.

## 1. Easiest route, in one sentence

Re-run the existing Toolbox DAG with (a) the hybrid input files from
`verification/Data - IC1 and PECD1`, (b) VRE pre-aggregated from PECD2 to
country level for the four neighbours, and (c) `userconfig.yaml` extended to
list the four countries - then re-apply the four standing patches to the built
model.

## 2. Step-by-step

### Step 0 - baseline reproduction (do not skip)
Re-run the DAG **unchanged**, with current inputs, and confirm it reproduces the
live Toolbox model in entity counts. **Half a day.** This is cheap insurance: it
proves we can drive Toolbox before any variable changes. If this fails,
everything downstream is guesswork.

**CORRECTION (7 Oct 2026) - acceptance criterion.** This step originally said
"matching `checkpoints/Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite`".
**That is the wrong target.** Measured counts:

| artefact | entity | parameter_value |
|---|---:|---:|
| live `.spinetoolbox/items/final_spineopt_model/` | **28,925** | **35,814** |
| `checkpoints/...7day.sqlite` (and 7day siblings) | 28,925 | 35,814 |
| `checkpoints/...tiny.3day.gascap.vre15.sqlite` | 25,227 | 31,704 |

The live Toolbox store sits at the **7-day post-scenario-setup** state. The 3-day
`vre15` model was derived later by re-clustering plus the standing patches, so a
clean DAG re-run cannot and should not reproduce it.

**Acceptance criterion: entity 28,925 and parameter_value 35,814** against
`run_logs/baseline_fingerprint.json`. Reaching the 3-day `vre15` state is a
*later* step (re-cluster to 3 days, then re-apply patches), not part of Step 0.

Backup taken before any execution:
`backups/spinetoolbox-items-pre-mixedres/` (32 files, 2.54 GB) - restore from
here if a re-run corrupts the live stores.

**RESULT (8 Oct 2026): PASS, but only after fixing a blocking defect.**

The first unchanged re-run did **not** reproduce the baseline. Cause: an
unseeded `random.choice` assigning every existing plant's retirement year
(`docs/FINDING_random_retirement_dates.md`). Swings were multi-GW in exactly the
technologies our conclusions rest on - NL y2030 6,273 -> 12,214 MW, BE nuclear
y2030 4,710 -> 5,765 MW - i.e. **far larger than the mixed-resolution effect we
intend to measure**.

Resolution adopted: **pin, do not structurally fix** (user decision). The power
sector is made a controlled variable by overwriting `units_existing` with the
exact `vre15` values after every `power_importer` run.
See `docs/WORKFLOW_pin_power_fleet.md` and `tools/pin_power_fleet.py`.

Verification of the pinned re-run (`ines_builder`, 25.47 min, exit 0):

| | entity | parameter_value | existing units |
|---|---:|---:|---:|
| baseline (`vre15` fleet) | 14,966 | 20,984 | 201 |
| unpinned drift run | 14,982 | 21,008 | 205 |
| **pinned rebuild** | **14,966** | **20,984** | **201** |

Checked beyond counts: **full entity set identical**, and **all 20,984 parameter
values identical** (md5 `932473ec1ca6` both sides). A 28-row patch in `Power_DB`
reproduces `INES_DB` bit-for-bit through a 25-minute build.

**The DAG is therefore demonstrably reproducible** - previously only inferred
from the artefacts it left behind.

Caveat carried forward: the pin covers **NL+BE only**. DE/DK/NO/UK have no
baseline to pin to, so their existing fleets come from the now-seeded
(`random.seed(20261008)`) but arbitrary draw - reproducible, not validated.
Their thermal capacity must not be quoted as a result in its own right.

### Step 1 - stage the new inputs (0.5 day)
Point the `*_input` Data Connections at `verification/Data - IC1 and PECD1`.
Coverage for NO/DE/DK/UK is verified complete across demand, buildings,
transport, biomass, industry, power plants, transmission, cargo, CH4, VRE
(`ASSESSMENT_scope_NLBE_IC1_plus_NO_DE_DK_UK.md` §1).

Keep the `_update` industry catalogue: it is a **pure superset** (capture
coefficients for 9 extra sectors, zero changed values in the 77 shared rows).

### Step 2 - VRE aggregation PECD2 -> country (1-2 days) **[main new code]**
The only genuinely new work. Aggregate the four countries' PECD2 regions:
DE 7, UK 6, NO 5, DK 2 = 20 regions -> 4 nodes. Leave BE/NL IC1 columns and all
offshore zones untouched.

- Capacity factors: weight by **`capacity`/`potential`** columns from the
  `PECD2_PECD1` sheet of `region_transformation.xlsx`, **not `area`**.
  Area-weighting blends dissimilar wind regimes and flattens the profile,
  suppressing the low-wind events that set firm-capacity need.
- Potentials (GW): **sum**, do not average.
- Write a standalone script under `tools/`, run it once to produce aggregated
  CSV/XLSX, and feed those to the importer. Do not modify the importer.
- **Validation:** aggregated country CF must lie within the min/max of its
  constituent PECD2 regions, and the annual mean must be within ~1-2% of the
  capacity-weighted mean. Assert this.

### Step 3 - enable the countries (hours)
`data-pipelines/europe/userconfig.yaml` L96: `[BE, NL]` ->
`[BE, NL, DE, DK, NO, UK]`.
`ines_target.py` L65 already has DE/DK/NO/UK **uncommented** - FR too, so
comment FR out to honour the requested scope.

Check `mopo_resolutions` (L1380, `["PECD1","IC1","NUTS3"]`). `PECD1_IC1` already
contains 37 country identity rows, so the hybrid is supported as-is.

### Step 4 - rebuild (1-2 days)
Run importers -> `ines_builder` -> `ines_to_spinetop` -> `scenario_setup` ->
clustering. Keep the 3-day representative structure for comparability.

### Step 5 - port the patches (1 day) **[silent-failure risk]**
The standing patches are **hard-coded to 17 regions** and will under-apply
without erroring:

| patch | hard-coded assumption | action |
|---|---|---|
| `patch_gas_availability.py` | 17 LNG + 9 extraction units | re-derive by query, not count |
| `patch_onshore_vre_potential.py` | BE/NL country totals | extend or restrict to BE/NL |
| `patch_co2_bidirectional.py` | CO2 network is IC1-only | should be unaffected - verify |
| `patch_co2_cap_div365.py` | 365x convention | unchanged |

**Decide explicitly whether the gas cap and onshore limits apply to the four new
countries.** Applying BE/NL-derived caps to DE/NO is wrong; applying nothing
re-creates the unlimited-gas defect outside BE/NL - which would leak straight
back in through imports. Recommendation: apply the same *method* per country,
not the same *numbers*.

The cross-border guard (`investment_count_initial_cumulative`, 327 rows, sum
1522.5048) **will legitimately change**. Record a new baseline rather than
asserting the old one.

### Step 6 - solve and validate (2-3 days)
Gurobi, 3 representative days, `tools/solve_tiny_gurobi.jl`.
**Check `penalties == 0` first.** Register predictions in
`docs/PREDICTION_mixed_resolution.md` *before* solving.

## 3. Effort

| step | days |
|---|---|
| 0 baseline reproduction | 0.5 |
| 1 stage inputs | 0.5 |
| 2 VRE aggregation | 1-2 |
| 3 enable countries | 0.25 |
| 4 rebuild | 1-2 |
| 5 port patches | 1 |
| 6 solve + validate | 2-3 |
| **total** | **6-9 working days** |

## 4. Risks, in order

1. **Solve time.** 21 regions, and the four new ones are large with full
   generation fleets. Units plausibly 1.5-2.5x current 1,690. We are already at
   ~88 min on a barrier solve; scaling is superlinear, so budget multi-hour.
   **Do not drop representative days to compensate** - temporal resolution is
   already the weakest link behind the nuclear and offshore conclusions.
2. **Patches under-applying silently** (step 5). Verify through the Spine API
   and assert expected row counts.
3. **VRE aggregation flattening profiles** (step 2). Guard with the validation
   assertion.
4. **Toolbox re-run diverging from the current model** - caught by step 0.

## 5. What this buys

Today DE/FR/UK/LU are dead stubs with **exactly zero** net exchange; NL+BE are an
island. After this run, 96 transmission links are live, including BE-NL (8),
NL-DE (4), DE-DK, DE-NO, DK-NO, DK-UK, NL-NO, NL-UK, BE-UK, NO-UK -
**43,980 MW** of in-scope cross-border capacity. Norwegian hydro and Danish wind
become real flexibility sources rather than absent ones.

## 6. The France caveat, restated for the record

Excluding FR leaves **23,200 MW** severed - more than half of all retained
in-scope capacity, and the largest single external link. Total severed across all
excluded neighbours is 75,580 MW vs 43,980 MW retained (**63%**).

This is not a reason to delay the run, but it bears on one specific result:
`vre15` builds ~5.9 GW of Belgian nuclear, and the mechanism
(`FINDING_nuclear_BE_vs_NL_asymmetry.md`) is Belgium exhausting its single
offshore zone with nothing cheaper left. **A model that cannot import from France
remains predisposed to build firm capacity in Belgium.** Adding NO/DE/DK/UK will
move that number, and it would be easy to read the movement as the model becoming
more realistic when the dominant missing link is still absent.

Suggested mitigation, cheap: after the run, test FR sensitivity by adding France
as a **fixed-price boundary node** at its stated 23,200 MW rather than a full
region. Hours of work, and it tells us whether the Belgian nuclear result is
robust or an artefact of the boundary.

## 7. Recommended first action

**Step 0 only.** Reproduce the current model through Toolbox before changing any
input. Everything above is conditional on that working, and it has not yet been
demonstrated in this engagement - only inferred from the artefacts it left behind.
