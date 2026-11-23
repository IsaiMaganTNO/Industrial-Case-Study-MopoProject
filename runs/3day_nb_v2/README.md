# Run 3day_nb_v2 - NL+BE IC1 baseline (SpineOpt, 2026-10-09)
The NL+BE industrial decarbonisation baseline: 17 IC1 regions, 3 representative days, milestones 2030/2040/2050, Gurobi.

## Contents
| Path | What |
|---|---|
| `RESULT_3day_nb_v2.md` | **Start here**: findings, sector routes, VRE, CO2, caveats |
| `RUN_3day_nb_v2.md` | How the model was built and verified |
| `input/Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite` | SpineOpt input DB (as solved) |
| `output/Investment_Results.3day_nb_v2.sqlite` | SpineOpt results DB |
| `plots/summary/` | 9 curated overview figures (recommended for slides) |
| `plots/report_v2/` | 9 detailed figures + PDF + CSV per sector |
| `plots/postprocess/` | 25 diagnostic figures (incl. maps) + PDF report + CSV tables |
| `logs/` | solve log, Gurobi log, results cache (pickle) |

## Key assumptions
- Scenario `baseline_blended_representative_periods` (weather year 2009, medium biomass, high CO2 storage, GA flex0); explicit scenario filter.
- CO2 budget NL+BE 165.4 / 36.8 / 0 Mt per year (2030 / 2040 / 2050).
- CO2 storage (high_CO2): NSNL012 0 -> 21 Mtpa, NSNL031 2.5 -> 6.2 Mtpa.
- No DAC; LNG import availability 1.0; NL gas extraction 0.
- New nuclear caps (TYNDP2024): BE 0/6/6 GW, NL 0/4/5 GW.
- Biomass from the corrected pipeline (BE 175 PJ, NL 135 PJ medium).
- Neighbours (DE, DK, NO, UK, FR, LU) are border nodes without a modelled energy system.

## Units
Energy TWh/yr; capacity GW; CO2 Mt/yr. Objective in model units (M EUR scaled).

