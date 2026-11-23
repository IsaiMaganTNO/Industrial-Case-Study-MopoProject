# PREDICTION - biomass coverage fix + global constraints (mixed-res run)

Registered BEFORE making changes.

## Context
`biomass_DB.py` maps NUTS3 -> IC1 using `region_transformation_IC1.xlsx`
sheet `NUTS3_IC1` (84 rows -> 17 targets). Rows whose source has no mapping are
DROPPED at L138 with only a warning; exit code stays 0.
`run_logs/02_biomass_importer.log`: "1440 source regions have no mapping to ic1
and will be dropped".

## Measured facts (source CSV, medium scenario, PJ)
    BE 175.1   NL 135.1   DE 1870.9   DK 149.0   NO 144.8   UK 1243.0
Rows carrying nuts3 == '-' (no NUTS3 code at all):
    BE 47.6    NL 48.8    DE 109.3    DK ?        NO 144.8 (ALL)   UK ?
Built biomass_db medium totals: BE 111.3 PJ, NL 68.0 PJ.
    => BE loses 63.8 PJ (36%), NL loses 67.1 PJ (50%).
This is a PRE-EXISTING defect in the 17-region baseline, not new.

## Predictions

P1. Adding DE/DK/UK NUTS3->country rows to `NUTS3_IC1` will produce
    biomass-stock__bio__{DE,DK,UK} with non-zero annual_production.
    CONFIRM: query biomass_db after re-run.

P2. NO will get ZERO or no entity from a NUTS3-only mapping, because all 132 NO
    rows have nuts3 == '-'. NO data exists only at NUTS2 (NO01..NO07).
    A NUTS2 fallback or explicit '-'-row handling is required.
    CONFIRM: check NO appears and totals ~144.8 PJ * (1 - any loss).

P3. The '-' rows are dropped for BE/NL today. If I ALSO fix those, BE/NL
    biomass RISES ~36%/50% and BE/NL results will shift vs the vre15 baseline.
    DECISION NEEDED: fixing it changes the BE/NL comparison basis.
    Prediction: BE medium 111.3 -> ~175 PJ, NL 68.0 -> ~135 PJ.

P4. `_split` will be 1 for every new row (each NUTS3 -> exactly one country),
    so no quantity dilution. CONFIRM: country totals in DB match CSV sums.

P5. CO2 budget 165.4 -> 1146.35 Mt(2030) / 254.745(2040) / 0(2050) will appear
    in INES_DB atmosphere `storages_existing` as y2030=1146.3525 (units: /1000).

P6. fossil-CH4 1102262/440905/220452 GWh. HAZARD: `limited_commodity` has a
    known 365x defect class (see FINDING_biomass_cap_365x_CONFIRMED.md).
    Must verify how scenario_setup applies it BEFORE trusting the number.
    Prediction: it is applied per-representative-day without /365 -> need check.

## Blind spot being guarded
I previously concluded "the 4 countries have no biomass data". FALSE - the
source CSV is pan-European (39 countries in nuts0). I had inferred coverage
from the OUTPUT DB instead of locating the region-loop driver. Instance #16.
Guard here: verify against the RAW CSV totals, not the DB, and check the
warning log of every importer re-run.
