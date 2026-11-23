# ASSESSMENT: what would disabling DAC do? (prediction, pre-run)

**Date:** 2026-10-06 | **Baseline:** `Investment_Results.3day_routeemis.sqlite`
**Status:** PREDICTION registered BEFORE any run. Not yet tested.

## 0. FIRST, A CORRECTION I MUST MAKE

I previously told the user **"DAC is 0.0 in both runs"** and used that to argue
the DAC-vs-injection split was sampling-dependent. **That was WRONG.**

The error: I looked for DAC in the `emis` frame, where it correctly appears as
**0.0** - because DAC does not emit, it **captures**. Its activity lives in
`co2net` with `role='captured'`, which I did not check.

Actual DAC activity:

| year | DAC captured |
|---|---|
| 2030 | 0.0 |
| 2040 | **92,899.6** |
| 2050 | **92,899.6** |

**DAC is the single largest capture technology in the system.**

| 2050 capture | t | share |
|---|---|---|
| **DAC** | **92,900** | **56.4%** |
| CCGT+CC | 36,372 | 22.1% |
| (LN)O-MEA | 8,931 | 5.4% |
| SMR+CC | 8,208 | 5.0% |
| all industrial MEA/CC combined | ~18,300 | ~11% |

This is the **same class of error** as the "CCGT books no carbon" claim: reading
a single frame without checking whether the quantity is represented elsewhere.
`FINDING_co2_storage_saturation.md` S8 must be corrected accordingly.

## 1. Is DAC free to be built? YES - it is a genuine economic choice

- `investment_count_max_cumulative` = **1000.0** (uncapped)
- `investment_count_fix_new` exists but is **only `{2030: 0.0}`** - the standard
  "not investable by 2030" rule, **not** a forced build level
- fleet: 0 -> **10.605** -> **10.605** units, all in **NLC5 only**

So the 10.605 units are chosen, not imposed.

## 2. Why DAC wins

2050 capex: DAC **2,993.3** vs CCGT+CC 1,438.8 vs CEM2-(Afm)MEA 2,959.3.
DAC capex collapses 10,941.7 -> 6,046.1 -> **2,993.3**.

DAC consumes per unit CO2 captured: **0.785 CH4** + **4.923 elec**.

The decisive asymmetry (per `FINDING_upstream_carbon_gate.md`): DAC's CH4 is
charged **upstream at the gate**, and its electricity comes from a grid that is
itself largely CCGT+CC - whose carbon is **also** captured. So DAC is buying
inputs whose carbon is already handled, and selling a **credited** CO2 output.

## 3. PREDICTION if DAC is made non-investable

### 3a. The constraint is a SYSTEM-WIDE net-zero scalar

2050 net CO2 = **0.0 exactly** (`atm` level 0.000000, binding). Removing DAC
does **not** remove the obligation - it removes the cheapest way to meet it.
**92,900 t of offset must be replaced.**

### 3b. What I expect to happen - ranked

1. **More CCGT+CC.** Already 22.1% of capture and the cheapest capture per unit
   capex. Most likely absorbs the bulk. **This is the opposite of "more
   realistic"** - it would deepen gas dependence.
2. **Industrial CCS finally moves.** `CEM2-(Afm)MEA` is flat at **1,594** with a
   cap of 1000.0 units (non-binding, currently 0.182 units). With DAC gone the
   marginal offset price rises, which is exactly the condition
   `RUN_3day_routeemis.md` prediction 5 said would move cement. **This is the
   most scientifically interesting outcome.**
3. **Objective rises.** DAC is being chosen over alternatives, so removing it
   must cost money. Expect **+1% to +5%**.
4. **Possibly less total gas burn**, if the system abates rather than offsets.

### 3c. Would we see offshore wind? PROBABLY NOT - and here is why

| | 2050 capex | 2050 fleet |
|---|---|---|
| `wind-on-SP277-HH100` | **2,624 -> 933.9** | **38.73 units** |
| `wind-off-FB-SP370-HH155` | **5,734 -> ...** | **0.22 units** |

Offshore is **~2.2x** onshore capex at 2030 and both are **uncapped at 1000.0**.
Offshore loses on cost, not on availability.

**DAC's electricity demand is tiny**: 92,899.6 x 4.923 = **~457 GWh**, against
total 2050 supply of **344,193 GWh** - i.e. **0.13%**. Removing DAC removes
0.13% of electricity demand. That is **far too small to change the wind
merit order.**

**So: disabling DAC will NOT meaningfully produce offshore wind.** If offshore
wind is the goal, the binding issue is its **capex ratio vs onshore**, plus the
absence of any onshore siting/land constraint - 38.73 units of onshore wind in
NL+BE is already questionable on land-use grounds and is the more likely
modelling gap.

## 4. Would results be "more realistic"? MIXED - and worth stating honestly

**More realistic:** DAC at 56% of all capture by 2040 is aggressive versus most
published pathways. Suppressing it would force the industrial abatement the
study actually cares about.

**Less realistic:** the likely substitute is **more gas+CCS**, not renewables.
The run may simply shift the same fossil dependence into a different unit.

**Recommended framing:** run it as a **sensitivity / bounding case**, not as a
"more correct" baseline. Its value is revealing *how much the net-zero result
depends on DAC*, which is a legitimate and interesting question for colleagues.

## 5. Falsification

If DAC is disabled and **cement still does not move**, then the "cheap marginal
offset" explanation in `FINDING_co2_storage_saturation.md` S7 is **wrong** and
something else blocks industrial CCS. That makes this a genuinely decisive test,
independent of whether the result looks more realistic.
