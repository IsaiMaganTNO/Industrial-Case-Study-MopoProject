# RUN 3day_vre15 - onshore VRE potential cut to 15% / historical floor

Model DB: `checkpoints/Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite`
Results : `checkpoints/Investment_Results.3day_vre15.sqlite` (127.3 MB)
Cache   : `run_logs/vre15.pkl`   Log: `run_logs/3day_vre15_solve`
Patch   : `tools/patch_onshore_vre_potential.py` (34 rows, on top of gascap)

## Status

**OPTIMAL. `penalties == 0.000000`** (checked first, per standing practice).
Objective **3,510,170** vs gascap 3,411,250 = **+2.90%**; vs co2bidir 3,331,603 = +5.36%.
Runtime ~88 min (17:50:37 -> 19:18:37). RAM 22.8 -> 39.9 GB.

Objective split: fixed_om 2,018,882; unit_investment 1,289,512; taxes 176,151;
variable_om 15,227; storage_investment 4,369; connection_investment 3,392;
connection_flow 2,635; **fuel_costs 0**; **penalties 0**.

## Scoring against `docs/PREDICTION_onshore_vre_cut.md`

| # | Prediction | Outcome |
|---|---|---|
| 1 | Onshore caps become **binding** (pinned exactly at cap) | **PASS, exactly.** 2050 wind-on BE 3.6000/3.6000 = ratio 1.00000; NL 7.2000/7.2000 = 1.00000. Solar BE 12.7652/12.766 = 0.99994; NL 33.5000/33.5000 = 1.00000. All four at the cap. The old "onshore not binding" finding is now formally stale. |
| 2 | Offshore absorbs the gap (107.63 GW headroom) | **PASS.** Offshore 2050 rises 88,453 -> 193,376 GWh (+104,923, +119%). Two new sites activate: `NSNL031` 0 -> 50,130 and floating `NSBE01` 0 -> 13,339, `NSNL033` 0 -> 2,579. |
| 3 | CCGT+CC stays 0 | **PASS.** Still 0; `fuel_costs` 0. |
| 4 | Objective rises > +2.39% | **PASS**, +2.90%. |
| 5 | Nuclear plausible but rated **< 50%** | **FAIL (prediction wrong, in the informative direction).** `nuclear-3` enters at 51,382 GWh in 2050 -- now the **third-largest** source. See below. |
| 6 | Penalty risk elevated | **PASS (no penalty).** Feasible with room to spare. |

Net: 5 of 6 predictions correct; the miss is the interesting one.

## 2050 electricity mix, gascap -> vre15 (GWh)

| tech | gascap | vre15 | delta |
|---|---|---|---|
| wind-on-SP277-HH100 | 164,675 | 37,327 | **-127,348** |
| solar-PV-no-tracking | 86,370 | 54,052 | -32,318 |
| offshore wind (all sites) | 88,453 | 193,376 | **+104,923** |
| **nuclear-3** | **0** | **51,382** | **+51,382** |
| CCGT-H2 | 2,803 | 2,229 | -574 |
| batteries (all) | 15,250 | 7,173 | -8,077 |
| **TOTAL** | **359,978** | **347,684** | -12,294 |

Onshore+solar lose 159,666 GWh; offshore+nuclear supply 156,305 of it. Total
demand served falls 3.4%, i.e. a little demand-side response absorbs the rest.

## The nuclear result is the headline, and it corroborates `verification/`

I rated nuclear < 50% likely and was wrong. What makes it notable is *where* it
lands. Build is **BE-only**, across BEC1-BEC7, and **zero in NL**:

- BE: 0 (2030) -> **2.545 GW** (2040) -> **5.866 GW** (2050)
- NL: 0 / 0 / 0

`docs/VERIFICATION_external_assumptions.md` records the external sheet expecting
**BE 0 / 6 / 6 GW** and NL 0 / 4 / 5 GW. The model has only a single pan-EU
120/150/180 cap sitting in an **inert** alternative, so this buildout is *not*
being forced by any floor -- it is **endogenous**. Landing at BE 5.87 GW against
an independently-stated expectation of BE 6 GW, in a run where nothing about
nuclear was touched, is strong corroboration of the cap-vs-floor reading: the
economics alone reproduce the Belgian figure once onshore land is constrained.

The NL 0 vs expected 4-5 GW gap is the live discrepancy. Caution: this is a
single sensitivity, and I have not checked whether a BE-specific cost, a
`max_capacity_history` term, or regional availability differs between BE and NL.
**Do not report the BE match as validation until that asymmetry is explained** --
a coincidence at 5.87 vs 6 is entirely possible.

> **RESOLVED -- see `docs/FINDING_nuclear_BE_vs_NL_asymmetry.md`.** It *is* a
> coincidence. All 17 `nuclear-3` units are parameter-identical (one distinct
> value for cost, FOM, lifetime, discount rate; cap 1000 = non-binding;
> `investment_count_fix_new` NaN after 2030, so nothing is forced). The driver is
> **offshore seabed scarcity**: BE has **one** offshore zone (NSBE01, cap 5.235 GW,
> built to **100%**) while NL has **five** and still has ~17.9 GW unused in 2050.
> Once the onshore patch pinned BE at its land caps, nuclear was simply the
> cheapest firm option Belgium had left. **The BE ~6 GW figure must not be
> presented as the model reproducing the Belgian nuclear plan.**

## Reading

The chain across three runs is now coherent and each step was forced by the
previous one:

1. Gas at 100% load factor -> CCGT+CC dominates, offshore and nuclear both absent.
2. Cap gas (af=0.50) -> CCGT+CC collapses to 0; onshore wind + solar take over at
   165 + 86 TWh, which implied onshore land use far beyond anything credible.
3. Cap onshore land -> offshore doubles and nuclear enters.

Step 3 is the first run in which the 2050 mix is not obviously unphysical on its
face. The earlier "offshore excluded on capex" claim is now doubly superseded:
offshore was gated first by cheap gas, then by unconstrained onshore land.

## Caveats

- Batteries **fall** 15,250 -> 7,173 and relocate from BE to NL. Not predicted,
  not yet explained. Plausibly nuclear baseload displacing arbitrage value, but
  that is a hypothesis, not a measurement.
- Still 3 representative days. The offshore/nuclear split is exactly the kind of
  result that is sensitive to temporal resolution; 3 days cannot resolve the
  low-wind periods that justify firm capacity. **Treat the 51 TWh nuclear figure
  as indicative only.**
- The onshore caps implemented are "historical floor" in 3 of 4 cases, not
  "15% of potential" -- see `tools/patch_onshore_vre_potential.py`. If the
  authors meant something looser, this run is too tight.
- 2030 `SCPC-existing` coal artefact and the 2050 `gas-boiler` rebuild are
  untouched by this patch and remain open.

## Next

Highest value remains **adopting the IC1 fossil-CH4 trajectory**
(1,102.3 / 440.9 / 220.5 TWh) in place of the flat af=0.50, which is ~4x too
strict in 2030 and ~27% too loose in 2050 and is the prime suspect for the 2030
coal artefact.
