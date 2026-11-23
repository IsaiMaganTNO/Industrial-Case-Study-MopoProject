# FINDING: the Group 1 retirement patch covers 26 of 292 permanent incumbents

Status: **confirmed from the input DB**. No new solve has been run, so the
*magnitude* of the effect of extending the patch is a prediction, not a result.

## 1. What the patch actually did

`tools/patch_group1_retirement.py` rewrites `investment_count_max_cumulative`
from a flat float to a declining series `{2030: X, 2041: X/2, 2050: 0, 2060: 0}`
for **26 units across 3 technologies**: `BF-BOF` (2), `(NG)PEA` (12),
`(NG)PE` (12). Two further units (`Scraps_EAF_BEC3/BEC5`) were deliberately
excluded because they are the sole producers of their sector node and forcing
them to zero is provably infeasible - that is recorded in the script docstring
and was demonstrated by an INFEASIBLE_OR_UNBOUNDED result on a 28-unit attempt.

## 2. Why only 26 - the honest answer

The script documents its *scope* but never its *selection rationale*. Reading
the surrounding work, the 26 were chosen to test a **hypothesis**, not to model
a policy: `docs/FINDING_legacy_fleet_never_retires.md` showed that endowed
incumbents never retire, and the patch was the minimal intervention needed to
show that forcing retirement changes the steel and plastics result. It was a
**probe**, and it was never widened afterwards.

So the answer to "why not the others" is: **no principled reason**. It is an
unfinished job, not a modelling decision.

## 3. How much was left out

From the Group 1 input DB (`investment_count_initial_cumulative > 0`):

| | count |
|---|---:|
| endowed units total | **485** |
| forced to zero by 2050 | **193** |
| **permanent (flat cap, never retire)** | **292** |

Note the 193 is larger than 26: the pipeline itself already retires some
technologies. The patch added to an existing, partial retirement scheme.

Largest permanent groups: `LNG-terminal` (17), `air-heatpump-cool-existing`
(17), `electric-heating-existing` (17), and **14 `*-production-reference`
industry families** (9-17 regions each), plus `bio-diges-up` (9),
`gas-extraction` (9), `(LN)O` (7), `(NG)_gco` (6), `Diaphragm` (5).

## 4. Would patching the others change the result? Sector by sector

This is where it splits, and the split is sharp.

### 4a. Sectors where it would change nothing - no alternative exists

- **`chemical-chlorine`: 1 route only** (`Diaphragm`). There is no second
  technology feeding the chlorine node. Retiring the incumbent makes the sector
  infeasible, exactly like the excluded `Scraps_EAF` case.

### 4b. Sectors where it would change a lot - alternatives exist and are unused

These are the six sectors sitting at a flat 100% single route in the
`report_v2` plots, and in each the incumbent is endowed with **zero capex**
while the alternative must be **paid for**:

| sector | routes available | incumbent | incumbent capex | alternative capex (2050) |
|---|---:|---|---|---|
| glass (container) | **6** | `(NG)_gco` endowed 0.0143 | - (endowed) | `(H2)_gco` 16,086 / `(NG)-CC_gco` 16,086 |
| glass (float) | **6** | `(NG)_gfl` endowed | - | similar |
| glass (fibre) | **5** | `(NG)_gfi` endowed | - | similar |
| pulp | 2 | `pulp-production-reference` endowed | **none** | `-alternative` 237.0 |
| paper | 2 | `paper-production-reference` endowed | **none** | `-alternative` |
| aluminium | 2 | `-reference` endowed 1.7576 | **none** | `-alternative` 1,022.6 |

The incumbents in pulp, paper and aluminium have **no `unit_investment_cost`
row at all** and a flat cap of 1000.0. They are free, unlimited and immortal.
No alternative with a positive capex can ever displace them on cost. This is
the same defect as steel, in five more sectors.

Glass is the strongest case: **5-6 routes including hydrogen and carbon
capture are fully specified and priced**, and every one of them is at exactly
zero in all years while `(NG)` holds 100%.

## 5. What this means for the current results

The headline "industry decarbonisation" in `reports_v2_*` is carried by the
sectors that either (a) had their incumbent retired by the patch or the
pipeline - steel, plastics - or (b) decarbonise via **bolt-on capture** on a
route that has an `-MEA`/`-CC` variant - ammonia, cement, olefins. The six
sectors above do not move **because their incumbent was never given a
vacancy**, not because their clean routes are uneconomic.

Stated plainly: of 12 charted sectors, **6 are flat, and at least 5 of those 6
are flat for a reason that is an artefact of the endowment convention.**

## 6. What I have NOT established

- I have not re-solved with a widened patch. The direction of the effect is
  certain (removing a free incumbent can only help priced alternatives); the
  **magnitude, the cost impact and whether it stays feasible are unknown**.
- Feasibility is a real risk, not a formality. The `Scraps_EAF` exclusion
  proves that retiring a sole-producer breaks the model. Chlorine would break
  the same way. Each sector needs the sole-producer check before patching.
