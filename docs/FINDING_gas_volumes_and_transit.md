# FINDING: Natural gas volumes NL+BE - magnitudes, transit, and the gas-extraction correction

Run `3day_co2bidir`. Scripts: `run_logs/_gx1.py`, `_ch4flow.py`, `_ch4exp.py`, `_ch4use.py`,
`_cmp2.py`, `_transit.py`. Supersedes parts of `FINDING_gas_supply_overstated.md`.

## 1. CORRECTION - `gas-extraction` is NOT storage withdrawal
The user queried whether `gas-extraction` is storage rather than production. **It is
genuine production, and my Groningen framing was right, but the two must not be confused -
they are separate objects:**

| object | class | topology |
|---|---|---|
| `gas-extraction_NLC3` | **`unit`** | `fossil-CH4` -> unit -> `CH4_NLC3`, plus `-> atmosphere` (0.2 upstream CO2) |
| `CH4-geo-formation_NLC3` | **`node`** (storage) | bidirectional pair `CH4-geo-formation<->CH4_NLC3` |

`gas-extraction` draws from the `fossil-CH4` commodity source and books upstream emissions -
that is domestic production, not a withdrawal. Storage is the separate `CH4-geo-formation`
node (BE 1.10375 TWh, 11.0175 GWh/d inj, 21.2075 GWh/d wdr) which is cyclical and
inventory-limited. **So the Groningen point stands**, but note the NL figure 284.5 GWh/d
(103.9 TWh/yr) is sourced from "Scenario report 2022 + adjustments" and is a **2025-vintage
production capacity held static to 2050**.

## 2. Gas actually consumed in the solution (TWh)

| | 2030 | 2040 | 2050 |
|---|---:|---:|---:|
| **BE** | 191.3 | 282.8 | **304.0** |
| **NL** | 242.8 | 341.6 | **358.1** |
| **total** | **434.1** | **624.4** | **662.1** |

Top consumers 2050 (TWh): CCGT+CC 269.9, gas-boiler 99.8, DAC 81.7, `(NG)PEA-MEA` 80.8,
REF-SMR 41.1, `(NG)NH3-MVR-DEA` 28.3, `(NG)DRI-EAF-MEA` 25.5.

## 3. Transit - the user's hypothesis, tested
**Concern:** the input capacities may include throughput to Germany and beyond.
**Two distinct answers, and they point in opposite directions.**

### 3a. In the MODEL, transit is exactly zero
Measured weighted `connection_flow` at all foreign CH4 nodes:

| node | 2030 in/out | 2041 in/out | 2050 in/out |
|---|---|---|---|
| `CH4_DE` | 166,969 / 166,969 | 132,982 / 132,982 | 145,273 / 145,273 |
| `CH4_FR` | 61,318 / 61,318 | 55,206 / 55,206 | 60,532 / 60,532 |
| `CH4_LU`, `CH4_UK` | 0 | 0 | 0 |

**Net exchange = exactly 0.0 TWh in every milestone.** Inflow equals outflow at each
foreign node to the last digit, because those nodes have **no feeders and no sinks** - they
are pure pass-through artefacts. So the 662.1 TWh is **100% domestic NL+BE consumption**;
none of it is transit. (Confirms the earlier blind-spot check by direct flow measurement.)

### 3b. But the SOURCE capacity IS transit-capable - the user's concern is valid upstream
The capacities come from **ALSI/ENTSOG terminal send-out**, i.e. the maximum rate gas can
enter the NL/BE system - which historically serves re-export and transit, not just inland
demand:

| | model GWh/d | TWh/yr @100% | ~bcm/yr |
|---|---:|---:|---:|
| BE (Zeebrugge) | 669.0 | 244.2 | ~23.1 |
| NL (Gate + Eemshaven) | 860.3 | 314.0 | ~29.8 |

Real nominal send-out is roughly Zeebrugge ~9 bcm (~95 TWh), Gate ~16 bcm (~169 TWh),
Eemshaven ~8 bcm (~84 TWh). The BE figure in particular (~23 bcm implied vs ~9 bcm real)
looks inflated unless it bundles pipeline entry capacity alongside LNG.

**Therefore:** using a transit-capable *entry* capacity as a ceiling on *domestic* supply
is a genuine modelling error - it lets inland demand draw on headroom that in reality
exists to serve Germany and re-export. This is the correct form of the user's concern.

## 4. Are the volumes realistic? Order of magnitude yes, trend wrong
Approximate recent inland consumption: BE ~170-190 TWh/yr, NL ~310-330 TWh/yr (~500 total).

| | model 2030 | vs present |
|---|---:|---|
| BE | 191.3 | ~1.06x |
| NL | 242.8 | ~0.76x |
| total | 434.1 | ~0.87x |

**2030 is credible.** The problem is the **trajectory**: consumption *rises* to 662.1 TWh by
2050 - about **1.3x present-day combined inland demand** - in a scenario that is supposed to
be deeply decarbonised. Every national and EU pathway has NL+BE gas demand falling sharply
by 2050. Specific implausibilities:
- **`gas-boiler` 99.8 TWh in 2050**, up from 0.0 in 2040, while `gas-boiler-existing` goes
  to 0 - the model *rebuilds* fossil boilers in 2050.
- **DAC 81.7 TWh of methane** - burning fossil gas to run direct air capture.
- **`gas-extraction` 103.9 TWh in 2050** - Groningen closed Oct 2023.
- Gas supply is **100% load factor, binding** (see `FINDING_gas_supply_overstated.md` SS2):
  the model would consume still more if permitted.

## 5. Why this matters for CCGT+CC
CCGT+CC alone burns 269.9 TWh in 2050 - 41% of all gas, and more than Belgium's entire
present-day consumption. Its 39.2% electricity share is underwritten by a fuel supply that
is (a) capped by a transit-capable entry capacity, (b) available at 100% LF year-round, and
(c) priced at a *falling* commodity rate (0.0271 -> 0.0215).

## 6. Recommended fixes (revised priority)
1. **Re-base the supply ceiling on inland demand, not terminal send-out.** Either apply an
   `availability_factor` (~0.5-0.6) or set an explicit domestic-consumption budget. This
   directly addresses the transit contamination in SS3b.
2. **Decline `gas-extraction` to ~0 by 2050** (static 2025 value; Groningen closed).
3. **Activate `limited_fossil-CH4`** (2500/1000/500 TWh) - already authored, inert, and
   would cut 2050 by ~25%.
4. **Investigate the 2050 `gas-boiler` rebuild and DAC gas use** - these look like genuine
   model defects independent of the supply cap.
5. Raise with data authors: confirm whether BE 669 GWh/d is LNG-only or includes pipeline
   entry, and whether transit obligations should be netted out.

**Prediction before any such run:** with a 0.55 availability factor and extraction decline,
2050 gas falls below ~400 TWh; CCGT+CC share drops below 39.2%; `gas-boiler` 2050 build
disappears or shrinks; objective rises. If `gas-boiler` persists, it is a cost/catalogue
defect, not a fuel-availability artefact.

## 7. Caveats
- Terminal send-out capacities, bcm conversions (~10.55 TWh/bcm) and inland consumption
  figures in SS3b/SS4 are **from memory, order-of-magnitude only**, and must be checked
  against ALSI/GIE, ENTSOG TYNDP and Eurostat/CBS before external use. **The model-side
  numbers (SS2, SS3a) are computed exactly and do not depend on them.**
- Transit measured via `connection_flow` at foreign CH4 nodes only; weighted by the 3
  representative days (9-day wmap), so annual totals inherit sampling error.
- No cross-border component was modified - measurement only.
