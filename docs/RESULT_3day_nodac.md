# RESULT - 3day_nodac (NL+BE IC1: no DAC, LNG 1.0, CO2 storage /365), 2026-10-09
- **Status:** OPTIMAL, **penalties 0**. Objective **3,811,785** (vre15 3,510,170, +8.6%). Gurobi 9.5 min, run about 82 min.
- **Cache:** `run_logs/nodac.pkl`. **Scripts:** `run_logs/_nd_a1.py`, `_nd_a2.py`.
- **Industry output is identical to vre15** (46,190 per year).

## CO2 (Mt)
- **Storage is now binding exactly at the data values:**
  - NSNL031: 2.5 / 2.5 / 6.2
  - NSNL012: 0 / 6.5 / 21.0
  - Total 2050: **27.2** (vre15: 73.5)
- **2040 storage:** NSNL012 stores 6.5 Mt. That is half its 13 Mtpa (medium) value, so the 2041 timestamp effect is visible here.
- **Capture in 2050:** 32.2 Mt (vre15: 73.6 incl. 28.9 DAC).
  - Sources: SMR+CC 16.0, chemicals 11.1, cement 2.6, ammonia 2.4.
  - Steel, plastics and BECCS capture are gone.
  - 5 Mt of captured CO2 is reused in industry.
- **Budget:** fully used; emissions 165.4 / 36.8 / 0, same as vre15.

## Electricity (TWh): 2030 / 2040 / 2050
| | vre15 | nodac |
|---|---|---|
| total | 172 / 159 / 152 | 183 / **246 / 224** |
| new nuclear-3 | 0 / 22 / 51 (BE 5.9 GW) | 0 / **119 / 119** (BE 11.4 + NL 2.2 = 13.6 GW) |
| unabated gas (existing CCGT) | 0 (coal SCPC 34.6 in 2030) | 52.5 / 1.4 / 0 |
| H2 turbine | 5.4 / 12.4 / 2.2 | 0 / 0 / 2.6 |
| onshore wind / solar | at cap | at cap (identical) |

- **Nuclear is the main replacement for the lost CO2 sinks.**
  - BE builds 11.4 GW, roughly double the external workbook's 6 GW.
  - NL builds 2.2 GW (workbook: 4-5 GW).
  - There is no per-country nuclear cap, so this is uncapped.
- **2030 switches coal to gas:** 2030 LNG is now 1.0, so gas is cheaper than coal.

## Gas and hydrogen (TWh)
- **LNG use:** 419.6 / 108.8 / 99.6. The 1.0 ceiling (558) binds nowhere.
  - 2030 uses more gas than vre15's 279 because of the coal-to-gas switch.
  - 2040+ uses far less, because storage limits make gas+CCS unattractive.
- **Methanation:** 73.5 / 25.4 TWh in 2040/2050. This is synthetic methane from H2 plus captured CO2.
- **PEM electrolysis:** 51.8 / 46.3 TWh (vre15: 0 / 4.4). LH2 import at its cap (42.5) in both runs.
- **REF-SMR-MEA rises** to 107.7 units (vre15: 63.7). This is blue hydrogen for refineries, with its captured CO2 going into the 27.2 Mt of storage.

## Investment delta vs vre15 (units summed over vintages)
| change | technologies |
|---|---|
| **More** | REF-SMR-MEA +44, air heat pumps +19.5, methanation +8.5, nuclear +7.7 GW, PEM +6.9, ground heat pumps +5.8, batteries +5.9, H2/electric industry routes ((EL)PEA, (H2)PE, MOE, (EL)PE) |
| **Less** | gas boilers -16.4, bio-boilers -8.2, DAC -4, NG+CCS industry routes ((NG)PEA/PE/DRI-EAF-MEA) |

## Assessment
- **Plausible.** The patched storage cap now drives the solution: once storage is scarce, the model electrifies more, uses green H2, keeps blue H2 for refineries, and builds nuclear.
- **Points to watch:**
  - **Nuclear at 13.6 GW** (BE 11.4) is above national plans. Per-country caps would change this; that needs a schema change.
  - **2041 timestamp:** 2040 storage sees partial values.
  - **2030 gas:** 420 TWh of LNG at 1.0 (2030 needs a coal-vs-gas sanity check).
- **Ready for the mixed-resolution run with the same settings.**
