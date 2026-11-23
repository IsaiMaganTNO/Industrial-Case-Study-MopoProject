<!-- filepath: docs/FINDING_vre_buildout_timing.md -->
# FINDING: why onshore VRE barely grows before 2050

**Date:** 2026-10-07 | **Run:** `Investment_Results.3day_co2bidir.sqlite`
**Status:** mechanisms identified; one is a **methodological defect**, the rest
are model logic behaving as specified.

## 1. The observation

Onshore VRE capacity (GW; `capacity_per_unit = 1.0` so fleet units = GW):

| | | 2030 | 2040 | 2050 |
|---|---|---:|---:|---:|
| Solar PV | BE | 11.18 | 10.05 | **15.77** |
| | NL | 33.49 | 32.75 | **35.22** |
| Wind onshore | BE | 2.94 | 2.38 | **6.77** |
| | NL | 14.50 | 13.97 | **20.79** |

Capacity **declines** 2030->2040 everywhere. Vintage split shows why: the 2050
fleet is **100% new-build** appearing in a single step, while existing stock
retires to exactly 0. **Zero new solar PV is built before 2050 in either
country.** Only NL onshore wind builds early (8.10 GW by 2030).

## 2. RULED OUT

- **Potential caps.** `include_onshore_potential_limitations: False`, verified
  empirically: all 34 region-tech caps match source
  `potential_{solar-PV,wind-on}.xlsx` at **ratio 1.0000**
  (BE solar 85.10, NL solar 110.92, BE wind 21.27, NL wind 27.72 GW).
  Utilisation at 2050 is only 19% / 32% / 32% / 75%. **Not binding.**
- **New-build restriction.** No `investment_count_fix_new` on any new VRE unit.
- **Bad capacity factors.** Annual CFs are realistic: solar 0.133, wind 0.375.

## 3. Mechanism A - capex collapse + a 2060 horizon (dominant, by design)

| tech | 2030 | 2041 | 2050 | decline |
|---|---:|---:|---:|---:|
| solar-PV | 888.9 | 523.1 | **269.5** | **-69.7%** |
| wind-on | 2624.0 | 1710.0 | **933.9** | **-64.4%** |
| CCGT+CC | 3113.0 | 2500.7 | 1438.8 | -53.8% |

Solar capex falls **70%**. With `model_end = 2060`, anything built in 2050 runs
10 years inside the horizon against a 40-year economic lifetime, so the model
pays ~1/4 the price for the capacity it actually needs at the end. Waiting is
rational: **build late, build cheap.** This is the intended optimiser response
to the cost curve, not a bug - but it makes the 2030/2040 milestones
**not interpretable as capacity-expansion pathways**.

## 4. Mechanism B - representative-day sampling is biased (DEFECT)

The 3 sampled days (2050) and their realised CFs for `NLC3`:

| block | date | weight | solar CF | wind CF |
|---|---|---:|---:|---:|
| rp_1 | **14 May** | 100.81 | 0.2460 | 0.2333 |
| rp_2 | **10 Sep** | 159.38 | 0.2581 | 0.2293 |
| rp_3 | **24 Dec** | 104.81 | 0.0073 | 0.0827 |

| tech | annual CF | **weighted sampled CF** | bias |
|---|---:|---:|---:|
| solar-PV | 0.1335 | **0.1827** | **+36.9%** |
| wind-on | 0.3753 | **0.1883** | **-49.8%** |

**Solar is overvalued by ~37% and onshore wind undervalued by ~50%.** The
sample has no windy winter day: the highest-weighted day (10 Sep, weight 159)
is a low-wind day, and the only winter day is near-calm for wind *and* dark for
solar. This **systematically distorts the wind-vs-solar trade-off** and is a
genuine methodological problem, independent of mechanism A.

Note the direction: it biases *towards* solar, yet solar still builds nothing
before 2050 - so mechanism A dominates. But any wind/solar **ratio** from a
3-day run must be treated as unreliable.

## 5. What the system does instead: gas-with-capture

Electricity supply (GWh):

| tech | 2030 | 2040 | 2050 |
|---|---:|---:|---:|
| **CCGT+CC** | 5,316 | **126,642 (38.6%)** | **131,102 (39.2%)** |
| wind-on (new) | 40,212 | 41,962 | 106,696 (31.9%) |
| solar-PV (new) | 0 | **0** | 69,375 (20.7%) |
| solar-PV-existing | 53,315 | 51,185 | 0 |
| nuclear-3-existing | 46,232 | 34,793 | 0 |
| CCGT-existing | 52,192 | 0 | 0 |

In 2040 the retiring fleet is replaced **almost entirely by CCGT+CC**, not by
renewables. Gas-with-capture is the cheapest way to satisfy the CO2 cap while
VRE capex is still falling. Combined with S4, the 2040 milestone is the least
trustworthy of the three.

## 6. Assessment

- The **declining 2030->2040 capacity is real model logic**, not a data error.
- The **2050 jump is a horizon/capex artefact**, not a forecast.
- **Do not present 2030/2040 VRE capacity as a projected build-out.**
- The **sampling bias (S4) is a defect worth fixing** regardless.

## 7. NOT yet tested

- Whether a 7-day or wind-inclusive sample changes the wind/solar split.
- Whether extending `model_end` beyond 2060 pulls build-out earlier.
- Whether offshore wind (excluded here; it is not "onshore") behaves the same.
- No myopic/perfect-foresight comparison was run - this is a perfect-foresight
  result and that assumption drives the "wait for cheap capex" behaviour.
