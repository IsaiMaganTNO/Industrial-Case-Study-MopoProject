# Standalone (IC1, 17 zones) vs Country-level (NL, BE) - analysis

Runs: `3day_nb_v2` (SA) and `3day_nb_ctry` (CL). Same data, scenario, CO2 budget and storage caps; the only difference is the network resolution.
Scripts: `run_logs/_inv1.py` to `_inv10.py`; flow extract `run_logs/_bal_sa_cl.pkl`.

## 1. Totals that are identical
- Industry output 46.2 (all years), emissions path (165 / 37 / 0 Mt), CO2 stored 2.5 / 27.2 / 27.2 Mt (cap binding in both), total biomass, onshore wind, solar, existing offshore build-out.

## 2. Cost: -41.7k (-1.1%)
Unit investment -42.7k, fixed O&M -4.6k, connection flow -0.5k; storage investment +6.8k (batteries). Expected direction: CL removes the zone-to-zone transport limits.

## 3. Root cause: transport limits between zones in SA
- In SA, 120 of 158 intra-country elec/H2/CH4 connections spend >=20% of hours at their own peak flow (binding-limit proxy).
- SA also invests in 6 NL electricity links between zones (NLC3-4, NLC2-3, NLC1-3, NLC2-5, NLC3-8, NLC3-5).
- Intra-country flows in SA in 2050: elec 733 TWh, H2 108 TWh, CH4 3,721 TWh, CO2 19 Mt.
- CL has none of these limits, and every difference below follows from that.

## 4. Mechanism chain (2050)
1. **Nuclear: 80 -> 53 TWh.** SA builds new nuclear spread over 10 zones (BEC2-7, NLC4/6/8/9) to supply load locally behind grid bottlenecks. CL concentrates it in BEC1 and BEC7 and builds less overall.
2. **Polyethylene (PEA) route switch.** SA: the NLC6 plant runs on hydrogen (18.7 TWh H2). CL: the same plant runs on the electric route (32 TWh elec). Overall: H2-PEA 57.9 -> 33.0 TWh H2; EL-PEA 21.6 -> 46.2 TWh elec.
   - With a country-wide electricity node, power reaches NLC6 freely. In SA, electricity into NLC6 is limited, so H2 delivered by pipeline was the cheaper route there.
3. **Hydrogen supply: 106.5 -> 68.1 TWh.**
   - PEM falls 64 -> 25.6 TWh, because H2 demand falls (PEA -24.9, methanation -13).
   - The rest of the H2 supply is LH2 imports (42.5 TWh, unchanged). SMR units feed the `HC` node (used by olefins), not `H2`; their CH4 input is 55.0 -> 51.6 TWh (NLC2 in SA, NLC1 in CL).
   - CL also runs some unabated SMR in 2050 (existing units in NLC6, 3.4 TWh CH4, 1.1 Mt CO2). This is offset elsewhere: gross 2050 emissions are 27.2 Mt in both runs, balanced by -27.2 Mt.
   - Methanation 34.5 -> 24.4 TWh, hence CH4 from methanation -10.
4. **Salt caverns.** SA keeps ~88 units across NL and invests 15 more in NLC2; they are cycled 66 TWh in 2050 to buffer PEM output, which follows wind. CL decommissions all of them in 2030, because PEM is small and SMR runs flat. Cavern connections were checked and correctly attached to `H2_NL`, so this is a model choice, not a build error.
5. **Batteries: 2050 fleet ~8.9 -> ~16.9 units.** Batteries replace part of the PEM-plus-cavern flexibility. This is the +6.8k storage investment.
6. **Electricity: 502 -> 474 TWh.** PEM demand -62 TWh; PEA +25 and heat pumps / electric heating +8. Offshore wind roughly the same total, only spread over different NS sites (degenerate).
7. **Heat 2050.** Bio-boiler 7.1 -> 0 and gas boiler -9, replaced by heat pumps +12. The freed biomass goes to ammonia (see section 5).

## 5. Industrial decarbonisation choices
Essentially the same. 2050 total industrial output is identical; the largest single route difference is 0.72 out of 46.2 (1.6%). CCS share is 100% in cement, glass, olefins and steel-primary (42.9%) in both runs.

| Sector / year | SA | CL |
|---|---|---|
| Cement 2030: oxy-fuel+CCS / reference kiln | 1.50 / 5.63 | 0.78 / 6.35 |
| Glass float 2040: H2 furnace / gas furnace | 0.93 / 0 | 0.46 / 0.46 |
| Glass float 2050: H2 / electric furnace | 0.93 / 0 | 0.46 / 0.46 |
| Glass container 2050: electric / H2 | 1.03 / 0.33 | 1.19 / 0.16 |
| Ammonia 2050: biomass gasification / SMR+CCS (DEA) | 3.11 / 0.80 | 3.83 / 0.08 |

All other sector-routes differ by less than 0.01.

Logic:
- **Glass:** cheap country-wide electricity favours electric furnaces over H2 (same mechanism as PEA).
- **Ammonia:** biomass freed from heating and moved freely within BE replaces SMR+CCS. This saves ~1 Mt of capture, so scarce CO2 storage goes to SMR-MEA hydrogen instead (storage is binding in both runs).
- **Cement 2030:** a 2030-only timing shift with the same 2040/2050 outcome.
- **Industry fuel 2050:** gas 17.1 -> 16.4, H2 1.4 -> 0.8, electricity 9.5 -> 10.1, biomass 3.1 -> 3.8.

## 6. Caveats
- **Unit locations within a country are not meaningful in CL.** Placement is degenerate: SMR NLC2 -> NLC1, batteries spread evenly over all zones, nuclear in BEC1/BEC7. Only compare country totals.
- **SA's existing intra-country capacities are modelled limits from the dataset.** Their realism drives the size of the differences.
- **Single solve per configuration.** Small differences (<1 TWh) can be tie-breaking between equally cheap solutions (near-degenerate), not real effects.



