# PREDICTION - 17-region companion run (controlled resolution comparison)

## Purpose
Produce a 17-region (BE+NL only) `INES_DB` that differs from the 21-region
mixed-resolution build in **resolution alone**. Achieved by narrowing
`countries` in `userconfig.yaml` to BE+NL and re-running `ines_builder` ONLY.
No data file, no source DB, no geojson, no workbook is touched.

Why this is a true control: `define_polygons` (ines_target.py L61-110) is the
sole consumer of `config["countries"]` (grep-verified, 1 call site). The 17 IC1
polygons in `IC1_NWEU.geojson` are geometrically identical to `IC1.geojson`
(0 mismatches, verified earlier). So BE/NL inputs are byte-identical.

## Predictions (register BEFORE running)

P1. `ines_builder` exits 0 in roughly the same ~41 min.
    Possibly faster - fewer polygons to iterate.

P2. Region count: onshore 17, offshore 6 (BE+NL OFF3 zones only).
    DE/DK/NO/UK revert to *stub* nodes, not full regions.

P3. **The headline test.** Every BE/NL-keyed parameter value that exists in BOTH
    the new 17-region DB and the 21-region DB is **bit-identical**, EXCEPT where
    a value is genuinely resolution-dependent. I predict the exceptions are
    confined to **cross-border link capacities / `link` entities** touching
    DE/DK/NO/UK, because those borders now terminate on stubs.
    -> Concretely: 0 differing values among `unit`/`node`-keyed parameters
       (investment_cost, fixed_cost, equality_ratio, flow_profile,
       profile_limit_upper, storage_*). Any nonzero count here falsifies P3
       and means something else still varies with the country list.

P4. Entity count drops from 17,027 to approximately the baseline 14,966
    (+ a little, since the new gas workbook has more network rows than the
    placeholder the old baseline used). I expect ~15,0xx-15,3xx, NOT exactly
    14,966. Predicting exactly 14,966 would be wrong because the old baseline
    read `Gas_Sectors_Dataset_IC1_placeholder.xlsx`.

P5. `harber-bosch` entities present in BOTH runs (84 in 21-region; expect ~68
    in 17-region = 4 per region x 17). It comes from the new gas workbook,
    which both runs share.

## Known blind spot in this prediction
I have verified the *regional entity loop* driver. I have NOT verified the
**independent cross-border link builder** (the path that produced the
AT/CH/CZ/FI/FR/IE/LU/PL/SE stubs - see FINDING_border_link_stubs.md). That
builder reads the gas network sheet directly and may NOT consult
`config["countries"]`. If so, the 17-region run will still contain DE/DK/NO/UK
*link* stubs. That is expected and acceptable - it is exactly the baseline
behaviour - but I must CHECK rather than assume, since misreading this builder
is what caused the P4 failure last time (blind-spot instance n).
