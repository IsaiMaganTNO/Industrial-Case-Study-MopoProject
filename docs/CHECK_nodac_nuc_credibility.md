# CHECK - credibility of 3day_nodac_nuc as baseline (2026-10-09)
Scripts: `run_logs/_nv1.py`-`_nv3.py` (cache `run_logs/nodac_nuc.pkl`).

## CO2 storage fix: confirmed
| Site (cap Mtpa) | vre15 2030/40/50 | nodac_nuc 2030/40/50 |
|---|---|---|
| NSNL031 (6.2) | 9.2 / 66.9 / 73.5 | 2.5 / 2.5 / 6.2 |
| NSNL012 (21) | 0 / 0 / 0.01 | 0 / 6.5 / 21.0 |
In 2050 both sites are at their cap (27.2 Mt). Capture equals injection in every year (2.5 / 21.9 / 32.9 Mt); the rest of the captured CO2 is used.
NSNL031 2040 = 2030 value (2041 timestamp caveat).

## Industry decarbonisation (route shares, NL+BE)
- Steel: BF-BOF 100% (2030) -> 0% (2040). MOE 57% + NG-DRI-EAF-MEA 43%.
- Olefins: 100% unabated -> 33% MEA (2040) -> 100% MEA (2050).
- Ammonia: NG 79% -> 0% (2040); bio 56%, H2 44%.
- Cement: Oxy-MEA 96% already in 2030.
- Glass: CCS route from 2040. Paper uses the alternative route from 2030. Chlorine is all Diaphragm.
- Output is identical in all years (exogenous demand).
- Residual industry emissions in 2050 are about 6.9 Mt gross (CCS residuals, other-chemicals alt 1.3, ceramics 0.8). They are offset by storage.

## 2050 net-zero balance
LNG-terminal fossil CH4 +19.9, industry about +6.9, electrolysis +0.3; storage -27.2 -> 0.
Atmosphere budget: 2050 binding (0); 2030 emissions 165 Mt.

## Credibility flags
1. Speed: the 2030 shifts happen instantly (cement oxy-CCS 96%, paper 100% alternative) while only 2.5 Mt is stored. Check whether the 2030 capture/route costs and availability limits are realistic.
2. Technology readiness: MOE (molten-oxide electrolysis) provides 57% of primary steel from 2040, which is optimistic.
3. 2050 still uses about 100 TWh of fossil LNG, enabled by storage.
4. 2040 = 2030 inputs for storage/budget (2041 timestamps).
5. Methodology: 3 representative days, perfect foresight; DE/UK interaction missing (IC1 only).
6. Chlorine 100% Diaphragm and ammonia 56% bio: check bio-feedstock limits.
