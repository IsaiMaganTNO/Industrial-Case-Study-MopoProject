# FINDING: aluminium false zero + residual fuel-based booking (scope & fix plan)

Run: `Investment_Results.7day_hcco2_co2fix.sqlite`. Date: 2026-10-05.
Extends `FINDING_fuel_based_emissions.md` (the S6.3 route fix landed only partly).

## 1. Aluminium: a true accounting hole

`aluminium-primary-production-reference_NLC1` flow ratios (output per unit input):

| input | ratio | booked? |
|---|---|---|
| `CH4` | 0.574 | **NO** |
| `HC` | 10.396 | **NO** |
| `bio` | 1044.197 | n/a (biogenic) |
| `coal` | 17.545 | yes |
| `elec` | 0.075 | n/a |

Its **only** `atmosphere` ratio is `...__atmosphere__coal__... = 0.35`.
The route consumes **no coal in the solution**, so reported CO2 = **0.000 in
all three milestones** while it burns CH4 and HC.

### The correct factor exists in the source data and is LARGE

`data/Industry/technology_catalogue_ind_nuts0_nuts3.xlsx`,
sheet `ind_process_routes_co2_emission`:

| Industry | unit | 2025-2050 |
|---|---|---|
| `alumina-production-reference` | tco2_t | 0.624331 |
| **`aluminium-primary-production-reference`** | **tco2_t** | **1.841858** |
| `aluminium-secondary-production-reference` | tco2_t | 0.255066 |

**1.84 tCO2/t is booked as 0.00.** This is the largest single mis-booking found
so far. (Physically right: primary aluminium's carbon anode consumption is a
*process* emission, independent of fuel - precisely what a fuel-keyed ratio
cannot express.)

Note `ind_process_routes_co2_capture` has **no** aluminium rows and its
`sector_id` list covers only cement/chemical/fertiliser/glass/refineries/steel,
so there is no capture route for aluminium - consistent, not a second defect.

## 2. Scope of the residual defect: 175 units, 21 families

Classifying every `atmosphere` ratio as **fuel-keyed** vs **route-keyed**:

- **route-based: 70 families** - the S6.3 fix landed
- **fuel-based only: 248 units**, of which **175 consume a carbon fuel that is
  never booked**, across **21 families**:

| family | units | source factor 2050 |
|---|---|---|
| leather-and-textile-production-reference | 17 | 0.2217 |
| machinery-equipment-production-reference | 17 | 0.1449 |
| other-chemicals-production-reference | 17 | **0.8177** |
| other-industrial-sectors_production-reference | 17 | 0.3428 |
| printing-and-media-production-reference | 17 | 0.0503 |
| transport-equipment-production-reference | 17 | 0.1388 |
| food-beverages-tobacco-production-reference | 16 | 0.2570 |
| pharmaceuticals-production-reference | 12 | **0.7536** |
| wood-and-wood-products_production-reference | 12 | 0.0899 |
| pulp-production-reference | 10 | 0.2049 |
| ceramics-and-other-non-metalic-minerals-prod | 9 | 0.1756 |
| paper-production-reference | 9 | 0.2486 |
| other-non-ferrous-metals-production-reference | 3 | **0.6137** |
| **aluminium-primary-production-reference** | **2** | **1.8419** |

**15 of 21 fuel-based families have route data available.** The 6 that do not
are genuine fuel-burners where the fuel key is **correct** and must be kept:
`SCPC-existing`, `coal-boiler-existing`, `oil-boiler-existing`, `oil-eng`,
`oil-eng-existing`, `wasteST-existing`. This matches
`VERIFICATION_co2_pipeline.md` S3 ("11 have no route data -> keep fuel fallback").

## 3. Method note - a naive scan over-counts

A first pass flagged 175 units including `REF-SMR` (crude 5,486), `CCGT+CC`
(CH4 820) and `DAC` (CH4 461) as "unbooked". **That was wrong.** Those are
*route-based* units that legitimately book on their own output, so their fuel
inputs are deliberately not keyed. Only units with **fuel-keyed ratios and no
route-keyed ratio** are defective. Always separate the two modes before counting.

## 4. Chlorine and secondary steel: user's assumption CONFIRMED

Checked directly - these are **not** artificially constrained by the screen
beyond reality:

- `chemical-chlorine` producers in the whole DB: **`Diaphragm` only** (5 units)
- `steel-secondary` producers: **`Scraps_EAF` only** (2 units)
- No `Membrane`/`Mercury` chlor-alkali variants exist anywhere in the catalogue.

So `n_alternatives = 0` in `retire_screen_7day.csv` is **factually correct**;
blocking their retirement was right and unavoidable. **However** the earlier
statement that their flat intensity is "an artefact of my patch" is only half
right: the patch keeps them alive, but even without it there is **no cleaner
route to switch to**. The flat trajectory is a **catalogue gap**, not a patch
artefact. Correction recorded.

`Diaphragm` is chlor-alkali and still mislabelled "electrolysis"; it books
`atmosphere <- CH4 = 0.21` and does consume CH4, so that one is **correctly**
fuel-keyed.

## 5. Recommended fix order

1. **Aluminium + the other 14 route-data families** - mirror the S6.3
   route-based pattern: write `atmosphere <- <own output>` from
   `ind_process_routes_co2_emission`, and **delete the fuel-keyed ratio** for
   those units so carbon is not double-booked. 175 units.
2. Keep the fuel key for the 6 genuine fuel-burner families.
3. Re-solve and re-check cement: adding ~1.84 t/t on aluminium and 0.82 on
   other-chemicals **raises the shadow price of the net-zero budget**, which may
   on its own make `CEM2-(Afm)MEA` competitive. Cement should therefore be
   re-assessed **after** this fix, not before.

## 6. Why cement is probably downstream of this

`FINDING_co2_storage_saturation.md` S7 concluded cement is left dirty because
the system buys a cheaper offset elsewhere (DAC 1,810 vs cement capture 15.8).
That trade depends on the **marginal** cost of a tonne. With 175 units currently
emitting free, the budget is artificially loose and the marginal tonne is
artificially cheap. **Fix the accounting first; re-judge cement afterwards.**
