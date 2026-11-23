# FINDING: CO2 storage saturation blocks industrial CCS

Run: `Investment_Results.7day_hcco2_co2fix.sqlite` (7-day, OPTIMAL, penalties 0).
Date: 2026-10-05

## 1. Symptom

Cement **de-abates** between 2030 and 2050:

| cement | route | output | CO2 | intensity |
|---|---|---|---|---|
| 2030 | `EU-mix-2018` (unabated) | 5,538 | 2,757.9 | 0.498 |
| 2030 | `CEM2-(Afm)MEA` (capture) | 1,594 | 205.6 | 0.129 |
| 2050 | **`CEM2-(Afm)` (unabated)** | 5,538 | **2,962.8** | **0.535** |
| 2050 | `CEM2-(Afm)MEA` (capture) | 1,594 | 205.6 | 0.129 |

The 2050 unabated route is **dirtier than the 2018 EU reference**. The capture
variant is frozen at exactly 1,594 in all three milestones. `LC3-(Afm)MEA`
appears in 2040 (1,385) then vanishes in 2050.

## 2. Hypothesis tested and REJECTED

Initial hypothesis: cement process (calcination) emissions are mis-booked
fuel-based, per `FINDING_fuel_based_emissions.md`, so capture is undervalued.

**Rejected by direct inspection.** Cement is already **route-based**, keyed on
*output*, exactly as the S6.3 fix intends:

| route | `atmosphere<-cement` | `CO2<-cement` | gross |
|---|---|---|---|
| `CEM2-(Afm)` | 0.535 | - | 0.535 |
| `CEM2-(Afm)MEA` | **0.129** | **0.516** | 0.645 |
| `LC3-(Afm)MEA` | 0.098 | 0.391 | 0.489 |

Capture is correctly represented: MEA emits 0.129 vs 0.535 = **75.9% abatement**,
and the captured 0.516 goes to the `CO2` node. Not a coefficient defect.

Costs are also not the blocker: `CEM2-(Afm)MEA` capex 2,959 vs `CEM2-(Afm)`
2,791 in 2050 = **+6.0%**, same `fom_cost` 0.029, and both have
`investment_count_max_cumulative = 1000.0` with **no** `*_fix` rows.

## 3. Actual root cause: the CO2 sink is full

`node_state_longterm` on the two reservoirs, 2050:

| reservoir | 2050 fill | cap (`fix_cumulative` x `state_max`) | used |
|---|---|---|---|
| **`CO2-storage-NSNL031`** | **6,200.00** | **6,200** | **100.0% SATURATED** |
| `CO2-storage-NSNL012` | 1.03 | 21,000 | 0.005% |

NSNL031 is **exactly at its cap**. Capture cannot expand because there is
nowhere to put the CO2, so the model keeps cement unabated and meets the
net-zero budget with the capture it already has.

The 2050 `atmosphere` budget is **0.0**, i.e. net zero is binding. Gross
emissions +157,891 are offset -157,891, of which `CO2-injection-NSNL031`
supplies -157,516 (**99.8%**).

## 4. The anomaly within the anomaly

NSNL012 has **21,000 units of capacity and is essentially unused** while the
system is sink-constrained. Checked and ruled out:

- **Not a scenario-alternative problem.** Both reservoirs carry
  `storage_investment_count_fix_cumulative` under `high_CO2`/`medium_CO2`/`low_CO2`,
  and `high_CO2` **is** in the active scenario. (I initially mis-read this as
  "no active alternative" - corrected.)
- **Not injector cost.** `CO2-injection-NSNL031_NLC5` `vom_cost` **0.0191** is the
  *cheapest* of the six injectors; NSNL012's are 0.0239-0.0255. The model
  correctly fills the cheap one first - but then does **not** spill into NSNL012.
- **Not pipeline capacity.** The 35 CO2 connections carry only
  `connection_flow_cost` and `fix_ratio_out_in_connection_flow = 1.0`.
  There is **no capacity parameter on any CO2 pipeline** - they are unlimited.
- **Not topology.** Both reservoirs are fed from the *same* three regions
  (`CO2_NLC1`, `CO2_NLC5`, `CO2_NLC6`).

Same regions, same unlimited pipes, ~25-33% higher injection cost, 21,000 free
units - yet the model prefers to leave cement unabated. **Unexplained.**

## 5. Structural issue: Belgium cannot store CO2 at all

