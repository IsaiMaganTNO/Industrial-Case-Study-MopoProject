# FINDING: the legacy fleet never retires

**Status:** confirmed, reproduced upstream in the EU case.
**Impact:** high. Any sector whose incumbent technology is endowed via
`units_existing` cannot decarbonise, regardless of how cheap the clean route is.

## Symptom

Primary steel is 100% coal-based BF-BOF in **every** milestone year (2030, 2040,
2050). Every clean route is exactly `0.0`:

| route          | 2030 | 2040 | 2050 |
|----------------|------|------|------|
| `BF-BOF`       | 1.409 | 1.409 | 1.409 |
| `BF-BOF-MEA`   | 0.0  | 0.0  | 0.0  |
| `DRI-EAF-*`    | 0.0  | 0.0  | 0.0  |

The BF-BOF fleet is perfectly constant and nothing is ever decommissioned.

## It is not a cost problem

DRI-EAF is cheaper than the incumbent on both capex and fixed O&M:

| | BF-BOF | DRI-EAF | delta |
|---|---|---|---|
| capex | 118,143 | 87,216 | **-26%** |
| FOM   | (base)  | (base)  | **-28%** |

A cost-minimising model that was free to choose would build DRI-EAF. It does
not, because it is never *required* to replace anything.

## Root cause

Three facts combine:

1. `lifetime = 40.0` is set, but `lifetime_constraint_sense = "<="`.
   That makes lifetime an **upper bound on how long a unit may stay**, not a
   mandate that it must leave. Nothing forces retirement.
2. `units_existing` is given as `{"y2030": <value>}` **only**. There is no
   commissioning vintage, so there is no date from which to measure 40 years.
   The fleet shows `vintage = new` and simply persists.
3. `retirement_method` has **0 rows**. No retirement logic is active at all.

The endowment is therefore a free, permanent, zero-capex asset. The clean route
has to compete against a plant that costs nothing to keep and never dies.

## Scope: this is systemic, not a steel quirk

- **IC1:** 278 of 485 `units_existing` entries (**57%**) are `y2030`-only.
- **EU case:** 59 of 90 (**66%**), with the identical pattern
  `BF-BOF_FR {'y2030': 1.201}`.

The EU case's own solved results reproduce the symptom:
`BF-BOF_FR = [0.643, 0.0, 0.0]` with every clean steel route at zero. The EU
case has no `units_decommissioned` parameter at all.

So this is inherited from upstream data conventions, not introduced here.

## Why it matters for the results

Wherever an incumbent is endowed this way, the model reports "no transition" and
the reader may conclude the clean technology is uneconomic. The correct reading
is that the clean technology was never given a vacancy to fill. Emission
reductions in these sectors come only from bolt-on capture (`-MEA` variants) on
routes that have one, which is why refining, ammonia and cement move while steel
does not.

## Fix options

1. **Give the endowment a vintage** - express `units_existing` as a dated series
   so the 40-year lifetime has an anchor, and let it expire.
2. **Switch the sense** - set `lifetime_constraint_sense = ">="` (or the
   equivalent forced-retirement flag) so lifetime becomes binding.
3. **Add an explicit decommissioning schedule** - populate `retirement_method`
   and a `units_decommissioned` profile per technology.

Option 1 is the most faithful to the intent of the data and is the one to raise
upstream, since the EU case has the same defect.

## How to reproduce

- Fleet by vintage: `plot_scripts/presentation/out/P14_capacity_vintage.png`
- Route mix by sector: `plot_scripts/presentation/out/P08_industry_detail.png`
- Parameter check: read `units_existing`, `lifetime`,
  `lifetime_constraint_sense` and `retirement_method` for `BF-BOF_*` in
  `INES_DB.sqlite`.
