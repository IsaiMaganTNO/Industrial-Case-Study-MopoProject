<!-- filepath: docs/RUN_3day_co2bidir.md -->
# RUN: 3-day, bidirectional CO2 network

**DB:** `checkpoints/Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite`
**Baseline:** `Investment_Results.3day_routeemis.sqlite` (OPTIMAL, obj
**3,390,860**, penalties 0.000000, 85.1 min)
**Patch:** `tools/patch_co2_bidirectional.py`
**Rationale:** `docs/FINDING_co2_network_unidirectional.md`

## 1. What changed

Mirrored all 35 CO2 connections. Verified:

| metric | before | after |
|---|---:|---:|
| CO2 connections | 35 | **70** |
| directed edges | 35 | **70** |
| reverse twins | **0** | **70** |
| `CO2_BEC6` closure | **1** | **17** |
| `CO2_BEC7` closure | 8 | **17** |
| `CO2_BEC6/7` reach injector | **NO** | **YES (all 3)** |
| cross-border guard | 327 / 1522.5048 | **327 / 1522.5048 (unchanged)** |
| `PRAGMA integrity_check` | - | ok |

Tariffs copied unchanged (distance-proportional, distance symmetric).
Only `_CO2_` entities created; **no electricity/cross-border change**.

## 2. PREDICTIONS (registered BEFORE the run)

**P1 - penalties == 0.** Pure structural addition, no demand/capacity change.
Check this FIRST; anything else is meaningless otherwise.

**P2 - objective falls slightly: -0.1% to -1.5%** (3,340,000-3,388,000).
Relaxing a binding structural constraint can only expand the feasible set, so
obj **cannot rise**. If it RISES, the patch is wrong -> abort and inspect.
Magnitude small because the net-zero cap is met today by a cheap marginal
offset (DAC + NSNL031), so new Belgian capture only has to beat that margin.

**P3 - Belgian cement capture appears.** 2050 `CEM2-(Afm)` in BEC6/BEC7
(4,154 t unabated) partly or wholly displaced by `CEM2-(Afm)MEA` /
`LC3-(Afm)Oxy-MEA`. **This is the headline test.**
- P3a strong: BE unabated cement -> < 2,000
- P3b weak: any BE MEA increase at all
- **Falsification: if BE cement does not move, direction was NOT the binding
  constraint** and the S3 economic explanation returns.

**P4 - 2050 net CO2 still == 0.** Cap binds in both runs; unchanged.

**P5 - cement net intensity 2050 improves from 0.1670**, narrowing or
reversing the +15% 2040->2050 worsening. Gross may fall below 0.3536.

**P6 - CO2 flows on at least one new reverse edge > 0**, specifically
BE -> NLC6/NLC8 -> injector. If every new edge carries exactly 0, P3 cannot
hold and the patch had no behavioural effect.

**P7 - DAC capture falls from 92,899.6**, as cheaper Belgian industrial
capture displaces part of the marginal offset. Low confidence - DAC may be
cheap enough to persist.

**P8 - runtime 60-130 min** (+35 vars/constraints is negligible).

## 3. Blind spots of this test (stated up front)

- Mirroring assumes **cost symmetry**. True for distance-proportional tariffs,
  but if the authors intended a compression/one-way-service asymmetry, the
  reverse tariff is wrong. Low risk given `km`.
- **Pipelines remain uncapped** (no capacity parameter on any CO2 link, S4 of
  `FINDING_co2_storage_saturation.md`). So this test CANNOT reveal transport
  bottlenecks; it only removes the direction block.
- Does **not** address NSNL012 idleness (both reservoirs' injectors sit on the
  same `CO2_NLC1/5/6` nodes, so topology was never their constraint).
- 3-day sampling: do not read small deltas as robust.

## 4. OUTCOME

_(to be filled after the solve)_

## 5. Implementation audit (done BEFORE solving)

Audited the patch rather than trusting it. **One real bug found and fixed.**

### BUG FOUND: `parameter_value.type` was NULL

First build wrote the 70 new parameter rows with `type = NULL`, while **all
3,517 pre-existing rows use `type = 'float'`**:

| | baseline | first build | after fix |
|---|---|---|---|
| all flow-cost/ratio rows | `float: 3517` | `float: 3517`, **`NULL: 70`** | **`float: 3587`** |
| CO2-only | `float: 70` | `float: 70`, **`NULL: 70`** | **`float: 140`** |

