# FINDING: Why no offshore wind and no nuclear in 2050

Run: `3day_co2bidir` (OPTIMAL, penalties 0). Source DB
`checkpoints/Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite`.
Scripts: `run_logs/_off.py`, `_off2.py`, `_offcf.py`, `_lcoe.py`, `_grp.py`, `_nsconn.py`.

## 0. Correction to earlier note
The earlier lookup `wind-off-FO-SP316-HH155_NSNL031` returned no `unit_investment_cost`
because **the unit does not exist**. Real naming is `SP370-HH155`. There are 15 offshore
units: `wind-off-{FB,FO}-SP370-HH155_{NSBE01,NSNL011,NSNL012,NSNL031,NSNL032,NSNL033}`
plus 3 `wind-off-FB-existing_*`. Costs are present and normal.

## 1. Structural availability - NOT the cause
- Investment groups exist with non-zero caps in `Base`:
  FB 5.235/9.8048/6.1267/17.4689/3.6596/5.8237, FO 5.235/9.8048/28.5913/17.4689/9.5149/5.8237
  (~68 GW floating-bottom + ~76 GW floating-offshore headroom).
- Grid connection exists: offshore units feed onshore elec nodes **directly** via
  `unit__to_node` (e.g. `wind-off-FB-SP370-HH155_NSBE01__elec_BEC8`). There are **zero**
  `connection__from_node`/`connection__to_node` rows mentioning NS zones - this is by
  design, not a missing link. (Blind spot checked explicitly: absence of a `connection`
  does NOT mean islanded here.)
- Nuclear: 17 `nuclear-3_*` candidates + 5 `nuclear-3-existing_*`. The only cap is
  `investment_count_total_max_cumulative` = 120 under alternative `limited_nuclear-3`,
  which is **not active**. So nuclear is formally unconstrained.

Result: both are free to build and build **nothing**. Existing stock only:
nuclear-3-existing 5.285 (2030) -> 3.9725 (2040) -> **0 (2050)**;
wind-off-FB-existing 7.600 (2030) -> 7.050 (2040) -> **0 (2050)**.

## 2. Cause A - capex ranking (dominant)
`unit_investment_cost` trajectories (2030 / 2041 / 2050):

| tech | 2030 | 2041 | 2050 |
|---|---:|---:|---:|
| nuclear-3 | 16594.7 | 11865.2 | 6948.2 |
| wind-off-FO | 10647.8 | 5710.9 | 2855.1 |
| wind-off-FB | 5734.7 | 3596.4 | 1920.5 |
| CCGT+CC | 3113.0 | 2500.7 | 1438.8 |
| wind-on | 2624.0 | 1710.0 | 933.9 |
| solar-PV | 888.9 | 523.1 | 269.5 |

Crude annuitised capex-only LCOE at 2050 costs, r=0.05, at **annual** CF:
CCGT+CC 11.9, solar 12.6, wind-on 19.4, wind-off-FB 27.4, wind-off-FO 40.7,
nuclear 46.6 (EUR/MWh-equivalent, model units).
Offshore is 2.3x onshore and nuclear 3.9x even before the sampling penalty, while
CCGT+CC - which also earns the CO2 network/capture credit - sits at the bottom.
**Nuclear is never within reach of the margin; its absence is a pure cost-input story,
not a bug.**

## 3. Cause B - representative-day sampling penalises offshore hardest (DEFECT)
Same three sampled days as before (14 May w=100.81, 10 Sep w=159.38, 24 Dec w=104.81,
no windy winter day). Weighted-sampled vs annual capacity factor:

| tech | annual CF | sampled CF | bias |
|---|---:|---:|---:|
| wind-off-FO/FB NSNL031 | 0.5209 | 0.3378 | **-35.2%** |
| wind-on NLC3 | 0.3584 | 0.2691 | -24.9% |
| solar-PV NLC3 | 0.1422 | 0.1608 | **+13.1%** |

Effect on LCOE: offshore **+54.2%**, onshore +33.2%, solar **-11.6%**, thermal 0%.
So the sampling error is not neutral - it is ordered exactly against the technologies
that are missing, and in favour of solar and firm thermal.

## 4. Answer to the user's two questions
1. *Is offshore uncompetitive for the same sampling reason?* **Partly.** Sampling inflates
   offshore LCOE by ~54%, the largest penalty of any technology. But even with the
   unbiased annual CF, offshore-FB (27.4) is still ~2.3x CCGT+CC (11.9) and ~1.4x
   onshore (19.4). Better sampling would **narrow but very likely not close** the gap at
   these capex assumptions. The honest statement is: sampling is a real defect that
   biases against offshore, and it compounds a cost assumption that already excludes it.
