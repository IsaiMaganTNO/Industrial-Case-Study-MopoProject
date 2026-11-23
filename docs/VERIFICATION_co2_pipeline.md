# Verification log - CO2 emission pipeline defect

Date: 2026-10-01. **Read-only.** No database or pipeline code was modified.

Purpose: independently re-check the claims in `docs/FINDING_fuel_based_emissions.md`
before implementing any fix, per the instruction that "the source data should be OK,
but somewhere in the pipeline problems occur".

Reproduce with the scripts in `logs/_step*.py`, `logs/_db*.py`, `logs/_net.py`.

---

## 1. Source data - CONFIRMED CORRECT

`data/Industry/technology_catalogue_ind_nuts0_nuts3.xlsx`

| sheet | rows | cols |
|---|---:|---|
| `ind_process_routes_co2_emission` | 120 | `sector_id, Industry, to_node, emission, unit, 2025, 2030, 2040, 2050` |
| `ind_process_routes_co2_capture` | 80 | identical |

- Both keyed on `(Industry, to_node)`; **80 rows pair, 0 unit mismatches**
  (case-insensitive).
- Emission values are **already net of capture**. Verified across three families
  by checking that `emitted + captured` reproduces the unabated sibling:

| route | emitted | captured | sum | unabated sibling |
|---|---:|---:|---:|---:|
| `REF-SMR-MEA` | 0.002 | 0.017 | 0.019 | `REF-SMR` = 0.019 |
| `CEM2-(BMW)MEA` | **-0.308** | 0.650 | 0.342 | `CEM2-(BMW)` = 0.342 |
| `CEM2-(BMW)CaL` | **-0.188** | 0.530 | 0.342 | `CEM2-(BMW)` = 0.342 |
| `(NG)NH3-DEA` | 0.322 | 1.420 | 1.742 | `(NG)NH3` = 1.742 |

=> emission and capture must be written **as-is, with no subtraction**.

The BECCS negatives are internally consistent, which is strong evidence the sheet
is trustworthy.

### 1.1 Two data hazards for any fix

1. **Unit casing is inconsistent.** Emission sheet units are
   `tCO2_t`, `tco2_mwh`, `tco2_t`, `tco2_t_bricks_eq`, `tco2_t_ethylene_eq`,
   `tco2_t_lead_eq`, `tco2_t_paper_eq`. Note `tCO2_t` **and** `tco2_t`.
   Any unit comparison must be case-normalised.
2. **A `> 0.0` guard would silently corrupt the result.** In the 2030 column:
   26 rows are exactly 0 and **2 rows are negative** (the BECCS routes). The
   existing capture block uses `if value_param["y2030"] > 0.0:`. Copying that
   guard would drop both BECCS routes. The emission guard must be `!= 0.0`,
   or better, "row exists".

---

## 2. Pipeline - DEFECT CONFIRMED

### 2.1 The emission sheet is never read

`data-pipelines/europe/_industry-aidres/industry_DB.py::add_tech_parameters()`
reads `ind_process_route_life`, `ind_process_routes_capex`,
`ind_process_routes_fom`, `ind_process_routes_co2_capture`.
It does **not** read `ind_process_routes_co2_emission`. Confirmed by reading
lines 290-345.

### 2.2 Emissions are synthesised from fuel instead

`ines-spineopt/ines-spineopt/ines_to_spineopt.py::process_emissions()` (line 177)
assigns, for every unit drawing a commodity that carries `co2_content`:

```python
flow_ratio_equality_coefficient[(unit, "atmosphere", fuel, unit)] = co2_value[fuel]
```

The `co2_content` values in the INES DB are exactly four fuel properties:

| node | co2_content |
|---|---:|
| coal | 0.35 |
| waste | 0.30 |
| crude | 0.26 |
| fossil-CH4 | 0.20 |

No process-route property is consulted, so capture equipment cannot influence
the emission coefficient.

### 2.3 Confirmed in the solved model DB

`checkpoints/Final_SpineOpt_Model.tiny.1rep.repfix.sqlite` -
330 `atmosphere` `flow_ratio_equality_coefficient` rows:

| fuel | coefficient | units |
|---|---:|---:|
| coal | 0.35 | 209 |
| crude | 0.26 | 51 |
| waste | 0.30 | 38 |
| fossil-CH4 | 0.20 | 26 |
| (CO2 injection - see 2.4) | 1.0 | 6 |

All three refinery routes carry `atmosphere <- crude = 0.26`, including
**`REF(H2)`**, which is hydrogen-fired and should emit 0.016.

