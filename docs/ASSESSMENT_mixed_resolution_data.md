# Assessment: does `verification/Data - IC1 and PECD1` enable a mixed-resolution run?

**Verdict: yes for the data, with one caveat.** This directory is a near-complete
hybrid IC1 + country-level input set -- materially better than I assumed in
`docs/ASSESSMENT_spatial_resolution_options.md`, where I judged option B a
3-6 week data-acquisition problem. **That estimate is hereby revised down.**
The data is largely here. What remains is build/orchestration risk, plus one
missing region-mapping sheet.

~5 GB across 13 sector folders.

## 1. The key structural finding

Every region-keyed dataset uses the **same hybrid convention**: BE/NL carried as
the 17 IC1 clusters, every other country as a single PECD1/PECD2 region, with
**no duplicate bare `BE`/`NL` rows**. I checked this explicitly in each file
because double-counting would be the obvious failure mode:

| dataset | IC1 | country-level | bare BE/NL (must be absent) |
|---|---:|---:|---|
| `Rdemand/other_electricity_demand.csv` | 17 | 30 PECD1 | **none** |
| `Buildings/scenario_total_yearly_demands_GWh.csv` | 17 | 28 PECD1 | **none** |
| `Transport/fleets_per_scenario.csv` | 17 | 28 PECD1 | **none** |
| `Electricity_Transmission.csv` | 17 | 37 PECD1 | **none** |
| `Gas_Sectors_Dataset.xlsx` (CH4_Production) | 35 rows | 52 rows | **none** |
| `VRE_time_series/*.csv` (on/solar) | 17 | 103 PECD2 | **none** |
| `potential_wind-on/solar-PV.xlsx` | 17 | 104 PECD2 | **none** |

Decisive consistency check on gas -- IC1 clusters aggregate to **exactly** the
national totals (`data/Gas/Gas_Sectors_Dataset.xlsx`):

| technology | IC1 sum | national | ratio |
|---|---:|---:|---:|
| LNG-terminal BE | 669.0000 | 669.0000 | **1.0000** |
| LNG-terminal NL | 860.3000 | 860.3000 | **1.0000** |
| gas-extraction NL | 284.5479 | 284.5479 | **1.0000** |
| bio-diges-up NL | 8.5190 | 8.5190 | **1.0000** |

So the hybrid partitions the national totals rather than replicating them -- the
same conclusion as the earlier retracted "8.6x replication" claim, now confirmed
on the new file.

## 2. Sector-by-sector readiness

| sector | file | coverage | ready? |
|---|---|---|---|
| Residual electricity demand | `other_electricity_demand.csv` (197 MB, hourly from 1982) | 17 IC1 + 30 countries | **yes** |
| Buildings / heat | 5 CSVs incl. COP + demand timeseries | 17 IC1 + 28 countries | **yes** |
| Transport | `fleets_per_scenario.csv` | 17 IC1 + 28 countries | **yes** |
| Electricity transmission | `Electricity_Transmission.csv`, 251 links | 17 IC1 + 37 countries, with length/capacity/CAPEX/lifetime | **yes** |
| Gas (CH4 + H2) | `Gas_Sectors_Dataset.xlsx` | production/storage/network all hybrid | **yes** |
| VRE timeseries | 15 CSVs, ~4.5 GB | 17 IC1 + 103 PECD2 onshore; 61-70 offshore zones | **yes** |
| VRE potentials | 4 workbooks | 17 IC1 + 104 PECD2 | **yes** |
| VRE existing capacity | 3 workbooks | 39 PECD1 (country only) | **yes**, needs IC1 split |
| Power plants | `powerplants.csv` (20 MB, 158,548 units) | 36 countries, **lat/lon per plant** | **yes** -- geolocated, so assignable to any resolution |
| Conversion costs | `costs_2020/30/40/50.csv` | technology-level | **yes** |
| Industry | `technology_catalogue_..._update.xlsx`, `production_JRC_IDEES_nuts3.xlsx` | NUTS3 (386) + NUTS0 (31) | **yes** -- NUTS3 aggregates to either resolution |
| Biomass | `db_biomass_ener_mopo.csv` (16 MB) | 1,509 NUTS3, 39 NUTS0 | **yes** |
| Hydro | `EU_parameters_data...xlsx` + inflow/RoR 1980-2023 | 18 countries | **yes** |
| CO2 network | low + high cost workbooks | IC1 | **partial** -- see §4 |
| Cargo | `cargo_network.csv`, 145 links | country pairs | **yes** |
| Commodities | `commodity_data.csv` | prices + CO2 content, 14 carriers | **yes** |

