<!-- filepath: c:\Users\maganih\Documents\github-repos\Industrial-Case-Study-MopoProject\docs\TEST_RUN_FINDINGS.md -->
# Tiny test run - findings and improvement plan

Model: `checkpoints/Final_SpineOpt_Model.tiny.sqlite`
(2 representative periods x 1 h x 3 investment years = 6 representative
timesteps, plus 3 annual operational timesteps).

Two runs are recorded here:

* **Run A (2026-09-27, pre-fix)** - baseline, before the CCS cost fix.
  Archived as `Investment_Results.prefix.sqlite` /
  `Final_SpineOpt_Model.tiny.prefix.sqlite`.
* **Run B (2026-09-27, post-fix)** - after populating `bio-diges-up+CC`.

## Outcome

| | Run A (pre-fix) | Run B (post-fix) |
|---|---|---|
| Termination | **OPTIMAL** (pure LP, dual simplex) | **OPTIMAL** |
| Objective | 2,209,998 | **2,701,430** (+22.2 %) |
| Solve time | 4.92 s | **5.64 s** (17,711 simplex iterations) |
| Build time | 8 min 24 s | 11 min |
| Total wall time | 12.6 min | 13.1 min |
| Results DB | 10.3 MB, 22,046 values | 22,002 values |

Presolve removes 77,081 rows and 138,876 columns, leaving 15,649 rows /
28,238 columns. The LP itself is trivial; **the build dominates runtime.**

The pipeline works end to end: 16 steps -> SpineOpt build -> solve -> results.
The IC1 sub-national resolution (17 polygons) is viable.

## Validated

* **CO2 penalty is exactly zero** in both runs. The carbon budget is met
  without slack, so the earlier decision to REMOVE `co2_budget_floor` was
  correct - a floor would have produced a fake overshoot masking a broken CCS
  chain.
* **CCS chain works**: `CO2-injection-NSNL031` carries 341.1 flow.
* **The problem is an LP, not a MIP.** No integer variables; no need to relax
  integrality.
* **Time series are correctly aligned.** All 2,169 long series are stamped 2018
  while the model runs 2030-2050, but every one carries `ignore_year: True`, so
  SpineOpt maps them by month/day/hour. Solar availability at the representative
  hours is healthy (0.63 in BEC1, 0.74 in NLC4 at Aug 20 12:00).

## Issue 1 - `bio-diges-up+CC` was free and unlimited (FIXED, VERIFIED)

In Run A it was built to its cap of 1000 in **all 17 regions** = 17,000 units,
98.3 % of all installed capacity, which drove the 88.8 % fixed-O&M share.

Root cause: in the gas workbook, sheet `Technology_Costs`, the
`bio-diges-up+CC` row was **entirely NaN**. `gas_import.py` guards every write
with `if pd.notna(...)`, so the row was silently skipped - yet the entity was
still created and still received an `investment_count_max_cumulative` cap.
Declared, capped, but never priced: free to build.

It was the ONLY genuinely unconstrained technology:

| units with investment cap | 1572 |
|---|---|
| ...with an investment cost | 1102 |
| ...free (cap, no cost) | 470 |
| ...of those, have existing stock (`investment_count_initial_cumulative`) | 402 |
| ...of those, have a fixed schedule (`investment_count_fix_cumulative`) | 87 |
| **...truly unconstrained** | **17** (= `bio-diges-up+CC` x17) |

**Fix applied** (`tools/fill_ccs_technology_data.py`): derived the +CC uplift
from the dataset's own SMR -> SMR+CC pair rather than guessing - capex/FOM
x1.1600, VOM x1.3206, efficiency penalty 0.9079, CO2 per fuel in 0.132.

**Verified in Run B:**

| | Run A | Run B |
|---|---|---|
| total units invested | 17,000+ | **244.9** |
| `bio-diges-up+CC` share of capacity | 98.3 % | **5.9 %** |

The investment mix is now plausible (DAC, biomass, solar PV, reformers, OCGT)
and **solar PV is built in three regions**, which never happened before.

`bio-gasif-metha+CC` was equally blank and was filled at the same time, but it
turns out **not to be instantiated in this model at all** (no matching entity),
so it was never a live second loophole.

## Issue 2 - fuel costs - WITHDRAWN