All 6 `CO2-injection-*` units sit in **NLC1 / NLC5 / NLC6**. Belgian `CO2_BEC*`
nodes feed only e-fuel/chemical consumers (`(COEL)FT-MEA`, `methanation`, ...),
never an injector. BE capture can only be stored by piping to NL. Given Antwerp
is one of Europe's largest industrial CO2 clusters, this is worth confirming
against intent.

## 6. Open question (NOT yet answered)

Why does the optimiser not use NSNL012? Candidate explanations, untested:

1. A long-term storage/representative-period interaction (the same family of
   defect as the `/365` cap bug) limiting the *rate* of fill rather than the level.
2. `storage_state_max = 1000.0` combined with the 21.0 count may cap the
   **per-period** inflow, not just the total.
3. An injector availability/capacity limit not expressed as a parameter I checked.

Until this is resolved, **do not interpret the cement result as an economic
finding**. The 78%-unabated-cement outcome is an artefact of a saturated and
partially unusable CO2 sink.

---

## 7. SELF-CORRECTION (same session): S3's headline claim is TOO STRONG

The section-3 framing - "capture cannot expand because there is nowhere to put
the CO2" - is **not supported by the evidence in S4 and must be withdrawn.**

If the sink were genuinely scarce, `CO2-storage-NSNL012` would be full too.
It is at **1.03 of 21,000**. There are **~21,000 units of unused, reachable,
pipeline-unconstrained storage** sitting next to the saturated reservoir.
A system that is sink-constrained does not leave 21,000 units idle.

So the correct statement is narrower:

- **True:** the *cheapest* reservoir (NSNL031, `vom_cost` 0.0191) is used to
  exactly 100.0% of its cap. That is expected merit-order behaviour.
- **True:** total sink capacity is **not** exhausted - 21,000 units remain.
- **Therefore:** "storage saturation blocks cement CCS" is **unproven**, and on
  the face of it contradicted.

### More likely explanation (now leading, still untested)

Net zero is enforced **system-wide**, not per sector: the 2050 `atmosphere`
budget is a single scalar 0.0. The model is therefore free to let cement emit
0.535 t/t and offset it with the cheapest negative-emission tonne available
anywhere in the system. Cement capture (+6.0% capex, 2.09x the electricity
input) only has to beat the *marginal* offset cost - not reach zero itself.

That is **economically rational optimiser behaviour, not necessarily a bug.**
Whether it is *realistic* is a separate question: in reality cement CCS is
driven by sectoral policy (ETS free-allocation phase-out, CBAM), which this
model does not represent.

### What this changes

The S1 observation stands and is still the most interesting result: 2050 cement
is **dirtier than the 2018 EU reference** (0.535 vs 0.498). But the cause is
most likely **absence of any sector-level constraint**, not a blocked sink.

**Do not cite S3 as a finding.** The verified facts are S2 (coefficients and
costs are correct - capture is properly represented and affordable) and S4
(NSNL031 saturated, NSNL012 idle, topology/pipelines/alternatives all ruled out).

### Cleanest test to settle it

Raise the `atmosphere` budget constraint from system-wide to per-sector, or
simply force `CEM2-(Afm)MEA` and re-read the objective delta. If the objective
rises only slightly, cement CCS was a near-miss on economics and the result is
"rational but policy-naive". If it rises sharply, something really is blocking it.

---

## S8. CORRECTION from the 3-day route-emissions run (2026-10-06)

S6 of this document reported, from the **7-day** run, that "DAC is the real
offset" (2050 capture 6,177.7 total, DAC 1,810.4, cement MEA only 15.8).

The **3-day** route-emissions run contradicts this: **DAC = 0.0 in 2050**, in
both the baseline and the patched run. The entire offset is carried by
`CO2-injection-NSNL031` (-154,137.3 baseline, -157,084.3 patched).

The two runs therefore select **different offset technologies**. The
DAC-vs-injection split is **sampling-dependent** and must NOT be reported as a
robust finding of the study. What IS robust across both runs is the *mechanism*:
a single cheapest marginal offset clears the system-wide net-zero constraint,
whichever technology that happens to be under the sampled weather.

Additionally, NSNL031's 2050 **state** rose 2,811.312 -> 2,865.529 under the
patch, so it was **not** at a hard ceiling. The "exactly saturated 6,200.0/6,200"
figure in S5 refers to a different quantity (cumulative capacity, not the 2050
state) and must not be cited as evidence that storage is exhausted.

