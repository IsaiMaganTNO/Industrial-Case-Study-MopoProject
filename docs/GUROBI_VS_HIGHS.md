# Gurobi vs HiGHS - controlled comparison (summer model)

Date: 2026-09-30. Branch: session-2026-09-27-guardrails-and-scaling.

One variable changed: the solver. Same checkpoint
(`checkpoints/Final_SpineOpt_Model.tiny.summer.sqlite`, 19 Aug representative
day, 75 timesteps, 1,069,205 LP columns), same tolerances (1e-6), same 8
threads, same machine. HiGHS via `tools/solve_tiny.jl`, Gurobi via the new
`tools/solve_tiny_gurobi.jl` (`solve_tiny.jl` deliberately untouched).

## Headline

| | HiGHS 1.24.1 | Gurobi 13.0.3 |
|---|---|---|
| termination | OPTIMAL | OPTIMAL |
| **objective** | **3,019,450** | **3,019,451.698** |
| `penalties` | 0.0 | 0.0 |
| build | 24.6 min | 28.0 min |
| **solve** | **37.0 min** | **1.9 min** |
| total wall | 65.5 min | 33.8 min |
| iterations | 547,497 (dual simplex) | 79,216 (barrier + crossover) |

**Solve is ~19.6x faster; end-to-end ~1.9x** (the build is Julia-side model
construction and is unaffected by the solver - it is now 83% of the run).

Objective agrees to 9 significant figures (relative difference 9.0e-10). Every
objective component matches to ~1e-9. This is the important result: the HiGHS
answer was NOT conditioning-limited. The scaling warnings
(`Cost [3e-07, 2e+06]`, `Bound [4e-07, 1e+07]`) are real but did not corrupt
the optimum, so the missing EU-case `NumericFocus=2` was not costing us
accuracy here. `NumericFocus=0` was enough; it was never tested at 2 because
there was nothing to fix.

Barrier alone hit 3.01945170e+06 in 57 iterations / 39.7 s. Concurrent
(`Method=-1`) is doing the work, not raw speed.

## Physically identical where it matters

Verified by comparing every results CSV:

* `objective` - max relative difference 9.0e-10
* `industry_output` (4,038 rows) - 6.1e-09
* `emissions` - totals identical: 553.973 overall; 2030 453.1507, 2040
  100.8219, 2050 ~0 in BOTH
* `atmosphere`, `storage` - exactly 0.0
* **new solar 32.16, new wind 0, new battery 0 in BOTH** - the key finding of
  the summer run is reproduced exactly

## Where they differ: alternate optima (NOT an error)

The LP has multiple optimal vertices. The two solvers land on different ones.

1. **175 `industry: reference process` rows pinned at `candidate_units=1000`**
   in Gurobi, absent in HiGHS (total units 175,217 vs 218). These are
   zero-investment-cost units - they can sit at their bound without changing
   the objective by a single euro. Gurobi's crossover happens to terminate on
   that vertex.
   => `total_units` from `fleet.csv`/`investments.csv` is NOT a meaningful
   quantity for reference-process technologies. Do not report it.
   => the real issue is that `candidate_units=1000` with zero investment cost
   is a modelling gap, exposed (not caused) by Gurobi.

2. **Capacity relocated between regions at constant total.** e.g.
   `bio-diges-up+CC` moves 0.7596 between NLC4 and NLC5 in 2030 and back in
   2050, but the technology total is identical: 82.1801 in both, and per-year
   2030 20.8645 / 2040 41.0900 / 2050 20.2255 agree to 1e-8. Same for
   `solar-PV-no-tracking` (32.1609 both).
   => region-level siting of a single technology is not pinned down by this
   model. Aggregate before reporting, or expect it to move.

This degeneracy was always present; HiGHS simply never showed it to us. It is
a genuine caution for any conclusion drawn at region level.

## Licence gotcha (cost several failed runs)

`GRB_LICENSE_FILE` was set only in an interactive shell, never persisted, so
background launches inherited an empty value and died mid-run with
`Gurobi Error 10009: No Gurobi license found` - several minutes in, AFTER the
DB read. Diagnosis was slow because every isolated test passed: it ran in the
shell that had the variable.

Fixed three ways, all retained:
1. persisted `GRB_LICENSE_FILE` at User scope (`setx`);
2. `tools/run_solve_live.ps1` sets it explicitly before invoking Julia;
3. `solve_tiny_gurobi.jl` creates ONE shared `Gurobi.Env()` at startup (with
   retry + a clear diagnostic) and passes it to every optimizer, so a licence
   failure is immediate rather than surfacing minutes into a run.

Note `ENV["GRB_LICENSE_FILE"]=...` inside Julia does NOT work - the native
library reads the licence when it loads. It must be set before Julia starts.

## Recommendation

Use Gurobi for the multi-day runs. The 3-representative-day model
(3,043,463 cols) hit TIME_LIMIT at 6 h under HiGHS and returned an EMPTY
database. At ~20x on the solve that becomes tractable, which is exactly the
run needed to settle the representative-day spread (12 Jan wind 44.53 vs
19 Aug solar 32.16). That, not the solver, is still the open question.
