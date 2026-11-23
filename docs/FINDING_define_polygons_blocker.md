# FINDING: the real blocker is `define_polygons`, not VRE or `mopo_resolutions`

Step 2 investigation, concluded. Scripts: `run_logs/_reg1.py` .. `_reg5.py`.
Supersedes the "add PECD2 to mopo_resolutions" hypothesis in
`FINDING_vre_no_aggregation_needed.md` S4.

## 1. How regions are actually selected
`ines_target.py:define_polygons()` (L61-111) builds the region set as:

```python
on_poly = region_data[on_level][region_data[on_level].country == country_id].id.tolist()
```

`on_level` is the pipeline's `target_resolution` from `userconfig.yaml`. **Every
pipeline is set to `IC1`** (VRE is `{on: IC1, off: OFF3}`).

So the region list comes from the **`IC1` sheet** of
`region_transformation.xlsx`, filtered by country.

## 2. The blocker
The `IC1` sheet contains **17 rows: BE (8) and NL (9) only**.

| sheet | rows | BE | NL | DE | DK | NO | UK |
|---|---:|---:|---:|---:|---:|---:|---:|
| `IC1` | 17 | 8 | 9 | **0** | **0** | **0** | **0** |
| `PECD1` | 39 | 1 | 1 | 1 | 1 | 1 | 1 |
| `PECD2` | 126 | 3 | 4 | 7 | 2 | 5 | 6 |

`ines_target.py` L63-93 **already lists DE/DK/NO/UK/FR as uncommented
countries**, and has done all along. They produce nothing because
`region_data["IC1"].country == "DE"` matches **zero rows**.

**Un-commenting countries was never going to be sufficient.** That was step 3 of
the plan and it is a no-op on its own.

## 3. Corollary: the sector stores are consistent, not conflicting
Measured region codes in the built stores:

| store | IC1 | country-code | note |
|---|---:|---:|---|
| `power_db`, `heat_db`, `biomass_db`, `transport_db` | 17 | 0 | IC1 only |
| `rdemand_db` | 17 | 15 | |
| `transmission_db` | 17 | **6** | `DE DK FR LU NO UK` |
| `gas_db` | 17 | 4 | |
| `vre_db` | 17 | 0 | 77 others are **offshore sea zones** (`NS`/`BAL`/`ATL`), not PECD2 |

The DE/DK/NO/UK entries in `transmission_db`/`gas_db` are **2-letter PECD1-style
country stubs** - the dead boundary nodes. Nothing currently emits PECD2 onshore
codes, so there is no code clash today; the clash would be *created* by moving
VRE to PECD2 while the rest stay at IC1.

## 4. Two viable routes

**A. Country-level neighbours (matches the agreed scope).** Add DE/DK/NO/UK as
single rows to the `IC1` sheet, reusing their PECD1 geometry. The existing
`PECD1_IC1` sheet already has identity rows DE->DE, DK->DK, NO->NO, UK->UK, so
aggregation from PECD1 source data resolves cleanly. Smallest change; 21 onshore
regions exactly as scoped; keeps every pipeline on one resolution.

**B. PECD2 neighbours.** Richer (20 regions, retains DKE1/DKW1 and the five
Norwegian zones) but requires `IC1` to carry 20 new rows, `PECD2_IC1`/`IC1_PECD2`
sheets to be authored (**currently missing**), and `mopo_resolutions` extended.
Larger problem, more solve time, more new artefacts.

**Recommendation: A.** It is what was scoped, it is a data edit rather than a
code change, and B can be revisited later without rework.

## 5. Correction to my own prior claim
I wrote in `FINDING_vre_no_aggregation_needed.md` that "the VRE pipeline is
already PECD2-native" and that `mopo_resolutions` was the blocker. **Both are
wrong.** `VRE_DB.py` does call `add_region(..., "PECD2")`, but that writes the
*source* `vre_db` store; `ines_builder` subsequently aggregates to the pipeline's
`target_resolution`, which is `IC1`. `mopo_resolutions` governs only
cross-resolution *network link* creation, not region existence.

What remains correct from that finding: **no VRE time-series aggregation code is
needed** - `ines_aggregrate` does the weighting internally, driven by the
transformer sheets.
