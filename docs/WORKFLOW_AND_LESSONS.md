# How we work: the IC1 tiny-model method

**Audience.** A colleague - or an LLM - picking up this repository on another
machine, who needs to run cases "our way" without rediscovering the traps.

**Scope.** Stage 1 (investment planning) only, Belgium + Netherlands,
17 sub-national polygons (BEC1-BEC8, NLC1-NLC9) plus exogenous neighbours.
SpineOpt v1.0.0, solved with HiGHS, orchestrated by Spine Toolbox.

Companion documents, in the order you will need them:

| document | what it is for |
|---|---|
| `docs/RUNBOOK.md` | the commands, step by step. Start here to RUN something. |
| `docs/TIME_REPRESENTATION.md` | how temporal resolution actually works, section 7 especially |
| `docs/EU_CASE_MIGRATION.md` | how IC1 relates to the EU reference case |
| `docs/TEST_RUN_FINDINGS.md` | earlier run notes |
| **this file** | WHY the workflow looks the way it does |

---

## 1. The short version

We do not run the full model. We run a deliberately shrunken "tiny model"
whose only purpose is to answer structural questions in about an hour rather
than overnight.

The pipeline is:

```
make_cluster_seed.py          pick WHICH representative days
run_pipeline.py               cluster + build the SpineOpt model
make_tiny_model.py            coarsen operations 1h -> 8760h
patch_co2_caps.py             rescale cumulative CO2 caps by 1/365
preflight_check.py            four checks - DO NOT SKIP
run_solve_live.ps1            solve
postprocess.py                26-page PDF + CSVs
```

Two of those steps - `patch_co2_caps.py` and `preflight_check.py` - exist
purely because we were burned. They are not optional polish. Skipping the
first produces a model whose carbon budget is **365x too loose**, which solves
fine and looks plausible. Skipping the second means nothing catches it.

---

## 2. What the tiny model is, and why

The full model at 8760 hourly timesteps per year made build time explode
before the solver ever started. The tiny model attacks the build, not the
solve.

`tools/make_tiny_model.py` coarsens the `operations_y*` temporal blocks from
`1h` to `8760h` - one single timestep per year. The **representative period
blocks stay at 1 h resolution spanning a full 24 h day**, so intra-day
dynamics survive.

A common misreading, which we made ourselves early on: "the tiny model has no
intra-year variation". Wrong. It always had 24 hourly timesteps per year per
representative day. The question is never the resolution WITHIN a
representative day - it is WHICH days you picked, and how many.

Resulting sizes:

| configuration | timesteps | LP columns |
|---|---|---|
| 1 representative day | 75 | 1,069,205 |
| 2 representative days | 147 | 2,056,334 |
| 3 representative days | 219 | 3,043,463 |

Build is roughly 25-30 min for 1 day, ~52 min for 2, ~72 min for 3.

---

## 3. The two hard-won lessons

### 3.1 Cumulative budgets break when you coarsen operations

**The mechanism.** A cumulative cap such as the `atmosphere` CO2 budget is
drawn down once per operational timestep. Coarsening `operations_y*` from 1 h
to 8760 h means it is drawn down **once per year instead of 365 times**, so
every cumulative limit becomes 365x too loose.

**How it showed.** Net CO2 pinned at exactly 165,400 and 36,800 - the raw cap
values - instead of tracking a binding constraint. It never errored.

**The fix.** `tools/patch_co2_caps.py` divides the `atmosphere` node's
`storage_investment_count_max_cumulative` and
`storage_investment_count_initial_cumulative` by 365:

```
165.4 / 36.8 / 0 / 0   ->   0.45315068 / 0.10082192 / 0 / 0
```

After the fix, net CO2 matched the caps to 4 decimal places.

**Which nodes to patch, and which to leave alone.** The rule, from
`TIME_REPRESENTATION.md` section 7.4:

| node | state_max | headroom | verdict |
|---|---|---|---|
| `atmosphere` | 1000 | ~171 days | annual budget -> **rescale** |
| `biomass-stock` | 1 | 1.5 days | already per-period -> leave |
| `CH4-geo-formation` | 1 | 10 days | already per-period -> leave |
| `CO2-storage` | 1000 | 11,623 days | never binds -> leave |

Heuristic: `state_max = 1000` plus tens or hundreds of days of headroom means
it is an annual budget and must be rescaled. `state_max = 1` means it is
already expressed per period.

**Why it fails silently.** SpineOpt absorbs an infeasible balance into
`balance_penalty` rather than refusing to solve. A too-loose cap simply never
binds, so there is nothing to absorb and nothing to report. Always check
`objective_objective_penalties` afterwards - it should be `0.00`.

### 3.2 The representative day IS the result

With ONE representative day, whichever day the clustering picks gets weighted
x365 and becomes the entire year as far as the model is concerned.

Measured against the wy2009 profiles:

