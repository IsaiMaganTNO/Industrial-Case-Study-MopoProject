# RUN: 7-day rebuild (clustering option B)

Input: `checkpoints/Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.sqlite`
Reference: 3-day `hcco2` (OPTIMAL, objective 3,376,630, penalties 0.00)
Date: 2026-10-04

## Build

Pipeline steps 16-20 re-run from the intact `SpineOpt_target`:
`merge_spineopt` -> `clustering_input` -> `run_clustering` -> `clustering_output`
-> `scenario_setup`. Seed file renamed to `.disabled3day` so the **unseeded**
convex-hull branch ran with `number_of_representatives = 7`.

Days chosen by clustering (wy2009): **12 Jan, 18 Feb, 19 Aug, 23 Aug, 17 Sep,
5 Nov, 13 Dec**. Weights 45.629 / 71.269 / 48.376 / 41.647 / 27.596 / 75.383 /
55.100, **sum exactly 365.000** per milestone year.

Note this is NOT a superset of the 3-day run (14 May / 10 Sep / 24 Dec); only
19 Aug is near a previous pick. Comparisons are therefore between two different
samplings, not nested refinements.

Patch chain, all re-derived on the fresh build:
1. `patch_biomass_cap_div365.py` - 204 rows (identical count to 3-day)
2. `screen_retirement.py` -> **225 RETIRE-SAFE**, 7 BLOCKED sole producer
3. `patch_retire_industry.py --tier both` - 225 units (priced=50, scaffold=175)
4. `patch_hc_co2.py` - 61 units at 0.24 t/MWh (identical set to 3-day)

### Why 225 and not 199

The 3-day chain had `patch_group1_retirement.py` applied upstream, so its 26
units ((NG)PE 12, (NG)PEA 12, BF-BOF 2) reported as ALREADY RETIRING. This build
is fresh, so they screen as RETIRE-SAFE: **199 + 26 = 225**. Same final target
set, reached in one step instead of two.

### Tooling defect found and fixed

`patch_retire_industry.py` hardcoded `run_logs/retire_screen.csv`, so the first
attempt silently applied the **stale 3-day screen** (199 units) to the 7-day DB.
Added a `--screen` argument and re-applied from a clean copy. Without this the
26 group1 units would have been left unpatched.

## Verification (all passed)

- 21 representative blocks (7 x 3 years); weights sum to 365.000000 in each year
- 504 representative timesteps (7 x 24 x 3); operations blocks coarsened to 365D
- 61 HC-CO2 rows, all `typeof=blob`, value `0.24`; no unit double-booked
- exactly **225** rows changed type, all screened RETIRE-SAFE, all
  `float -> time_series`; 0 screened units missed
- `Scraps_EAF_BEC3/BEC5`, `Diaphragm_BEC1` still `float` (sole-producer guards)
- cross-border electricity initial sum **26.060** - trade untouched, as instructed
- the 532 total `time_series` rows are **identical in the 3-day DB**; the extra
  307 are pre-existing (H2 connections, CCGT-existing, salt caverns), not patch
  artefacts. An earlier assertion of "225 total" was my error, not a defect.

## Predictions (registered BEFORE the solve)

1. `objective_objective_penalties == 0.00`. **Check first.**
2. Objective differs from 3,376,630 by **< 10%**. Different days change the
   sampled weather, so an exact match is not expected and not required.
3. **Batteries stay at or near zero.** Each representative period is still an
   independent 24 h block with `cyclic_condition = true`, so there is still no
   inter-day arbitrage. 7 samples instead of 3 does not create seasonal storage
   value. *If batteries appear in quantity, my time-representation explanation
   is WRONG and must be retracted.*
4. `oil-eng` stays at **0.0** in 2050 - the HC patch is day-independent.
5. All three VRE families present in 2050. Shares will move (the 7 days include
   two August days and no May day), but the qualitative picture should hold.
6. Net CO2 still hits the cap exactly (165,400 / 36,800 / ~0).
7. Solve time **3-4 h**, peak RAM **80-110 GB** (3-day: 83 min, 44.9 GB).

## Falsification

If batteries appear with meaningful capacity, prediction 3 fails and the
"daily cyclicity blocks storage" explanation in `FINDING_hc_co2_unpriced.md` S7
and in the share README must be corrected.

---

## ABORTED RUN + CO2 cap defect (2026-10-04 22:04)

The first 7-day solve (PID 8828, launched 21:50:42) was **killed 12 min in**,
during `variable_connection_flow` construction and therefore **before any
optimisation**. No result was lost.

### Defect

The 7-day DB carried the **raw annual** CO2 budget, not the /365 form:

| DB | cap 2030 | cap 2041 | 2050 |
|---|---|---|---|
| 3-day (solved, correct) | **0.45315068** | 0.10082192 | 0.0 |
| 7-day (as built) | **165.4** | 36.8 | 0.0 |

