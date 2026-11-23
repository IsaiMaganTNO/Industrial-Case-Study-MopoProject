# RESULT 3day_nb_v2 - NL+BE IC1 baseline, current data (2026-10-09)
Solve: Gurobi, 85.5 min, OPTIMAL, **penalties 0 (PASS)**, objective **3,644,339**.
Split: fixed O&M 2,018,468; investment 1,427,867; taxes 171,671; variable O&M 12,770; storage investment 7,562; connection flow 3,814; connection investment 2,187.

## 1. Does each industry sector decarbonise?  Yes, all 12 sectors by 2050.
Output is identical in all years (exogenous demand: steel 12,347; olefins 11,036; cement 7,132; ammonia 3,910 ...).

| Sector | 2030 | 2040 | 2050 |
|---|---|---|---|
| Primary steel | 100% BF-BOF | MOE 57%, NG-DRI-EAF+CC 43% | same |
| Secondary steel | Scrap EAF (electric) | same | same |
| Olefins | 100% naphtha cracker, unabated | 100% with capture (MEA) | same |
| Ammonia | NG 59%, NG+CC 33%, bio 8% | bio 67%, NG+CC 33% | **bio 80%**, NG+CC 20% |
| Cement | 79% reference, 21% oxy-fuel+CC | 100% oxy-fuel+CC | same |
| Glass (float / fibre / container) | gas | H2 / electric furnaces, container 50% | 100% H2/electric |
| Aluminium | 96% reference | 99% alternative | 100% alternative |
| Pulp / paper | paper alternative, pulp reference | pulp 51% alternative | 100% alternative |
| Chlorine | Diaphragm (electric) | same | same |
Residual 2050 industry CO2 is about 7 Mt (capture slip, other chemicals 1.3, ceramics 0.8); it is offset by storage.

## 2. Is VRE represented?  Yes.
| | 2030 | 2040 | 2050 |
|---|---|---|---|
| Offshore wind GW / TWh | 13.7 / 69 | 34.0 / 161 | 61.1 / 318 |
| Onshore wind GW / TWh | 10.7 / 29 | 10.8 / 33 | 10.8 / 37 |
| Solar PV GW / TWh | 43.4 / 51 | 46.2 / 54 | 46.3 / 54 |
| Electricity total TWh | 256 | 355 | 502 |
VRE share: 58% / 70% / 82%. Onshore wind and solar stay near their potential caps; offshore is the growth technology.

## 3. CO2 system
- Emissions 165.4 / 36.8 / 0 Mt (the budget binds in 2040 and 2050).
- Storage 2.5 / 27.2 / 27.2 Mt: both NL sites at their cap from 2040. Capture equals injection in every year.
- Capture 2050 (34 Mt): SMR+CC 16.0, olefins 11.1, steel 3.1, cement 2.6, ammonia 1.1.

## 4. Energy carriers
- Nuclear: existing 46 / 23 / 0 TWh; new BE 6.0 GW (at cap), NL 2.2 / 3.1 GW (below the 4 / 5 cap).
- Hydrogen: LH2 import 12.7 / 42.5 / 42.5 TWh (at terminal capacity); PEM only in 2050 (12 GW, 64 TWh); blue SMR+CC 108 GW (H2 output not included in the table).
- Methane: LNG 412 / 223 / 99 TWh; methanation 35 TWh in 2050.
- Heat: existing gas boilers retire by 2050; heat pumps 74 TWh; new gas boilers 17.6 GW / 40 TWh in 2050.

## 5. Flags / caveats
1. **Ammonia 80% bio-based in 2050** now that biomass is corrected (was 45% with too little biomass). Biomass stocks are fully used (state reaches 0). Check whether bio-NH3 is realistic.
2. **Blue hydrogen (SMR+CC 108 GW) dominates**; PEM appears only in 2050. Driven by cheap LNG + 27 Mt storage.
3. **New gas boilers** 40 TWh fossil heat in 2050, possible only through storage offsets.
4. **MOE 57% of primary steel from 2040**: low technology readiness, optimistic.
5. **Reporting artefact:** 2030 "direct air capture" 0.1 Mt shows in `co2net` although DAC investment = 0 (existing-unit flows from the data). Negligible.
6. Model scope: 3 representative days, perfect foresight, NL+BE only; neighbours are border stubs.
