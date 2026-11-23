# RUN: 3day_gascap - LNG availability 0.50, NL gas extraction 0.0

Model DB: `checkpoints/Final_SpineOpt_Model.tiny.3day.gascap.sqlite`
Baseline: `3day_co2bidir` (OPTIMAL, penalties 0.000000, obj **3,331,603**, 83.2 min)
Patch: `tools/patch_gas_availability.py` (applied on top of all 6 standard patches)

## 1. What changed
26 `availability_factor` rows in alternative `Base`:
17 x `LNG-terminal_*` = **0.50**, 9 x `gas-extraction_*` = **0.00**.

Verified through the Spine reader (not just raw SQL): 26 rows visible, LNG all 0.5,
extraction all 0.0, alternative Base, type float. Cross-border guard
**(327, 1522.5048) unchanged**. Integrity ok. No duplicates.

Supply ceiling: **662.1 -> 279.1 TWh** (BE 122.1 + NL 157.0; extraction 103.9 -> 0.0).

Rationale: 0.50 chosen over 0.55 for explicability to colleagues. Extraction zeroed in
**all** years because the Groningen field is already closed - not a decline trajectory.

## 2. Predictions (registered BEFORE the run)
| # | Prediction | Falsifier |
|---|---|---|
| P1 | Status OPTIMAL, **penalties == 0.000000** | any penalty > 0 => cut is infeasibly tight; relax to 0.65 |
| P2 | Objective **rises** above 3,331,603 | a fall means the patch loosened something - investigate |
| P3 | 2050 methane supply = **279.1 TWh** (mechanical) | anything else => af not applied as understood |
| P4 | `gas-extraction` = **0.0** in every year | non-zero => wrong lever |
| P5 | CCGT+CC 2050 elec share falls below **39.2%** (was 131,102 GWh) | unchanged => cost dominates, not fuel |
| P6 | 2050 `gas-boiler` build (99.8 TWh) shrinks or disappears | persists => independent catalogue/cost defect |
| P7 | DAC methane use (81.7 TWh) falls | - |
| P8 | Total capture + CO2 pipe throughput fall (was 92,693) | - |
| P9 | BE gas 304.0 -> ~122, NL 358.1 -> ~157 | - |

**Most likely surprise:** BE was saturated at 100% in *all three* milestones, so halving it
bites in 2030 too. 2030 gas was 434.1 TWh against a new ceiling of 279.1 - so **2030 is
also forced down ~36%**. If anything triggers penalties it will be 2030, where little
replacement capacity has been built yet. That is the main infeasibility risk.

## 3. Known blind spots of this patch
- Caps **supply**, not demand. It may MASK the 2050 gas-boiler rebuild and DAC-on-gas
  defects rather than reveal them. P6 is deliberately included to detect this.
- 0.50 is a judgement, not derived. The ~40-65% utilisation benchmark is unsourced.
- A flat factor ignores seasonality; real send-out peaks in winter. The 3 sampled days
  (14 May, 10 Sep, 24 Dec) mean winter stress is represented by one day at weight 104.81.
- `limited_fossil-CH4` remains inert and untested (possible 365x long-term-stock issue,
  see `patch_biomass_cap_div365.py`). Not used here deliberately.

## 4. Outcome
_pending_

## 4. OUTCOME (run completed 2026-10-07 17:11)

`Investment_Results.3day_gascap.sqlite` (133.6 MB). **OPTIMAL**, **penalties 0.000000**,
87.1 min (15:44:19 -> 17:11:07). Objective **3,411,250** vs baseline 3,331,603 = **+2.39%**.
Cache `run_logs/gascap.pkl`. Scripts `_gpen.py`, `_gload.py`, `_gs1.py` .. `_gs4.py`.

### Scorecard vs registered predictions

| # | Prediction | Outcome | Verdict |
|---|---|---|---|
| P0 | penalties 0.000000 | 0.000000 | **PASS** |
| P1 | 2050 gas -> ~279 TWh | **279.1** TWh | **PASS (exact)** |
| P1b | gas-extraction 0 in all years | 0.0 / 0.0 / 0.0 | **PASS** |
| P2 | CCGT+CC share < 39.2% | **0.0%** (131,102 -> **0**) | **PASS (overshot)** |
| P3 | gas-boiler 2050 shrinks | 99.8 -> **62.2** TWh | **PASS (partial)** |
| P4 | DAC gas falls | 81.7 -> **48.1** TWh | **PASS** |
| P5 | CO2 pipeline throughput falls | 92,693 -> **39,733** (-57%) | **PASS** |
| P6 | objective rises | 3,331,603 -> 3,411,250 (+2.39%) | **PASS** |