Note the industry catalogue is an `_update` file, **not** the
`technology_catalogue_ind_nuts0_nuts3.xlsx` the repo currently uses. Contents
differ; it should be diffed before adoption rather than swapped in blind.

## 3. The one real data gap: PECD2 <-> IC1 mapping

`data-pipelines/europe/_ines-builder/region_transformation.xlsx` has
`PECD1_IC1`, `IC1_PECD1`, `IC1_NUTS3`, `NUTS3_IC1` -- but **no `PECD2_IC1` or
`IC1_PECD2` sheet.**

This matters because the VRE data (timeseries *and* potentials) is keyed at
**PECD2** (103-104 regions), not PECD1. `coupling_spatial_resolutions` in
`ines_target.py` hardcodes `mopo_resolutions = ["PECD1","IC1","NUTS3"]` -- PECD2
is **not in the list** (it is in the commented-out EU-case line).

Two options, neither large:
- Aggregate VRE PECD2 -> PECD1 before ingest (the `PECD2_PECD1` sheet exists), or
- Add the two missing sheets and put `PECD2` into `mopo_resolutions`.

The first is simpler and loses little, since neighbours are wanted at country
level anyway.

## 4. Smaller gaps

- **CO2 network is IC1-only.** Both cost workbooks cover IC1 regions; there is no
  CO2 transport topology for DE/FR/UK. For a mixed run, either keep the CO2
  network confined to NL+BE (defensible -- it is the case-study focus) or extend
  it. **Note these are the same two files already in `verification/`, so the
  earlier finding stands: the repo's active `CO2_data_IC1.xlsx` is byte-identical
  to the LOW-cost variant.**
- **Offshore mapping is BE/NL-only.** `OFF3_map` has IC1 values for just **6 of
  86** offshore zones. Neighbour offshore wind would land at country level, which
  is consistent with treating them at PECD1 anyway.
- **VRE existing capacity is country-level only** (39 PECD1, no IC1 column), so
  BE/NL existing fleet must be split across clusters. The companion files
  `Existing_GW_per_industrial_region.xlsx` and
  `Technical_potential_GW_per_industrial_region.xlsx` supply exactly those
  17-region shares (`share_of_inst_cap`, `share_of_potential`) -- so the split
  keys are present, just in a separate workbook.
- **No `Nuclear` or policy/global-constraint folder**, so CO2 budgets and the
  fossil-CH4 trajectory still come from `verification/global_constraints_...xlsx`.

## 5. Revised difficulty

