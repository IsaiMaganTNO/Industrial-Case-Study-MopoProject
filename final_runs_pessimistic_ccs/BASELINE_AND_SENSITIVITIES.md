# Baseline and sensitivity runs (status 2026-10-28)

## Baseline
**Mixed resolution, 3 representative days, pessimistic CCS** — `mr_ccslow_ccu_cap16_dac0`
(folder `3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK`). Objective 7.607e6, OPTIMAL, penalties 0.

- NL+BE in 17 IC1 zones + DE, DK, NO, UK as one node each.
- One shared 6-country CO2 cap (`atmosphere`): 1146 Mt (2030), 255 Mt (2040), 0 (2050).
- Pessimistic CCS: scenario alternative `low_CO2` (storage caps) + high-cost CO2 tariffs
  (`verification/CO2_data_IC1_high_cost.xlsx`: pipelines x6, injection x1.2–4.7).
- NL storage NSNL012 set to 16 Mt/yr total NL in 2050 (in `low_CO2`).
- Fixes: DAC `existing_units = 0`; methanation CCU leak closed (0.2 t CO2/MWh synthetic CH4).
- Caches: `run_logs/mr_ccslow_ccu_cap16_dac0{,_NLBE,_xbbio}.pkl`.

Comparison runs at other resolutions (same assumptions; not sensitivities on this baseline):
`1_IC1_NLBE_17zones`, `2_CountryLevel_NLBE`.

## Sensitivity runs (each changes ONE thing vs the baseline)

| # | Sensitivity | Run / folder | Change vs baseline | Status |
|---|---|---|---|---|
| S1 | National CO2 caps, credit to emitter (**preferred**) | `5_MixedRes_CountryCO2caps_emitter_credit` (`ctryco2B_mr`) | Shared cap split into per-country caps (1990 × 45%/10%/0); cross-border CO2 carries its credit back to the exporter | Done. 7.785e6 (+2.3%), penalties 0, all caps met |
| S1b | National CO2 caps, credit to storage host | `4_MixedRes_CountryCO2caps_storagehost_credit` (`ctryco2_mr`) | As S1 but no credit transfer | Done. 8.70e6 excl. penalty (+14%); BE 2.0 Mt and DE 6.1 Mt over cap in 2050 → stress test only |
| S2 | 10 representative days | `runs/rp10_mr_noblend` (`rp10nb_mr_ccslow_ccu_cap16_dac0`) | 10 non-blended representative days instead of 3 | Done. 8.418e6 (+10.7%) |
| S3 | Optimistic CCS | `6_MixedRes_OptimisticCCS` (`mr_ccsopt_ccu_dac0`) | Scenario `low_CO2` → `high_CO2` (storage caps); CO2 tariffs back to low-cost file. DAC and CCU fixes kept. NL 16 Mt cap not applicable (it lives in `low_CO2`) | Done. 7.190e6 (−5.5%), penalties 0. 2050: 356 Mt stored (vs 135), more fossil+capture, less bio heat/offshore wind/electrolysis |

### Notes
- `runs/3day_mr_fix` was the old optimistic run but lacks the DAC fix, the CCU fix and the cap16 change.
  It is **not** a valid sensitivity; S3 replaces it.
- A/B comparison details: `run_logs/_ctryco2_all.out`; per-country cap check: `country_co2_balance.txt` in folder 5.
- 10-day details: `runs/rp10_mr_noblend/README.md`, `run_logs/_rp10nb_cmp.out`, `_rp10nb_routes.out`.

## S3 build check (`run_logs/_ccsopt_build.py` → `.out`)
- Scenario: `low_CO2` → `high_CO2` at rank 7.
- 132 values changed vs baseline (112 `connection_flow_cost`, 20 `vom_cost`); nothing added or removed.
- Tariffs vs `mr_fix`: 129 of 144 match exactly; the other 15 differ only by floating-point rounding (e.g. 0.00168378 vs 0.0016837800000000002), so effectively all match.
- All 16 `high_CO2` values identical to `mr_fix`; DAC `existing_units=0` (21) and methanation atmosphere links (21) kept.
