# FINDING: VRE aggregation is NOT required - the importer already supports PECD2

Found during PLAN step 2, by reading `VRE_DB.py` before writing aggregation code.
Scripts: `run_logs/_vre10.py`, `_vre11.py`.

## 1. The plan's premise was wrong
`PLAN_mixed_resolution_run.md` step 2 called for aggregating DE 7 + UK 6 + NO 5 +
DK 2 = 20 PECD2 regions down to 4 country nodes, weighted by `capacity`/
`potential`, and budgeted **1-2 days** for it as "the main new code".

**That work is unnecessary.** The VRE pipeline is already PECD2-native.

## 2. Evidence
`data-pipelines/europe/_variable-renewables/VRE_DB.py` builds regions from the
**Excel potential/capacity files**, not from a country list, and stamps every one
with GIS level `"PECD2"`:

```python
for poly in existing_wind_on.index:
    if existing_wind_on.round(2).at[poly, 2030] > 0 and poly in availability[tech].columns:
        add_region(db_map, poly, "onshore", "PECD2")
```

Gating condition is `poly in potential_*.index` **and** `poly in
availability[tech].columns`. Both now contain the 20 target regions:

| source | rows | IC1 | DE | DK | NO | UK |
|---|---:|---:|---:|---:|---:|---:|
| `potential_wind-on.xlsx` [Data] | 136 | 17 | 7 | 2 | 5 | 6 |
| `capacity_wind-on-existing.xlsx` [Regional_decomm_2025] | 143 | 17 | 7 | 2 | 5 | 6 |
| `wind-on-*.csv` headers | 136 | 17 | 7 | 2 | 5 | 6 |

All three agree. Existing 2030 onshore wind is populated and plausible, e.g.
DE01 18.328 GW, DKW1 3.958 GW, NOM1 2.173 GW, UK04 5.943 GW.

## 3. Consequence - keep PECD2, do not flatten
The four neighbours will enter the model at **PECD2 resolution** (20 regions),
not as 4 country nodes. This is *better* than the plan intended:

- No aggregation code, no weighting choice, no flattening risk. Risk #3 in the
  plan ("VRE aggregation flattening profiles") **disappears entirely**.
- Sub-country wind diversity is retained - DKE1 vs DKW1, the five Norwegian
  zones - which is exactly the diversity that sets firm-capacity need.

Cost: more regions than the "country level" wording of the original scope, so
a larger problem. Relevant to solve time (plan risk #1), which was already first.

## 4. What still must be checked
`add_region(..., "PECD2")` only covers the VRE store. The **other** sector
pipelines (demand, transmission, industry) must agree on the same region codes,
or the VRE nodes will dangle unconnected. `ines_builder`'s
`coupling_spatial_resolutions` / `mopo_resolutions` is where that is resolved -
verify before the rebuild.

## 5. Correction to my own prior claim
`ASSESSMENT_mixed_resolution_data.md` listed as a gap: "VRE at PECD2 but no
`PECD2_IC1`/`IC1_PECD2` sheets; `mopo_resolutions` hardcoded." The missing sheets
are real but **not blocking**, because no PECD2->IC1 conversion is needed - the
two resolutions coexist side by side in one file, which is precisely the hybrid
design.