This was my error. All 30/30 IC1 import units ARE priced (`gas-extraction`
0.015, `LNG-terminal` 0.01111-0.012, `LH2-terminal` 0.00018-0.00055). Neither
IC1 nor the EU case uses SpineOpt's `fuel_cost` parameter - fuel enters via
import units priced as `vom_cost`. **The EU case also reports
`objective_fuel_costs = 0.00`.** It is a reporting convention, not a data gap.

## Issue 3 - cost breakdown (improved, still off the EU benchmark)

| term | Run A | Run B | EU reference |
|---|---|---|---|
| fixed O&M | 88.8 % | **77.0 %** | 38.1 % |
| unit investment | 3.1 % | **13.1 %** | 53.8 % |
| taxes | 7.5 % | 7.7 % | - |
| variable O&M | 0.6 % | 1.4 % | - |
| connection flow | 0.02 % | 0.9 % | - |
| storage investment | 0.00 | **0.00** | 3.3 % |
| fuel / CO2 penalty | 0.00 | 0.00 | 0.00 |

This was never a units bug: `capex/fom` ratios are consistent across
technologies (solar 862,523; OCGT 1,091,560).

Fixing Issue 1 moved every term in the right direction - unit investment
quadrupled, fixed O&M fell 11.8 points - but **we are not yet at the EU
profile** (13.1 % vs 53.8 %). So the free-CCS bug was a real contributor, not
the whole story. The residual gap is most likely Issue 4: see below.

Caveat on the benchmark: EU ran 8760 h, these runs are 6 representative
timesteps. The shares are indicative, not like-for-like.

## Issue 4 - zero storage, thin renewables (NOW THE LEADING SUSPECT)

`objective_storage_investment_costs` is still exactly 0.00 against EU's 3.3 %.

**Only 2 weather hours, and badly chosen**: Feb 18 05:00 has solar = 0.0 and
Aug 20 12:00 is peak sun. With `number_of_timesteps = 1` each period is a
SINGLE timestep, so there is no intra-period dynamics whatsoever - storage has
nothing to arbitrage and no battery can pay for itself. Storage being exactly
zero is a structural consequence of the temporal setup, not an economic result.

This is the next thing to fix.

## Run C (24 h resolution) - hypothesis NOT supported

Run C raised the clustering to `number_of_representatives = 1`,
`number_of_timesteps = 24`: one full representative day, restoring the diurnal
cycle. 72 representative + 3 operational = **75 timesteps** (was 9).

| | Run B (9 ts) | Run C (75 ts) | EU |
|---|---|---|---|
| termination | OPTIMAL | **OPTIMAL** | - |
| objective | 2,701,430 | 2,381,233 | - |
| fixed O&M | 77.0 % | **84.3 %** | 38.1 % |
| unit investment | 13.1 % | **8.5 %** | 53.8 % |
| **storage investment** | 0.00 | **0.00** | 3.3 % |
| build | 11 min | 31.9 min | - |
| solve | 5.6 s | **31.2 min** (490,725 iter) | - |
| total | 13.1 min | **67.4 min** | - |

**The hypothesis was wrong.** Restoring a full diurnal cycle did NOT wake up
storage - it is still *exactly* 0.00 - and the cost shares moved AWAY from the
EU benchmark rather than toward it.

Storage being exactly zero across two very different temporal setups indicates
a **structural** cause (storage cannot be invested in at all), not an economic
one (storage is unattractive). Do not spend more runtime on resolution until
that is resolved.

**Cost estimate was also wrong.** I predicted ~30-45 min; it took 67.4 min. The
claim that "the solve is not the constraint" held only at 9 timesteps: at 75 it
became 31.2 min, co-equal with the build. Model size pre-presolve: 893,361 rows
/ 1,069,205 columns. The build bottleneck is `constraint_unit_flow_capacity`
(169.8 s, 72 GB allocations).

### Next step: investigate storage as a data problem

Check, for IC1 storage entities, whether they are investable at all:
`storage_investment_cost`, `storage_investment_count_max_cumulative` (is it 0?),
and the `storage_investment_*` family. A missing cost or a zero cap reproduces
exactly this signature - the same failure mode as the NaN CCS row in Issue 1,
but in the opposite direction (excluded rather than free).

`storage_state_min_fraction` - present in EU (2 values), absent in IC1 - is now
the leading lead rather than a deferred curiosity.

## Raising the time resolution

### Where the knob is

`Pan-European-Framework-Energy-System-Planning/src/_clustering/tulipa_call.jl`:

