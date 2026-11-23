# FINDING: cement IS decarbonising - the earlier "regression" was a reporting artefact

**Date:** 2026-10-06 | **Run:** `Investment_Results.3day_routeemis.sqlite`
**Status:** CORRECTS `FINDING_industry_sector_trajectories.md` and the cement
reading in `RUN_3day_routeemis.md`

## 1. The correction

Every previous cement statement in these docs used **GROSS** emissions and
therefore ignored captured CO2 - the same frame-reading error that produced the
false "DAC = 0" claim. Cement routes send captured carbon to the `CO2` node, so
it never appears in `emis`.

**Gross (what I reported before):**

| year | gross int | verdict |
|---|---|---|
| 2030 | 0.4155 | - |
| 2040 | 0.3321 | improving |
| 2050 | **0.3536** | **"REGRESSES"** |

**Net of capture (correct):**

| year | output | gross | captured | **NET** | **net int** |
|---|---|---|---|---|---|
| 2030 | 7,132 | 2,963.6 | 822.5 | 2,141.1 | **0.3002** |
| 2040 | 7,132 | 2,368.2 | 1,330.6 | 1,037.6 | **0.1455** |
| 2050 | 7,132 | 2,521.9 | 1,330.6 | 1,191.3 | **0.1670** |

Against the 2018 reference of **0.4980**, cement achieves a **66% net intensity
reduction** by 2050. **It is decarbonising substantially.**

## 2. What remains true: a real 2040 -> 2050 worsening

Net intensity still rises **0.1455 -> 0.1670 (+15%)**. The mechanism is
confirmed and is NOT an artefact:

| route | 2040 | 2050 | gross int |
|---|---|---|---|
| `EU-mix-2018` | 4,154 | **0** | 0.4980 |
| `CEM2-(Afm)` | 0 | **4,154** | **0.5350** |
| `CEM2-(Afm)MEA` | 1,594 | 1,594 | 0.1290 |
| `LC3-(Afm)Oxy-MEA` | 1,385 | 1,385 | 0.0680 |

The 2018 reference plant retires and is replaced **1:1** by `CEM2-(Afm)`, which
is **dirtier per tonne (0.535 vs 0.498)** and has **no capture**. The two
capture routes are frozen at exactly 1,594 and 1,385 across both years.

## 3. Why the clean routes do not expand - it is REGIONAL, not economic

2050 cement output by region:

| region | route | output | captured? |
|---|---|---|---|
| **BEC6** | `CEM2-(Afm)` | 1,160.6 | **no** |
| | `LC3-(Afm)Oxy-MEA` | 386.9 | yes |
| **BEC7** | `CEM2-(Afm)` | 2,992.9 | **no** |
| | `LC3-(Afm)Oxy-MEA` | 997.6 | yes |
| **NLC5** | `CEM2-(Afm)MEA` | 994.0 | yes |
| **NLC6** | `CEM2-(Afm)MEA` | 600.0 | yes |

**All 4,154 t of uncaptured 2050 cement is in BELGIUM. All Dutch cement is
captured.** The Belgian plants run a mix where ~75% is unabated; the Dutch
plants are 100% MEA.

Ruled out as causes:
- **route availability**: all four regions have the **same 23 cement routes**
- **investment caps**: `investment_count_max_cumulative` = 1000.0, non-binding
  (`CEM2-(Afm)MEA` uses 0.182 units)
- **`*_fix` forcing**: none on any cement route
- **capex**: **identical across regions** - `CEM2-(Afm)` 2,791.4,
  `CEM2-(Afm)MEA` 2,959.3 (only **+6.0%**), `LC3-(Afm)Oxy-MEA` 3,194.2
- **CO2 node missing**: `CO2_BEC6` and `CO2_BEC7` both exist

## 4. ~~RETRACTION: "Belgium cannot store CO2"~~ -- THIS RETRACTION WAS WRONG

> **WITHDRAWN 2026-10-06.** The text below is kept only as a record of the error.
> The original "Belgium cannot store CO2" claim is **correct and re-instated**.
> See S4b and `FINDING_co2_storage_saturation.md` S10.

~~An earlier note claimed Belgium cannot store CO2 because all six injectors~~
~~(`CO2-injection-NSNL012/031_NLC1/5/6`) are in Dutch regions.~~
~~**The conclusion does not follow.** Traversing the 35-edge CO2 pipeline network,~~
~~**BEC6 and BEC7 both reach the injector regions** (connected component of 17~~
~~nodes). Belgian carbon *can* physically be transported to Dutch storage.~~

## 4b. RESOLVED: the anomaly is directed-network topology

The retraction above used an **UNDIRECTED** traversal. The CO2 pipelines are
strictly one-way: 35 edges, **0 with a reverse twin**, no connection declaring
multiple `from_node`/`to_node`, and no parameter permitting reverse flow.

Directed reachability to an injector region:

| source | directed closure | reaches injector? | (undirected) |
|---|---:|---|---:|
| `CO2_BEC6` | **1** (itself, no out-edges) | **NO** | 17 |
| `CO2_BEC7` | **8** | **NO** | 17 |
| `CO2_NLC5` | 14 | yes | 17 |
| `CO2_NLC6` | 8 | yes | 17 |

Injectors are fed only from `CO2_NLC1/5/6`. `CO2_BEC7`'s closure is all-Belgian
plus `NLC7` (which flows onward only to `BEC8`). **Belgium is a directed dead
end**, and `CO2_BEC6` has no out-edges at all.

**This answers S3.** Belgian cement is unabated because capture there is
**infeasible** - the captured stream has no path to storage - not because of
cost. That is consistent with every economic factor in S3 being ruled out.

**Treat as a model defect**, not a result: real CO2 pipelines are not one-way,
and Antwerp (BEC7) is a major CO2 cluster with active storage-export projects.
No Belgian CCS outcome in this study should be read economically.

**Root cause traced** (see `FINDING_co2_network_unidirectional.md`): the source
sheet `CO2_data_IC1.xlsx!network` lists each corridor **once** (171 rows = 171
undirected pairs, **0 reverse twins**), whereas the gas sheets list every
corridor **twice** (CH4 91 rows, 88 reverse twins). The builder writes one
directional INES link per row, so CO2 - alone among all commodities - ends up
one-way. **Source-data defect, not a bug in our code.**

## 5. Honest summary for colleagues

- Cement **is** decarbonising: **0.498 -> 0.167 net, -66%**.
- The headline "cement regresses" claim was **wrong** - it ignored capture.
- A real but smaller 2040->2050 worsening (+15%) exists, caused by a **dirtier
  replacement plant (0.535 > 0.498) deployed without capture**.
- The anomaly is **geographic and now explained**: Belgium builds unabated
  cement because the CO2 pipeline network is **directed** and Belgian CO2 nodes
  have **no directed path to any injector**. Capture in BEC6/BEC7 is
  infeasible, not uneconomic. This is a **model defect** to raise with the
  authors, so Belgian CCS results must not be interpreted economically.
