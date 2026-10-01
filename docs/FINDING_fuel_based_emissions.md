# Finding: industrial CO2 emissions are fuel-based, not process-route-based

Status: **confirmed, reproducible, upstream**
Date: 2026-10-01
Evidence run: `checkpoints/Investment_Results.1rep_repfix.sqlite` (OPTIMAL, 78 min)

---

## 1. Summary

Every unit in the model that burns a carbon-bearing fuel is assigned an emission
coefficient that depends **only on the fuel**, never on the technology. Carbon
capture equipment is therefore invisible to the emissions accounting: a
CCS-equipped process emits exactly as much to `atmosphere` as its unabated twin.

The source data contains correct per-route emission factors. They are never read.

Consequence in the only run where the CO2 budget is both correctly scaled and
binding: the model cannot decarbonise refineries at all, and pays
**4.52e9 in CO2 slack penalties (99.8% of the objective)** while real system
costs are only ~8.2M.

This is **not** an IC1 regression. The EU case database carries identical values.

---

## 2. Evidence

### 2.1 What the model database contains

All three refinery routes, in **all 17 regions** (BEC1-8, NLC1-9):

| tech          | `atmosphere<-crude` | `CO2<-HC` |
|---------------|--------------------:|----------:|
| REF-SMR       | 0.26                | -         |
| REF-SMR-MEA   | **0.26**            | 0.017     |
| REF(H2)       | **0.26**            | -         |

The MEA variant and the hydrogen-fired variant carry the *same* emission
coefficient as the unabated route.

EU case (`EU_case/.spinetoolbox/items/final_spineopt_model/Final_SpineOpt_Model.sqlite`),
regions ES and FR: identical values. Upstream, not local.

### 2.2 What the source data says

`data/Industry/technology_catalogue_ind_nuts0_nuts3.xlsx`,
sheet `ind_process_routes_co2_emission` (tCO2 per MWh of HC output):

| Industry     | co2_emission | co2_capture | sum   |
|--------------|-------------:|------------:|------:|
| REF-SMR      | 0.019        | 0.000       | 0.019 |
| REF-SMR-MEA  | **0.002**    | 0.017       | 0.019 |
| REF(H2)      | **0.016**    | 0.000       | -     |

Internally consistent: MEA captures 0.017 of 0.019 = **~89% capture**, exactly as
expected for post-combustion MEA. The data is correct; it is simply not used.

### 2.3 Where 0.26 comes from

`data/Commodities/commodity_data.csv`, column `CO2_content` (ton/MWh):

| commodity | CO2_content |
|-----------|------------:|
| crude     | **0.26**    |
| coal      | 0.35        |
| waste     | 0.30        |
| CH4       | 0.20        |
| HC        | 0.24        |

These are fuel properties, and they are exactly the coefficients found in the DB.

### 2.4 The code path

`ines-spineopt/ines-spineopt/ines_to_spineopt.py`, `process_emissions()` (lines 177-196):

```python
co2_value = {node: co2_content for each node carrying co2_content}
for unit_entity in target_db.get_entity_items(entity_class_name="unit"):
    unit__from_nodes = [nodes with co2_content feeding this unit]
    ...
    elif len(unit__from_nodes) == 1:
        add_entity(target_db, "unit__to_node", (unit_name, "atmosphere"))
        add_parameter_value(target_db, "unit_flow__unit_flow",
                            "flow_ratio_equality_coefficient", "Base",
                            (unit_name, "atmosphere", unit__from_nodes[0], unit_name),
                            co2_value[unit__from_nodes[0]])
```

The coefficient is `co2_value[fuel]`. The loop iterates over units but never
consults any process-route property. Capture equipment cannot influence it.

`data-pipelines/europe/_industry-aidres/industry_DB.py::add_tech_parameters()`
(lines 290-345) reads `ind_process_route_life`, `ind_process_routes_capex`,
`ind_process_routes_fom`, and `ind_process_routes_co2_capture`.
It does **not** read `ind_process_routes_co2_emission`.

A text search for `emission` across the entire pipeline returns **zero matches**.

### 2.5 Two compounding errors

1. **Emissions are fuel-based.** Abatement is invisible; the MEA route emits like
   the unabated route.
2. **Capture is added without being subtracted.** `CO2_captured = 0.017` creates a
   separate capture flow, but the `atmosphere` flow remains at the full fuel rate.
   The two are never reconciled, so captured carbon is counted as both captured
   *and* emitted.

This explains why a capture-fraction audit looks wrong in **both** directions:

| group | behaviour |
|---|---|
| `REF-SMR-MEA` | emission ratio present, capture ignored -> **4% effective capture** |
| `DAC`, `SMR+CC`, `CCGT+CC`, `(COEL)FT-MEA`, `(NG)PE-MEA` ... | consume no `co2_content` fuel, so get a capture ratio and **no** emission ratio -> appear as **100% capture** |

Neither is physically correct.

### 2.6 Unit error on top of the structural error