- I have not checked whether the `*-production-reference` units are physically
  meaningful plants or modelling scaffolding. They have **zero capex, zero FOM
  and rail to their 1000.0 bound** (see `reports_v2_*/README.md`), which
  suggests scaffolding - in which case retiring them is the wrong fix and the
  right fix is upstream in the pipeline.

## 7. Per-region sole-producer check (the feasibility gate)

Aggregate route counts can hide a region with only one producer, which is what
made `Scraps_EAF` infeasible. Counting feeding units **per region node**:

| sector node | regions | producers per region | safe to retire incumbent? |
|---|---:|---:|---|
| `glass-container_*` | 6 | **6 each** | yes |
| `glass-float_*` | 2 | **6 each** | yes |
| `glass-fibre_*` | 2 | **5 each** | yes |
| `pulp_*` | 10 | **2 each** | yes (one alternative) |
| `paper_*` | 9 | **2 each** | yes (one alternative) |
| `aluminium-primary_*` | 2 | **2 each** | yes (one alternative) |
| `chemical-chlorine_*` | 5 | **1 each** | **NO - sole producer everywhere** |

No region in glass, pulp, paper or aluminium has a sole producer, so the
declining-cap shape should stay feasible there. Chlorine is sole-producer in
**all five** regions and must be excluded, for the same reason `Scraps_EAF`
was.

## 8. Recommended next step

Do not blanket-patch. For each of glass (3 sectors), pulp, paper, aluminium:
1. confirm an alternative route exists that is not the same unit (done, s4b);
2. confirm >1 feeding unit **per region** (done, s7);
3. apply the declining-cap shape to the incumbent only;
4. re-solve and compare against `reports_v2_biocap365`.

Glass alone is the cleanest test: six priced routes including H2 and CC, the
incumbent endowed and free, six producers in every region, and no sole-producer
risk. If retiring `(NG)_gco/_gfl/_gfi` does not move those sectors, my reading
in section 4b is wrong.

## 9. CORRECTION + the widened patch (`retireall`)

My first screen hardcoded a list of 12 sectors. **That list was wrong** - it
silently omitted 13 more commodity families, including `chemical-PE` and
`chemical-PEA` (plastics), which are precisely what the ORIGINAL 26-unit patch
targeted. Any coverage claim based on it understated the problem. The screen
now DISCOVERS industrial nodes from the DB (any non-energy-carrier node fed by
an endowed unit) instead of trusting a hand-written list.

Full picture across **25** industrial commodity families:

| verdict | units |
|---|---:|
| RETIRE-SAFE | **199** |
| ALREADY RETIRING (the original patch) | **26** |
| BLOCKED: sole producer | **7** |

The 26 "already retiring" resolve to exactly `(NG)PEA` 12 + `(NG)PE` 12 +
`BF-BOF` 2 - the screen reproduces the original patch's scope without being
told about it. The 7 blocked are `Scraps_EAF` x2 (the known historical
infeasibility) and `Diaphragm` x5 (chlorine, sole producer in all 5 regions).

### Answering "does this treat all sectors like steel?"

Not exactly, and the distinction matters:

- **Steel-primary** got the treatment and had 6 priced alternatives to move to.
- **Steel-secondary** did NOT and never can - sole producer, demand == endowment,
  no `balance_penalty`, no import connection. It stays coal-free-by-assumption.
- **Chlorine** is in the same position and is likewise excluded.

So "all industrial sectors" is true for 23 of 25 families; 2 are structurally
incapable of it.

### Two tiers, deliberately separable

`tools/patch_retire_industry.py --tier priced|scaffold|both`

| tier | units | what they are |
|---|---:|---|
| `priced` | **24** | `(NG)_gco/_gfl/_gfi` (glass), `(LN)O` (olefins), `(NG)NH3`, `EU-mix-2018` (cement) - real plants with a `unit_investment_cost`, competing against priced alternatives |
| `scaffold` | **175** | `*-production-reference` - **no capex row, no FOM row**, flat 1000.0 cap that they rail to |

The scaffold tier is included because it is the reason 6 of 12 charted sectors
are flat, but it is tagged so the run can be repeated without it. If those
units are modelling scaffolding rather than physical plant, retiring them is
arguably the wrong fix and the real fix is upstream in the pipeline.

### Run launched

`checkpoints/Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.sqlite`
- built on top of `biocap365` (so the corrected biomass cap is retained)
- row-level diff: **exactly 199 rows differ, all `investment_count_max_cumulative`,
  all previously type `float`**; row counts identical (31,470 both)
- BLOB-safe (`typeof(value)='blob'` asserted; 0 violations)
- guards confirm `Scraps_EAF_BEC3/BEC5` and `Diaphragm_BEC1` remain untouched floats

Results -> `checkpoints/Investment_Results.3day_retireall.sqlite`.

### What this run can and cannot settle

It CAN show whether the flat sectors move once the free incumbent is forced out.
It CANNOT prove the screen is sufficient: the screen removes the known
capacity-adequacy failure mode, but a different constraint (e.g. a regional H2
or electricity balance once glass switches) could still bind. An infeasible
result would mean the screen needs a second condition, not that the idea is
wrong - and the `priced`/`scaffold` split exists so that can be bisected.
