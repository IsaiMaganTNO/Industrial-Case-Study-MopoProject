# FINDING: HC combustion was unpriced - oil engines eliminated

Run: `Investment_Results.3day_hcco2.sqlite`, **OPTIMAL**, 83 min,
objective **3,376,630**, `objective_objective_penalties = 0.00`.
Parent: `retireall` (3,368,121). Patch: `tools/patch_hc_co2.py`.
Predictions registered before the solve in `docs/RUN_3day_hcco2.md`.
Cache: `run_logs/hcco2.pkl` (weighted - see S6).

## 1. The defect

The model books CO2 in two consistent tiers:

| tier | keyed on | examples |
|---|---|---|
| carrier fuels, upstream at supply | fuel input | fossil-CH4 **0.200** (LNG-terminal, gas-extraction), coal **0.350**, waste **0.300**, crude **0.260** |
| industry process routes, at the unit | unit's OWN OUTPUT | 66 families: REF-SMR 0.019, REF-SMR-MEA 0.002, CEM2-(BMW)MEA **-0.308** |

**HC fell through both.** No HC supply node carried a `CO2_content` booking the
way `fossil-CH4` does, and power/heat units get no process-route factor. 61
units across 5 families burned HC with *zero* emission accounting:

    oil-eng (17), oil-boiler-existing (17),
    printing-and-media-production-reference (17),
    (LN+EL)O (7), oil-eng-existing (3)

Effect: HC priced ~10x cleaner per MWh than CH4 (0 vs 0.200). `oil-eng` was the
system's only **unpriced escape valve** from the CO2 cap.

Note the route-based fix of `FINDING_fuel_based_emissions.md` S6.3 **has landed**
- `REF-SMR-MEA` is 0.002, not 0.019, and negative BECCS values survive. That
document's "not yet fixed" status is stale for industry routes.

## 2. The patch

`atmosphere <- HC` at **0.24 ton/MWh** (`data/Commodities/commodity_data.csv`,
`HC.CO2_content`) on all 61 units, keyed on the HC **input** flow, mirroring
`SCPC-existing_BEC4__atmosphere__coal__SCPC-existing_BEC4 = 0.35`.

Units already carrying an atmosphere flow were skipped, so nothing is
double-booked. `(LN)O` (0.967) and `(LN)O-MEA` (0.111) deliberately untouched.

Verified before solving: entity +122, entity_element +244, parameter_value +61;
all new values `typeof=blob`, `'0.24'`, `type=float`, alternative `Base`; no unit
double-booked; wiring asserted on both relationship classes; no duplicate names.

## 3. Result - oil engines eliminated

| | retireall | hcco2 |
|---|---:|---:|
| `oil-eng` 2050 generation | 43,035.7 GWh | **0.0** |
| `oil-eng` fleet 2040 / 2050 | 1.857 / 5.484 | **none, any year** |
| `oil-eng` new investment | 1.857 / 3.627 | **zero** |
| `oil-eng-existing` | 0.084 | **gone** |
| `oil-boiler-existing` 2030 / 2040 | 10.316 / 7.423 | **0.666 / 0.666** |

Objective +0.25%. Net CO2 unchanged (165,400 / 36,800 / -0.0) - the cap binds in
both runs, so the patch changes *how* the target is met, not whether.

### 2050 electricity (GWh, weighted)

| tech | retireall | hcco2 | delta |
|---|---:|---:|---:|
| wind onshore | 118,303.3 | 134,816.2 | +16,512.9 |
| CCGT+CC | 100,800.1 | 87,608.5 | -13,191.6 |
| solar PV | 70,643.9 | 78,830.6 | +8,186.8 |
| **CCGT unabated** | 4,513.3 | **29,251.6** | **+24,738.3** |
| **wind offshore** | 0.0 | **10,187.1** | **+10,187.1** |
| OCGT | 0.0 | 1,574.8 | +1,574.8 |
| CCGT-H2 | 0.0 | 385.4 | +385.4 |
| `oil-eng` | 43,035.7 | **0.0** | -43,035.7 |
| total | 337,600.8 | 342,974.7 | +5,373.9 |

Heat also electrified: `air-heatpump` 2,940 -> **16,506**, `ground-heatpump`
969 -> **5,261**, `gas-boiler` 117,065 -> 99,526. Heat-pump fleet 0.479 -> 2.602.

