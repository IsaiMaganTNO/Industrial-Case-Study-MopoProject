# PROPOSAL: How to reduce allowed natural-gas use

Status: recommendation, **not yet implemented or run**. Evidence in
`FINDING_gas_volumes_and_transit.md` and `FINDING_gas_supply_overstated.md`.
Scripts: `run_logs/_lev1.py` .. `_lev4.py`, `_opt.py`.

## The problem restated
Gas supply is capped only by an hourly power limit that the model saturates:
**100% load factor, every hour, every year** (BE all three milestones, NL by 2050).
Consumption rises 434 -> 624 -> **662 TWh**, about **1.3x present-day NL+BE inland demand**,
in a scenario meant to be deeply decarbonised. The ceiling itself derives from
**ALSI/ENTSOG terminal send-out**, a transit-capable *entry* capacity that in reality also
serves Germany/re-export.

## Recommended: Option A - `availability_factor` on the two supply units
**This is the primary recommendation.**

Verified mechanics (`_lev3.py`, `_lev4.py`):
- `availability_factor` is parameter definition **id 217 on class `unit`**, default **1.0**,
  described as *"Availability of the unit, acting as a multiplier on its
  `capacity_per_unit`"*. Exactly the right lever.
- Scalar floats are accepted (VRE rows use time_series, but default is float).
- **No thermal unit currently sets it** - so this introduces a new convention; it is
  additive and touches nothing else.
- Targets: `LNG-terminal_{17 regions}`, `gas-extraction_{9 NL regions}`.

Resulting 2050 ceilings (extraction -> 0):

| af (LNG) | BE TWh | NL TWh | total | vs today (BE 180 / NL 320) |
|---:|---:|---:|---:|---|
| 1.00 (now) | 244.2 | 417.9 | **662.1** | 1.36x / 1.31x |
| 0.75 | 183.1 | 235.5 | 418.6 | 1.02x / 0.74x |
| 0.65 | 158.7 | 204.1 | 362.8 | 0.88x / 0.64x |
| **0.55** | **134.3** | **172.7** | **307.0** | **0.75x / 0.54x** |
| 0.50 | 122.1 | 157.0 | 279.1 | 0.68x / 0.49x |

**Suggested: af = 0.55 for LNG**, which lands total 2050 supply at ~307 TWh - comfortably
below today and consistent with a decarbonising pathway, while still leaving gas able to
cover genuine peaks. It is also near real LNG terminal utilisation (~40-65%).

Plus **Option A2: decline `gas-extraction`** via a time series 1.0 -> ~0.3 -> ~0.0, since the
284.5 GWh/d value is a static 2025-vintage figure and Groningen closed Oct 2023.

**Why this is the best lever:** it is targeted, physically interpretable, uses a documented
SpineOpt parameter at its intended meaning, is trivially reversible, and - unlike the
budget route below - has **no representative-day scaling hazard**.

## NOT recommended as the primary fix: Option B - activate `limited_fossil-CH4`
I previously suggested this twice. On inspection it is **risky**, and I withdraw it as the
first choice:

- It works by making `fossil-CH4` a **long-term storage stock** (`balance_type` 2,
  `storage_longterm_active` 5, `storage_state_max` 2500000/1000000/500000).
- **`tools/patch_biomass_cap_div365.py` documents a verified SpineOpt defect** for exactly
  this construct: with representative days, the stock balance is debited one *average day's*
  net change while the fuel flow is annualised by day weights summing to 365 - a measured
  **365x** mismatch on `biomass-stock_BEC1`. The `atmosphere` cap in this very DB was
  already divided by 365 for this reason.
- The `fossil-CH4` budget is **not** /365-adjusted. If it shares the long-term-stock
  semantics, the "500 TWh" 2050 budget could behave as either a binding 500 TWh cap **or**
  an effectively inert ~365x-too-loose one. **Which it is has not been tested.**

So Option B's true stringency is **unknown** until the 365x question is resolved for this
node. It remains valuable as a *sensitivity* and as a question for the data authors, but it
should not be the mechanism we rely on.

## Suggested plan
1. Write `tools/patch_gas_availability.py` (mirroring existing patch conventions:
   positional SRC DST, `--dry-run`, idempotent, self-checks, `type='float'` on every row,
   cross-border guard assertion **1522.5048**).
2. Apply `af=0.55` to the 17 `LNG-terminal_*`; apply a declining series to the 9
   `gas-extraction_*`.
3. Re-solve 3-day; compare against `3day_co2bidir` (obj 3,331,603).
4. Only then, separately, test Option B to settle the 365x behaviour.

## Predictions to register BEFORE the run
- 2050 methane supply falls from 662.1 to ~307 TWh (**mechanical, near-certain**).
- CCGT+CC 2050 electricity share falls below 39.2%; absolute output falls from 131,102 GWh.
- The 2050 `gas-boiler` build (99.8 TWh) shrinks or disappears.
- DAC gas use (81.7 TWh) falls; total capture and CO2 pipeline throughput fall.
- Objective **rises** above 3,331,603 (a constraint is being added).
- Penalties must stay **0.000000**. If penalties appear, the cut is infeasibly tight and
  af should be relaxed toward 0.65-0.75.

**Falsifiers:** if CCGT+CC's share is roughly unchanged, then gas availability was not the
binding driver and the cost assumptions dominate - which would redirect attention to CCGT+CC
capex/the CO2 price. If `gas-boiler` persists at 2050, it is an independent
catalogue/cost defect, not a fuel-availability artefact.

## Caveats
- The ~40-65% real LNG utilisation benchmark is **from memory** and should be checked
  against ALSI/GIE before the 0.55 choice is defended externally. The *model-side*
  arithmetic in the table above is exact.
- af=0.55 is a judgement, not a derived value. If the authors supply real send-out profiles
  or ENTSOG utilisation data, a time series should replace the flat factor.
- This caps **supply**, which is a blunt instrument: it constrains the fuel rather than
  fixing the demand-side defects (2050 gas-boiler rebuild, DAC on gas). Those should be
  investigated on their own merits - capping supply may mask them.
