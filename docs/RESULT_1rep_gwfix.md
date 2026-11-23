# Run conclusions: `1rep_gwfix` (option 1, refinery gateway restored)

Companion to `docs/FINDING_co2_gateway_accounting.md`, which contains the
diagnosis. This file records what the confirming solve showed.

- model DB : `checkpoints/Final_SpineOpt_Model.tiny.1rep.gwfix.sqlite`
- results  : `checkpoints/Investment_Results.1rep_gwfix.sqlite`
- log      : `run_logs/1rep_gwfix_solve.out`
- change   : `tools/revert_refinery_gateway.py` - 51 UPDATEs, nothing else
- commit   : `c0fe455` (branch `fix/co2-route-emissions`)

---

## 1. The diagnosis is confirmed

The objective converged to **~4.5050e9**, which puts the model back in the
pre-patch regime:

| run | objective | CO2 cap | reading |
| --- | ---: | --- | --- |
| `1rep_repfix` (pre-patch) | 4.53e9 (penalties 4.52e9) | bought out | honest-ish, but refineries over-charged |
| `1rep_co2patch` | 2.577e6 (penalties 0) | "met" | **invalid** - free refined-product carbon |
| **`1rep_gwfix`** | **4.5050e9** | **bought out** | refinery gateway restored |

Restoring the 51 refinery coefficients to crude's `CO2_content` = 0.26
reproduces the pre-patch objective to within 0.6%. The near-zero objective and
the "2050 net zero" of the co2patch run were **purchased entirely by the
oil-eng loophole**, not earned by decarbonisation.

This is the main result. It closes the question that started the session: the
CO2 numbers were wrong, and the wrongness was ours
(`patch_co2_in_model_db.py`), layered on top of a genuine upstream pipeline
defect.

## 2. What "bought out" means here

`atmosphere` is a storage node with `storage_investment_count_max_cumulative`
= 165.4 / 36.8 / **0.0** (2030/2040/2050) and `balance_penalty` = 10000. When
the cap cannot be met the model does not go infeasible - it pays. An objective
of 4.5e9 against a "real" system cost of order 2.6e6 means penalties dominate
by roughly **three orders of magnitude**.

Consequence for interpretation: **investment decisions in this run are driven
by penalty avoidance, not by cost-optimal decarbonisation.** The capacity mix
is therefore not a meaningful scenario result. Its value is diagnostic.

So: under correct carbon accounting, the 2050 zero-emission cap is **not
attainable in this model configuration**. That is a scenario-design finding,
not a code defect. The cap trajectory needs a decision - relax 2050, extend the
horizon, or admit more mitigation options - before any run produces an
interpretable mix.

## 3. Numerical behaviour

Build ~44 min (the model is build-heavy: `constraint_unit_lifetime` alone
allocated 185 GiB, `constraint_unit_flow_capacity` 72 GiB). Gurobi barrier +
crossover finished at 187 s; simplex cleanup then ran very long.

| solver time | iteration | objective | dual inf. |
| ---: | ---: | ---: | ---: |
| 187 s | 333,827 | 4.5095884e9 | 1.29e12 |
| 627 s | 366,939 | 4.5051653e9 | 6.56e9 |
| 947 s | 388,881 | 4.5050739e9 | 4.61e8 |
| 1382 s | 418,042 | 4.5050232e9 | 1.32e8 |

Primal infeasibility was 0.0 throughout. The objective was effectively
converged by ~630 s (last 50k iterations moved it 0.003%); the remaining time
is dual-feasibility cleanup, oscillating noisily (spikes to 1.4e10). This is
the known ill-conditioning - `Cost [3e-07, 2e+06]`, `Bound [4e-07, 1e+07]` -
recorded in `tools/solve_tiny_gurobi.jl`. `NumericFocus=2` is worth trying on
the next long run.

## 4. What this run does NOT tell us

Stated plainly, because several of these were tempting to over-read:

1. **Not a CCS result.** Option 1 makes `REF-SMR` and `REF-SMR-MEA` emit
   identically (both 0.26), so refinery CCS has no incentive by construction.
2. **Not a technology-mix result.** See section 2 - penalties dominate.
3. **Not a VRE result.** The single summer representative day gives solar ~1.94x
   its annual availability and onshore wind ~0.45x, a ~4x swing in relative
   economics. Offshore wind is investable (12 units, caps non-binding) and is
   never built. Fix the representative days before reading any mix.
4. **Not a verdict on option 2.** Charging `HC_*` consumers at 0.24 and zeroing
   the gateway would preserve the CCS incentive and is the better fix; it is
   deferred, not rejected.

## 5. Open items, in priority order

1. **Representative-period selection.** Dominates the technology mix and
   corrupts any policy reading. Highest leverage of anything outstanding.
2. **CO2 cap trajectory.** 2050 = 0.0 is unreachable under honest accounting.
   Needs a scenario decision.
3. **Pipeline fix (upstream).** `commodity_data.csv` defines `CO2_content` for
   9 commodities; only 4 survive into `INES_DB` because the commodity -> node
   projection only lands on *global* nodes, and `CH4`/`HC`/`MeOH`/`bio` are
   regionalised. `commodity_price` is lost identically. **Still unfixed - a
   rebuild reintroduces it.**
4. **Free negative emissions.** 225 of 288 CO2-capturing units have no
   atmosphere row, so `CO2-injection-*` (which consumes `atmosphere` at ratio
   1.0) credits them a removal they never paid for. Includes fossil units:
   `CCGT+CC`, `SMR+CC`, `(NG)PE-MEA`, `(COEL)FT-MEA`. Pre-existing, untouched
   by this run.
5. **Option 2**, blocked on a structure decision: `HC_*` is shared between
   fossil refineries and `(BM)FT`/`(H2)FT-DC`. Flat 0.24 would mis-charge
   synthetic HC - 0.0% today, but `CH4_*` is 44.7% synthetic by 2050, which
   shows the trap is real.
6. **`solar-PV-existing`** 90.2 GW in 2030 vs ~33 GW actual for NL+BE, and it
   does not reproduce its own generation (90.2 x 0.27 = 24.4 GW avg vs 12.2 GW
   reported). Suspect double-count in `investment_count_initial_cumulative`.

## 6. Reverting

Option 1 is 51 `parameter_value` UPDATEs and nothing else. To undo, either
re-copy `Final_SpineOpt_Model.tiny.1rep.co2patch.sqlite`, or go back further to
`Final_SpineOpt_Model.tiny.1rep.repfix.sqlite` (pristine, pre-patch). Tag
`pre-co2-emission-fix` (`d9a1b7d`) and `tools/revert_co2_fix.ps1` remain valid.
