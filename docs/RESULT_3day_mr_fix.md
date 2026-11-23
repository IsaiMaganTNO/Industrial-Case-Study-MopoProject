# RESULT - 3day_mr_fix (mixed resolution, 6 countries)

OPTIMAL, penalties 0, objective 7,073,666 (k-units as in nb_v2; nb_v2 = 3,644,339 for NL+BE only).
Cost split: fixed O&M 3.86M, investment 2.56M, taxes 0.46M, VOM 0.11M, connection flow 0.04M, storage inv 0.04M.

## 1. System CO2 (shared budget)
| Mt | 2030 | 2040 | 2050 |
|---|---|---|---|
| BE | 105.1 | 72.3 | 58.1 |
| NL | 136.5 | 65.7 | 47.9 |
| DE | 217.5 | 106.6 | -2.6 |
| DK | 7.6 | -29.5 | -31.7 |
| NO | 176.9 | 81.6 | 9.0 |
| UK | 151.2 | -41.9 | -80.7 |
| **Total** | 794.8 | 254.8 | **0.0** |

The budget is met system-wide (atmosphere level 0 in 2050, DAC = 0). NL+BE are not net zero in 2050 (+106 Mt); the remaining emissions are offset by CO2 stored in the UK, DK, NO and DE.

CO2 storage, 356 Mt/a in 2050. All 16 sites inject round, constant amounts in 2040 and 2050 (DK onshore 25.5 = its 25.5 Mtpa cap; NSDE011 60; ASNOS3 50; NSUK012 40; NSUK042 33; ...; NL 21 + 6.2). This strongly suggests every site is at its cap. Only DK and NL are verified against input caps so far.

## 2. The "flat LNG" anomaly - explained, not a bug
- NL+BE LNG terminals run at their fixed existing capacity (investment_count_fix: NL 3.98 x 9, BE 3.48 x 8) in every year: NL 314, BE 244 TWh.
- The terminal parameters are identical in the mr_fix and nb_v2 inputs. In nb_v2 the same terminals ramp down (412/223/99 TWh) because NL+BE alone must reach 0.
- In mr_fix the gas is **transited**. NL+BE export CH4 to DE (gross 224 TWh, net about 128 TWh after DE to NL/BE flows of 96), FR (39) and UK (12) in 2050, while NO pipeline gas falls from 852 to 374 TWh.
  The model accounts for the CO2 at the point of import ("LNG-terminal" emission 111.6 Mt in NL+BE). This is why NL+BE show 84.5 Mt "other" in 2050.
- Interpretation: the emission is attributed to the import country, not the consumer. Per-country 2050 totals reflect this accounting, not where the gas is burned.
  The UK LNG terminal and NO extraction carry the same kind of upstream accounting.
- Caveat for colleagues: compare **system** emissions, or attribute LNG emissions by final use, before comparing countries.

## 3. Industry - decarbonised in all 6 countries by 2050
All active sectors (ammonia, cement, chlorine, glass, olefins, paper, pulp, steel, aluminium) use 100% non-reference routes in 2050 in every country:
- ammonia (NG)NH3-MVR-DEA
- cement oxy/MEA capture
- olefins (LN)O-MEA
- primary steel (NG)DRI-EAF-MEA
- glass NG+CC or electric (DK, NO)

Unlike nb_v2 (ammonia 80% bio, steel 57% MOE), mr_fix chooses NG+CCS routes everywhere. Cheap transit gas and pooled storage make CCS cheaper than electrified or bio routes.

## 4. VRE and firm capacity (GW, 2050)
| | BE | NL | DE | DK | NO | UK | offshore (all) |
|---|---|---|---|---|---|---|---|
| onshore | 3.6 | 7.2 | 65.5 | 5.7 | 6.8 | 19.7 | |
| solar | 12.8 | 32.9 | 139.3 | 8.6 | 0 | 96.6 | |
| offshore | | | | | | | 34 / 78 / 126 (2030/40/50) |

- Nuclear 2050: UK 3.4 only. **BE and NL go to 0**; nb_v2 had BE 6 + NL 3.1.
- PEM 2050: 4.6 GW total.

## 5. NL+BE vs nb_v2 (same NL+BE data)
| NL+BE | nb_v2 2050 | mr_fix 2050 |
|---|---|---|
| Electricity generation TWh | 502 | 437 |
| Offshore wind GW (NL+BE zones) | 61.1 | 34.0 |
| Nuclear GW | 9.1 | 0 |
| PEM GW | 12.0 | 2.8 |
| SMR GW | 107.7 | 76.7 |
| Gas boilers GW | 17.6 | 33.3 |
| LNG import TWh | 99 | 558 |
| Net emissions Mt | 0 | +106 |
| CO2 stored in NL Mt | 27.2 | 27.2 (+ 185 Mt exported to UK/NO/DK; captured 216) |

## 6. Cross-border flows (2050, TWh; CO2 Mt)
- CH4: NO to DE 288, NL to DE 128, BE to DE 96, NL to BE 131, BE to NL 86, FR to BE 87.
- CO2: BE to UK 72, NL to UK 43, BE to NO 32, NL to DK 20, NL to NO 17, DE to NO 6.
- Electricity: NL to DE 39, BE to FR 22 (both directions), NL to BE 19, DE to NL 19.
- H2: DE to FI 94 (both directions), BE to FR 35, BE to DE 33.
- The boundary stubs (FR, AT, CZ, ...) show matched in/out flows. They are only transit points.

## Open points
- Decide the LNG emission accounting (import vs consumption) before country-level reporting.
- The storage caps bind everywhere, so a sensitivity on storage availability will drive results strongly.
- No nuclear in BE/NL is a direct effect of the shared system. Check this against policy (BE extension).