165.4 / 365 = 0.45315068 exactly. The budget was **365x too loose** in 2030 and
2041. Because the 2050 cap is 0.0 in both, the run would **not** have looked
obviously broken - it would have silently reproduced the historical
"unabated fossil displaces biomass/CCS" artefact described in
`FINDING_fuel_based_emissions.md` S5.

### Why the fresh build did not fix it natively

A prior working assumption held that `patch_co2_caps.py` was superseded because
the real fix was "restoring 365 daily entries in `representative_blocks_by_period`,
which the fresh pipeline build should do natively". **This is false.** Measured:

| DB | `representative_blocks_by_period` inner entries |
|---|---|
| 3-day | 9 (3 reps x 3 milestones) |
| 7-day | 21 (7 reps x 3 milestones) |

Both store **one entry per representative block, not 365 daily entries**. The
`make_tiny_model.py` collapse is still in force in the fresh build, so nothing
compensates for an annual-scale cap. The /365 division remains **required**.

Provenance confirms it: 165.4 is the *pipeline default*, present in
`SpineOpt_target.pre-clustering`, `pre-clustering`, `post-scenario-setup` and
every `7day.*` DB. 0.45315 appears only in DBs descended from the manual
`co2rebuild` patch. The 7-day chain was rebuilt from `SpineOpt_target`, which is
precisely why it never inherited the correction.

### The 365 factor, verified from results (not inferred)

`node_state_longterm` for `atmosphere` in `Investment_Results.3day_hcco2.sqlite`:

| timestamp | state | x365 |
|---|---|---|
| 2030 | 453.1507 | **165,400.0** |
| 2041 | 100.8219 | **36,800.0** |
| 2050 | 0.0 | 0.0 |

453.1507 = 0.45315068 x 1000 (`storage_state_max`), and x365 reproduces the
reported headline exactly. Earlier I flagged that the "coefficients sum to
1.000000" evidence in `RUN_3day_group1_biocap365.md` S3 was not reproducible -
`representative_block_coefficient` has **0 rows** in both DBs. That caveat is now
**resolved by this direct measurement**, which does not depend on that parameter.

### Fix

New `tools/patch_co2_cap_div365.py` (positional SRC DST, `--dry-run`). Divides
the `atmosphere` cap by 365; aborts if a value already looks divided.

Verification: full `parameter_value` diff across **35,875 rows** shows **exactly
1 changed row** (`atmosphere` / `storage_investment_count_max_cumulative`),
blob -> blob, no rows added or removed. Readback asserts 165.4/365 and 36.8/365.
Connection `investment_count_initial_cumulative`: 327 rows, sum **1522.505**,
byte-identical before and after - **electricity trade untouched**, as instructed.

> **Guard defect caught during this patch:** the first version of the
> cross-border guard queried a non-existent parameter
> (`connection_investment_count_initial`) and returned **0.000**, so it asserted
> nothing. The real name is `investment_count_initial_cumulative` on the
> `connection` class. Fixed, re-applied, and the guard now reports 1522.505.
> A guard that returns 0 because its parameter name is wrong is worse than no
> guard - it manufactures false confidence.

### Relaunch

- DB: `checkpoints/Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite`
- Out: `checkpoints/Investment_Results.7day_hcco2_co2fix.sqlite`
- Log: `run_logs/7day_hcco2_co2fix_solve.out`
- Launched 22:04:41, PID 4064, confirmed reading the `co2div365` DB.

Predictions 1-7 above stand unchanged. **Prediction 6 (net CO2 hits
165,400 / 36,800 / ~0) is now the load-bearing check** - it is the test that
would have exposed this defect had the first run completed, and if it fails the
cap is still not binding as intended.

---

## OUTCOME (completed 2026-10-05 03:13, before the 05:01 reboot)

The reboot did **not** affect this run: the solve finished at 03:13:38 and the
results DB was written at 03:13:46, ~1h48m before the machine restarted.

- termination **OPTIMAL**, primal FEASIBLE_POINT
- **308.9 min** (5h09m), RAM 28.7 -> **62.7 GB**
- objective **3,466,640** (3-day: 3,376,634, **+2.67%**)
- `penalties` = **0.000000**

### Prediction scorecard

| # | prediction | result |
|---|---|---|
| 1 | penalties == 0 | **PASS** (0.000000) |
| 2 | objective within 10% | **PASS** (+2.67%) |
| 3 | batteries stay at/near zero | **FAIL** - see below |
| 4 | `oil-eng` stays 0.0 in 2050 | **FAIL** - 3,697 GWh, 4.74 units |
| 5 | all 3 VRE families present 2050 | **PASS** (on 39.2 / solar 25.1 / off 1.5%) |
| 6 | net CO2 hits cap exactly | **PASS** - 165,400 / 36,800 / 0.0 |
| 7 | 3-4 h, 80-110 GB | **PARTIAL** - 5.15 h (over), 62.7 GB (under) |

