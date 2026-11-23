# SCAN - workbook limits vs model (2026-10-09)
Source: `verification/global_constraints_industry_case_study.xlsx`, two sheets (`userconfig.yaml`, `scenario_config.yaml`).
Model checked: `checkpoints/Final_SpineOpt_Model.tiny.3day.nodac.sqlite` and `scenario_config.yml`.

| # | Workbook item | Workbook values | In the model? | Status |
|---|---|---|---|---|
| 1 | CO2 budget per country (45% / 10% / 0% of 1990) | NL 99.8/22.2/0, BE 65.6/14.6/0, NO 22.8/5.1/0, DE 563/125/0, DK 32.3/7.2/0, UK 362.8/80.6/0 Mt | Only as a single **summed** budget (NL+BE 165.4/36.8/0; six countries 1146/254.7/0) | Applied as a total; no per-country split |
| 2 | Nuclear-3 max invested capacity (GW; comment: TYNDP2024) | NL 0/4/5, BE 0/6/6, UK 6/11/13, NO/DE/DK 0/0/0 | **No.** Only a pan-EU 120/150/180 cap in the inactive `limited_nuclear-3` alternative | **Missing** |
| 3 | Refinery trajectory (bio / syn shares of ~2,800 PJ/yr NL refinery capacity) | bio 0.10/0.25/0.25, syn 0.02/0.20/0.65 | **Yes:** `biofuels` / `synfuels` investment groups in Base | Applied (the workbook flags NL potential as "quite high; we might want to restrict this?") |
| 4 | Flex in industry | comfort_industry **0.2**, flex_industry 0.1 | `flex_industry` alternative active; config comfort_industry **2.0**, flex 0.1 | **Possible mismatch** (0.2 vs 2.0; units unclear) |
| 5 | `fossil-CH4` volume limit (Pan-EU scaled by the CO2 budget share) | six-country 1,102,262 / 440,905 / 220,452 GWh; NL+BE 159,000 / 63,600 / 31,800 | In `limited_fossil-CH4`, **inactive** | Missing (needs a /365 check before use) |