```julia
number_of_representatives = 2
number_of_timesteps = 1   # period DURATION in hours; EU uses 24
```

`number_of_timesteps` is the period **duration in hours**. One representative
day = `number_of_timesteps = 24`. `clustering_output.py` derives block
boundaries from the weights file (`8760 / n_periods`), so it follows this value
automatically - no second place to edit.

### What has to be re-run

**From `merge_spineopt` onwards** - five steps. The importers and
`ines_builder` (the 27 min one) are upstream of clustering and are unaffected
by temporal resolution:

```
python tools/run_pipeline.py --from merge_spineopt
```

That is `merge_spineopt` -> `clustering_input` -> `run_clustering` ->
`clustering_output` -> `scenario_setup`, about **8 min** total. Then rebuild
the tiny model and solve.

**Do NOT start from `clustering_input`.** `scenario_setup` writes entities
(e.g. `heatpump-ratio_BEC1`) into `Final_SpineOpt_Model`, and the only step
that purges that database is `merge_spineopt`. Skipping it leaves the previous
run's entities in place and `scenario_setup` dies on a duplicate entity. This
was tried and it failed exactly that way.

**Important:** `tools/make_tiny_model.py` coarsens the `operations_y*` blocks
from 1 h to 8760 h and truncates the `representative_blocks_by_period` maps to
one entry. It must be re-run after any clustering change, and its
representative-period coefficients must **sum to 1** per represented interval
(normalised) - not preserve the 8760 h weight sum. Getting that wrong is a hard
SpineOpt error, not a silent one.

### What it will cost

Representative timesteps scale linearly: `representatives x timesteps x 3
investment years`.

| setting | rep. timesteps | vs now | est. total wall time |
|---|---|---|---|
| 2 x 1 h (now) | 6 | 1x | 13 min |
| **1 x 24 h (one rep. day)** | **72** | **12x** | **~30-45 min** |
| 2 x 24 h | 144 | 24x | ~45-70 min |
| 5 x 24 h (EU) | 360 | 60x | several hours |

The solve is NOT the constraint - it is 5.6 s on a presolved 15,649-row LP, and
even 12x that is seconds. **The build is the cost**, and it does not scale
linearly: a large part of the 11 min is Julia compilation and data reading
(~100 s) which is fixed, while constraint generation scales with timesteps.

Your instinct on one representative day is the right call: 24 h x 1
representative restores the full diurnal cycle - the thing storage actually
needs - for roughly the cost of the smallest useful step. Going from 1 to 2
representatives doubles cost but adds only a second weather pattern; going from
1 h to 24 h is what changes the physics.

Recommended next step: `number_of_representatives = 1`, `number_of_timesteps = 24`.
Keep the external monitor attached and expect ~30-45 min end to end.

## Two pipeline bugs found and fixed while re-running

1. **`INES_DB.sqlite` was a 4,096-byte non-Spine file**, so `ines_builder` died
   instantly with "Unable to determine db revision". Recreated with a proper
   Spine schema; the builder then ran its full 27.2 min.
2. **`run_pipeline.py` never implemented purge-before-merge.** The Toolbox
   connection specifies `purge_before_writing: true` across 19 item types, but
   the Tool-only runner skipped it, so each re-run stacked new data on top of
   the old and `scenario_setup` died on a duplicate `heatpump-ratio_BEC1`
   entity. Now honoured via `DatabaseMapping.purge_items`; the log line
   "purged 19 of 19 item types held data" confirms stale data really was
   present. **This would have broken every future re-run.**

Also: `run_solve_live.ps1` used `Resolve-Path` on the results DB, which fails
when the file does not exist and silently produced an empty `url_out`. It now
builds the absolute path without requiring the file to be there.

## Open items carried forward

* Investigate `storage_state_min_fraction` - present in EU (2 values), absent
  in IC1. Check after the resolution change so the experiments do not confound.
* Re-check `investment_count_max_cumulative` on the remaining 470 free units -
  402 have existing stock, which is legitimate, but confirm the caps represent
  existing capacity rather than build potential.
* Wind turbine class review (SP199 -> SP277).
* ~190 FOM-cost warnings during `ines_builder`.
* Oil-boiler x17 removal.
* `docs/EU_CASE_MIGRATION.md` 6.2 says "31 existing units"; actual is 42
  `technology__region` pairs.
* Delete unused 67 MB `geodata/onshore_plus_ic.geojson`.
