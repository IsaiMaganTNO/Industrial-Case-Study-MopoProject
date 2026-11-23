# 5 – Mixed resolution, per-country CO2 caps, credit to emitter (Option B)

Base: run 3 (MR 3-day, `mr_ccslow_ccu_cap16_dac0`), atmosphere split per country as in run 4.
Change vs run 4: the 70 cross-border CO2 pipelines also move one tonne of "atmosphere credit" from the
importer's `atmosphere_<importer>` to the exporter's `atmosphere_<exporter>` (fix_ratio_out_in_connection_flow = 1).
So a country that exports CO2 for storage gets the credit for it.

Caps (Mt): 1990 emissions × 45% (2030), 10% (2040), 0 (2050). Source: `verification/global_constraints_industry_case_study.xlsx`.

Result: OPTIMAL, 2 h 39 min, objective 7.785e6 (+2.3% vs run 3), **no balance penalty**.
Every country is at or below its cap in every year (see `country_co2_balance.txt`; leftover differences of about 0.1 Mt come from rounded block weights).
2050: DE exports 49 Mt, NL 30 Mt and BE 24 Mt; NO, UK and DK are the net hosts of storage.

Build script: `run_logs/_ctryco2B_build.py`; check: `run_logs/_ctryco2B_pen3.py`.
