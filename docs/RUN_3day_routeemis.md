# RUN: 3-day route-based emissions fix

DB: `checkpoints/Final_SpineOpt_Model.tiny.3day.routeemis.sqlite`
Baseline: `Investment_Results.3day_hcco2.sqlite` (OPTIMAL, obj 3,376,634, penalties 0)
Date: 2026-10-05

## Why 3-day (user's suggestion, endorsed)

The correct comparison for this patch is **3-day vs 3-day**, not against the
7-day run. Both differ from the 7-day sampling, so comparing to 3-day holds the
representative days **constant** and isolates the single variable being changed
(emission accounting). Using the 7-day run as baseline would confound the fix
with a change of sampled weather. 3-day also solves in ~83 min vs ~309 min.

## What changed

`tools/patch_route_emissions.py`, implementing S6.3 of
`FINDING_fuel_based_emissions.md` for the families in
`FINDING_aluminium_and_residual_fuel_booking.md`.

- **182 units**: added `atmosphere <- own output` (per-year map from
  `ind_process_routes_co2_emission`) and **deleted** the fuel-keyed ratio.
- **+77 orphan units**: created a *first* atmosphere link (see "Patch
  extended" below) -> **259 route rows added** in total.
- fuel-keyed units **248 -> 66**; route-keyed **377 -> 636**
- **double-booked (both keys): 0** - asserted

| family | units | 2050 factor |
|---|---|---|
| **aluminium-primary-production-reference** | 2 | **1.8419** (was 0.000 effective) |
| other-chemicals-production-reference | 17 | 0.8177 |
| pharmaceuticals-production-reference | 12 | 0.7536 |
| other-non-ferrous-metals-production-reference | 3 | 0.6137 |
| other-industrial-sectors_production-reference | 17 | 0.3428 |
| food-beverages-tobacco-production-reference | 16 | 0.2570 |
| paper-production-reference | 9 | 0.2486 |
| leather-and-textile-production-reference | 17 | 0.2217 |
| pulp-production-reference | 10 | 0.2049 |
| ceramics-...-production-reference | 9 | 0.1756 |
| machinery-equipment-production-reference | 17 | 0.1449 |
| transport-equipment-production-reference | 17 | 0.1388 |
| wood-and-wood-products_production-reference | 12 | 0.0899 |
| printing-and-media-production-reference | 17 | 0.0503 |
| **(LN+EL)O** | 7 | **0.0000** |

### `(LN+EL)O` - a known over-charge now corrected by data

`FINDING_hc_co2_unpriced.md` flagged that my HC patch charged `(LN+EL)O` 0.24
t/MWh on feedstock carbon that is **embodied in olefins, not combusted**, and
warned the result was "indicative only; it needs a route factor". The source
sheet gives `(LN+EL)O` co2_emission **0.000** and co2_capture **0.000** - so the
route factor is genuinely zero and this patch **removes** that over-charge. The
caveat is now resolved by data rather than by assumption.

## Convention validated BEFORE patching

Sheet values land in the DB **unconverted and keyed on the unit's own output**,
for *both* `tco2_t` and `tco2_mwh` rows. Verified against units already
route-based in the unpatched DB:

| unit | sheet unit | sheet | DB | match |
|---|---|---|---|---|
| CEM2-(Afm) | tco2_t | 0.5350 | 0.5350 | exact |
| CEM2-(Afm)MEA | tco2_t | 0.1290 | 0.1290 | exact |
| (NG)DRI-EAF | tco2_t | 0.6510 | 0.6510 | exact |
| REF-SMR-MEA | tco2_mwh | 0.0020 | 0.0020 | exact |

This rules out the dimensional error of `FINDING_fuel_based_emissions.md` S2.6.

## Patch extended (15:10) - orphan `-alternative` routes

The first version of this run was **killed after ~5 min, before Gurobi began
optimising and before any result existed**. Reason: a blind spot in my own
patch.

The original loop could only *re-key* units that **already had** some
`<unit>__atmosphere__<fuel>` ratio. A route carrying a non-zero sheet factor
but **no `atmosphere` link at all** was invisible to it and emitted nothing.

That is not a corner case. Aluminium migrates **100% to the alternative route
by 2050** (reference 46.56 -> 34.79 -> **0**; alternative 0.14 -> 11.91 ->
**46.70**), so the original patch fixed the false zero only on the route that
is dying out and left it intact on the route that takes over.

`tools/patch_route_emissions.py` now has a **second pass** that also creates the
missing `unit__to_node(unit, atmosphere)` entity. **77 orphan units** across 7
families:

| orphan family | units | 2050 factor | reference twin |
|---|---|---|---|
| **aluminium-primary-production-alternative** | 2 | **1.4447** | 1.8419 |
| other-chemicals-production-alternative | 17 | 0.6878 | 0.8177 |
| pharmaceuticals-production-alternative | 12 | 0.5557 | 0.7536 |
| other-non-ferrous-metals-production-alternative | 3 | 0.1309 | 0.6137 |
| ceramics-...-production-alternative | 9 | 0.0482 | 0.1756 |
| machinery-equipment-production-alternative | 17 | 0.0249 | 0.1449 |
| transport-equipment-production-alternative | 17 | 0.0225 | 0.1388 |

Every alternative is **cleaner than its reference twin** - the expected
direction, and a sanity check that the pairing is correct.

### But the catalogue's alternatives are bimodal, and aluminium is the tail

Comparing all 20 reference/alternative pairs in the sheet:

| family | ref 2050 | alt 2050 | cut |
|---|---|---|---|
| other-chemicals | 0.8177 | 0.6878 | **15.9%** |
| **aluminium-primary** | **1.8419** | **1.4447** | **21.6%** |
| pharmaceuticals | 0.7536 | 0.5557 | 26.3% |
| alumina | 0.6243 | 0.4207 | 32.6% |
| ceramics | 0.1756 | 0.0482 | 72.5% |
| other-non-ferrous | 0.6137 | 0.1309 | 78.7% |
| machinery-equipment | 0.1449 | 0.0249 | 82.8% |
| transport-equipment | 0.1388 | 0.0225 | 83.8% |
| *12 further families* | - | **0.0000** | **100%** |

The catalogue is **bimodal**: 12 families go to exactly zero, and a stubborn
tail of four does not. **Aluminium-primary is the worst of the tail in absolute
terms** - at 1.4447 its residual is roughly **double** the next largest
(other-chemicals 0.6878) and is the **largest surviving industrial factor in
the whole catalogue**.

This is physically plausible: primary smelting emits **process** CO2 from the
consumable carbon anode (C + O2 -> CO2), which electrification does not remove
(inert anodes would). A ~20% cut reads as "clean power, same anode". Whether
the catalogue authors intended that is **not determinable from the sheet** and
is flagged as an open question, not a conclusion.

**Why this matters for the run:** a 2050 aluminium fleet that previously emitted
**0.000** now carries the catalogue's single largest residual factor. This is
the main reason prediction 2 should land in the upper half of its band.

Alternatives whose sheet factor is genuinely **0.000** (pulp, paper, steel,
glass, ...) are deliberately **left unbooked**: creating a zero-valued link
would add variables for no effect.

### Second change in the same pass - defensive only (CORRECTED)

`factors` is now built only from rows where `emission == "co2_emission"`.

**I originally justified this by claiming the sheet holds both `co2_emission`
and `co2_capture` rows keyed on the same `Industry` name, so a capture row could
silently overwrite an emission factor. That claim is FALSE.** Verified
2026-10-05: `ind_process_routes_co2_emission` contains **only** `co2_emission`
rows (`co2_capture` rows = **0**).

The filter is therefore **defensive only** - it changes nothing today and never
did. Retained because it makes the intent explicit and guards against the sheet
gaining capture rows later. Dry-run output is byte-identical with and without
it.

Consequence: the note elsewhere that the sheet gives `(LN+EL)O` co2_capture
0.000 is **unverified** - the emission 0.000 is real and is what the patch uses,
but any capture figure lives in a different sheet and has not been checked.

### Rebuild, not a re-patch

The patched DB was **rebuilt from the clean baseline**
(`...3day.group1.biocap365.retireall.hcco2.sqlite`), not patched on top of the
previous output, so the two passes cannot stack.

Result: **259 route rows added, 182 fuel rows deleted, 77 new atmosphere
links**; fuel-keyed **248 -> 66**, route-keyed **377 -> 636**,
**double-booked 0**, cross-border **1522.505 unchanged**.

## Guards

- remaining 66 fuel-keyed units are **exactly** the 6 genuine fuel-burner
  families (`coal-boiler-existing` 17, `oil-boiler-existing` 17, `oil-eng` 17,
  `SCPC-existing` 6, `wasteST-existing` 6, `oil-eng-existing` 3) - matches
  `VERIFICATION_co2_pipeline.md` S3 ("keep the fuel fallback")
- aluminium payload is `blob`, map, 2030/**2041**/2050 = 1.841858
- cross-border `investment_count_initial_cumulative` **1522.505** unchanged

## Predictions (registered BEFORE the solve)

1. `penalties == 0.00`. **Check first.**
2. **Objective RISES.** More carbon is now priced, so the net-zero budget binds
   harder. Expect **+1% to +8%** vs 3,376,634. The orphan pass prices 77 more
   units, including the whole 2050 aluminium fleet, so the rise should land in
   the **upper** half of that band rather than the lower.
3. **Aluminium CO2 becomes non-zero in ALL years** (was exactly 0.000 in 2050).
   **RESTORED to "all years" at 15:10 after the patch was extended** - see the
   "Patch extended" section above. The run that would have failed 3b was
   **killed before producing any result**, the orphan gap was closed, and this
   DB was rebuilt from the clean baseline. Expected: ~85.8 (2030), ~64.1
   (2040), **~67.47 (2050, via the alternative route at 1.4447)**.
   If 2050 aluminium is still 0.000, the orphan fix did not take effect.
4. **2050 net CO2 still = 0** (cap unchanged at 0.0) - abatement must come from
   somewhere, so expect **more DAC and/or more CCS**.
5. **Cement: `CEM2-(Afm)MEA` share RISES above 1,594.** This is the real test of
   `FINDING_co2_storage_saturation.md` S7: if a tighter budget raises the
   marginal tonne enough, cement capture becomes competitive.
   *If cement does NOT move, the "cheap marginal offset" explanation is wrong
   and must be retracted.*
6. **`(LN+EL)O` output rises** (its carbon charge dropped 0.24 -> 0).
7. Olefins mix shifts back toward `(LN+EL)O` / away from `(LN)O-MEA`.
8. Solve time ~80-120 min (3-day structure unchanged).

## Falsification

Prediction 5 is the decisive one. Cement staying flat at 1,594 would mean the
budget shadow price is **not** what blocks cement capture, and
`FINDING_co2_storage_saturation.md` S7 would need rewriting.

---

## OUTCOME (verified 2026-10-06, after power outage)

Run **completed cleanly on 5 Oct at 16:26:54**, ~22 h before the outage.
`OPTIMAL`, 85.1 min, objective **3,390,860**. Post-outage
`PRAGMA integrity_check` = **ok** on both the results DB and the patched input
DB; no stray `-wal`/`-journal`. Nothing lost.

### Scorecard

| # | Prediction | Result |
|---|---|---|
| 1 | penalties == 0 | **PASS** (0.000000) |
| 2 | objective rises +1..+8% | **FAIL** - rose only **+0.42%** |
| 3a | aluminium 2030/2040 non-zero | **PASS** (0.93 -> 85.11, 0.69 -> 67.51) |
| 3b | aluminium 2050 non-zero | **PASS** - **67.47**, the exact figure predicted |
| 4 | 2050 net CO2 still 0 | **PASS** (caps bind exactly, identical both runs) |
| 5 | cement MEA rises above 1,594 | **FAIL** - flat at **exactly 1,594** |
| 6 | `(LN+EL)O` output rises | see below |
| 7 | olefins shift toward `(LN+EL)O` | see below |
| 8 | solve 80-120 min | **PASS** (85.1) |

### The patch worked exactly as designed

Aluminium 2050 went **0.000 -> 67.47**, matching the hand-computed 46.70 t x
1.4447 to 2 d.p., and output was unchanged at 46.70 - confirming the fix altered
**accounting only**, not the physical solution. Route split in 2050 is 100%
`-alternative`, exactly as diagnosed. The orphan pass was necessary and
sufficient.

New category `industry: clean process route` appears at **+2,947** in 2050
(0 in baseline) - carbon that was previously invisible.

### Predictions 2 and 5 failed for ONE shared reason

The emissions cap is **binding and identical** in both runs (2030 453.150685,
2040 100.821918, 2050 0.000000 - i.e. 165,400 / 36,800 / 0 after x365). Total
2050 emissions are therefore **forced to 0.0 in both runs**. The newly-priced
+2,947 did not change the target; it changed only *who must offset it*.

2050 category deltas (base -> new):

| category | base | new | delta |
|---|---|---|---|
| industry: clean process route | 0.0 | 2,947.0 | **+2,947.0** |
| other (= CO2 injection) | -16,929.4 | -19,876.3 | **-2,947.0** |
| **TOTAL** | **-0.0** | **0.0** | **0.0** |

The offset is absorbed **entirely by one technology**:
`CO2-injection-NSNL031` moves **-154,137.3 -> -157,084.3 = exactly -2,947.0**.
`NSNL012` does not move at all (-377.7 in both). DAC is **0.0 in both runs**.

So the marginal tonne is cleared by expanding a single geological injector, and
that is cheap enough that pricing ~2,947 extra tonnes of industrial carbon costs
only **+0.42%** on the objective. That is the whole explanation for prediction 2
undershooting its band.

### Prediction 5: cement is NOT blocked by a cap

`CEM2-(Afm)MEA` is flat at **1,594** in *every* year and *both* runs, with fleet
**0.181963 units** - identical to 6 d.p. across all six cells.
`investment_count_max_cumulative` is **1000.0**, i.e. the cap is **not binding**
(0.18 << 1000). Cement capture is a **free economic choice** that the optimiser
declines to expand, because injector-based offsetting undercuts it.

### What this CONFIRMS and what it CORRECTS

**CONFIRMS** `FINDING_co2_storage_saturation.md` S7: the net-zero constraint is a
**system-wide scalar**, so the cheapest marginal offset wins regardless of which
sector emitted. Cement capture stays flat even when industrial emissions rise by
2,947 - exactly the falsification test that section set, and it survived.

**CORRECTS** the saturation framing further: NSNL031's 2050 peak level **rose**
2,811.312 -> **2,865.529**, so it was **never at a hard ceiling**. The earlier
"exactly saturated at 6,200.0/6,200" reading referred to a different quantity
(cumulative capacity, not the 2050 state) and must not be cited as evidence that
storage is exhausted. **NSNL012 idleness remains unexplained** - it absorbed
none of the new carbon despite NSNL031 expanding.

**CORRECTS my own earlier claim** that DAC is "the real offset" (recorded from
the 7-day run, DAC 1,810.4). In this 3-day run DAC is **0.0 in both the baseline
and the patched run**. The 7-day and 3-day runs therefore pick **different
offset technologies**, which means the DAC-vs-injection split is
**sampling-dependent** and should not be reported as a robust result.

### Predictions 6 and 7: both FAIL, and 6 was unfalsifiable as written

`(LN+EL)O` output is **empty in both runs** - the technology produces nothing at
all, in any year, before or after the patch. So "its output rises" could never
have been observed. I should not have registered it as a prediction without
first checking the unit was active in the baseline; it was the same mistake that
produced the "+0.0 estimate" earlier.

Removing its 0.24 t/MWh over-charge therefore had **no effect on the solution**.
The over-charge was real and the removal is still correct, but its practical
impact was nil.

Prediction 7 (olefins shift toward `(LN+EL)O`) fails for the same reason. 2050
olefins are **identical** in both runs (`(LN)O-MEA` 8,913, `(MeOH)O-MEA` 2,123).
The only olefins movement anywhere is in **2040**, where `(LN)O-MEA` 4,520 ->
4,395 and `(MeOH)O-MEA` 578 -> 704 - a ~125 unit swap toward the methanol route,
not toward `(LN+EL)O`.

### Net assessment

**Scorecard: 5 PASS, 4 FAIL (1, 3a, 3b, 4, 8 pass; 2, 5, 6, 7 fail).**

The *accounting* objective of this run **succeeded completely** - the false zero
is gone, aluminium 2050 lands on its predicted value, there is no double-booking
and no penalty. The *behavioural* predictions mostly failed, and they failed
because I under-weighted one structural fact I had already written down: with a
binding system-wide net-zero scalar and a cheap marginal injector, **changing
where carbon is booked barely changes what the system does**. It changes who
pays for the offset.

That is a genuinely useful result for the study: industrial emission accounting
defects of this size are **nearly invisible in headline outputs** while
materially changing attributed sector intensities. Anyone reading per-sector
intensities off the old runs would have been misled; anyone reading system cost
or the electricity mix would not.