| option | previous estimate | revised |
|---|---|---|
| A2 post-hoc 2-region aggregate | 2-4 days | unchanged (doesn't use this data) |
| A1 honest re-run, current scope | 1-2 weeks | **unchanged** -- still gated on never-executed pipeline |
| **B mixed resolution** | **3-6 weeks** | **~1.5-3 weeks** |

The reduction is entirely because the *data-acquisition* component -- which I had
flagged as the dominant cost -- is essentially already done, and done in exactly
the hybrid convention the IC1 level was designed for (recall `PECD1_IC1` already
carries 37 country identity rows).

**What has not changed, and is now the dominant risk:** the pipeline has never
been run end-to-end in this engagement; it is orchestrated as a Spine Toolbox DAG
(`EU_case/.spinetoolbox/project.json`, 96 KB) that we have not driven; and solve
time at ~23 regions with 2-3x the entities, on a model already taking ~88 min at
3 representative days, is a genuine unknown that may force temporal resolution
down.

> **CORRECTION (7 Oct 2026) -- the paragraph immediately above is wrong on its
> first two clauses.** The pipeline **has** been run end-to-end on this machine,
> and we do have the artefacts. The **repo root is itself a Spine Toolbox
> project** (`.spinetoolbox/project.json`, 59 items), and `.spinetoolbox/items/`
> contains populated per-sector databases: `ines_db` 656 MB / 14,966 entities,
> `vre_db` 403 MB, `transport_db` 418 MB, `spineopt_target` 156 MB / 21,016
> entities, plus `power_db`, `gas_db`, `industry_db`, `biomass_db`, `heat_db`,
> `rdemand_db`, `transmission_db`, `hydro_db`, `cargo_db`, `commodity_db`.
>
> I reached the false conclusion by searching only `data-pipelines/europe/**` and
> `EU_case/` -- the two places I expected the artefacts to be -- and treating
> their absence there as absence everywhere. `EU_case/` *is* an empty skeleton;
> that part was right. But it is not the project that was used.
>
> Consequence: a mixed-resolution build is a **re-run with different inputs**, not
> a first-ever run. Revised estimate **6-9 working days**; the dominant risks
> become VRE aggregation quality and solve time. See
> `docs/PLAN_mixed_resolution_run.md`.
>
> Resolution of those built stores was checked and they are the current IC1-only
> build (`vre_db` 17 IC1 + 50 offshore + 0 country; `transmission_db` 17 IC1 + 7
> country stubs), so they must still be rebuilt -- but the machinery is proven.

## 6. Recommendation

1. **Diff `Data - IC1 and PECD1` against the active `data/` tree first.** Several
   files are newer or larger supersets of what the repo uses (gas 87 vs 35 rows;
   industry catalogue `_update`). Establishing which inputs the *current* model
   was actually built from is a prerequisite -- and may itself explain open
   anomalies such as the 2030 coal switch.
2. **Resolve the PECD2 question** (aggregate to PECD1 -- cheapest).
3. **Prove the pipeline runs at current scope** before attempting the mixed run.
   This remains the gate; the data being ready does not de-risk the build.
4. Decide explicitly whether the CO2 network stays NL+BE-only.

## 7. Confidence

Measured: every coverage count, the absence of bare BE/NL rows in all seven
region-keyed datasets, the gas aggregation ratios (exactly 1.0000), the missing
`PECD2_IC1` sheets, the 6/86 offshore IC1 mapping, powerplant geolocation.

Not verified: whether the files are mutually consistent in *vintage* (e.g. gas
dataset vs industry `_update` may be from different rounds); whether the sector
pipelines accept these files without schema changes; whether `ines_to_spineopt`
and clustering are resolution-agnostic. **I have characterised coverage, not
correctness** -- the files could be complete and still disagree with each other.

---

## 8. Addendum: diff against the active `data/` tree (recommendation #1, executed)

Ran the diff this document recommended, because a vintage mismatch would
invalidate the readiness conclusion. Result: **the new files are supersets of the
active ones, with no contradicting values.** That is the reassuring outcome.

| new file | active file | verdict |
|---|---|---|
| `Gas/Gas_Sectors_Dataset.xlsx` (51.5 KB, 87 rows) | `data/Gas/..._IC1_placeholder.xlsx` (21.6 KB, 35) and `data/Gas/...xlsx` (26.5 KB, 56) | **superset** -- IC1 rows aggregate to national totals, ratio 1.0000 |
| `Industry/technology_catalogue_..._update.xlsx` (603 KB) | `data/Industry/technology_catalogue_ind_nuts0_nuts3.xlsx` (595 KB) | **superset**, see below |
| `CO2_network/CO2_data_IC1_low_cost.xlsx` | `_ines-builder/CO2_data_IC1.xlsx` | values identical (bytes differ) |

### Industry catalogue: what actually changed

Same 10 sheets. Six are unchanged in shape; three gained rows; one grew
substantially:

| sheet | new | old |
|---|---|---|
| `ind_process_routes_co2_capture` | **120** | **80** |
| `ind_production_2018_nuts3` / `_30_50_nuts3` | 6,670 | 6,666 |
| `ind_production_2018_nuts0` / `_30_50_nuts0` | 717 | 714 |
| `ind_process_routes_sec`, `_life`, `_co2_emission`, `_capex`, `_fom` | unchanged | unchanged |

The 40 added capture rows give CO2-capture coefficients to **nine "other
industry" sectors** that previously had none:

`pulp-and-paper`, `food-beverages-and-tobacco`, `non-ferrous-metals`,
`machinery-equipment`, `transport-equipment`, `textiles-and-leather`,
`wood-and-wood-products`, `ceramics-and-other-non-metallic-mineral-products...`,
`other-industrial-sectors`.

**Critically, the 77 shared rows have identical values in all four year columns
(2025/2030/2040/2050) -- zero changed entries.** So adopting the update cannot
alter any existing result; it can only *add* capture options. The three added
production rows are `glass` for CH, NO and UK -- i.e. neighbour countries, which
is precisely consistent with this being the mixed-resolution data round.

### Why this matters beyond the resolution question

`docs/FINDING_alternative_routes_unbooked.md` and the taxonomy gaps printed by
the deck build (`gas-extraction`, `Scraps_EAF`, `REF(H2)` and others falling
through to "Other") both touch the same area: industry routes that the model
carries but does not fully account for. The update supplying capture
coefficients for nine previously-uncovered sectors is **plausibly relevant to
those open items**, and is a cheap, low-risk change *because it is a pure
superset*.

**Not yet tested, and required before adopting it:** whether the pipeline reads
`ind_process_routes_co2_capture` for those nine sectors at all, or whether they
are filtered out upstream. Supplying a coefficient changes nothing if the sector
never reaches the builder. Do not assume the added rows will have an effect --
that is exactly the blind-spot pattern this project keeps hitting.