The coefficients are also dimensionally inconsistent.

- Source `co2_emission` is per **MWh of HC output**.
- The DB ratio `atmosphere<-crude` is applied per **MWh of crude input**.
- `HC<-crude = 0.64`, i.e. `crude/HC = 1.5623`.

Effective emission per MWh HC in the model:

```
0.26 (per MWh crude) x 1.5623 (MWh crude / MWh HC) = 0.40620 tCO2/MWh HC
```

Against source values:

| tech        | source | model effective | overstated |
|-------------|-------:|----------------:|-----------:|
| REF-SMR     | 0.019  | 0.4062          | **x21.4**  |
| REF-SMR-MEA | 0.002  | 0.4062          | **x203.1** |
| REF(H2)     | 0.016  | 0.4062          | **x25.4**  |

So refinery emissions are overstated by **one to two orders of magnitude**, before
any consideration of capture.

Note `crude` and `HC` *both* carry a `CO2_content` (0.26 and 0.24). Carbon is
therefore charged when crude is refined and chargeable again when HC is burned -
a double-counting risk inherent to the fuel-based design.

---

## 3. Observed consequences

From `reports_1rep_repfix/` (CO2 budget correctly scaled and binding):

Net CO2 by year: 2030 = 265,873 | 2040 = 212,742 | 2050 = 175,628
Cap:             2030 = 165,400 | 2040 =  36,800 | 2050 = 0

2030 emissions by technology:

| tech | net CO2 |
|---|---:|
| **REF-SMR-MEA** | **267,810** |
| (NG)DRI-EAF-MEA | 485 |
| Scraps_EAF | 77 |
| all other industry / hydrogen / boilers | ~0 |
| other (capture) | -2,423 |

**One technology is 99.8% of total emissions.**

Measured flows for `REF-SMR-MEA` in 2030: emits 733.7 to `atmosphere`, captures
30.7 to `CO2` -> **4.0% effective capture**, against ~89% in the source data.

The optimiser behaves rationally given this data:

- `REF-SMR` (unabated) is at **0.0** - the CCS variant is already chosen.
- `REF(H2)` is **cheaper** (investment 914 vs 1,104) and should emit 0.016, but
  offers zero emission saving in the model, so it is never built.
- PEM electrolysis **is** deployed aggressively: 124,942 -> 619,180 -> 1,118,790 MWh H2.
  Clean hydrogen is not the bottleneck.
- Coefficients are `flow_ratio_equality_coefficient` - **equalities**. There is no
  freedom to abate.
- Refinery `HC` output is exogenous demand that must be met.

Result: 5.5M invested, no abatement possible, **4.52e9 paid in slack**.

The penalty is the model correctly reporting that the input data contains no
representable abatement path for refinery emissions.

---

## 4. Scope

Affected: every unit consuming a commodity with a `CO2_content`.

| fuel | ratio | units affected |
|---|---:|---:|
| coal | 0.350 | 209 |
| crude | 0.260 | 51 |
| waste | 0.300 | 38 |
| fossil-CH4 | 0.200 | 26 |

324 units in total. Refineries dominate the 2030 result only because `HC` demand
is large and exogenous; the same flaw silently inflates emissions for every
CCS-equipped industrial route and suppresses the value of all capture investment.

---

## 5. Relationship to earlier findings

This is the **second** of two independent defects found in the CO2 chain. Both had
to be fixed/understood before the result could be interpreted:

1. **`representative_blocks_by_period` collapse** (fixed, verified).
   `make_tiny_model.py` collapsed the 365-entry daily map to 1 entry, which made the
   long-term CO2 budget draw down once per year instead of 365 times - a 365x
   weakening. Fixed by restoring 365 daily entries; the budget now binds exactly at
   `cap x state_max` (165,400 / 36,800 / 0), reproducing the EU signature at no LP cost.
   `tools/patch_co2_caps.py` and `tools/patch_biomass_units.py` were both reacting to
   this symptom and are superseded.

2. **Fuel-based emissions** (this document) - not yet fixed.

Earlier runs produced apparently "implausible" results (unabated fossil replacing
biomass/CCS) because defect 1 loosened the budget by ~2.54x, which left headroom for
unabated fossil **once** refinery emissions were already consuming most of the budget
via defect 2.

**All emissions results produced before 2026-10-01 are untrustworthy.**

---

## 6. Proposed fix

### 6.1 Principle

Emissions must be a property of the **process route**, not of the fuel. The source
data already provides this per route, in the same units and on the same key as the
`co2_capture` data that is *already* flowing through the pipeline correctly.

The existing `co2_captured` path is therefore a **working template**: it writes
`CO2_captured` on `technology__to_commodity__to_commodity = (industry, node, "CO2")`,
and that value arrives in the model DB as `CO2<-HC = 0.017` - keyed on **output**,
with no unit conversion needed. The fix mirrors it exactly for emissions.

### 6.2 Unit correctness - verified, no conversion required

This was the main risk, and it is resolved:

