# DISCUSSION NOTE - mixed-resolution run vs NL+BE IC1 run (vre15), 2026-10-09
Sources: `docs/RESULT_3day_mixedres.md`, `docs/FINDING_gas_supply_overstated.md`, `docs/FINDING_gas_volumes_and_transit.md`, plots in `reports_v2_mixedres/`. Units: TWh/yr.

## 1. Gas supply before and after the gas patch
The gas patch (`tools/patch_gas_availability.py`) does two things:
- LNG terminals: availability set to **0.5** (all countries).
- NL gas-extraction: availability set to **0**.

DE/DK/NO extraction is unchanged, and UK has no extraction in the data.

**NL+BE before the patch (run `3day_co2bidir`, 100% load factor all year):**

| source | capacity GWh/d | 2030 | 2040 | 2050 |
|---|---:|---:|---:|---:|
| LNG BE | 669.0 | 244.2 | 244.2 | 244.2 |
| LNG NL | 860.3 | 189.9* | 314.0 | 314.0 |
| NL extraction | 284.5 | 0 | 66.2 | 103.9 |
| **total** | | **434.1** | **624.4** | **662.1** |

\*2030 NL used at 45.5%.

**After the patch (same in vre15 and mixed):**
- LNG BE: 122.1 TWh.
- LNG NL: 157.0 TWh.
- Extraction: 0.

Both LNG caps bind in every year, so domestic supply is 279 TWh. The mixed run adds 44 TWh of biomethane+CCS in 2050.

The patch therefore cut 2050 supply from 662 to 279 TWh (58%):
- LNG halving: 279 TWh.
- NL extraction closure: 104 TWh.

**In vre15 the 279 TWh limit is hard. In the mixed run, NL+BE also import about 125 TWh net of Norwegian pipeline gas in 2050 (BE 104, NL 21).** Neighbours' LNG at 0.5: DE 91, UK 295 TWh. Norwegian extraction: 1,096 / 1,289 / 1,302 TWh, and the `fossil-CH4` budget is inert.

## 2. Main findings
1. **NL+BE results are not robust to adding neighbours.** Industry output is identical, but the energy system changes:

   | NL+BE electricity (TWh) | vre15 2050 | mixed 2050 |
   |---|---:|---:|
   | nuclear | 51.4 | 0 (existing fleet retires; mixed 2040: 34.8) |
   | gas + CCS (CCGT+CC) | 0 | 71.2 (also 70.6 in 2040) |
   | gas unabated | 0 | 0 (but 50.0 in 2030) |
   | H2 turbine | 2.2 (12.4 in 2040) | 0 |
   | biomass power | 0 | 25.2 |
   | solar / onshore wind | 54.1 / 37.3 | 53.1 / 37.0 (at caps) |
   | offshore BE / NL | 35.2 / 158.2 | 21.1 / 138.7 |

2. **Cheap, effectively unlimited Norwegian pipeline gas is the main driver.** It bypasses the LNG halving.
3. **The CO2 budget is met system-wide.**
   - Negative emissions move abroad: DK storage 243 Mt and DAC in NO/DK about 100 Mt in 2050.
   - NL DAC (35/29 Mt in vre15) disappears.
   - Offsite sinks let NL+BE keep gas+CCS instead of nuclear and H2.
4. **The 2030 CO2 budget does not bind** (655 of 1,146 Mt used), which allows unabated gas and coal in 2030.
5. **Hydrogen:** LH2 imports hit their 42.5 TWh cap from 2040 in both runs. 2030 imports are 35.5 vs 9.7 TWh. Electrolysis stays at 34 TWh, and blue H2 (SMR+CCS) appears only outside NL+BE.
6. **System as a whole:** UK gas+CCS 315 TWh with no new onshore wind; NO exports about 1,280 TWh of gas. The objective is 7.20M vs 3.51M (6 countries vs 2).

## 3. Unrealistic points to check or fix

| # | Issue | Fix |
|---|---|---|
| 1 | Unlimited NO extraction (1.3 PWh/yr, constant), inert `fossil-CH4` budget | Activate the budget (check /365 scaling) and/or add a NO decline path |
| 2 | DK CO2 storage 243 Mt/yr (vs about 4060 Mt/yr in plans, from memory; needs a source check) | Cap injection per country/site |
| 3 | DAC about 100 Mt/yr in NO/DK | Review cost/potential; per-country cap |
| 4 | Producer-gate CO2 accounting (NO shows 263 Mt in 2050) | Consumption-based reporting |
| 5 | One shared CO2 budget, no national targets | Per-country budgets or limits on CO2 trade |
| 6 | No UK gas extraction in the data; UK 315 TWh gas power, no new onshore wind | Add UK extraction (ENTSOG TYNDP); check UK onshore costs |
| 7 | No per-country nuclear caps | Workbook caps BE 6 / NL 45 / UK 613 GW (schema change) |
| 8 | Flat LNG availability of 0.5 | Terminal-specific or seasonal values |
| 9 | Neighbours at country level (no internal grid limits) | Accept; keep in mind |
| 10 | FR/LU/etc. are transit-only nodes | Known boundary choice |

## 4. Next steps
1. Gas-budget / NO-cap sensitivity. Expected effect: nuclear and H2 return in NL+BE.
2. Cap CO2 storage and review DAC.
3. Consumption-based emissions.
4. Nuclear caps.

## 5. Plot labels (fixed 2026-10-09)
- **Old labels:** `postprocess.classify` labelled every "+CC" technology as "industry: CCS-equipped". In the electricity plots this was **only CCGT+CC (gas power with CCS)**; in methane plots it was biomethane+CCS, and in hydrogen plots SMR+CCS. Nuclear, hydro, batteries, LNG, extraction and LH2 imports were lumped into "other".
- **Fix:** `tools/plot_mixedres_compare.py` now relabels by technology. `postprocess.py` is unchanged because other reports use it.
- **Clarified titles:** gross supply including storage discharge, offshore wind not region-assigned, producer-gate emissions, and investment units that differ by technology.
