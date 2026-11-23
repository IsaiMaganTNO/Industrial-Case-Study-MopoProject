# FINDING - P3 BE/NL drift (571 values) RESOLVED

## Verdict
The 571 differing BE/NL parameter values are **NOT caused by the mixed-resolution
(21-region) change**. They are caused by the *input datasets themselves having been
replaced* when the mixed-res inputs were staged. Specifically a **newer, rounded
revision of two workbooks** was dropped in alongside the region repoints:

- `data/Energy_Conversion/assumptions.xlsx`  (12,927 B -> 39,132 B)
- `data/Gas/Gas_Sectors_Dataset.xlsx`        (27,142 B -> 52,736 B)

Evidence: every differing value is **identical across all 17 IC1 regions**
(BEC1..NLC9 share the same old->new number pair). A regional-resolution effect
cannot produce region-invariant deltas; a technology-parameter table change can.

## Breakdown of the 571 (script `run_logs/_rc28.py`)
Correcting an earlier mis-classification: the "89 SHAPE changes" were a **false
positive** of my parser - they are plain scalar floats which the JSON timeseries
decoder returned `None` for. All 571 parse fine. Nothing lost shape.

    parsed n=571   median rel change = 1.27e-05   p90 = 1.36e-01   max = 1.49e+00

    rel > 0.01 (n=119):  equality_ratio 51, investment_cost 34,
                         other_operational_cost 17, fixed_cost 17
    rel <=0.01 (n=452):  investment_cost 119, fixed_cost 102,
                         other_operational_cost 92, profile_limit_upper 57,
                         equality_ratio 31, flow_profile 17,
                         storage_fixed_cost 17, storage_investment_cost 17

### The 452 small ones = rounding only
New workbooks store **2-decimal rounded** figures where the old ones carried full
precision. e.g. `Technology_Costs` SMR capex `0.522201 -> 0.52`;
`Technology_Conversion` PEM 2030 `0.585 -> 0.59`, AEC `0.622 -> 0.62`.
Median 1.3e-05 is exactly this.

### The 119 larger ones = four genuine data revisions
1. `bio-diges-up+CC`: CH4 yield `0.5447 -> 0.60`, CO2 capture `0.132 -> 0.15`,
   fom `78,685 -> 78,007`. Drives the 17 `other_operational_cost` entries that
   roughly **double** (`0.003496 -> 0.007108`, rel 1.49) - the largest change in
   the whole set.
2. `DAC`: capex 2040/2050 `2.1/1.8 -> 3.0/3.0` (flat). Drives the 17
   `fixed_cost DAC_*__CO2_*` changes `[147.07, 98.05] -> [147.07, 147.07]`
   (rel 0.714). **DAC got materially more expensive post-2030.**
3. `DAC` second input switched `CH4 -> heat`. New DB has 84 DAC entities vs 68.
4. `bio-gasif-metha+CC` rows are now **all-NaN** in both `Technology_Costs` and
   `Technology_Conversion` -> the tech is dropped (0 entities in both DBs, so no
   regression, but the data gap is now in the costs sheet too).

### New techs introduced by the swap
- `harber-bosch` (elec+H2 -> NH3): **0 -> 84 entities** in `INES_DB`.
- `bioST+CC` added to `assumptions.xlsx` and to `units_new` in
  `Energy_Conversion/config.json` (16 -> 17). Still **0 entities** - not yet
  instantiated, so inert for now.
- `assumptions.xlsx` gained explicit `lifetime` for `bioST` 30, `geothermal` 30,
  `wasteST` 30, `SCPC` 40, `CCGT` 25, `nuclear-3` 80, `oil-eng` 25 (previously
  NaN -> defaulted). This is the source of the `equality_ratio` changes on
  `nuclear-3-existing_*` and `wasteST-existing_*`.

### flow_profile (17) and profile_limit_upper (57) - benign
- `flow_profile` on `elec_BEC*/elec_NLC*`: 26,280 points each, pointwise median
  rel **2.5e-04**, max **3.4e-03**, series sum `-64597.411 -> -64597.401`.
  This is the `;`->`,` re-export of the residual demand CSV losing a digit of
  precision. Immaterial.
- `profile_limit_upper` on BE/NL VRE: **pointwise max difference is exactly 0.0**.
  The BLOBs differ only in JSON float formatting / key encoding produced by the
  VRE aggregation re-write. Confirms `tools/aggregate_vre_to_country.py` left
  BE/NL numerically untouched, as designed.

## Consequence for comparability
BE/NL results from this run are **not** directly comparable to the
`vre15` baseline, but the reason is a deliberate (if accidental) input-data
refresh, not a resolution artefact. Two of the revisions are economically
material and will move results:
  - DAC 2040/2050 capex +43% / +67%  -> expect **less DAC**, higher CO2 prices.
  - `bio-diges-up+CC` opex ~2x, but CH4 yield +10% and capture +14%.

**Decision: treat this run as a NEW BASELINE.** Do not diff its BE/NL numbers
against `vre15`. If a clean resolution-only comparison is ever needed, restore
the two workbooks from `backups/data-pre-mixedres/` and re-run `ines_builder`.

## Blind spot caught (instance #15 avoided)
My working hypothesis had been "gas workbook swap + rdemand swap". That was only
half right - I had not checked `data/Energy_Conversion/assumptions.xlsx`, which
turned out to carry the `lifetime` and `bioST+CC` changes. The fix was to stop
hypothesising and do a **full md5 sweep of `data/` vs the backup**
(`run_logs/_rc29.py`), which surfaced 30 changed files, not 2.