- `ind_process_routes_co2_emission` and `ind_process_routes_co2_capture` were merged
  on `(Industry, to_node)`: **80 rows paired, 0 unit mismatches**. The two sheets
  always agree on units.
- Both are expressed **per unit of `to_node` output** (`tco2_mwh` for refineries /
  MeOH / several light sectors, `tco2_t` and `tco2_t_*_eq` for mass-based sectors).
- `CO2_captured` is already written **unconverted** on the output key, and lands
  correctly in the DB (0.017). Because emission uses the identical key and unit,
  it needs **the same treatment and no scaling**.
- Product-mass vs MWh normalisation (`kt -> 1000/8760`, else `1/8760`) is applied to
  *capacity and demand*, not to these intensity ratios, so it does not interact.

=> **Writing `co2_emission` the same way `co2_capture` is written is dimensionally
correct by construction.** This is what makes the fix safe.

By contrast the current fuel-based value is dimensionally wrong: `atmosphere<-crude`
is applied per MWh of **crude input**, while the source is per MWh of **HC output**,
with `HC<-crude = 0.64` (`crude/HC = 1.5623`) between them:

```
model effective = 0.26 x 1.5623 = 0.40620 tCO2 / MWh HC
```

| tech        | source | model effective | overstated |
|-------------|-------:|----------------:|-----------:|
| REF-SMR     | 0.019  | 0.4062          | x21.4      |
| REF-SMR-MEA | 0.002  | 0.4062          | x203.1     |
| REF(H2)     | 0.016  | 0.4062          | x25.4      |

### 6.3 Change 1 - emit the route emission factor

`data-pipelines/europe/_industry-aidres/industry_DB.py::add_tech_parameters()`

Add a block directly mirroring the existing `co2_captured` block, reading
`sheets["ind_process_routes_co2_emission"]` and writing a `CO2_emitted` parameter on
`technology__to_commodity__to_commodity = (industry, node, "atmosphere")`.

Two differences from the capture block, both required:

- the guard must be `!= 0.0`, **not** `> 0.0`: `CEM2-(BMW)MEA = -0.308` and
  `CEM2-(BMW)CaL = -0.188` are legitimate **negative** (BECCS) emissions and must
  survive;
- a route present in the emission sheet but absent from the capture sheet is normal
  (120 emission rows vs 80 capture rows) and must not raise.

### 6.4 Change 2 - stop deriving industrial emissions from fuel

`ines-spineopt/ines-spineopt/ines_to_spineopt.py::process_emissions()`

This function currently assigns `atmosphere <- fuel = co2_content(fuel)` to **every**
unit consuming a carbon-bearing commodity (324 units: coal 209, crude 51, waste 38,
fossil-CH4 26), as a `flow_ratio_equality_coefficient`.

It must **skip any unit that has a route-specific emission factor**, and emit that
instead, keyed on the unit's output commodity. The fuel-based path remains the
fallback for units with no route data (power plants, boilers, terminals).

Without this change, Change 1 alone would make things worse - the unit would then be
charged *both* the fuel-based and the route-based emission.

### 6.5 Change 3 - reconcile capture with emission

Today `CO2_captured` adds a capture flow while the `atmosphere` flow stays at the
full fuel rate, so captured carbon is counted as captured **and** emitted.

Once Change 2 lands this resolves itself, because the source data is already net:
`co2_emission` is the **post-capture** residual (REF-SMR-MEA: 0.002 emitted +
0.017 captured = 0.019 = the unabated REF-SMR figure). So emission and capture
should be written as-is, with **no subtraction** - the arithmetic is already done
upstream. Verified across all 80 paired rows.

### 6.6 Validation plan (static, before any solve)

After rebuilding the model DB, assert in the DB:

| check | expected |
|---|---|
| `REF-SMR-MEA` emission ratio | ~0.002 per MWh HC (not 0.26 per MWh crude) |
| `REF(H2)` emission ratio | ~0.016 |
| `REF-SMR` emission ratio | ~0.019 |
| `CEM2-(BMW)MEA` | **negative** (~-0.308) |
| no unit carries both a fuel-based and a route-based `atmosphere` ratio | 0 units |
| units with no route data (CCGT, boilers, LNG-terminal) | unchanged fuel-based ratio |

Then re-solve `tiny.1rep.repfix` (78 min, known-good temporal structure) and check
**penalties first**. Expected: `objective_objective_penalties` falls from 4.52e9 by
orders of magnitude, and `REF(H2)` appears in the fleet (it is cheaper than
`REF-SMR-MEA` at 914 vs 1,104 and should win once its lower emissions are visible).

### 6.7 Risk and scope note

Change 2 touches `ines-spineopt`, which is shared with the EU case. Direct
comparability with the EU case is **not** required (confirmed with the user), so the
change can be made in-tree. It should still be flagged upstream, since the EU case
database was verified to contain the identical defect.

The fix is confined to industry, which is where the route data exists. Power-sector
and heat units keep the fuel-based path unchanged.
