# RESULT 3day_nodac_nuc - NL+BE IC1, no DAC, LNG 1.0, storage /365, nuclear country caps (2026-10-09)
Results: `checkpoints/Investment_Results.3day_nodac_nuc.sqlite`; cache `run_logs/nodac_nuc.pkl`.
Status: OPTIMAL, **penalties 0 (PASS)**, objective 3,835,677 (+0.6% vs nodac 3,811,785; +9.3% vs vre15).

## Changes vs nodac (uncapped nuclear 13.6 GW)
| Item | nodac | nodac_nuc |
|---|---|---|
| Nuclear-3 capacity | BE 11.4, NL 2.2 GW | BE 6.0, NL 4.0 (2040) / 4.85 (2050) GW: caps respected |
| Nuclear-3 generation | 118.9 TWh | 87.6 / 95.0 TWh (2040/2050) |
| Electricity total 2030/40/50 | 182.6 / 245.6 / 223.1 | 182.3 / 222.4 / 209.0 TWh |
| Onshore wind 2040 | 19.8 | 30.7 TWh |
| CO2 storage 2050 | binds 27.2 Mt | binds 27.2 Mt |

## How the missing nuclear is replaced (2050)
- CCGT-H2 7.5 TWh; new CCGT 4.4 TWh (1.9 GW, unabated); more batteries (BEC8 +1.3).
- PEM 55.7 / 54.5 TWh; LNG 417 / 104 / 99.6 TWh; methanation 65 / 28.8 TWh.
- Capture 2050: SMR+CC 16, chemicals 11.1, steel 3.1, cement 2.6 Mt.
- Investment deltas: nuclear -2.7, PEM +1.7, air HP +1.7, CCGT +1.9, BEC8 battery +1.3, (NG)DRI-EAF-MEA +0.6.

## Emissions and industry
Emissions 165.4 / 36.8 / 0 Mt; industry output unchanged (46,190).

## Takeaways
- The nuclear cap costs little (+0.6%). Gas, H2-CCGT and wind fill the gap.
- CO2 storage (27.2 Mt/yr) is still the binding net-zero constraint.
- Caveat: 2041 timestamps on storage/budget inputs, so the 2040 period uses 2030 values.