### 2.4 One claim NOT a defect - CO2 injection

The six `CO2-injection-*` units carry an atmosphere ratio of `1.0`, which looks
alarming. Resolving the entity elements shows the relationship is
`(injection -> CO2-storage) : (atmosphere -> injection)` - `atmosphere` is the
**input** side. This is geological removal and is correctly signed.
**No action needed.** Flagged here so it is not "fixed" by mistake later.

---

## 3. Scope of a fix - measured

From the model DB (1690 units total):

- 45 distinct emitting unit base names carry a fuel-based atmosphere ratio.
- **34 of them have route-specific emission data** -> should switch to route-based.
- **11 have no route data** -> must keep the fuel fallback:
  `LNG-terminal`, `SCPC-existing`, `coal-boiler-existing`, `gas-extraction`,
  `wasteST-existing`, and the 6 `CO2-injection-*` units.

Route-name to unit-name matching: **108 of 120** emission routes match a unit
base name. The 12 unmatched are all `steel-*` / `alumin*-reference|alternative`
aggregate rows, which are not instantiated as units in this case.

---

## 4. Where `CO2_captured` lands (the template to mirror)

`industry_DB.py` writes `CO2_captured` on
`technology__to_commodity__to_commodity = (industry, node, "CO2")`.

`data-pipelines/europe/_ines-builder/sysconfig.yaml` then maps it (lines 310, 361):

```yaml
technology__to_commodity__to_commodity:
  unit_flow__unit_flow:
    CO2_captured: [equality_ratio,1.0,[[1],[3],[1],[2]]]
```

i.e. keyed on **(technology, output-commodity)** with scaling factor `1.0` -
no unit conversion. This is why `0.017` arrives in the model DB unchanged, and
it is why mirroring this path for emissions is dimensionally safe.

Note line 93 uses a different index pattern `[[2],[3],[1],[2]]` for the
`commodity__to_technology__to_commodity` class - the correct pattern for the
emission mirror is the **line 310/361** one, `[[1],[3],[1],[2]]`.

---

## 5. Conclusion

The user's framing is correct: **the source data is fine; the pipeline is wrong.**

Two distinct, compounding pipeline defects:

1. **Route emission data is never ingested** (`industry_DB.py`).
2. **Emissions are fabricated from fuel content** (`ines_to_spineopt.py`),
   which is both technology-blind *and* dimensionally wrong - the ratio is
   applied per MWh of **input** fuel while the source is per unit of **output**.
   For refineries (`HC<-crude = 0.64`) this inflates emissions by
   `0.26 x 1.5623 = 0.406` tCO2/MWh HC against a true 0.019, i.e. **x21 to x203**.

Both must be fixed together. Fixing only (1) would double-charge, because the
fuel-based ratio from (2) would remain in place.

## S7. Full CO2 accounting verification (2026-10-06)

Exhaustive check of the patched 3-day DB against **both** source sheets.

| check | result |
|---|---|
| `ind_process_routes_co2_capture`, 43 non-zero 2050 rows | **43/43 present and value-exact** |
| `ind_process_routes_co2_emission`, 92 non-zero 2050 rows | **85/85 exact** for families that exist |
| families in sheet but **absent from model** | 7 (see below) |
| 2050 techs producing with zero CO2 | 3, all legitimately zero (elec/bio only) |
| double-booked (fuel AND route key) | **0** |
| 2050 mass balance | +157,462.0 / -157,462.0 = **NET -0.0** |

### The 7 "missing" families are NOT a defect

`alumina-production-{reference,alternative}`,
`aluminium-secondary-production-reference`, and the four
`steel-{electric-arc,integrated-steelworks}-{finishing,rolling}-reference`
rows carry non-zero factors in the sheet but have **zero entities** in the
model. They were never instantiated for NL+BE, so there is nothing to book.
Catalogue breadth, not a modelling error.

### Capture is represented, and my patch correctly left it alone

`patch_route_emissions.py` only ever touched `atmosphere` flows. The capture
sheet is realised **separately** as a `CO2` **output node** per unit, and all 43
coefficients already matched source. Had the patch also written capture rows it
would have double-counted.

### Methodological warning for future audits

A naive `LIKE '<family>_%'` match produced **6 false mismatches** - it caught
`-MEA` variants (e.g. `(LN)O` matching `(LN)O-MEA` = 0.111 instead of the true
`(LN)O` = 0.967, `BF-BOF` matching `BF-BOF-MEA` = 0.79 instead of 2.002). The
underlying data was correct in every case. **Suffix-bearing variants must be
excluded explicitly** before concluding a mismatch exists.