### Prediction 6 - the load-bearing check

`node_state_longterm(atmosphere)` = 453.1507 / 100.8219 / 0.0, x365 =
**165,400 / 36,800 / 0.0** - identical to the 3-day run. The /365 patch is
confirmed correct and the budget binds exactly as intended. Had the aborted
run completed, this figure would have been 365x larger.

### Prediction 3 FAILED - batteries appear

`storages_invested_available`, summed by family:

| family | 3-day 30/40/50 | 7-day 30/40/50 |
|---|---|---|
| **battery-storage** | 0.00 / 0.00 / 0.00 | **4.50 / 5.34 / 10.94** |
| battery-storage-iron-air | 0 / 0 / 0 | 0 / 0 / 0 |
| salt-cavern | 0.69 / 0.69 / 0.10 | 0.08 / 0.08 / 0.00 |

Batteries also **generate**: `battery-storage_BEC6` 4,012 GWh (1.0%) and
`battery-storage_NLC7` 545 GWh in 2050. A new `storage_investment_costs`
objective line of **2,480.9** appears (3-day: exactly 0.0).

**This falsifies the "daily cyclicity blocks all storage" explanation** given in
`FINDING_hc_co2_unpriced.md` S7 and in the `share_hcco2/README.md` S5 caveat.
Both must be corrected.

The mechanism is now clear and was mis-stated before: `cyclic_condition` blocks
*inter-day* arbitrage, but batteries only ever needed *intra-day* arbitrage, which
was always available. What was missing in the 3-day run was a **day with a steep
enough within-day net-load swing** to pay for them. The 3 sampled days (14 May /
10 Sep / 24 Dec) did not contain one; the 7 days (which include 12 Jan, 18 Feb,
5 Nov, 13 Dec) do. So the earlier zero was a **sampling artefact, not a structural
block** - a much weaker and more contingent claim than the one I made.

Corollary: the 3-day storage result was never evidence of anything structural,
and seasonal storage remains **untested** - 24 h blocks with cyclic conditions
still cannot represent it at any number of representative days.

### Prediction 4 FAILED - `oil-eng` returns

2050: **3,696.8 GWh**, 4.74 units (3-day: absent in every year).

Checked for a patch regression: **not one.** All 20 `oil-eng*` x `atmosphere`
rows carry `flow_ratio_equality_coefficient = 0.24` in the solved DB. The HC
carbon price is intact; the unit is simply competitive on these days.

This is consistent with the OCGT story below: `oil-eng` is a peaker, and the 7-day
sample contains winter days the 3-day sample lacked.

### 2050 electricity mix

Total 2050 electricity **342,975 -> 395,401 GWh (+15.3%)**.

| tech | 3-day | 7-day |
|---|---|---|
| wind-on | 134,816 (39.3%) | 155,056 (39.2%) |
| CCGT+CC | 87,608 (25.5%) | 107,452 (27.2%) |
| solar-PV | 78,831 (23.0%) | 99,243 (25.1%) |
| **OCGT** | 1,575 (0.5%) | **11,754 (3.0%)** |
| **CCGT unabated** | **29,252 (8.5%)** | **7,321 (1.9%)** |
| wind-off | 10,187 (3.0%) | 6,032 (1.5%) |
| battery-storage | 0 | 4,557 (1.2%) |
| oil-eng | 0 | 3,697 (0.9%) |
| CCGT-H2 | 385 | 0 |
| **VRE share** | **65.3%** | **65.9%** |

Headline VRE share is essentially unchanged (+0.6 pp), which is reassuring for the
robustness of the main result. The **peaking segment is what moved**: unabated
CCGT falls by three quarters (8.5% -> 1.9%) and is replaced by a mix of OCGT,
batteries and `oil-eng`. This partially addresses the open "29 TWh unabated CCGT"
anomaly - with richer day coverage the model prefers cheaper peaking capital,
supporting the earlier capacity-factor diagnosis rather than the DAC hypothesis.

### 2050 net-zero verified

Gross +157,890.9 / gross -157,890.9 / **net 0.0**. The negative side is
`CO2-injection-NSNL031` (-157,516) and `-NSNL012` (-375). Largest positives:
LNG-terminal 111,640, gas-extraction 20,773, REF-SMR 13,380, CEM2-(Afm) 2,963,
(NG)DRI-EAF 2,588, oil-eng 2,535. So `oil-eng` running in 2050 under a zero cap
is **offset by CCS**, not a leak in the cap.

### Analysis defect caught (my error, not the model's)

I first de-duplicated `supply` on `[tech,region,year,carrier,vintage]`, which
collapsed legitimate per-period rows and produced a nonsense 2050 total of
3,964 GWh. The raw sum reproduces the known-good 3-day figures exactly
(wind-on 134,816; total 342,975), proving the rows are **distinct period entries
to be summed, not duplicates**. All figures above use raw sums.
**Validating against a known-good prior run is what caught this.**
