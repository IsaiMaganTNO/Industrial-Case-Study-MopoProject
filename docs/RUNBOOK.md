# IC1 tiny-model runbook

How to run an IC1 stage-1 (investment planning) case end to end, and how to
change the temporal resolution. Written so the workflow can be reproduced on a
different machine without reconstructing it from scratch.

Background on WHY the temporal handling works this way is in
`docs/TIME_REPRESENTATION.md` - especially section 7 on cumulative budgets.

---

## 0. The short version

```powershell
cd <repo>
.\.venv\Scripts\python.exe tools\make_cluster_seed.py --days 12 231   # pick days
.\.venv\Scripts\python.exe tools\run_pipeline.py --from merge_spineopt
.\.venv\Scripts\python.exe tools\make_tiny_model.py
.\.venv\Scripts\python.exe tools\patch_co2_caps.py
.\.venv\Scripts\python.exe tools\preflight_check.py --expect-days 12 231
pwsh tools\run_solve_live.ps1 -Db checkpoints\Final_SpineOpt_Model.tiny.sqlite `
     -Out .spinetoolbox\items\investment_results\Investment_Results.myrun.sqlite `
     -LogPath run_logs\myrun_solve.out -Threads 8
.\.venv\Scripts\python.exe tools\postprocess.py `
     .spinetoolbox\items\investment_results\Investment_Results.myrun.sqlite `
     -o reports_myrun -m checkpoints\Final_SpineOpt_Model.tiny.sqlite
```

**Never skip steps 4 and 5.** Both failures they guard against are SILENT: the
model solves to OPTIMAL and gives a plausible answer to the wrong question.

---

## 1. What the tiny model is

The full model at 8760 h resolution is not buildable in reasonable time. The
tiny model keeps the full spatial and technological detail but collapses the
temporal dimension:

| block | full model | tiny model |
|---|---|---|
| `operations_y2030/40/50` | 8760 x 1 h | 1 x 365D |
| `representative_period_*` | 1 h, N days | **unchanged** - 1 h, N days |

`make_tiny_model.py` only coarsens the `operations_y*` blocks. The
representative periods keep hourly resolution over a full 24 h day, so the
diurnal cycle survives. Timestep count is `3 + (reps x 24 x 3)`:

| representatives | timesteps | LP columns | build | solve |
|---|---|---|---|---|
| 1 | 75 | 1.07 M | ~27 min | ~36 min |
| 2 | 147 | 2.06 M | ~52 min | ~5.8 h |
| 3 | 219 | 3.04 M | ~72 min | 9-25 h (est.) |

Cost grows much faster than linearly. 3 representatives hit a 6 h limit with
`primal: NO_SOLUTION` and an EMPTY results DB - a stopped dual-simplex run
yields **nothing**, so the time limit must be generous.

---

## 2. Changing the temporal resolution

Two independent knobs.

### 2a. WHICH days (recommended)

```powershell
.\.venv\Scripts\python.exe tools\make_cluster_seed.py --days 12 231
```

Pins representative days by day-of-year and writes BOTH files that must agree:

* `results/initial_representative_periods_<wy>.csv` - seeds the clustering
* `results/representative_periods.csv` - read by `clustering_output.py` for dates

It also prints each day's profile means against the annual mean, so an
unrepresentative pick is visible immediately:

```
profile          annual     day12    day231
solar            0.1433    0.0624    0.2776
wind             0.3969    0.9778    0.2045
cool             0.0917    0.0000    0.4309
```

Cooling demand is **exactly zero** on 12 January - a single winter day means no
cooling load anywhere in the horizon.

### 2b. HOW MANY days (unpinned clustering)

Delete `results/initial_representative_periods_<wy>.csv`, then set
`number_of_representatives` in
`Pan-European-Framework-Energy-System-Planning/src/_clustering/tulipa_call.jl`.

`number_of_timesteps` is the period DURATION in hours. **Keep it at 24.** Below
24 the periods are no longer whole days; at 1 there is a single timestep per
period and storage is degenerate by construction.

### 2c. Solver limits

`tools/solve_tiny.jl`: `TIME_LIMIT` (currently 48 h), feasibility tolerances
(1e-6), `threads` (8 - leave cores for the OS so RDP stays responsive).

---

## 3. Why each step exists

### `make_cluster_seed.py`
Pins the days. Column order in the seed is **load-bearing**: TulipaClustering
derives key columns positionally and compares them order-sensitively, so the
file must be `period, timestep, profile_name, value`. The intuitive ordering
fails with `Key columns of initial represenatives do not match clustering data`.

### `run_pipeline.py --from merge_spineopt`
Five steps, ~9 min: merge, clustering input, clustering, clustering output,
scenario setup. Starting at `merge_spineopt` matters - it purges
`Final_SpineOpt_Model` first, so stale entities do not accumulate.

### `make_tiny_model.py`
Coarsens `operations_y*` to 365D and rewrites `representative_blocks_by_period`
to a single convex entry. Writes `checkpoints/Final_SpineOpt_Model.tiny.sqlite`.

### `patch_co2_caps.py`
Divides the `atmosphere` cumulative caps by 365. After coarsening, a cumulative
budget is drawn down once per YEAR instead of 365 times, so the cap is 365x too
loose. Silent because `atmosphere` carries `balance_penalty = 10000.0`. Only
`atmosphere` is patched - see section 7.4 of `TIME_REPRESENTATION.md`.

### `preflight_check.py`
Four checks, each matching a failure that actually happened. Check 4 (dates) is
the one that cost 6h42m: a run pinned to (12 Jan, 19 Aug) was built on
(12 Jan, 18 Feb) and solved to OPTIMAL as a two-WINTER-day model. Checks 1-3 all
passed that day. Always pass `--expect-days`.

### `run_solve_live.ps1`
Tees output to a log. Do not use `Start-Process -RedirectStandardOutput` - it
block-buffers stdout and the log stays empty until the process exits.

### `postprocess.py`
26-page PDF + PNGs + CSVs. Includes supply-mix and capacity-vs-energy figures,
which matter because capacity and delivered energy can move in OPPOSITE
directions - the summer run built zero new wind while retaining existing solar
that delivered 35.6% of 2030 electricity.

---

## 4. After a solve: sanity checks

1. `termination : OPTIMAL` and `primal : FEASIBLE_POINT` in the log.
   `TIME_LIMIT` + `NO_SOLUTION` means the results DB is empty (~0.2 MB).
2. Results DB size - a real run is 60-90 MB.
3. **`penalties = 0.00`** in `reports_*/..._objective.csv`. Non-zero means
   constraint violations were absorbed as slack, which the relaxed 1e-6
   tolerance makes possible.
4. Final simplex line shows `Pr: 0(0)`.

A flat primal-infeasibility count during the solve is **NOT** a failure signal:
a run that finished OPTIMAL held `Pr` at ~27,000-28,700 for 99% of its duration,
then collapsed to zero in the last ~20 s.

---

## 5. Known open questions

* **2050 collapse** - all wind and existing solar go to zero and bioenergy takes
  81-99% of electricity, in every run so far. Unexplained; do not present 2050
  results externally until understood.
* **Zero battery investment** in all runs. Appears structural: a single 24 h
  block offers no cross-day arbitrage regardless of which day is chosen.
* **Single-day sampling bias** - one winter day gives 44.5 wind / 0 solar; one
  summer day gives 0 wind / 32.2 solar. Neither is a result; the spread is.
