# FINDING: nuclear exists, is unconstrained, and is still never built

**Date:** 2026-10-06 | **Run:** `Investment_Results.3day_routeemis.sqlite`
**Trigger:** colleague question - why CCGT+CC for firm capacity but no nuclear?

## 1. Nuclear IS in the model

| family | units |
|---|---|
| `nuclear-3` (investable new-build) | **17** (one per NUTS3) |
| `nuclear-3-existing` (brownfield) | **5** |
| node `U-92` (uranium) | present |

So "nuclear is missing" is **false**. The question is why it loses.

## 2. It is NOT blocked by a cap or a scenario switch

- `investment_count_max_cumulative` = **1000.0** - effectively unlimited.
- An alternative named **`limited_nuclear-3` EXISTS** - but it is **NOT active**
  in the solved scenario. Active ranks 1-10 of `baseline_blended_rep` are:
  `Base`, `wy2009`, `medium_bio`, `current`, `GA`, `GA_flex0`, `high_CO2`,
  `flex_buildings`, `flex_buildings_wy2009_current`, `flex_industry`.

`docs/EU_CASE_MIGRATION.md` notes a `no_investable_2030` restriction listing
`nuclear-3`; that only blocks **2030**, not 2040/2050. Nuclear is free to be
built in the later milestones and still is not.

**Therefore the zero is a pure economic outcome, not a constraint artefact.**

## 3. The result

| | 2030 | 2040 | 2050 |
|---|---|---|---|
| `nuclear-3` (new) | **absent** | **absent** | **absent** |
| `nuclear-3-existing` | 5.285 | 3.972 | **0.000** |

Existing nuclear **retires to zero by 2050** and nothing replaces it.

2050 electricity mix (total 344,193 GWh):

| tech | GWh | share |
|---|---|---|
| wind-on | 139,136 | 40.42% |
| **CCGT+CC** | **98,144** | **28.51%** |
| solar-PV | 85,581 | 24.86% |
| CCGT (unabated) | 15,742 | 4.57% |
| OCGT | 3,500 | 1.02% |
| wind-off | 1,315 | 0.38% |
| CCGT-H2 | 457 | 0.13% |

**CCGT+CC is the firm-capacity backbone.** It supplies 28.5% of electricity.

## 4. Why CCGT+CC wins: capex, and a carbon charge that does not reach it

2050 parameters:

| tech | capex | fom | lifetime |
|---|---|---|---|
| **`nuclear-3`** | **6,948.2** | 0.01023 | 40Y |
| `CCGT+CC` | **1,438.8** | 0.00438 | 25Y |
| `OCGT` | 619.8 | 0.00160 | 25Y |
| wind-on | 933.9 | 0.00217 | 30Y |
| solar-PV | 269.5 | 0.00103 | 40Y |

Nuclear costs **4.8x** CCGT+CC per unit of capacity and **2.3x** its fixed O&M.
Even with nuclear's capex falling steeply (16,594.7 -> 11,865.2 -> 6,948.2) it
never closes the gap.

Crucially, CCGT+CC is **not penalised on carbon**:

- its CH4 is charged **upstream** at `LNG-terminal` (0.2), not at the plant
  (`FINDING_upstream_carbon_gate.md`)
- it then **diverts 0.18 tCO2/MWh CH4** into the `CO2` node, which is
  **credited** when injected

So CCGT+CC delivers firm, dispatchable, effectively net-zero electricity at
roughly a fifth of nuclear's capital cost. Nuclear's main real-world selling
point - firm zero-carbon power - is **exactly matched by CCGT+CC in this model**,
and far more cheaply.

## 5. Is this realistic? Partly - and the caveats are important

**Defensible:** gas+CCS genuinely is a cheaper route to firm low-carbon capacity
than new nuclear on overnight-cost grounds, and NL/BE are gas-rich with North
Sea storage.

**Questionable, and worth raising with colleagues:**

- **CCGT+CC runs at very high utilisation.** 98,144 GWh from 12.671 units. It is
  acting as **baseload**, not as a peaker. Real post-combustion capture plants
  are penalised by cycling; the model has no such penalty.
- **No financing-cost differentiation.** Nuclear's real barrier is WACC and
  construction risk over a ~10-year build. A single `unit_investment_cost` with
  no technology-specific discount rate **flatters** short-build technologies.
  This is the single most likely reason nuclear is understated.
- **No build-time / lead-time constraint** was found for nuclear - it could in
  principle appear instantly in 2040, and still does not.
- **CCS availability is assumed generous**: `CO2-injection-NSNL031` absorbs
  everything the system throws at it (see `FINDING_co2_storage_saturation.md`).
  If storage were tighter or dearer, nuclear would look better.

## 6. NOT concluded here

I have **not** computed a full LCOE with discounting - the comparison above is
on capex/fom/lifetime, which is indicative but not decisive. A proper test would
be a **sensitivity run forcing nuclear capacity** (or activating
`limited_nuclear-3` in reverse) to see what it costs the objective. That is the
clean way to answer "how far from competitive is it?" and has not been run.
