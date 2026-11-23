# PREDICTION: power_DB date fix + seed

Registered BEFORE applying the fix. See `FINDING_random_retirement_dates.md`.

## Changes to apply
1. `random.seed(20261008)` at module import, so any residual random branch is
   reproducible.
2. L1489/1493: `float("DateIn")` -> `float(unit_ppm["DateIn"])`, same for
   `DateOut`. Guard non-numeric/blank.
3. L1346: `unit["DateIn"]` -> `unit["date_in"]` (latent KeyError once dates flow).

## Predictions

P1. **Determinism.** Two consecutive `power_importer` runs after the fix produce
    byte-identical `parameter_value` md5. (Pre-fix they differed:
    `98310ece7624` vs `b93da1766e7e`.)

P2. **Branch shift.** Of 722 NL+BE plants, 546 have `DateIn` and 48 have
    `DateOut` in source. After the fix the random branch should take **well under
    25%** of plants, versus 100% now.

P3. **NL 2030 existing capacity falls below the 12,214 MW random draw.** Real
    retirement dates should retire less of the fleet before 2030 than a uniform
    draw over {2030,2040,2050}, which kills ~1/3 of capacity immediately. I
    expect NL y2030 to RISE above both prior draws (6,273 / 12,214) because most
    plants have DateIn + long lifetimes and so survive to 2030.
    **Direction uncertain - this is the prediction most likely to fail.**

P4. **Nuclear BE y2030 becomes stable** across runs (was 4,710 vs 5,765).

P5. **No KeyError / no crash**; `power_importer` exits 0 and `Power_DB` keeps
    350 entities / 157 parameter values (entity set is unaffected by dates).

P6. **Downstream drift disappears**: re-running `ines_builder` twice after the
    fix gives identical `INES_DB` counts.

## Falsification
If P1 fails, something else is non-deterministic and the seed is not the only
issue. If P5 fails with a KeyError at L1346, the latent bug was real and my fix
was incomplete.

---

# OUTCOME (8 Oct 2026)

| | prediction | result |
|---|---|---|
| P1 | determinism after seed | **PASS** - two runs, md5 `0cbf70ce6f14` both |
| P2 | random branch < 25% of plants | **PASS** - 0% once dates are read |
| P3 | NL y2030 rises above 12,214 MW | **FAIL** - collapsed to 1,565 MW |
| P4 | BE nuclear stable across runs | **PASS** (stable, but value 0) |
| P5 | no KeyError, entity set stable | **PASS** - exit 0, 350 entities, md5 `9d1d0cab51e0` |
| P6 | downstream drift disappears | **PASS** - `INES_DB` reproduced bit-for-bit |

**5 of 6 pass. P3 failed, and I had flagged it as the one most likely to fail.**

## Why P3 failed - and why the date fix was NOT adopted
Fixing the lookup makes `DateIn + catalogue lifetime` binding. The NL+BE fleet is
old:

| fuel | median DateIn | capacity | +25y | +40y |
|---|---:|---:|---:|---:|
| Hard Coal | 1968 | 10,630 MW | 1993 | 2008 |
| Nuclear | 1975 | 6,794 MW | 2000 | 2015 |
| Natural Gas | 1997 | 22,045 MW | 2022 | 2037 |

So coal and nuclear retire decades before 2030 and BE nuclear goes to exactly
zero. Arithmetically correct, physically wrong: `DateRetrofit` exists in the
source and is never read, and Belgium's Doel 4 / Tihange 3 have a legislated
extension to 2035.

**Neither state is right.** The random fleet was irreproducible; the
date-corrected fleet is reproducible but implausible. Hence the decision to
**pin to the `vre15` fleet** instead - constant, and identical to the baseline
every published result so far has used.

The code fixes remain in `power_DB.py` (they are correct in themselves and are
overwritten by the pin for NL+BE), but a proper life-extension convention -
`max(DateIn, DateRetrofit) + lifetime`, plus known extensions - is needed before
the corrected dates can be used. **Out of scope for this run; raise with
authors.**