This is a **silent-ignore** failure mode: the value is present in SQLite, so
every graph/reachability check passes, but the Spine reader may not
materialise it - the links would exist with **no tariff and no flow ratio**.
The reachability "fix" would have looked perfect while the solve behaved
differently from intent. **DB rebuilt from the clean baseline, not stacked.**

The script now self-checks type uniformity, duplicate names and arity, and
exits non-zero on failure.

### FALSE ALARM recorded (so it is not re-investigated)

`PRAGMA foreign_key_check` reports **8,494 violations - in BOTH DBs**. These
are pre-existing (`entity_element.dimension_id` vs `entity.class_id`, an
artefact of how Spine stores multi-dimensional entities) and are **not**
introduced by the patch. My first count of "88 of my rows" was wrong: the
filter `entity_id >= 25000` also caught baseline entities. Correct method is
set-difference of entity ids between the two DBs.

### Verification passed

| check | result |
|---|---|
| entities created | **140** = 35x4 exactly |
| `entity_element` rows | **245** = 35x7 exactly |
| `parameter_value` rows | **70** = 35x2 exactly |
| my rows violating class/dimension | **0** |
| duplicate `(class,name)` | **0** |
| CO2 conns with wrong from/to/nnn arity | **0** of 70 |
| `node__node` orientation mismatches | **0** of 70 |
| structural signature vs forward link | **exact mirror** |
| `entity_alternative` | table is **empty** - no activation needed |
| cross-border guard | **327 / 1522.5048 unchanged** |
| `integrity_check` | ok |
| FK violations vs baseline | **8494 = 8494, unchanged** |

---

## 4. OUTCOME - run completed 2026-10-06 23:30:46

**OPTIMAL**, penalties **0.000000**, **83.2 min**, obj **3,331,603**.
Results: `checkpoints/Investment_Results.3day_co2bidir.sqlite` (127.5 MB).
Cache: `run_logs/co2bidir.pkl`.

### Scorecard: 7 PASS / 1 partial

| # | prediction | result | verdict |
|---|---|---|---|
| P1 | penalties == 0 | 0.000000 | **PASS** |
| P2 | obj falls 0.1-1.5% | 3,390,857 -> **3,331,603** = **-1.747%** | **PASS (dir.)**, slightly beyond band |
| P3 | BE cement capture appears | unabated **4,153.5 -> 0.0** | **PASS (strong, P3a)** |
| P4 | 2050 net CO2 == 0 | 0.0 both runs (2030 453.151, 2040 100.822 identical) | **PASS** |
| P5 | cement net int. improves | 0.1670 -> **-0.6860** | **PASS** |
| P6 | flow on new reverse edges | **7 of 12** active edges are new, **82,374.9** total | **PASS** |
| P7 | DAC falls | 92,899.6 -> **64,117.9** (-31%) | **PASS** |
| P8 | runtime 60-130 min | 83.2 min | **PASS** |

P2 overshot the predicted band (-1.75% vs -1.5% max). Direction was right and
the "cannot rise" guard held. The band was simply too tight - I underestimated
how much a structural infeasibility was costing.

### What actually happened: a route switch, not a retrofit

2050 cement, by region:

| run | BEC6 | BEC7 | NLC5 | NLC6 |
|---|---|---|---|---|
| baseline | `CEM2-(Afm)` 1,160.6 + `LC3-(Afm)Oxy-MEA` 386.9 | `CEM2-(Afm)` 2,992.9 + `LC3` 997.6 | `CEM2-(Afm)MEA` 994.0 | `CEM2-(Afm)MEA` 600.0 |
| **bidir** | **`CEM2-(BMW)Oxy-MEA` 1,547.5** | **`CEM2-(BMW)Oxy-MEA` 3,990.5** | **`CEM2-(BMW)Oxy-MEA` 994.0** | **`CEM2-(BMW)Oxy-MEA` 600.0** |

The whole sector - **including the Dutch plants** - converges on a single route
that **was not used at all** in the baseline. Verified from the model DB, this
route is **BECCS**:

- inputs are **only** `bio_<region>` (1.142) and `elec_<region>` (5.571)
- `atmosphere` coefficient **0.020**, `CO2_<region>` coefficient **0.706**

So cement goes **net-negative: net intensity -0.6860** (gross 142.6, captured
5,035.2). Cement becomes a **carbon sink**, and `CEM2-(BMW)Oxy-MEA` enters the
2050 capture table at 5,035.2.

### Why unlocking Belgian direction changed the DUTCH plants too