## 4. Prediction scorecard

| # | prediction | outcome |
|---|---|---|
| 1 | penalties == 0 | PASS |
| 2 | objective rises < 2% | PASS (+0.25%) |
| 3 | oil-eng 2050 < 5,000 GWh | PASS (0.0) |
| 4 | oil-eng investment -> ~0 | PASS (zero) |
| 5 | offshore wind does NOT appear | **FAIL** |
| 6 | batteries stay zero | PASS (identical) |
| 7 | olefins shift toward MeOH | **FAIL** (20.5% -> 19.2%) |
| 8 | net CO2 stays ~0 | PASS |

## 5. RETRACTION: `FINDING_offshore_wind_zero.md` reasoning was incomplete

**`wind-off-FB-SP370-HH155_NSNL011` builds 1.719 units / 10,187 GWh in 2050** -
the first new offshore in any run.

My earlier explanation said offshore stays out because onshore binds in only
5/17 regions while **solar still has headroom in 11/17**, so the model never
exhausts the cheaper option. The levelised-cost arithmetic in that document is
unchanged and still correct. What was wrong is the **conclusion**: solar is built
in the same 11 regions in both runs, yet offshore now enters anyway.

Offshore was not merely "more expensive than solar/onshore" - it was being
undercut by a **mispriced competitor**. Remove the unpriced oil and offshore
becomes economic *despite* unchanged solar headroom. The falsification test
proposed in that document (zero the solar caps) is no longer the decisive one.

## 6. Process error (mine), corrected

My first comparison showed 2050 electricity collapsing to 2,787 GWh. That was a
**postprocessing bug, not a model result**: I called `PP.load()` without `wmap`,
leaving `hcco2` raw while the cached `retireall` was weighted - the exact 365x
trap documented in `postprocess.py`. Reloaded with `PP.load_weights()`
(100.807 / 159.382 / 104.811, sum 365.0). All figures above are weighted.

## 7. Remaining defects - unchanged by this patch

- **Unabated `CCGT` 4,513 -> 29,252 GWh in 2050.** The new largest anomaly. Part
  of the oil was replaced by *unabated gas*, not clean capacity, with CCS gas
  falling 13,192. Net CO2 still 0 because DAC rises (9.778 -> 10.717 units).
- **`(LN+EL)O` is knowingly over-charged.** Its HC is partly feedstock - carbon
  embodied in olefins, not combusted. Charging 0.24 overstates it. The olefins
  mix moving *away* from MeOH (prediction 7 failed) is plausibly this artefact.
  Any `(LN+EL)O` result here is indicative only; it needs a route factor.
- **Industry reference units still book on `coal` only** (0.350) while also
  consuming CH4, HC and bio. Fuel-based leftovers the route fix did not cover.
- **Batteries still exactly zero**, storage `node_state` byte-identical to parent.

  > **CORRECTION (2026-10-05).** Wherever this document or the companion share
  > README attributed the zero to *daily cyclicity structurally blocking storage*,
  > that explanation is **wrong and is retracted**. The 7-day rebuild
  > (`RUN_7day_hcco2.md`) uses the **same** 24 h blocks with the **same**
  > `cyclic_condition`, and batteries are **non-zero**: 4.50 / 5.34 / **10.94**
  > units in 2030/2040/2050, generating 4,557 GWh in 2050, with a
  > `storage_investment_costs` objective line of 2,480.9 (3-day: exactly 0.0).
  >
  > `cyclic_condition` blocks *inter-day* arbitrage, but batteries only ever
  > required *intra-day* arbitrage, which was available all along. The 3-day
  > sample (14 May / 10 Sep / 24 Dec) simply contained **no day with a steep
  > enough within-day net-load swing** to pay for a battery; the 7-day sample
  > (12 Jan, 18 Feb, 5 Nov, 13 Dec) does.
  >
  > The zero was therefore a **sampling artefact, not a structural property** -
  > a far weaker and more contingent claim than the one originally made.
  > **Seasonal storage remains untested**: 24 h cyclic blocks cannot represent
  > it at *any* number of representative days.
- **Electrolysis still 0.152 units** (`Diaphragm` chlor-alkali only, not H2).
