# FINDING - biomass pipeline silently discarded most of its input

## Severity: HIGH - affects the EXISTING 17-region baseline, not just the new run

`biomass_DB.py` maps NUTS3 -> IC1 via sheet `NUTS3_IC1` of
`data-pipelines/europe/region_transformation_IC1.xlsx` (set at L16,
`DEFAULT_IC1_REGION_MAP`). Any source region absent from that sheet is DROPPED
at L138 with a warning only; the tool still exits 0.

    run_logs/02_biomass_importer.log:
    WARNING: 1440 source regions have no mapping to ic1 and will be dropped

Two distinct losses resulted.

### Loss 1 - rows with no NUTS3 code (affects BE/NL baseline)
The source CSV `db_biomass_ener_mopo.csv` carries 1,521 rows where
`nuts3 == '-'`. These are NOT missing data - they are reported at a coarser
level: 1,435 resolve at NUTS2 and 86 at NUTS0. The importer has no fallback,
so all were discarded.

    medium scenario, PJ      source    built DB     lost
    BE                        175.1       111.3    36%
    NL                        135.1        68.0    50%

Half of Dutch biomass was missing from every run to date.

### Loss 2 - 15 BE/NL NUTS3 codes absent from the mapping sheet
`BE221 BE222 BE321 BE322 BE324 BE325 BE326 BE327 NL121 NL122 NL123 NL322
NL326 NL338 NL339` - 34.6 PJ (medium). These look like a NUTS revision
mismatch (2016 vs 2021 codes); every one has mapped siblings under the same
NUTS2 parent.

### Loss 3 - the four new countries
DE/DK/UK had full NUTS3 detail in the CSV all along (403/12/174 codes).
**NO has NO NUTS3 data at all** - all 132 Norwegian rows are `nuts3 == '-'`,
reported at NUTS2 (NO01..NO07). A naive NUTS3->country mapping would have
given Norway exactly zero biomass while appearing to succeed.

## Fix applied
1. `tools`-free, two artefacts:
   - `data/Biomass/db_biomass_ener_mopo_mixedres.csv` - identical to the
     original except `nuts3 == '-'` is backfilled with a synthetic parent code
     `"<NUTS2>~2"` or `"<NUTS0>~0"`. Row count, column order and total
     `quantity` are byte-for-byte preserved (verified).
   - `region_transformation_IC1.xlsx` sheet `NUTS3_IC1`: 84 -> 833 rows.
     Added real NUTS3 -> country rows for DE/DK/UK, synthetic parent codes
     -> country for all four, synthetic BE/NL parent codes -> their IC1
     children, and the 15 revision-mismatch codes -> sibling targets.
2. `project.json` repointed to the corrected CSV (2 occurrences).

The existing `_split` logic divides a parent's quantity evenly across its
mapped children, so BE/NL NUTS2-level rows are distributed over their IC1
regions rather than double-counted.

## Verification
Rebuilt `biomass_db`: 21 regions. Every country, every scenario, matches the
raw CSV sum to rounding:

    ctry  medium   high    low      (PJ, CSV == DB)
    BE     175.1   226.9   105.1
    NL     135.1   178.9    85.3
    DE    1870.9  2267.9  1356.6
    DK     149.0   271.0    98.8
    NO     144.8   244.1   114.0
    UK    1243.0  1637.5   532.8

Dropped-region warning fell 1440 -> 1019 (the remaining 1,019 are the other 33
countries, correctly excluded).

## CONSEQUENCE - BE/NL results will move
BE biomass +57%, NL +99% versus every previous run. Combined with
`biomass_potential_realistic: 0.5`, available biomass still roughly doubles for
NL. Given `docs/FINDING_biomass_dominance_zero_vre.md` (biomass already
dominating), this is likely to be a material result change, not a rounding one.
This reinforces treating the current build as a NEW BASELINE.

## For the authors
- `biomass_DB.py` should either implement a NUTS2/NUTS1/NUTS0 fallback chain
  (`SOURCE_RESOLUTION_PRIORITY` already exists but is only used to pick ONE
  level for the whole frame) or fail loudly when it drops rows belonging to a
  country that is in scope.
- The dropped-region warning prints every code, so the one line that matters is
  buried in ~1,400 lines of output. Exit code 0 throughout.
- `biomass_DB.py` reads `region_transformation_IC1.xlsx`, a DIFFERENT copy from
  the `_ines-builder/region_transformation.xlsx` used by `define_polygons`.
