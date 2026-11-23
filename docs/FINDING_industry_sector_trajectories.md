# FINDING: industrial sector trajectories 2030-2050 (7-day run)

Run: `Investment_Results.7day_hcco2_co2fix.sqlite` (OPTIMAL, penalties 0).
Date: 2026-10-05

## 1. Sector table (output, CO2, intensity tCO2/unit)

| sector | 2030 int | 2040 int | 2050 int | verdict |
|---|---|---|---|---|
| aluminium | 0.000 | 0.000 | 0.000 | **suspicious** - see S4 |
| ammonia | 1.311 | 0.126 | 0.088 | decarbonises (-93%) |
| **cement** | **0.416** | **0.338** | **0.444** | **REGRESSES** |
| chlorine | 0.210 | 0.210 | 0.210 | **frozen by my patch** |
| glass (container) | 0.338 | 0.256 | 0.010 | decarbonises (-97%) |
| glass (fibre) | 0.634 | 0.475 | 0.009 | decarbonises (-99%) |
| glass (float) | 0.487 | 0.367 | 0.013 | decarbonises (-97%) |
| olefins | 0.967 | 0.572 | 0.102 | decarbonises (-89%) |
| paper | 0.000 | 0.000 | 0.000 | already electric |
| pulp | 0.025 | 0.017 | 0.000 | decarbonises |
| steel (primary) | 2.002 | 1.531 | 0.267 | decarbonises (-87%) |
| steel (secondary) | 0.040 | 0.040 | 0.040 | **frozen by my patch** |

**Output is identical in all three years for every sector.** Industrial demand
is fully exogenous - the model chooses *routes*, never volumes. No fuel
switching away from NL+BE, no demand response, no efficiency. Correct by design,
but it means "industrial decarbonisation" here = route substitution only.

## 2. Cement is the only sector that gets WORSE

0.416 -> 0.338 -> **0.444**. Route history:

| year | routes |
|---|---|
| 2030 | `EU-mix-2018` 5,538 + `CEM2-(Afm)MEA` 1,594 |
| 2040 | `EU-mix-2018` 4,154 + `CEM2-(Afm)MEA` 1,594 + `LC3-(Afm)MEA` 1,385 |
| 2050 | **`CEM2-(Afm)` 5,538** + `CEM2-(Afm)MEA` 1,594 |

2040 is the *cleanest* year because `LC3-(Afm)MEA` (intensity 0.098) is built -
then **abandoned** in 2050. The capture route `CEM2-(Afm)MEA` is pinned at
exactly 1,594 in all three years and never grows.

## 3. Where the negative tonnes come from - user's framing refined

The 2050 offset is **not** "negative emissions somewhere else" in the
BECCS sense. Capture into `CO2` nodes, 2050 (total 6,177.7):

| source | captured |
|---|---|
| `CO2-injection-NSNL031` (re-entry) | 3,007.0 |
| **`DAC`** | **1,810.4** |
| `CCGT+CC` | 738.0 |
| `(LN)O-MEA` | 191.7 |
| `(NG)PEA-MEA` | 122.9 |
| `REF-SMR-MEA` | 81.6 |
| `(NG)DRI-EAF-MEA` | 79.2 |
| **`CEM2-(Afm)MEA`** | **15.8** |

**`DAC` is the genuine negative-emission source**, and it is the second-largest
capture term in the system. Cement capture contributes 15.8 - **0.26%**.

So the user's reading is **correct in substance**: the optimiser leaves cement
dirty and buys the offset elsewhere, predominantly via DAC. Note this also
revises the earlier claim that `DAC` had zero `atmosphere` flow - it does not.

## 4. Other strange outcomes

### 4.1 Aluminium emits exactly ZERO while burning four fossil fuels

`aluminium-primary-production-reference_NLC1` inputs:
**`CH4`, `HC`, `bio`, `coal`, `elec`**.
Its only `atmosphere` ratio is keyed on **`coal` = 0.35**.
Reported CO2: **0.000 in all three years** - because the route uses no coal.

**CH4 and HC combustion are entirely unbooked for this sector.** Aluminium
appears perfectly clean while burning gas and oil.

### 4.2 The fuel-based defect is still live in 21 unit families

Classifying every `atmosphere` flow ratio by whether it is keyed on a **fuel
input** (legacy, `FINDING_fuel_based_emissions.md`) or the unit's **own output**
(correct, route-based):

- **route-based: 70 families** (the S6.3 fix landed for these)
- **fuel-based: 21 families**, incl. `coal-boiler-existing` (17 regions),
  `oil-eng` (17), `oil-boiler-existing` (17), and ~10 `*-production-reference`
  families (leather/textile, machinery, other-chemicals, transport-equipment,
  printing, food-beverages, pharmaceuticals, wood, pulp, ceramics).

These reference units book on **coal only** while consuming CH4/HC/bio - the
same pattern as aluminium. Their emissions are understated by construction.

### 4.3 Two sectors are frozen by MY retirement patch, not by economics

`chlorine` (0.210 flat) and `steel (secondary)` (0.040 flat) never change route.
`run_logs/retire_screen_7day.csv` shows **7 BLOCKED: sole producer** units -
5 `Diaphragm_*` (chlorine) and 2 `Scraps_EAF_*` (secondary steel). These were
deliberately exempted from forced retirement to keep their nodes feasible.

**Consequence: these two sectors cannot decarbonise in any of my runs.** Their
flat intensity is an artefact of the patch and must not be reported as a result.
`Scraps_EAF` additionally books on `coal` (0.04) while running on CH4+coal+elec.

### 4.4 Chlorine is still mislabelled "electrolysis"

`Diaphragm` is chlor-alkali. It is the *only* electrolysis-class unit running
(0.152 units). **No water electrolysis for hydrogen is deployed anywhere.**
2050 H2 comes from `REF-SMR` (13,380 CO2) and `SMR+CC`.

## 5. What is genuinely credible

Ammonia, all three glass sectors, olefins, pulp and primary steel all show
monotonic decarbonisation of 87-99%, driven by MEA/CCS and H2/electric route
substitution. Those trajectories are plausible and route-based.

---

## CORRECTION (2026-10-05): aluminium / non-ferrous line is INVALID

Any aluminium or non-ferrous-metals intensity reported above must be
discarded. Two stacked defects mean the booked figure is near-zero
regardless of actual activity:

1. The reference route was fuel-keyed on `coal`, a fuel it never
   consumes (false zero).
2. The alternative route - which carries 100% of 2050 aluminium output -
   has **no atmosphere link at all**, so it is unbooked even after the
   route-emissions patch.

True aluminium CO2 should be ~85.96 (2030), 81.28 (2040), 67.47 (2050),
i.e. a modest ~21% decline, NOT the decarbonisation the booked numbers
imply. See `FINDING_alternative_routes_unbooked.md`.

All OTHER sectors in this document are unaffected: none of them route
output through an unbooked alternative route (verified by checking output
on all 7 unbooked families with a non-zero source factor - only
aluminium has non-zero output).
