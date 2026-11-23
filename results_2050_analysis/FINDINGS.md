# 2050 analysis - NL+BE industrial decarbonisation (findings)
Figures in `figures/`, data in `data/`. `_all` = 2030/2040/2050, `_2050` = 2050 only.
Group A = spatial set-up. Group B = sensitivities on "With neighbours".

## The runs
| Name in figures | What it is |
|---|---|
| NL+BE 17 zones | NL and BE only, split into 17 zones with limited transport between zones. NL+BE must reach net zero on their own. |
| NL+BE 1 node/country | Same data, but NL and BE are one node each (no internal bottlenecks). |
| With neighbours | Reference for the sensitivities: NL+BE in 17 zones plus DE, DK, NO and UK (one node each), linked by electricity, gas, hydrogen and CO2 networks. One shared CO2 cap for all six countries. |
| National CO2 caps | As "With neighbours", but every country has its own CO2 cap. CO2 exported for storage counts for the exporting country. |
| 10 repr. days | As "With neighbours", with 10 instead of 3 representative days per year. |
| Optimistic CCS | As "With neighbours", with higher CO2 storage limits (NL 27 Mt/yr in 2050) and lower CO2 transport and injection costs. |
| With FR + LU | As "With neighbours", with France and Luxembourg added. France's existing nuclear is retired after 40 years (assumption). |

All runs: limited NL CO2 storage of 2.5 / 10.5 / 16 Mt per year (2030/40/50) unless stated, no BE storage, no direct air capture, same technologies, costs and demands.

**Note on CO2 emissions per country.** The model books the CO2 of natural gas where the gas enters the system (LNG terminals), not where it is burned. NL and BE land much LNG and pass a large part on by pipeline, so their booked emissions are mostly gas that is used abroad. Per-country emissions are therefore not used as a result, except in "National CO2 caps", where each country has its own cap.

## KPI 2050 (NL+BE) - `data/kpi_2050.csv`
| | 17 zones | 1 node | Neighbours | Nat. caps | 10 days | Opt. CCS | FR + LU |
|---|---|---|---|---|---|---|---|
| CO2 captured (Mt) | 31.9 | 27.6 | 50.7 | 63.1 | 35.6 | 96.3 | 35.7 |
| Stored NL / CCU / net export (Mt) | 16 / 15.9 / 0 | 16 / 11.6 / 0 | 16 / 0 / 34.7 | 16 / 0 / 47.1 | 16 / 0 / 19.6 | 27.2 / 0 / 69.1 | 16 / 0 / 19.7 |
| Offshore wind (TWh) | 423 | 413 | 246 | 248 | 311 | 169 | 218 |
| Nuclear (TWh) | 96 | 53 | 69 | 74 | 95 | 0 | 26 |
| Electrolytic H2 (TWh) | 130 | 73 | 28 | 25 | 46 | 9 | 16 |
| Electricity net export (TWh) | 0 | 0 | 41 | 37 | 31 | 20 | 17 |
Costs cover different systems (2, 6 or 8 countries); compare only 17 zones vs 1 node.

## Comparison A: NL+BE 17 zones vs 1 node per country vs With neighbours
**17 zones -> 1 node per country (spatial resolution)**
- Same pathway: ammonia on green hydrogen, primary steel mostly electric, glass on electricity/hydrogen, captured CO2 partly reused in methanol for plastics.
- 4% cheaper. Without bottlenecks between zones the model needs less electrolysis (130 -> 73 TWh), less nuclear (96 -> 53 TWh) and less CO2 reuse (15.9 -> 11.6 Mt).
- Primary steel becomes fully electric (17 zones: 71% electric, 14% hydrogen, 14% gas DRI + capture).
- Conclusion: one node per country is good for screening, but hides local bottlenecks for hydrogen and CO2.

**NL+BE alone -> With neighbours (system boundary)**
- The pathway changes. CO2 can be exported for storage abroad (35 Mt), so ammonia, primary steel, olefins and float glass move to gas with carbon capture.
- CO2 captured rises from 28-32 to 51 Mt; CO2 reuse in methanol stops.
- Much less electrolysis (28 TWh) and offshore wind (246 TWh); NL+BE become net electricity exporters (41 TWh).
- New nuclear: 6.0 GW in BE and 1.8 GW in NL.
- Conclusion: the system boundary matters much more than the spatial resolution.

## Comparison B: With neighbours vs its sensitivities
**National CO2 caps**
- Industry routes nearly the same; slightly more hydrogen in glass.
- More capture (63 Mt) and more export (47 Mt). Each country must meet its own cap, so NL+BE emissions (47 Mt) are exactly offset by the CO2 they export for storage.
- DE becomes the largest CO2 exporter (49 Mt); NO, UK and DK host the storage.

**10 representative days**
- Glass moves fully to gas + capture; the NL+BE refinery is not used, Danish refineries take over (capture 36 Mt).
- More offshore wind (311 TWh), nuclear (95 TWh) and electrolysis (46 TWh), plus 106 TWh of iron-air storage. With more days the model sees multi-day wind shortages and values long storage.

**Optimistic CCS**
- The most capture (96 Mt), including 37 Mt from gas power plants.
- No new nuclear in NL+BE; gas power with capture instead (BE 88 TWh), and less offshore wind (169 TWh) and electrolysis (9 TWh).
- 27 Mt stored in NL and 69 Mt exported.

**With FR + LU**
- Industry mostly unchanged. Ammonia moves from gas + capture to biomass (88%); cement uses gas instead of biomass (still with capture); more hydrogen in glass.
- Less capture (36 Mt) and export (20 Mt), mainly ammonia and plastics.
- Less nuclear in NL+BE (BE 3.0 GW new, NL none; 26 TWh), more biomass power in BE (47 TWh), less offshore wind (218 TWh) and electrolysis (16 TWh).
- NL+BE export less electricity (17 TWh) and import hydrogen by pipeline (8.5 TWh) instead of exporting it.
- France keeps only 1.7 GW of nuclear in 2050 under the 40-year assumption and builds no new nuclear; this makes the result for NL+BE nuclear sensitive to that assumption.
- The input of NL+BE is identical to "With neighbours". Adding FR+LU also raises the shared CO2 and biofuel limits by about 21% and changes the weights of the representative days.

## Notes per figure
1. **Industry routes** (`1_industry_routes_*`): chlorine is electric, paper/pulp/secondary steel/aluminium use biomass or scrap, and refinery hydrogen comes from gas reforming with capture in every run.
2. **Electricity mix** (`2_elecmix_*`): offshore wind is the main source in NL in every run; BE relies on nuclear, offshore wind and (Optimistic CCS, FR + LU) gas or biomass power.
3. **Energy panels** (`3_energy_*`): LH2 import is at its limit (42.5 TWh) in every run. Hydrogen turbines only when NL+BE are alone (23-24 TWh) and in 10 repr. days (11 TWh).
4. **Hydrogen and electricity balance** (`4_h2_elec_balance_*`): no gas-based hydrogen outside refineries. The use categories add up to within 2% of supply.
5. **CO2 capture and destination** (`5_co2_capture_dest_*`): NL storage is full in every run. Alone, the rest goes to methanol (CCU); with neighbours it is exported. The black line (NL+BE net emissions) is drawn only for "National CO2 caps" (see note above).