| profile | annual mean | 12 Jan | 19 Aug |
|---|---|---|---|
| solar | 0.1433 | 0.0624 | 0.2776 |
| wind | 0.3969 | 0.9778 | 0.2045 |
| cool | 0.0917 | **0.0000** | 0.4309 |
| DHW/space heat | 0.3469 | 0.5169 | 0.2439 |

The consequence, from three runs that all solved to OPTIMAL:

| run | days | new solar | new wind | new battery |
|---|---|---|---|---|
| atmfix | 12 Jan | 0.00 | **44.53** | 0.00 |
| 2rep | 12 Jan + 18 Feb | 0.00 | 0.00 | 0.00 |
| summer | 19 Aug | **32.16** | 0.00 | 0.00 |

**Read that table before interpreting any single-day result.** Single-day
sampling swings new build from "44.5 wind, no solar" to "32.2 solar, no wind".
Neither is a finding. The SPREAD is the finding.

Note also that cooling demand is exactly zero on 12 January, so the original
1-rep model had no cooling load anywhere in the horizon.

---

## 4. Two stale-file bugs, and why they matter to you

Both came from `results/representative_periods.csv`, which is written **only
by the unseeded branch** of `tulipa_call.jl`. When clustering is seeded from
`initial_representative_periods_<wy>.csv`, that file is left untouched and
goes stale.

**Bug 1 - wrong LENGTH.** A 3-medoid file left over from an earlier run made
`total_rps = 3` while the weights had 2 columns. `representative_block_index`
is `year_index * total_rps + rp_day`, which produced 1,2, 4,5, 7,8 - gaps at
3 and 6 - and SpineOpt failed the build with
`there's no representative temporal block(s) with indexes Any[3, 6]`.
Loud, immediate, harmless.

**Bug 2 - wrong CONTENTS.** `block_start` read row `rp_day` of the same stale
`[12, 49, 231]`, so pinning days `(12, 231)` silently stamped the blocks onto
**12 Jan and 18 Feb**. Two winter days. The run solved to OPTIMAL in 6 h 42 m
and every check we had at the time passed: weights summed to 365, coefficients
were convex, block indexes were contiguous. The summer day was simply absent
and nothing said so.

**Both are fixed**, in `clustering_output.py` (derive from the weights, and
raise rather than warn on mismatch) and `make_cluster_seed.py` (rewrite
`representative_periods.csv` alongside the seed so they cannot diverge).

**The lesson that generalises:** this model class fails silently. A wrong
model does not crash - it produces a plausible optimum. That is why check 4
below exists.

---

## 5. Pre-flight checks - run these every time

`tools/preflight_check.py` verifies four things against the patched tiny model:

1. `operations_y*` resolution is `365D`
2. `representative_blocks_by_period` sums to **exactly 1.0** (a convex average)
3. `atmosphere` caps are patched
4. **representative period DATES are the days you asked for**

Check 4 is the one that was missing. Verified against the two-winter-day
model: checks 1-3 pass exactly as they did on the day, and check 4 fails with
`days are [12, 49] but you expected [12, 231]`, exit code 1. It catches a
6 h 42 m mistake in under a second.

Usage:

```powershell
.\.venv\Scripts\python.exe tools\preflight_check.py --expect-days 12 231
```

---

## 6. Solver configuration and what we learned

Settings live in `tools/solve_tiny.jl`.

| setting | value | why |
|---|---|---|
| `time_limit` | 172800 (48 h) | a ceiling, not a commitment |
| `threads` | 8 | leaves cores for the OS so RDP stays responsive |
| `simplex_scale_strategy` | 4 | the model spans ~7.5e13 in magnitude |
| `primal/dual_feasibility_tolerance` | 1e-6 | relaxed from 1e-7, knowingly |
| IIS computation | **disabled** | it once left a host pingable but refusing RDP |

**On the time limit.** A dual-simplex run stopped early yields **nothing**.
The basis is dual-feasible but primal-infeasible throughout; primal
feasibility is attained only at termination. Our 3-representative-day run hit
`TIME_LIMIT` at 6 h and produced a 0.23 MB empty results DB against 67.57 MB
for a real run. There is no partial credit.

**A flat primal-infeasibility count is NOT a failure signal.** The atmfix run
held `Pr` at 27,000-28,700 for 99% of a run that finished OPTIMAL, then
collapsed to `Pr: 0(0)` in its final ~20 seconds. Do not abort a run because
`Pr` is not falling. (I got this wrong during a live run and let a doomed
7-hour job continue on bad reasoning - the real signal was elsewhere.)

**On tolerances.** `EU_CASE_MIGRATION.md` section 6A.4 argues for TIGHTENING
tolerances, on the principle that loosening them until an answer appears can
hide violated energy balances. We relaxed 1e-7 -> 1e-6 anyway, because dual
infeasibility drifted upward all run (8.26e-07 -> 3.66e-06) and holding the
tighter bar was pure refactorisation overhead. This is a knowing exception,
and it is why you must check `objective_objective_penalties = 0.00` after
every solve. It has been 0.00 on every successful run so far.

