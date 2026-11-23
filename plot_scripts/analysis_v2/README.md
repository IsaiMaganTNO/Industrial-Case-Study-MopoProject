# analysis_v2 — corrected report for the IC1 summer CO2-rebuild run

Rebuilds the figures and tables from the two SQLite databases in the parent
directory. **Nothing in the parent directory is written to.** All output lands in
`analysis_v2/out/` with a `v2_` prefix, so the original report is untouched.

## Run it

```powershell
python analysis_v2\build_report.py
```

Requires `pandas`, `numpy`, `matplotlib`. Reads:

- `../RESULTS_Investment_Results.summer_co2rebuild.sqlite`
- `../INPUT_Final_SpineOpt_Model.tiny.summer_co2rebuild.sqlite`

## Files

| file | role |
|---|---|
| `spine_io.py` | Spine DB reader. Resolves entity dimensions through `entity_element` rather than splitting names on `__`, because element names in this model contain `__` themselves (e.g. the storage unit `battery-storage_NLC5__elec_NLC5`). |
| `model.py` | Scenario logic: temporal mapping, flow annualisation, CO2 accounting classification, fleet handling, cap extraction. |
| `build_report.py` | Produces `out/v2_T*.csv`, `out/v2_F*.png` and `out/v2_SUMMARY.md`. |

## What is different from the original report

**1. CO2 accounting.** The original nets a tonne of captured CO2 twice. An abated
route books only its residual stack emission (`REF-SMR-MEA` atmosphere coefficient
0.002 vs `REF-SMR` 0.019) and sends the captured 0.017 to the CO2 network; the
injector then *also* withdraws 1 t from the `atmosphere` node per tonne injected.
Separately, `DAC`, `SMR+CC` and `CCGT+CC` have no `atmosphere` relationship at all,
so the fossil fuel they burn produces no booked emission yet still earns a full
removal credit at the injector.

Three nets are reported:

- `net_reported_by_model` — what the original figures show.
- `net_corrected_core` — removes only the unambiguous duplicate. No assumptions.
- `net_corrected_full` — also removes credit on fossil carbon that never entered
  the emission account, using an emission factor inferred from CH4-only units that
  *do* report to the atmosphere. Sensitivity band in `v2_F05`.

**2. Units.** Every value is annual (`hourly solver value × representative weight`,
read from the database, currently 365). The original mixes annual values with
per-representative-day values and labels several annual charts "per representative
day".

**3. Hourly rows are labelled.** `v2_T03_atmosphere_flows_hourly.csv` carries an
explicit `hour` column. The original CSVs write 24 rows per entity with no
timestamp, so the rows are indistinguishable duplicates and any `drop_duplicates()`
or `aggfunc='first'` understates totals 24-fold.

**4. Period mapping.** The 2040 milestone is solved on calendar **2041**. Keying on
`ts.year` silently drops it. `model.temporal_structure` derives the mapping from the
`temporal_block` definitions instead of assuming it.

**5. Existing vs new fleet.** `existing` is
`min(units_invested_available, investment_count_initial_cumulative)`. The original
derives it from the `-existing` suffix in the technology name, and its "retained
existing capacity" chart computes `total fleet − this period's additions`, which is
why it shows retained capacity growing from 0 to 175,000.

**6. Placeholders separated.** `*-production-reference` entities are generic sector
stand-ins whose `capacity_per_unit` is arbitrary and which mostly sit exactly on
their own 1000-unit investment bound. They are ~99.9 % of any "units" total. They
are excluded from the fleet figures and flagged (not dropped) in the tables.

## Knobs

In `model.py`:

- `FOSSIL_CARRIERS` / `BIOGENIC_CARRIERS` decide whether a removal credit can be
  legitimate. Edit if carrier naming changes. `waste` is currently counted as
  fossil, which is conservative.
- `ATMOSPHERE` is the only hard-coded node name.

The emission factor used for the full correction is the **median** implied
CO2-per-CH4 across units that both burn only CH4 and report to the atmosphere;
`v2_F05` shows the inter-quartile sensitivity.

## Standing caveat

The run samples **one day — 19 August — scaled by 365**. Solar is above its annual
mean on that day, heating demand is far below it. Wind falling to exactly zero by
2050 and cooling demand exceeding heat demand are artefacts of this sampling, not
findings. Treat every annual energy number as a summer-day extrapolation.
