# FINDING: Alternative-route emissions are entirely unbooked

**Status:** CONFIRMED defect. Found 2026-10-05 while the 3-day `routeemis`
solve was running. This is a **second, independent defect** and also a
**blind spot in `tools/patch_route_emissions.py`**.

## 1. Observation that triggered it

The pre-run impact estimate (`run_logs/_est.py`) returned delta +0.0. The
summary recorded this as "patched families show zero output in `prod`".
That diagnosis was **wrong**. The families are present in `prod`; the real
cause is narrower and more interesting:

    prod aluminium-primary-production-reference by year
      2030  count 144  sum 46.563682
      2040  count 144  sum 34.790416
      2050  --- NO ROWS ---

`_est.py` only evaluated `year == 2050`. The reference route is fully
retired by 2050, so the lookup was empty. Not a frame defect.

## 2. Where the output actually goes

    aluminium sector output by year
      2030  reference    46.563682   alternative     0.136189
      2040  reference    34.790416   alternative    11.909456
      2050  reference     0.000000   alternative    46.699872

Demand is exogenous and constant (46.7), so this is pure route
substitution: the model migrates primary aluminium from the reference
route to the alternative route between 2030 and 2050.

## 3. The defect

The source sheet `ind_process_routes_co2_emission` gives:

    aluminium-primary-production-reference     1.841858 tco2_t
    aluminium-primary-production-alternative   1.444697 tco2_t   <-- NOT zero
    aluminium-secondary-production-reference   0.255066 tco2_t
    aluminium-secondary-production-alternative 0.000000 tco2_t

The alternative route is only ~21.6% cleaner than the reference. But in
the database:

    alternative routes booked to atmosphere:   0
    reference routes booked to atmosphere:   525

**Every single `-alternative` unit in the model (175 of them) has no
`atmosphere` link whatsoever.** Not a wrong coefficient - no link at all.

## 4. Why my patch did not catch it

`patch_route_emissions.py` builds its candidate set from `fuelkeyed`,
which is populated by scanning entities matching `%__atmosphere__%`. A
unit with **no atmosphere link at all never enters that scan**, so it can
never become a target. The patch could only ever *re-key* existing
bookings; it structurally could not *create* a first booking.

This means the earlier verification "double-booked = 0, fuel-keyed
248 -> 66, route-keyed 377 -> 559" was sound but **incomplete** - it
audited only the units already inside the scan.

## 5. Scale

Unbooked units with a non-zero source factor:

    family                                                     n   2050 f
    aluminium-primary-production-alternative                    2   1.4447
    other-chemicals-production-alternative                     17   0.6878
    pharmaceuticals-production-alternative                     12   0.5557
    other-non-ferrous-metals-production-alternative             3   0.1309
    ceramics-and-other-non-metalic-minerals-production-alt.     9   0.0482
    machinery-equipment-production-alternative                 17   0.0249
    transport-equipment-production-alternative                 17   0.0225
    TOTAL                                                      77

The other 98 unbooked alternative units (paper, pulp, food, textile,
printing, wood, other-industrial) have a genuine 0.000 factor in the
sheet, so those are correct as-is.

Alternative routes carry **11.3% of 2050 industry output**, but most of
that is paper (4,641.6) and pulp (552.0), both legitimately zero.

## 6. Aluminium: the quantified miss

    year   ref out    ref CO2    alt out    alt CO2    TRUE total   model books
    2030     46.56      85.76       0.14       0.20         85.96        0.929
    2040     34.79      64.08      11.91      17.21         81.28        0.694
    2050      0.00       0.00      46.70      67.47         67.47        0.000

Two compounding errors:
1. The reference route was fuel-keyed on `coal`, which the route never
   consumes - hence 0.929 instead of 85.76 (the original aluminium
   false-zero defect, already documented).
2. The alternative route is unbooked entirely - hence the 2050 zero
   survives even after the route-emissions patch.

So the `routeemis` patch fixes 2030/2040 aluminium but **leaves 2050 at
exactly zero**, because by 2050 all output has migrated to the unbooked
alternative route.

## 7. Consequence for the running solve

**Prediction 3 of `RUN_3day_routeemis.md` ("aluminium CO2 becomes
non-zero") will FAIL for 2050 and PASS for 2030/2040.** Registering this
here before the solve finishes so the prediction is judged honestly
rather than retro-fitted.

Decarbonisation of aluminium in this model is therefore still largely an
accounting artefact: the model "decarbonises" by moving to a route whose
emissions are simply not counted, not by abating 1.44 -> 0.

## 8. Not yet done

A follow-up patch must create atmosphere bookings for the 77 units.
This requires *creating* `unit_flow__unit_flow` entities rather than
re-keying them, so it is a different code path from the current patch.
Deliberately NOT applied mid-solve.

## 9. Contamination is confined to aluminium

Checked output on all 7 unbooked-with-nonzero-factor families:

    family                                    2030     2040     2050  missed CO2 2050
    aluminium-primary-production-alternative  0.14    11.91    46.70            67.47
    other-chemicals-production-alternative       -        -        -                -
    pharmaceuticals-production-alternative       -        -        -                -
    other-non-ferrous-metals-prod.-alt.          -        -        -                -
    ceramics-...-production-alternative          -        -        -                -
    machinery-equipment-production-alt.          -        -        -                -
    transport-equipment-production-alt.          -        -        -                -

    TOTAL missed CO2:  2030 = 0.20   2040 = 17.21   2050 = 67.47

The other six families have **zero output in every year** - the model
never builds them - so although they are latently mis-specified, they do
not currently distort any result. The defect is live only for aluminium.

This **limits the blast radius** of
`FINDING_industry_sector_trajectories.md`: the reported ammonia, steel,
olefins, glass, pulp/paper, cement, chlorine and steel-secondary
intensities are *not* affected by this defect, because none of those
sectors route output through an unbooked alternative. Only the
aluminium/non-ferrous line in that document must be treated as wrong.

Caveat: the six silent families are a latent trap. If any future scenario
(different costs, tighter caps) makes them economic, they would supply
output at zero booked carbon and look like free decarbonisation. They
should be fixed even though they are currently inert.