**NSNL012 idleness remains unexplained**: it stayed at exactly -377.7 in both
runs and absorbed none of the +2,947 of newly-priced carbon, even as NSNL031
expanded to take all of it.

---

## S9. CORRECTION to S8 (2026-10-06, same day)

S8 claimed **"DAC = 0.0 in 2050, in both the baseline and the patched run"** and
concluded the DAC-vs-injection split was sampling-dependent.

**S8 IS WRONG.** I read the `emis` frame, where DAC correctly shows 0.0 because
DAC does not emit - it **captures**. Its activity is in `co2net` under
`role='captured'`, which I failed to check.

Actual 3-day values: DAC captures **92,899.6 t in BOTH 2040 and 2050** and is
the **largest single capture technology at 56.4% of all 2050 capture**.

The 7-day run reported DAC 1,810.4 on a different basis; the two are therefore
**not** evidence of sampling-dependence. **The S8 claim that DAC selection is
sampling-dependent is withdrawn** - it rested on a frame-reading error.

What remains true from S8: NSNL031's 2050 state rose under the patch, so it was
not at a hard ceiling; and NSNL012 idleness is still unexplained.

---

## S10. RESOLVED: Belgium genuinely CANNOT reach CO2 storage (S4 retraction was wrong)

**Date:** 2026-10-06. This **re-instates** the original "Belgium cannot store
CO2" claim of S5 and **withdraws the retraction** in
`FINDING_cement_net_vs_gross.md` S4.

### The error in the retraction

The retraction rested on a graph traversal that found BEC6/BEC7 in a
"connected component of 17 nodes". **That traversal was UNDIRECTED.** The CO2
pipelines are strictly one-way.

Measured on `Final_SpineOpt_Model.tiny.3day.routeemis.sqlite`:

- 35 CO2 connections, **35 directed edges, 0 with a reverse twin**
- **0 connections declare more than one `from_node`/`to_node`** (none bidirectional)
- the only parameters present are `connection_flow_cost` and
  `fix_ratio_out_in_connection_flow` - **nothing that re-enables reverse flow**

### Directed reachability (the number that matters)

| source | directed closure | reaches injector? | undirected |
|---|---:|---|---:|
| `CO2_BEC6` | **1** node (itself) | **NO** | 17 |
| `CO2_BEC7` | **8** nodes | **NO** | 17 |
| `CO2_NLC5` | 14 nodes | yes | 17 |
| `CO2_NLC6` | 8 nodes | yes | 17 |

Injectors are fed only from `CO2_NLC1`, `CO2_NLC5`, `CO2_NLC6`.
`CO2_BEC7`'s entire directed closure is
`{BEC1, BEC2, BEC4, BEC5, BEC6, BEC7, BEC8, NLC7}` - **all-Belgian plus NLC7,
which itself only flows onward to BEC8.** Belgium is a directed **dead end**.

`CO2_BEC6` is worse: it has **no out-edges at all** (in-edges from BEC2, BEC3,
BEC5, NLC9). It is a pure sink that cannot forward carbon anywhere.

### This fully explains the cement anomaly

The open question of `FINDING_cement_net_vs_gross.md` S3-S4 is answered.
Belgian cement is unabated **not** because of transport cost, and **not** by
economic choice - capturing CO2 in BEC6/BEC7 is **infeasible**, because the
captured stream has no directed path to any injector. The optimiser builds
`LC3-(Afm)Oxy-MEA` in Belgium only to the extent its captured CO2 can be
consumed locally by e-fuel/chemical units; beyond that it must run unabated.

Identical costs, identical route menus and non-binding caps were correctly
ruled out - the binding constraint was **network direction**, which every
previous check missed because the traversal ignored it.

### Status: this is a MODEL DEFECT to raise with the authors

Real CO2 pipelines are not one-way, and Antwerp (BEC7) is one of Europe's
largest industrial CO2 clusters with active export-to-storage projects. Either
the directionality is a data-generation artefact, or reverse/export links are
missing. **Belgian industrial CCS is structurally impossible in this model**,
so no Belgian CCS result from this study should be interpreted economically.

### Methodological note - the 4th instance of the same error pattern

This is the same failure as the orphan-route, CCGT-carbon and DAC=0 errors:
a query was run, and its **blind spot was not characterised** before drawing a
conclusion. Here the blind spot was `undirected traversal of a directed graph`.
Worse, it caused a *correct* earlier finding to be retracted. Any future
reachability claim must state explicitly whether it is directed.