2. *Why no nuclear?* Cost only. 2050 capex 6948.2 vs CCGT+CC 1438.8 (4.8x), FOM 0.0102 vs
   0.0044 (2.3x), and nuclear gets no sampling penalty, so it loses on the merits of the
   input data. The `limited_nuclear-3` cap is irrelevant - it is not even active.
   Models that do build nuclear typically impose policy floors
   (`investment_count_fix_new` / minimum capacity), which this model does not have.

## 5. Caveats / blind spots of this analysis
- The LCOE in SS2 is **capex-annuity only**: no fuel, no CO2 price, no FOM/VOM, no
  curtailment, no system-value (firmness, network relief). It ranks technologies, it does
  not predict dispatch. CCGT+CC in particular pays fuel and residual CO2 that this metric
  omits, so its true cost is higher than 11.9 - the offshore gap is smaller than shown,
  which is exactly why question 1 is answered "partly" and not "no".
- CF bias computed for NSNL031 / NLC3 only; not verified region-by-region.
- Discount rate 0.05 assumed flat; wind carries a tech-specific 0.055 which would worsen
  wind slightly.

## 6. Recommended test (not yet run)
Re-sample with a wind-inclusive day set (add a high-wind winter day, e.g. a day with
offshore CF > 0.75) and re-solve. Prediction to register before running: offshore still
does not enter in 2050, onshore wind increases relative to solar, and solar 2050 capacity
falls. If offshore *does* enter, the sampling defect is more severe than estimated here.

---

# CORRECTION (2026-10-07) - the sampling-bias section above is WRONG

## What was wrong
Section 3 reported offshore CF bias of **-35.2%** and concluded sampling penalises
offshore hardest. That used weather year **`wy2008`**. The active scenario
`baseline_blended_representative_periods` has rank-2 alternative **`wy2009`**, not
`wy2008`. (`run_logs/_alt.py`.) The helper `_offcf.py` also queried
`availability_factor` with **no alternative filter**, so it silently took whichever row
SQLite returned first - a second, independent defect in the method.

## Corrected numbers (`run_logs/_cfwy.py`, both years shown)

| tech | wy2008 bias | **wy2009 bias (ACTIVE)** |
|---|---:|---:|
| wind-off-FO NSNL031 | -11.5% | **+21.5%** |
| wind-on NLC3 | -49.8% | **+10.4%** |
| solar-PV NLC3 | +36.9% | **+7.6%** |

Under the weather year the model actually solves, the 3-day sample **over**-states
offshore wind by +21.5% and onshore by +10.4%. Sampling **favours** wind, most of all
offshore.

## Consequence
The conclusion inverts. Offshore wind is not excluded *despite* a sampling handicap - it
is excluded **even though sampling flatters it by ~21%**. Correcting the sampling would
make offshore look *worse*, not better. The answer to "would better sampling make
offshore compete with CCGT+CC" is therefore **no - it would widen the gap**.
The capex argument (Section 2) is unaffected and remains the sole explanation, and the
nuclear conclusion is unaffected (nuclear has no CF sampling exposure at all).

This is a 6th instance of the recurring pattern: a query was run without characterising
its blind spot - here, *which alternative the parameter was read from*.
Mitigation added: **always filter `availability_factor` by the scenario-active
alternative, and assert the alternative name in output.**

## UPDATE 2026-10-07: offshore conclusion superseded by `RUN_3day_gascap.md`

The run `3day_gascap` (LNG availability_factor 0.50, gas-extraction 0) caused offshore wind
to **enter immediately at scale**: 2050 fleet NSNL011 7.14 GW, NSNL033 5.48 GW, NSBE01
2.20 GW, NSNL012 2.11 GW, supplying 88,452 GWh = **24.6%** of 2050 electricity, with
**sampling unchanged**. CCGT+CC fell 131,102 -> **0**.

**The capex analysis in SS2 was correct but was NOT the binding explanation.** Offshore was
held out by **cheap, abundant, 100%-load-factor natural gas**, not primarily by its own
capex. SS4's answer to "would better sampling make offshore compete" ("partly - the gap
would narrow but likely not close") is therefore **superseded**: the gap closes completely
once the gas supply is made realistic, with no sampling change at all.

This is another instance of the recurring blind-spot pattern - attributing an outcome to the
factor I had measured (capex, CF bias) rather than testing the factor that actually bound
(fuel availability). The **nuclear** conclusion is unaffected: nuclear still builds 0 GW in
every year of the gascap run.