**On interior point.** It was suggested and then withdrawn. There is no
evidence for it on this model, and IPM is typically MORE sensitive to bad
scaling than simplex. The scaling warnings HiGHS emits
(`Cost [3e-07, 2e+06]`, `Bound [4e-07, 1e+07]`) point at conditioning, not at
algorithm choice. `user_objective_scale` / `user_bound_scale` remain untried.

---

## 7. Run history

All figures below are read from the solve logs, not from memory.

| run | days | timesteps | LP cols | iterations | wall time | outcome | objective |
|---|---|---|---|---|---|---|---|
| atmfix | 12 Jan | 75 | 1,069,205 | 675,067 | 68.6 min | OPTIMAL | 2,571,370 |
| 3rep | 12 Jan, 18 Feb, 19 Aug | 219 | 3,043,463 | 1,659,746 | 435.4 min | **TIME_LIMIT** | - |
| 2rep | 12 Jan + 18 Feb* | 147 | 2,056,334 | 2,394,023 | 402.2 min | OPTIMAL | 2,918,560 |
| summer | 19 Aug | 75 | 1,069,205 | 547,497 | 65.5 min | OPTIMAL | 3,019,450 |

\* intended as 12 Jan + 19 Aug; bug 2 above silently substituted 18 Feb. The
run is a valid optimisation of the wrong question.

Sizing rule of thumb: the LP grows roughly linearly in representative days,
but solve time grows faster than that. One day solves in about an hour end to
end; two days took nearly seven; three did not finish in six.

---

## 8. Open questions - do not present these as findings

1. **The 2050 collapse.** In every run, the entire renewable fleet drops to
   0.00 in 2050 and bioenergy takes 81-100% of electricity supply, while
   methane supply more than doubles. Not a plausible pathway. Unexplained.
2. **Batteries are exactly zero in all runs.** This now looks structural
   rather than weather-driven: a single 24 h block offers no cross-day
   arbitrage regardless of which day it is. Seasonal storage is invisible at
   this temporal resolution.
3. **2050 gross emissions rebound** (479 -> 218 -> 436 in atmfix), still
   unexplained.
4. **Scaling warnings persist.** `user_objective_scale = -1` and
   `user_bound_scale = -4` are HiGHS's own suggestions and have never been
   tried.

Smaller items: wind turbine class review (SP199 -> SP277), ~190 FOM warnings,
oil-boiler x17 removal, a 67 MB unused `geodata/onshore_plus_ic.geojson`, and
`EU_CASE_MIGRATION.md` section 6.2 says "31 existing units" where the actual
count is 42.

---

## 9. Practical notes for a fresh machine

- **`.venv` is not portable.** `pyvenv.cfg` hardcodes absolute paths. Delete
  and recreate. Python **3.14.4**. There is still no `requirements.txt` -
  this is a known gap.
- **The Julia depot lives outside the repo**, at `~/.julia`, and is ~7.4 GB.
  `jenv/Manifest.toml` pins exact versions, so
  `julia --project=jenv -e "using Pkg; Pkg.instantiate()"` reproduces it.
- **No absolute paths** are baked into `tools/*` or
  `.spinetoolbox/project.json`, so a directory copy does transfer cleanly.
- **Terminal opens in the user profile, not the repo.** Always `cd` first, and
  use `.\.venv\Scripts\python.exe` rather than a bare `python`.

### Gotchas that cost us time

- `create_file` in some tooling can write **zero-byte files**. Verify sizes
  after writing; use PowerShell here-strings (`$x = @'...'@`) if it happens.
- Results DB `entity_byname` is `('default_report', <name>, 'realization')` -
  the entity name is at **index 1**, not 0.
- Milestone **2040 is stored as calendar 2041** throughout.
- `%,.2f` is invalid in `%`-formatting; use `"{:,.2f}".format()`.
- Avoid the euro sign in output; the locale here uses comma decimals.

---

## 10. If you change the temporal resolution

This is the thing you are most likely to want to change, so it has its own
section in `docs/RUNBOOK.md` section 2. In brief:

- **WHICH days:** `tools/make_cluster_seed.py --days 12 231`. This writes both
  the seed and `representative_periods.csv`, keeping them in sync.
- **HOW MANY days, unpinned:** `number_of_representatives` in
  `_clustering/tulipa_call.jl`, and delete the seed file so clustering runs
  free.
- **Always** re-run `preflight_check.py --expect-days ...` afterwards and
  confirm check 4 reports the dates you intended.

Do not edit `block_start` or `representative_block_index` by hand. They are
derived, and the derivation is where both silent bugs lived.
