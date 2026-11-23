# RUN: 3day hcco2 - price HC combustion

Input:  `checkpoints/Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.hcco2.sqlite`
Parent: `...retireall.sqlite` (OPTIMAL, objective 3,368,121, penalties 0.00)
Patch:  `tools/patch_hc_co2.py`
Date:   2026-10-04

## Why

HC was the only carbon-bearing carrier with NO emission booking in either tier:

* carrier fuels booked upstream at supply: fossil-CH4 0.200, coal 0.350,
  waste 0.300, crude 0.260
* industry process routes booked at the unit on own output: 66 families
  (REF-SMR 0.019, REF-SMR-MEA 0.002, CEM2-(BMW)MEA -0.308)

61 units across 5 families burned HC carbon-free, so HC was priced ~10x cleaner
per MWh than CH4. Result: 5.484 units of NEW oil-eng built in 2050 running
43.0 TWh in a net-zero system.

## Change

Added `atmosphere <- HC` at **0.24 ton/MWh** (`data/Commodities/commodity_data.csv`,
`HC.CO2_content`) on 61 units, keyed on the HC INPUT flow, mirroring
`SCPC-existing_BEC4__atmosphere__coal__SCPC-existing_BEC4 = 0.35`.

| family | units |
|---|---:|
| oil-eng | 17 |
| oil-boiler-existing | 17 |
| printing-and-media-production-reference | 17 |
| (LN+EL)O | 7 |
| oil-eng-existing | 3 |

Units that already carried an atmosphere flow were skipped, so no unit is
double-booked. `(LN)O` (0.967) and `(LN)O-MEA` (0.111) deliberately untouched.

Verified: entity +122, entity_element +244, parameter_value +61; all new values
`typeof=blob`, `0.24`, `type=float`, alternative `Base`; no unit double-booked;
wiring asserted on both new relationship classes; no duplicate names.

## Predictions (registered BEFORE the solve)

1. `objective_objective_penalties == 0.00`. **Check this first.**
2. Objective RISES vs 3,368,121 (constraint added, feasible set shrinks).
   Expect < +2%.
3. `oil-eng` 2050 generation falls sharply from 43,035.7. Expect < 5,000.
4. `oil-eng` new investment in 2050 falls from 3.627 toward ~0.
5. Something must replace ~43 TWh. Most likely `CCGT+CC` (already 100,800) and
   wind-on (118,303). **Offshore wind is NOT predicted to appear** - the
   offshore study showed solar still has headroom in 11/17 regions.
6. Batteries still ZERO. The binding reason is `cyclic_condition=true` on 3
   representative days, which this patch does not touch. If batteries DO appear,
   my time-representation explanation is wrong.
7. `(LN+EL)O` olefins route becomes less attractive; olefins mix shifts further
   toward MeOH route (was NG 79.5% / MeOH 20.5%).
8. 2050 net CO2 stays at ~0 (the cap binds); the adjustment shows up as higher
   cost and more DAC, not as higher emissions.

## Falsification

If `oil-eng` persists at >20 TWh in 2050 with penalties at 0, then the 0.24
coefficient is not the binding mechanism and the explanation is wrong.

## Caveat recorded up front

`(LN+EL)O` uses HC partly as FEEDSTOCK (carbon embodied in olefins), not fuel.
Charging it 0.24 overstates its emissions. Included because it currently pays
ZERO, which is further from truth. Proper fix is a route factor. Any
`(LN+EL)O` result from this run must be treated as indicative only.

---

## OUTCOME (2026-10-04) - see `FINDING_hc_co2_unpriced.md`

**OPTIMAL**, 83 min, objective **3,376,630** (+0.25%), penalties **0.00**.

Scorecard: 1 PASS, 2 PASS, 3 PASS (oil-eng 2050 = 0.0), 4 PASS, 5 **FAIL**
(offshore DID appear, 10,187 GWh), 6 PASS, 7 **FAIL** (olefins moved away from
MeOH), 8 PASS.

Prediction 5 falsifying means `FINDING_offshore_wind_zero.md` needed a
retraction, now appended there as S10.