**8 / 8 PASS.** The gas cap was unambiguously binding: supply hit the new ceiling of
279.1 TWh in **every** milestone (flat 2030/2040/2050), so it still binds everywhere.

### 4a. The headline: CCGT+CC collapses to zero and OFFSHORE WIND ENTERS

2050 electricity supply (GWh):

| tech | baseline | share | gascap | share |
|---|---:|---:|---:|---:|
| wind-on | 106,696 | 31.9% | **164,675** | 45.7% |
| **CCGT+CC** | **131,102** | **39.2%** | **0** | **0.0%** |
| solar-PV | 69,375 | 20.7% | 86,370 | 24.0% |
| **wind-off-FB** (4 zones) | **0** | **0.0%** | **88,452** | **24.6%** |
| CCGT-H2 | 21,652 | 6.5% | 2,803 | 0.8% |
| battery discharge (several) | 0 | 0% | ~9,800 | 2.7% |
| TOTAL | 334,484 | | 359,978 | |

Offshore wind fleet 2050: NSNL011 **7.14 GW**, NSNL033 **5.48 GW**, NSBE01 **2.20 GW**,
NSNL012 **2.11 GW** (and 5.20 GW already in **2040**). **Batteries also enter for the first
time.** CCGT+CC capacity goes 15.11 GW -> **0**.

### 4b. This resolves the offshore-wind question from `FINDING_offshore_wind_and_nuclear_absent.md`
That finding concluded offshore was excluded on **capex**, and that better sampling would
"narrow but very likely not close" the gap. **The real gatekeeper was cheap abundant gas.**
Remove it and offshore enters immediately at scale (24.6% of 2050 supply) with sampling
untouched. The capex ranking was correct but was not the binding explanation - a textbook
case of attributing an outcome to the factor I measured rather than the one that bound.
**Nuclear still never builds** (0 in all years), so that half of the finding stands.

### 4c. Where the scarce gas goes: industry outbids power
2050 gas consumption (TWh), independently measured from `unit_flow` (`_gs4.py`) -
**CCGT+CC does not appear at all**:
gas-boiler 62.2, DAC 48.1, REF-SMR 37.8, `(NG)PEA-MEA` 37.4, `(NG)NH3-MVR-DEA` 28.3,
`(NG)DRI-EAF-MEA` 25.5, REF-SMR-MEA 17.5, `(LN)O-MEA` 8.0.
Industrial feedstock/heat uses have no cheap substitute, so they retain the gas while power
generation - which does have substitutes - is displaced entirely.

### 4d. Residual defects NOT fixed by this patch
- **`gas-boiler` still rebuilds in 2050** (62.2 TWh, from 0.0 in 2040, while
  `gas-boiler-existing` retires to 0). Reduced but not eliminated -> **confirms the
  registered falsifier: this is an independent catalogue/cost defect, not a fuel artefact.**
  Worth chasing separately.
- **DAC still burns 48.1 TWh of fossil gas.**
- CO2 pipeline throughput more than halved, which weakens the CCS narrative built on the
  baseline - any CCS conclusions quoted from `RUN_3day_co2bidir` need revisiting.

### 4e. Caveats
- Atmosphere CO2 levels are **identical** in both runs (2030 453.15, 2040 100.82, 2050 0.0)
  - the carbon cap binds in both, so this patch changed **how** the target is met, not
  whether. Do not read the emissions path as an improvement.
- af=0.50 remains a judgement, not a derived value; the ~40-65% real-utilisation benchmark
  still needs ALSI/GIE confirmation.
- Supply is still at 100% LF *of the reduced cap* - the patch rescales the ceiling, it does
  not introduce a realistic hourly send-out profile.
- 3 representative days; wy2009 sampling biases noted in
  `FINDING_offshore_wind_and_nuclear_absent.md` still apply.
