# FINDING: existing-plant retirement dates are random (power_DB.py)

Found during PLAN step 0 (baseline reproduction). Scripts: `run_logs/_pdbchk.py`,
`_pdbdiff2.py`, `_pdbagg.py`, `_pp3.py`, `_pp5.py`.

## 1. Symptom
Re-running the unchanged Toolbox DAG on unchanged inputs did **not** reproduce the
baseline. `Power_DB` entities were byte-identical (md5 `9d1d0cab51e0`) but 29
`units_existing` time series changed. Downstream: `INES_DB` +16 entities,
`SpineOpt_target` +18.

National totals are **not conserved** - this is not a reshuffle:

| | OLD | NEW | diff |
|---|---:|---:|---:|
| BE y2030 | 9,778 MW | 11,731 MW | +1,953 |
| BE y2040 | 3,746 MW | 5,666 MW | +1,920 |
| NL y2030 | 6,273 MW | 12,214 MW | **+5,941 (+95%)** |
| NL y2040 | 2,101 MW | 3,175 MW | +1,074 |

## 2. Root cause - a quoted string literal
`data-pipelines/europe/_power/power_DB.py` L1489 / L1493:

```python
datein_ppm  = float("DateIn")    # should be float(unit_ppm["DateIn"])
dateout_ppm = float("DateOut")   # should be float(unit_ppm["DateOut"])
```

`float("DateIn")` always raises `ValueError`, so both are caught and set to
`None` for **every one of the 158,548 plants**. In `decay_capacity()` (L1336):

- branch 1 `if unit["date_out"]` - never taken
- branch 2 `elif unit["date_in"] and lifetime` - never taken
- branch 3 `else: randomyear = random.choice(milestoneyears)` - **always taken**

The retirement year of every existing plant is therefore a **uniform random draw
over {2030, 2040, 2050}**, re-drawn on every pipeline run, and the real source
columns are discarded. The source data is populated: of 722 NL+BE plants, 546
have `DateIn` and 48 have `DateOut`.

`random` is never seeded (`import random`, L58), so runs are irreproducible.

## 3. Why this matters
It is not a small noise term. It lands on two live conclusions:

- **`nuclear-3 BE y2030` 4,710 -> 5,765 MW (+1,055)**. The BE nuclear asymmetry
  finding (`FINDING_nuclear_BE_vs_NL_asymmetry.md`) rests on this fleet.
- **`SCPC` (coal) NL y2030 3,358 -> 6,023 MW (+79%)**. Open item "investigate the
  2030 coal switch" may be substantially a random draw.

The `vre15` results are a self-consistent solve of **one random fleet draw**, not
a reproducible baseline. Any mixed-resolution comparison would be confounded by a
multi-GW random term far larger than the effect being measured.

## 4. Correction to my own earlier claim
I first attributed the drift to "non-deterministic geolocation in
`power_importer`" and sized it at "+-2 units". Both were wrong: geolocation is
deterministic (entity sets identical), and exposure is the entire existing fleet
(~66,000 MW NL+BE), not ~1.4 GW. The 1.4 GW figure counted only plants missing
*both* date columns in the source, which is irrelevant once the bug forces all
plants down the same branch.

## 5. Recommended fix
Two separate changes, in order:

1. **Seed** `random.seed(...)` - makes runs reproducible. Necessary but **not
   sufficient**: it freezes an arbitrary fleet rather than a correct one.
2. **Fix the lookup** to `float(unit_ppm["DateIn"])` / `["DateOut"]` so real
   retirement dates are honoured. This is the actual correction.

Note a second latent bug in `decay_capacity` L1345-1346: the guard tests
`unit["date_in"]` but the body reads `unit["DateIn"]` - a different key, which
will `KeyError` once dates start flowing. Must be fixed at the same time.

**Raise with authors.** This is an upstream pipeline defect, not a local
modelling choice.
