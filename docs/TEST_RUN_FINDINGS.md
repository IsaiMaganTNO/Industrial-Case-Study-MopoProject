# Tiny test run - findings and improvement plan

Run date: 2026-09-27. Model: `checkpoints/Final_SpineOpt_Model.tiny.sqlite`
(2 representative periods x 1 h x 3 investment years = 6 representative
timesteps, plus 3 annual operational timesteps).

## Outcome

| | |
|---|---|
| Termination | **OPTIMAL** (pure LP, dual simplex) |
| Objective | 2,209,998 |
| Solve time | **4.92 s** (build 8 min 24 s) |
| Peak RAM | 55.8 / 143.5 GB (39 %) |
| Results DB | 10.3 MB, 22,046 values |

The pipeline works end to end: 20 build steps -> SpineOpt build -> solve ->
results. The IC1 sub-national resolution (17 polygons) is viable.

## Validated

* **CO2 penalty is exactly zero.** The carbon budget is met without slack, so
  the earlier decision to REMOVE `co2_budget_floor` was correct - a floor would
  have produced a fake overshoot masking a broken CCS chain.
* **CCS chain works**: `CO2-injection-NSNL031` carries 341.1 flow.
* **The problem is an LP, not a MIP.** No integer variables; no need to relax
  integrality. Presolve removes 83 % of rows/columns.
* **Time series are correctly aligned.** All 2,169 long series are stamped 2018
  while the model runs 2030-2050, but every one carries `ignore_year: True`, so
  SpineOpt maps them by month/day/hour. Solar availability at the representative
  hours is healthy (0.63 in BEC1, 0.74 in NLC4 at Aug 20 12:00).

## Issue 1 - `bio-diges-up+CC` is free and unlimited (CRITICAL)

Built to its cap of 1000 in **all 17 regions** = 17,000 units, which is 98.3 %
of all installed capacity and therefore drives the 88.8 % fixed-O&M share.

Root cause: in `data/Gas/Gas_data.xlsx`, sheet `Technology_Costs`, the
`bio-diges-up+CC` row is **entirely NaN** - no capex, no FOM, no VOM, no
lifetime. Its conversion rates are NaN as well. `gas_DB.py` lists
`bio-diges-up` at lines 141 and 162 but omits `bio-diges-up+CC`, so the
technology is declared and given an investment cap but never parameterised.

It is the ONLY genuinely unconstrained technology:

| units with investment cap | 1572 |
|---|---|
| ...with an investment cost | 1102 |
| ...free (cap, no cost) | 470 |
| ...of those, have existing stock (`investment_count_initial_cumulative`) | 402 |
| ...of those, have a fixed schedule (`investment_count_fix_cumulative`) | 87 |
| **...truly unconstrained** | **17** (= `bio-diges-up+CC` x17) |

**Fix**: populate the `bio-diges-up+CC` row in `Technology_Costs` (capex, FOM,
VOM, lifetime, conversion rates) and add it to the technology lists in
`gas_DB.py`. If the data is unavailable, set
`investment_count_max_cumulative = 0` to exclude it rather than let it absorb
the whole system.

## Issue 2 - no fuel costs anywhere

`fuel_cost` has **zero** entries on both nodes and flows, so gas, coal and
biomass are free. `objective_fuel_costs = 0.00`. This removes the merit order
entirely and is why gas technologies dominate dispatch.

**Fix**: add fuel prices per commodity node and investment year.

## Issue 3 - fixed O&M is 88.8 % of total cost

| term | value | share |
|---|---|---|
| fixed O&M | 1,962,220 | 88.8 % |
| taxes | 166,674 | 7.5 % |
| unit investment | 67,885 | 3.1 % |
| variable O&M | 12,781 | 0.6 % |
| connection flow | 439 | 0.02 % |
| fuel / CO2 penalty / storage & connection investment | 0.00 | - |

This is NOT a units bug. `capex/fom` ratios are consistent across technologies
(solar 862,523; OCGT 1,091,560) - the ratio is uniform, so the scaling is
internally consistent. The share is a direct consequence of Issue 1: 51,000 of
51,872 available units (98.3 %) are the free biodigesters, and they are charged
FOM on capacity nobody chose economically.

Expect this to resolve once Issue 1 is fixed. Re-check afterwards.

## Issue 4 - zero renewables, zero storage

Solar, wind, batteries and nuclear are all built at 0.00. Two causes:

1. They are outcompeted by free biodigesters and free fuel (Issues 1-2).
2. **Only 2 weather hours, poorly chosen.** Feb 18 05:00 has solar = 0.0 and
   Aug 20 12:00 is peak sun. With `number_of_timesteps = 1` there is no diurnal
   cycle, so storage has nothing to arbitrage and no battery can pay for itself.

## Recommended order for the next test run

Fix the economics BEFORE raising resolution: at 24 h x 3 representatives the
run cost rises roughly 36x, and that should not be spent on a model where fuel
is free.

1. **Issue 1** - parameterise or disable `bio-diges-up+CC`. Highest impact,
   smallest change.
2. **Issue 2** - add fuel costs.
3. Re-run the tiny model (12 min) and confirm the cost breakdown is plausible:
   fixed O&M well under 50 %, non-zero fuel costs, renewables entering.
4. **Only then** raise to `number_of_timesteps = 24`, >= 3 representatives.
   Expect roughly 36x the operational timesteps; the build dominates runtime,
   so budget ~30-60 min, and keep the external monitor attached.
5. Re-check `investment_count_max_cumulative` on the remaining 470 free units -
   402 have existing stock, which is legitimate, but confirm the caps represent
   existing capacity rather than build potential.

## Open items carried forward

* Wind turbine class review (SP199 -> SP277).
* ~190 FOM-cost warnings during `ines_builder`.
* Oil-boiler x17 removal.
* `docs/EU_CASE_MIGRATION.md` 6.2 says "31 existing units"; actual is 42
  `technology__region` pairs.
* Delete unused 67 MB `geodata/onshore_plus_ic.geojson`.
