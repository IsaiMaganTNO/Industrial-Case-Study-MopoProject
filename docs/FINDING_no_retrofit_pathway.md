# FINDING: no retrofit pathway - abatement is greenfield-only

**Date:** 2026-10-06 | **Run:** `Investment_Results.3day_routeemis.sqlite`
**Trigger:** colleague question - are add-on CC retrofits modelled?

## 1. Answer: correct, retrofitting is NOT represented

Verified structurally, not assumed:

| check | result |
|---|---|
| `entity_class` with retro/upgrade/convert/replace | **none** |
| `parameter_definition` with those terms | **none** |
| entities matching `%retro%` | **0** |

There is no construct in the schema that lets an existing unit **acquire** a
capture module. SpineOpt here models units as atomic: a unit either has a `CO2`
output flow from birth, or it never will.

## 2. How abatement IS represented: paired independent technologies

`CCGT` and `CCGT+CC` are **separate unit families**, not a plant and its
add-on:

| | `CCGT` | `CCGT+CC` |
|---|---|---|
| inputs | CH4 | CH4 |
| outputs | elec | **CO2**, elec |
| `unit_investment_cost` | 1438.76 | **1438.76** |

Same pattern for `CEM2-(Afm)` / `CEM2-(Afm)MEA`, `BF-BOF` / `BF-BOF-MEA`,
`REF-SMR` / `REF-SMR-MEA`, `SMR` / `SMR+CC`.

## 3. The consequence that matters: capture is priced as a WHOLE NEW PLANT

`BF-BOF` and `BF-BOF-MEA` both cost **42,632.2**. `REF-SMR` and `REF-SMR-MEA`
both cost **442.2**. The abated variant carries the **full greenfield capex of
the entire plant**, not the incremental cost of bolting on a capture island.

In reality a CC retrofit is typically a **fraction** of plant capex. By pricing
abatement at 100% of a new plant, the model **systematically overstates the cost
of decarbonising existing assets**.

(Note `CEM2-(Afm)MEA` at 2,959.3 is *cheaper* than `CEM2-(Afm)` at 5,161.8 -
cement is costed on a different basis, so this is not uniform across sectors and
should not be generalised.)

## 4. Direct evidence: stranded capacity instead of conversion

Only **new-build** families carry `investment_count_initial_cumulative`; **no
existing/brownfield unit is capture-equipped**. The existing fleet is
`*-existing`, `REF-SMR`, `gas-boiler-existing`, `LNG-terminal`, `solar-PV-existing`.

In 2050 the model holds **80.39 units of unabated `REF-SMR`** in the fleet
alongside **23.22 units of newly built `REF-SMR-MEA`**. The old capacity is
**not retired and not converted** - it simply sits idle (output 0.0) while a
parallel abated fleet is built from scratch.

A retrofit formulation would instead have **converted** those 80.39 units at
incremental cost.

## 5. Why this matters for the study's conclusions

This biases results in a specific, predictable direction:

- **CCS on existing industry is too expensive**, so the model under-deploys it.
  This is consistent with - and may partly explain - the cement result: capture
  stays flat at 1,594 while cheap geological injection absorbs the marginal
  tonne (`RUN_3day_routeemis.md`, prediction 5).
- **Capital is over-counted** where abatement does happen, inflating investment
  cost relative to a retrofit world.
- Transition speed is understated: retrofits can be delivered faster than
  greenfield replacements.

## 6. NOT concluded here

Whether the capex values are *intended* as full-plant or already represent a
retrofit-equivalent increment is **a question for the catalogue authors**. The
identical `BF-BOF` / `BF-BOF-MEA` and `CCGT` / `CCGT+CC` figures strongly
suggest full-plant, but this has **not been confirmed against source
documentation**. The cement counter-example shows the convention is not uniform.

Adding a true retrofit pathway would require new `unit__unit` conversion
entities and is a **model-structure change**, not a data patch.