This is the non-obvious part and the main caveat. NL already had storage access,
so direction cannot be the cause there. The mechanism is the **system-wide**
net-zero constraint: cheaper Belgian capture lowers the **marginal** cost of the
last abated tonne, which re-prices the whole fleet. Consistent with DAC falling
31% (92,899.6 -> 64,117.9) and `CCGT+CC` rising (36,372.2 -> 48,586.2) - the
offset merit order was reshuffled, not just extended.

### Caveats - do NOT over-read this run

1. **BECCS switch is the dominant effect, not the Belgian pipe.** The headline
   "cement decarbonises" is carried by a biomass route that the baseline never
   picked. Treat P3's magnitude as *route substitution*, not proof that
   direction alone fixes cement.
2. **Biomass availability not verified here.** The `supply` frame returned no
   `bio` carrier rows (grouping produced `{}`), so total biomass draw and
   whether the `biocap365` cap binds is **unchecked**. If bio is effectively
   unlimited, net-negative cement is an artefact. **Open item.**
3. **CO2 pipelines still have no capacity limit**, so Belgian transport is free
   of congestion. Capture looks easier than reality.
4. 3-day sampling - small deltas are not robust.

---

## 5. CO2 FLOWS: before vs after (answers "is BE-NL flow different now?")

**Yes - transformed. BE->NL CO2 export was EXACTLY ZERO in every milestone of
the baseline; it is now the dominant cross-border flow.**

### Cross-border CO2 (ktCO2)

| year | run | **BE -> NL** | NL -> BE | all pipe flow | active edges |
|---|---|---:|---:|---:|---:|
| 2030 | baseline | **0.0** | 0.0 | 3,059.9 | 2 |
| 2030 | bidir | **3,097.6** | 1,530.0 | 7,082.8 | 4 |
| 2040 | baseline | **0.0** | 306.5 | 7,957.3 | 8 |
| 2040 | bidir | **46,553.8** | 2,777.6 | 79,695.2 | 12 |
| 2050 | baseline | **0.0** | 2,999.3 | 21,016.9 | 10 |
| 2050 | bidir | **55,853.9** | 2,810.5 | 92,692.6 | 12 |

Total pipeline throughput **4.4x** in 2050 (21,017 -> 92,693). The baseline's
only cross-border flow was NL->BE, i.e. carbon flowing INTO the cul-de-sac.

### Capture by country, 2050

| run | **Belgium** | Netherlands | total |
|---|---:|---:|---:|
| baseline | **3,672.7** | 161,052.4 | 164,725.1 |
| bidir | **53,043.4** | 104,161.7 | 157,205.0 |

**Belgian capture rises 14.4x.** Belgium goes from 2.2% to **33.7%** of all
capture - roughly its industrial share, which is the sanity check that matters.

### Mass balance - verified, closes exactly

`BE->NL export - (BE captured + NL->BE import + BE other use)`:

| year | BE captured | BE->NL | NL->BE | residual |
|---|---:|---:|---:|---:|
| 2040 | 43,776.1 | 46,553.8 | 2,777.6 | **0.0** |
| 2050 | 53,043.4 | 55,853.9 | 2,810.5 | **0.0** |

Belgium captures and exports **everything**; it stores nothing domestically
(no injector) and consumes none for e-fuels. The carbon is genuinely moving to
Dutch geology, not circulating.

### The corridors that opened (2050, ktCO2)

| connection | baseline | bidir | new? |
|---|---:|---:|---|
| `BEC1_CO2_NLC6` | 0.0 | **42,485.8** | **NEW** |
| `BEC2_CO2_BEC1` | 0.0 | **18,551.2** | **NEW** |
| `NLC7_CO2_NLC6` | 0.0 | 10,264.5 | **NEW** |
| `BEC5_CO2_NLC6` | 0.0 | 9,813.4 | **NEW** |
| `BEC7_CO2_BEC2` | 18.4 | 2,889.6 | existing |
| `BEC6_CO2_BEC5` | 0.0 | 1,102.4 | **NEW** |

This is exactly the Dijkstra path predicted pre-run:
**BEC7 -> BEC2 -> BEC1 -> NLC6**, plus **BEC6 -> BEC5 -> NLC6**. The trunk
route `BEC1_CO2_NLC6` alone carries 42,486 - and it **did not exist** before.
Antwerp (BEC7) is now connected to Dutch storage.

### Caveat

Injection totals barely moved (NSNL031 157,084 -> 156,837) because the net-zero
cap is binding in both runs - **total** stored carbon is set by the cap, not by
access. What changed is **WHERE** capture happens (BE 3,673 -> 53,043) and that
DAC backs off 31%. Belgium displaced more expensive offsets; it did not add
storage on top.
