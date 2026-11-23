# SURVEY: per-sector source-data coverage for DE/DK/NO/UK

Date: 2026-10-08. Evidence-based; no run launched.
Scripts: `run_logs/_rb1.py` .. `_rb9.py`.

## Headline

The Step 1 staging did more than I credited it for. Several staged inputs are
**already in exactly the hybrid shape this run needs**: IC1 cluster codes
(BEC1..BEC8, NLC1..NLC9) for BE+NL, and country or PECD2 codes for the rest of
Europe, *in one file*. This was not a coincidence - it is what the "hybrid
dataset" the colleague supplied actually is.

## Coverage table

| sector | source file | shape | DE/DK/NO/UK? |
|---|---|---|---|
| power | `Energy_Conversion/powerplants.csv` | pan-EU point data | YES - 36 countries, assigned by point-in-polygon |
| rdemand | `Rdemand/other_electricity_demand.csv` | **hybrid** 30 countries + 17 IC1 | YES (wired file is the restricted `_IC1` variant) |
| heat | `Buildings/scenario_total_yearly_demands_GWh.csv` | **hybrid** country cols + IC1 cols | YES |
| heat | `Buildings/peak_to_yearly_demand_ratios_MW_GWh.csv` | country cols | YES |
| heat | `Buildings/simplified_capacities_with_decommissioning_MW.csv` | country rows | YES |
| heat | `Buildings/cop-timeseries/*.csv` | **IC1 only, 17 cols** | **NO** |
| VRE | `VRE_greenfield.../potential_*.xlsx` | **hybrid** 136 = 17 IC1 + 119 PECD2 | YES but as **DE01..DE07 etc, not DE** |
| VRE | `VRE_installed.../capacity_*-existing.xlsx` | same 136-region hybrid | YES, same sub-country issue |
| VRE | `VRE_time_series/*.csv` | 136 region cols | YES, same sub-country issue |
| gas | `Gas/Gas_Sectors_Dataset.xlsx` | pan-EU country rows | YES (wired file is `_IC1_placeholder`) |
| hydro | `Hydro/EU_parameters_data_...xlsx` | country rows | PARTIAL - Reservoir: NO only; Pump: DE/NO/UK |
| hydro | `Hydro/Run-of-River .../*.csv` | 6 IC1 files only | **NO** |
| transport | `Transport/fleets_per_scenario.csv` | **hybrid** countries + IC1 | YES |
| transport | `Transport/fleet.csv` | IC1 only | **NO** (but superseded by the above) |
| transport | `Transport/non-road/*.csv` | 17 IC1 files only | **NO** |
| industry | `technology_catalogue_ind_nuts0_nuts3.xlsx` | NUTS3 + nuts0 sheets | YES at NUTS3 (DE11C...) and nuts0 |
| biomass | `Biomass/...` | NUTS-based, pan-EU shapefile | likely yes, not yet confirmed |
| transmission | already in `transmission_db` | - | YES (6 country stubs already present) |
| cargo | already in `cargo_db` | - | YES |

## The one genuine structural problem: VRE

Everything else is "repoint the Toolbox at the pan-EU file". VRE is not.

`VRE_DB.py` iterates `for poly in existing_wind_on.index` and writes whatever
region code it finds. With the staged workbooks that means it would emit
**DE01..DE07, DKE1/DKW1, NOM1/NON1/NOS1-3, UK01-UK05/UKNI** - 20 sub-country
PECD2 regions, not the 4 country regions the `IC1` sheet now defines.

`ines_builder` cannot rescue this. It picks the transformer sheet by
`f"{source_level}_{target_level}"`, and the VRE pipeline is configured
`source_resolution: {on: IC1, off: OFF3}`. Since source == target it takes the
**direct-lookup** branch and never aggregates. Asking it to aggregate would need
`source_resolution: on: PECD2` plus a `PECD2_IC1` sheet - **which does not
exist** (confirmed earlier: `PECD2_PECD1`, `PECD1_PECD2`, `PECD2_NUTS3`,
`NUTS3_PECD2`, `PECD1_IC1`, `IC1_PECD1` exist; `PECD2_IC1`/`IC1_PECD2` do not).
And flipping `source_resolution` to PECD2 would break BE+NL, whose data in
those same files is already at IC1 codes, not PECD2.

So VRE needs a **pre-aggregation step**: collapse the 20 sub-country columns to
4 country columns *before* `VRE_DB.py` reads them, leaving the 17 IC1 columns
untouched. That is a small, self-contained transform:
- potentials / existing capacity: **sum** the GW.
- availability timeseries: **capacity-weighted mean** of the hourly factors.
  The `PECD2_PECD1` sheet has a usable `capacity` weight column (its `area` and
  `population` columns are the constant-1.0 ones and must not be used).

## Secondary gaps, lower stakes

- **COP timeseries** (heat pumps) are IC1-only. Would need a country proxy.
- **Run-of-river** profiles are IC1-only; NO has 33.3 GW of hydro in the power
  fleet, so this matters for Norway specifically.
- **non-road transport** is IC1-only.
- **Hydro reservoir** parameters exist only for NO among the four.

## Recommendation

Do this in two stages rather than one big-bang rebuild.

**Stage A - repoint the easy sectors and prove the chain end-to-end.**
power (new geojson) + rdemand + heat + gas + transport-fleet. These are pure
input swaps. Accept that DE/DK/NO/UK get no VRE, no RoR and no non-road yet.
That is a *coherent* if incomplete model: thermal + hydro-pump + demand +
transmission. It will show whether the 21-region DAG builds and solves at all,
which is the real unknown.

**Stage B - add the VRE pre-aggregation** once Stage A builds, since it is the
only piece needing new code and should not be entangled with first-run
debugging.

Caveat on Stage A: without VRE the four countries are thermal-heavy, so their
marginal prices will be too high and BE/NL will under-import. Stage A results
are a **build/feasibility check, not a scenario result**. Do not interpret the
economics until Stage B lands.

## Blind spot

I have surveyed file *shape and region codes*. I have NOT verified that each
importer can parse the pan-EU variant it would be newly pointed at - delimiter
and date-format differences are a known hazard in this repo
(`other_electricity_demand.csv` uses `;` and `1-1-1982 00:00`, whereas the IC1
file uses `,` and `1/1/1982 0:00`). Each repoint must be smoke-tested
individually. Biomass coverage is inferred from its NUTS/pan-EU shapefile, not
measured.
