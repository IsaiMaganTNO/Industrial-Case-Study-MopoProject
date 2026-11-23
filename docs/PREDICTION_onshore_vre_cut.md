# PREDICTION: onshore VRE potential reduction (0.15) on top of gascap

Registered **before** any run. Scripts: `run_logs/_vp1.py`, `_vp2.py`, `_vp3.py`.
Baseline for comparison: `3day_gascap` (OPTIMAL, penalties 0, obj 3,411,250).

## 1. What the change is
`scenario_config.yml` `renewable_potentials.onshore_potentials: 0.15` with
`include_onshore_potential_limitations: True`. Multiplies
`investment_count_total_max_cumulative` on `wind-on_*` / `solar-PV_*` investment groups by
**0.15**, floored at `max_capacity_history[tech][polygon]`.

**KNOWN LATENT BUG (from `FINDING_vre_buildout_timing.md`):** `max_capacity_history` is keyed
**per country** (BE 3.6, NL 7.2 for wind-on) but the function looks up **per polygon**
(`BEC1`, `NLC3`, ...). It will **KeyError** on IC1 region names. The function cannot be
enabled as-is; a patch must either supply per-region history or bypass the floor.
**This must be resolved before the run - it is not a "just flip the flag" change.**

## 2. The caps are currently BINDING - this is the decisive fact
Measured on the gascap run (`_vp1.py`), 2050 fleet vs cap:

| group | cap now (GW) | x0.15 | 2050 used | binds? |
|---|---:|---:|---:|---|
| wind-on BE | 21.27 | 3.19 | **21.27** | **YES - at cap** |
| wind-on NL | 27.72 | 4.16 | **27.72** | **YES - at cap** |
| solar-PV BE | 85.10 | 12.77 | 38.29 | **YES** (38.29 > 12.77) |
| solar-PV NL | 110.92 | 16.64 | 31.46 | **YES** (31.46 > 16.64) |

**Onshore wind is already pinned exactly at its cap in both countries.** In the earlier
`co2bidir` baseline these caps were slack (utilisation 19-75%), which is why
`FINDING_vre_buildout_timing.md` concluded "not binding". **That conclusion is now stale -
removing the cheap gas made onshore wind hit its ceiling.** Any prediction reusing the old
"not binding" framing would be wrong.

## 3. Magnitude of the cut
2050 generation at the observed CFs (wind-on 0.384, solar 0.141):

| | now | at 0.15 | lost |
|---|---:|---:|---:|
| wind-on | 164,675 | 24,724 | -139,951 |
| solar-PV | 86,370 | 36,314 | -50,056 |
| **total** | **251,045** | **61,038** | **-190,007 GWh** |

That is **52.8% of total 2050 electricity supply (359,978 GWh)** removed from the cheapest
sources. This is a far more severe intervention than the gas cap.

## 4. Predictions
1. **Offshore wind explodes.** Headroom is **107.63 GW** (124.56 cap vs 16.93 used); at
   CF 0.50 that is ~471,403 GWh, comfortably more than the 190,007 GWh hole. Offshore is
   the obvious substitute and is already economic in the gascap solution.
   **wind-off-FB 2050 rises well above 16.93 GW; wind-off-FO (so far never built) likely
   enters** as FB zone caps saturate.
2. **CCGT+CC does NOT return** - it is gas-limited, not capacity-limited, and gas is
   already fully allocated to industry. Expect it to stay at/near 0.
3. **Nuclear becomes a genuine candidate for the first time.** It is the only *unconstrained
   firm* option left (no active cap). It has never been built in any run; this is the
   scenario most likely to change that. **I rate it under 50% - 2050 capex 6,948 vs
   offshore-FB 1,920 is still a 3.6x gap - but it is the run where it could happen.**
4. **Batteries increase** (15,250 GWh now) as the mix becomes more offshore-weighted.
5. **Objective rises materially**, more than the gas cap's +2.39%, plausibly +5-10%.
6. **Penalties: elevated risk of becoming non-zero.** Two binding constraints now stack
   (gas + VRE). **If penalties > 0 the result is not interpretable** and the cut must be
   relaxed (try 0.30-0.50 rather than 0.15).
7. **Industry:** gas is unchanged at 279.1 TWh, so ammonia/olefins/steel stay on gas.
   But **electricity gets scarcer and dearer**, so I expect the *electrification* trend seen
   in gascap to partially reverse - glass may move back off electricity toward hydrogen, and
   the cement BECCS/`CEM2-(Afm)MEA` split may shift again.
8. **CO2 capture may RISE slightly** if any fossil generation returns, but net CO2 totals
   will stay identical (165,400 / 36,800 / 0) because the carbon cap binds in all runs.

## 5. Falsifiers
- If offshore wind does **not** rise substantially, my reading of the offshore headroom or
  its economics is wrong.
- If CCGT+CC returns, then gas was **not** as fully committed to industry as SS4.2 assumes.
- If the objective moves less than the gas cap did (+2.39%), then the onshore caps were not
  as binding as SS2 indicates and I have misread the investment-group semantics.

## 6. Caveat on whether this test is even advisable
0.15 is an aggressive, Europe-wide default that was **never calibrated for IC1**. Combined
with a gas cap it stacks two severe restrictions, and the most likely outcome is an
infeasible-ish or penalty-laden solve that tells us little. **I would suggest running
0.50 first** to see the direction with a reasonable chance of a clean, interpretable
solution, then 0.15 only if 0.50 is clean. Also note the per-country/per-polygon KeyError in
SS1 must be fixed regardless.
