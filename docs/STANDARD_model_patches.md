<!-- filepath: docs/STANDARD_model_patches.md -->
# STANDARD patches - apply to EVERY model build from now on

Any new test-run DB must have these applied, in this order, or results are
not comparable with the current baseline.

| # | patch | tool | why |
|---|---|---|---|
| 1 | route emissions | `tools/patch_route_emissions.py` | process CO2 keyed on output, not fuel |
| 2 | CO2 cap /365 | `tools/patch_co2_cap_div365.py` | representative-period scaling |
| 3 | biomass cap /365 | `tools/patch_biomass_cap_div365.py` | same |
| 4 | industry retirement | `tools/patch_retire_industry.py` | reference plants must retire |
| 5 | HC CO2 | `tools/patch_hc_co2.py` | hydrocarbon carbon content |
| 6 | **CO2 bidirectional** | **`tools/patch_co2_bidirectional.py`** | **NEW - mandatory, see below** |

## 6. CO2 bidirectional network - MANDATORY as of 2026-10-07

**Decision:** standard in all future runs (user instruction, 2026-10-07).

**Why:** `CO2_data_IC1.xlsx!network` is an *undirected* edge list (171 rows =
171 undirected pairs, **0 reverse twins**, carries symmetric `km` + tariff),
but `ines_target.py` writes one *directional* INES link per row. CO2 was the
only commodity in the model with 0 reverse twins (CH4 88/91, H2 88/89).
Consequence: `CO2_BEC6` had **no out-edges**, Belgium could not reach any
injector, and Belgian CCS was **infeasible rather than uneconomic**.
Full write-up: `docs/FINDING_co2_network_unidirectional.md`.

**Usage:**

```powershell
.\.venv\Scripts\python.exe tools\patch_co2_bidirectional.py SRC.sqlite DST.sqlite
# add --dry-run to preview
```

**Expected output** (35-connection network): creates 35 reverse connections ->
`CO2 connections now: 70`, guard unchanged, `self-checks OK`, `integrity: ok`.

**Post-conditions to verify before trusting a run:**

- CO2 connections 35 -> **70**, reverse twins **70**
- `CO2_BEC6` directed closure **1 -> 17**; BEC6/BEC7 reach all 3 injectors
- cross-border guard `investment_count_initial_cumulative` on class
  `connection`: **327 rows, sum 1522.5048 UNCHANGED**
- `PRAGMA integrity_check` = ok

**Known pitfall (already fixed in the tool):** `parameter_value.type` must be
written as `'float'`, not NULL. A NULL type leaves the value in SQLite but can
be dropped by the Spine reader, producing links with **no tariff and no flow
ratio** - a silent failure that passes every graph/reachability check. The tool
now self-checks that `type` is uniformly `'float'` and exits non-zero otherwise.

**Validated by:** `docs/RUN_3day_co2bidir.md` - OPTIMAL, penalties 0,
obj -1.747%, BE->NL CO2 export 0.0 -> 55,853.9 kt in 2050, BE capture 14.4x,
mass balance closes to exactly 0.0.

**Caveat that travels with this patch:** CO2 pipelines carry **no capacity
limit**, so cross-border transport is congestion-free and capture may look
easier than reality.

## Latent inert caps - recurring pattern

Three volume/capacity caps exist in the DB but sit in alternatives that are **not** in the
active scenario `baseline_blended_representative_periods`
(Base, wy2009, medium_bio, current, GA, GA_flex0, high_CO2, flex_buildings,
flex_buildings_wy2009_current, flex_industry):

| alternative | what it would limit | status |
|---|---|---|
| `limited_fossil-CH4` | fossil gas volume budget | **inert** |
| `limited_nuclear-3` | nuclear build (120) | **inert** |

Always check `scenario_alternative` before concluding a cap binds or that a technology was
"allowed but not chosen". See `FINDING_gas_supply_overstated.md` and
`FINDING_offshore_wind_and_nuclear_absent.md`.

## 21-region (mixed-resolution) tool changes - 2026-10-09
Tools generalised for regions `(BE|NL)C\d` + country-level `DE|DK|NO|UK` (all regression-checked on 17-region vre15 - identical):
- `patch_route_emissions.py` (base regex), `screen_retirement.py` (REG), `postprocess.py` (REGION / REGION_ANY).
- `patch_onshore_vre_potential.py`: HIST floors for DE/DK/UK (NO none); caps never raised; guard only with `--expect-guard`.
- `patch_gas_availability.py`: LNG-terminal_% 0.5 for all 19 terminals; gas-extraction 0 for **NL only**.
- `patch_co2_bidirectional.py`, `patch_co2_cap_div365.py` (now also divides `storage_investment_count_initial_cumulative`): IDs resolved by name.
- `preflight_check.py --cap-below N`.
- **Cross-border guard for mixed-res builds: 377 rows, sum 2532.8882** (17-region guard unchanged).

## 9. CO2 storage-site caps /365 - MANDATORY as of 2026-10-09
Tool: `tools/patch_co2_storage_div365.py SRC DST`. Why: `docs/FINDING_co2_storage_cap_365x.md`
(site caps were 365x too loose in every earlier run, incl. vre15 and mixedres).

## Scenario patch (not standard): `tools/patch_nodac_lng.py`
DAC `investment_count_max_cumulative` -> 0; LNG availability -> 1.0 (NL extraction stays 0).
Used for the "nodac" runs (2026-10-09).

## 10. Per-country nuclear new-build caps - MANDATORY as of 2026-10-09
Tool: `tools/patch_nuclear_country_caps.py SRC DST`. Source: workbook `set_technology_buildout`
(TYNDP2024): NL 0/4/5, BE 0/6/6, UK 6/11/13, NO/DE/DK 0 GW. Adds investment groups
`nuclear-3_<CC>` (new-build units only, existing plants excluded), Base alternative, stamped
2030/2040/2050 so the 2040 cap binds from 2040. Other workbook limits deliberately NOT applied
(see `docs/SCAN_workbook_limits.md`; for later sensitivities).
