# FINDING: repointing is not enough - format conversion is required

Date: 2026-10-08.

## What I assumed, and why it was wrong

`SURVEY_sector_coverage_mixedres.md` concluded that most sectors were "pure
input swaps" - just point the Toolbox at the pan-EU file instead of the `_IC1`
one. That is **false for residual demand**, and the failure is silent.

`demand_DB.py` L37:

    electricity_demand = pd.read_csv(sys.argv[2], parse_dates=True, index_col=0)

Default separator is `,`. The pan-EU `other_electricity_demand.csv` is
**semicolon**-delimited with `1-1-1982 00:00` dates. Parsed with the default,
it yields **0 columns** - every row collapses into one giant index string
(measured, `run_logs/_rb10.py`). The importer would then loop
`for country in electricity_demand.columns` over an empty list, write no
regions at all, and **exit 0**. No exception, no warning, an empty RDemand_DB.

This is the same delimiter hazard already on record in the working notes; it
would have been a silent data-loss bug, not a crash.

## Fix applied

Built `data/Rdemand/other_electricity_demand_IC1_NWEU.csv` (94,906,555 B) by
converting the pan-EU file to the importer's expected dialect and subsetting to
the 21 regions we actually model:

- read with `sep=";"`, `dayfirst=True`
- keep BEC1-8, NLC1-9, DE, DK, NO, UK
- write comma-delimited with an ISO datetime index

Verified by re-reading it **exactly as `demand_DB.py` does** (default comma,
`parse_dates=True`, `index_col=0`):

- 21 columns, correct names and order
- index parses to `datetime64`, 1982-2021
- wy2009 complete: 8,760 hours, 0 NaNs
- 2009 annual demand: DE 400.8 TWh, UK 265.7, NO 91.8, DK 29.2 - all
  plausible against published national figures
- BE/NL columns reconcile against the currently-wired `_IC1` file to
  max |diff| = 0.5 MWh across all 350,640 shared hours, i.e. rounding only.
  **The 17 IC1 series are unchanged**, so BE/NL demand is not perturbed.

Note this also drops the 15 `Unnamed: 18..32` junk columns that the `_IC1`
file carries and which currently pollute `rdemand_db` with 15 phantom regions.

## Not yet wired

The file exists and is validated but the Toolbox still points at
`other_electricity_demand_IC1.csv`. Switching it is a `project.json` edit to
both `rdemand_importer` cmd_line_args and the `rdemand_input` Data Connection.

## Generalisation - treat every repoint as suspect

Each remaining repoint (heat, gas, transport, power-geojson) must be
smoke-tested the same way: read the candidate file **with the importer's own
call signature** and assert the column/row count is what is expected, before
running the DAG. A repoint that silently yields zero regions is far more
dangerous than one that crashes.

## Blind spot

I validated the *parse* and the *annual totals*. I did NOT check that the
hourly shape for DE/DK/NO/UK is sane (peak/trough ratio, diurnal profile), nor
that `index_pick` in `demand_DB.py` - which builds its own hour list and has a
leap-day quirk - lines up with this file's index for wy2009. Those are cheap to
check and should be done before accepting Stage A results.
