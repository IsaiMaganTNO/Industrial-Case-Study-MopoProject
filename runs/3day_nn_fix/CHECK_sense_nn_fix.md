# CHECK - sense check 3day_nn_fix (2026-10-09)
Scripts: `run_logs/_sc1.py`-`_sc3.py`.

## Sensible
- Penalties 0. The CO2 budget binds (36.8 Mt in 2040, 0 in 2050). Storage sits at its cap of 27.2 Mt from 2040. Captured CO2 equals injected (2.5 / 29.1 / 36.0 Mt).
- All 12 heavy-industry sectors reach clean, CCS or alternative routes by 2050. Chlorine (Diaphragm) and secondary steel (scrap EAF) are already electric.
- Heat: existing gas boilers are retired by 2050; heat pumps supply 78 TWh.
- VRE is present: offshore 71 / 166 / 320 TWh, solar 46 GW, onshore 10.8 GW.

## Odd / to watch
1. **Reporting:** offshore wind has no region (NaN), so NL+BE-filtered totals leave it out. Real electricity is 262 / 364 / 514 TWh, not about 190. Check the summary plots.
2. **New gas boilers:** 17.4 GW, 39 TWh fossil heat in 2050, offset by CCS storage.
3. **SMR+CCS:** concentrated in NLC2, 108 units in 2050, 16 Mt captured. H2 is supplied mostly by blue SMR, with PEM only in 2050.
4. **MOE** provides 57% of primary steel from 2040 (optimistic technology readiness).
5. **Ammonia** is 45% biomass-based.
6. **LH2 imports** are 20.5 TWh already in 2030.
7. 2050 still uses about 98 TWh of fossil LNG. Net zero holds only because of the 27 Mt storage.
