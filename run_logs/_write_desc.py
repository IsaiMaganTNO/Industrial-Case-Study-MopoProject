import io
a5 = io.open(r"run_logs\_a5.md", encoding="utf-8").read().replace("\r\n", "\n")
b5 = io.open(r"run_logs\_b5.md", encoding="utf-8").read().replace("\r\n", "\n")
head = """# Figure descriptions for the report (NL+BE)

Figures are in `figures/` (PNG at 400 dpi and SVG; `_vertical` = NL above BE). The data behind each figure is in `data/` (same file name, `.csv`). Figures have no titles; use the captions below.

## Scenario names used in this document

| Name | Short | What it is |
|---|---|---|
| NL+BE regional clusters | Regional clusters | NL and BE only, split into 17 zones. |
| NL+BE country level | Country level | NL and BE only, one node per country. |
| Mixed resolution | MR | NL+BE in 17 zones plus DE, DK, NO and UK at country level; one shared CO2 cap. Reference for all sensitivities. |
| National CO2 caps | - | As Mixed resolution, but each country has its own CO2 cap. |
| 10 repr. days | - | As Mixed resolution, with 10 instead of 3 representative days. |
| Optimistic CCS | - | As Mixed resolution, with higher CO2 storage limits and lower CO2 transport and injection costs. |
| With FR + LU | - | As Mixed resolution, with France and Luxembourg added. |

- **A figures:** Regional clusters, Country level and Mixed resolution, for 2030, 2040 and 2050.
- **B figures:** Mixed resolution, National CO2 caps, 10 repr. days, Optimistic CCS and With FR + LU, for 2050 only.
- **Numbers are per country (NL panel and BE panel), as read from the bars**, in TWh/yr, rounded. Year series are written 2030 / 2040 / 2050.
- **NL CO2 storage limit:** 2.5 / 10.5 / 16 Mt/yr (2030/2040/2050) in every scenario except Optimistic CCS.

---

## A1 - Electricity generation (`A1_electricity_generation`)

*Caption: Electricity generation in NL (top/left) and BE (bottom/right) by technology in 2030, 2040 and 2050 for NL+BE regional clusters, NL+BE country level and Mixed resolution.*

**What we see**
- **Offshore wind, NL:** Regional clusters 47 / 217 / 380, Country level 50 / 226 / 369, Mixed resolution 26 / 134 / 207 TWh. In 2050, Mixed resolution has about 45% less NL offshore wind than the two NL+BE-only scenarios.
- **Offshore wind, BE:** 8 / 31-33 / 44 TWh in Regional clusters and Country level; 8 / 20 / 39 TWh in Mixed resolution.
- **Nuclear, NL:** Regional clusters 5 / 36 / 44 TWh; Country level 5 / 0 / 0 TWh; Mixed resolution 5 / 0 / 16 TWh.
- **Nuclear, BE:** 41 TWh in 2030 and 53 TWh in 2050 in all three scenarios. In 2040: 75 TWh in Regional clusters and Country level, but only 24 TWh in Mixed resolution.
- **Gas power (no capture):**
  - 2030: NL 19 TWh (Regional clusters, Country level) and 29 TWh (Mixed resolution); BE 31-33 TWh in all three.
  - 2040: only Mixed resolution still has gas power (NL 9, BE 7 TWh).
  - 2050: none in any scenario.
- **Hydrogen turbines:**
  - Regional clusters: NL 20 / 3 / 6 TWh and BE 4 / 1 / 7 TWh.
  - Country level: BE only, 20 / 2 / 14 TWh.
  - Mixed resolution: none.
- **Biomass power:** only in Mixed resolution: BE 20 / 38 / 16 TWh, NL 6 / 5 / 0 TWh.
- **Solar and onshore wind** are almost the same in all three scenarios: NL solar ~42, BE solar ~12, NL onshore wind 20-27, BE onshore wind ~10 TWh.

**Why**
- In Regional clusters and Country level, NL and BE must meet their own hydrogen demand and CO2 cap without neighbours. Industry therefore electrifies or switches to hydrogen (see A5). This needs a lot of electrolysis in NL (see A3), and so a lot of NL offshore wind.
- In Mixed resolution, captured CO2 can be exported to storage in NO, UK and DK. Industry uses gas with capture instead (see A5), so less electricity is needed. The neighbours also provide flexibility, so no hydrogen turbines are built.

## A2 - Hydrogen supply (`A2_hydrogen_supply`)

*Caption: Hydrogen supply in NL and BE by source in 2030, 2040 and 2050 for NL+BE regional clusters, NL+BE country level and Mixed resolution (hydrogen made and used inside refineries excluded).*

**What we see**
- **LH2 import terminals:** NL ~23 TWh and BE ~20 TWh, at their limits in almost every year and scenario. Exceptions in 2030: Mixed resolution (NL 17, BE 0 TWh) and Country level (BE 14 TWh).
- **Electrolysis (all in NL; BE has none):** Regional clusters 0 / 35 / 130, Country level 0 / 3 / 73, Mixed resolution 0 / 0 / 28 TWh.
- **Gas reforming + CCS (outside refineries):** only in Mixed resolution, NL, 13 TWh in 2030 and 2040; zero in 2050.
- **Net pipeline import:**
  - BE in Regional clusters: 0 / 13 / 45 TWh; BE in Country level: 22 / 14 / 56 TWh. This is hydrogen from NL; NL shows the same amount as net export in A4.
  - NL in Regional clusters 2030: 13 TWh (from BE).
  - Mixed resolution: about zero (BE 1 TWh in 2050).

**Why**
- Imported LH2 is the cheapest low-carbon hydrogen, so the terminals are used up to their limit. Electrolysis in NL covers the remaining demand of NL and BE.
- Mixed resolution needs much less hydrogen because its industry uses gas with capture (see A4 and A5).
- In the two NL+BE-only scenarios, NL and BE together have zero net hydrogen trade with other countries; the flows to and from the DE and FR nodes are transit only.

## A3 - Electricity consumption (`A3_electricity_consumption`)

*Caption: Electricity use in NL and BE by category in 2030, 2040 and 2050 for NL+BE regional clusters, NL+BE country level and Mixed resolution.*

**What we see**
- **Fixed demand** (buildings, transport, other): NL ~97 TWh and BE ~65 TWh in every year and scenario.
- **Electrolysis (NL only):** Regional clusters 0 / 57 / 208, Country level 0 / 5 / 117, Mixed resolution 0 / 0 / 45 TWh.
- **Industry:**
  - NL: Regional clusters 46 / 112 / 130, Country level 46 / 129 / 146, Mixed resolution 42 / 69 / 77 TWh.
  - BE: Regional clusters 43 / 78 / 79, Country level 44 / 86 / 88, Mixed resolution 42 / 62 / 71 TWh.
- **Building heat (2050):** NL 20 (Regional clusters), 30 (Country level), 9 (Mixed resolution) TWh; BE 12, 14 and 3 TWh.
- **Storage charging (2050, NL):** Regional clusters 12, Country level 10, Mixed resolution 18 TWh; BE 0-2 TWh.
- **Net export:**
  - Mixed resolution: NL 21 / 21 / 37 TWh, BE 6 / 0 / 4 TWh.
  - Regional clusters and Country level: NL up to 9 TWh, BE about zero.

**Why**
- In Regional clusters and Country level, industry decarbonises through electricity and hydrogen (see A5), so electrolysis in NL and industrial electricity use are high.
- In Mixed resolution, gas with capture replaces much of this, and NL exports its surplus offshore wind to the neighbours.

## A4 - Hydrogen consumption (`A4_hydrogen_consumption`)

*Caption: Hydrogen use in NL and BE by category in 2030, 2040 and 2050 for NL+BE regional clusters, NL+BE country level and Mixed resolution (hydrogen made and used inside refineries excluded).*

**What we see**
- **Industry:**
  - NL: Regional clusters 0 / 40 / 97, Country level 0 / 12 / 39, Mixed resolution 0 / 0 / 15 TWh.
  - BE: Regional clusters 0 / 32 / 52, Country level 0 / 30 / 52, Mixed resolution 0 / 0 / 21 TWh.
- **Hydrogen turbines (H2 input):**
  - Regional clusters: NL 36 / 5 / 10, BE 7 / 1 / 13 TWh.
  - Country level: BE only, 37 / 4 / 24 TWh.
  - Mixed resolution: none.
- **Net pipeline export:**
  - NL in Regional clusters 0 / 13 / 45 and Country level 22 / 14 / 56 TWh: hydrogen sent to BE (BE shows it as import in A2).
  - NL in Mixed resolution 30 / 36 / 35 TWh: real export to neighbours, largely LH2 imports passed on. BE in Mixed resolution also exports 20 TWh in 2040.

**Why**
- In Regional clusters and Country level, hydrogen replaces fossil fuels in ammonia, glass and part of steel (see A5), and hydrogen turbines provide firm power.
- In Mixed resolution, these sectors use gas with capture, so NL acts mainly as a transit hub for imported hydrogen.

"""
b = """## B1 - Electricity generation, sensitivities (`B1_electricity_generation`)

*Caption: Electricity generation in NL and BE by technology in 2050 for Mixed resolution, National CO2 caps, 10 repr. days, Optimistic CCS and With FR + LU.*

**What we see (Mixed resolution as reference: NL offshore wind 207, NL nuclear 16, BE nuclear 53, BE offshore wind 39, BE biomass 16 TWh)**
- **National CO2 caps:** almost the same as Mixed resolution (NL offshore wind 207, NL nuclear 21 TWh), plus 2 TWh gas power + CCS in BE and no BE biomass power.
- **10 repr. days:**
  - NL: more offshore wind (274 TWh) and nuclear (42 TWh), slightly more solar (46 TWh), and 7 TWh gas power without capture.
  - BE: more solar (20 vs 12 TWh), 12 TWh biomass power and 6 TWh hydrogen turbines.
- **Optimistic CCS:**
  - No nuclear in NL or BE. Gas power + CCS replaces it: BE 88 TWh, NL 11 TWh.
  - Offshore wind drops to NL 148 and BE 21 TWh.
- **With FR + LU:**
  - NL offshore wind 187 TWh, NL nuclear 0 TWh.
  - BE nuclear 26 TWh (half of Mixed resolution) and BE biomass power 47 TWh.

**Why**
- **Optimistic CCS:** cheap CO2 storage makes gas power with capture cheaper than new nuclear in NL and BE.
- **10 repr. days:** with 10 days the model sees more varied weather, including longer low-wind periods. It builds more firm capacity (nuclear in NL) and long-duration storage (see B3).
- **With FR + LU:**
  - French existing nuclear is assumed to retire after 40 years, so France has little cheap firm power to offer.
  - Adding FR also enlarges the shared CO2 and biofuel caps (about x1.2), so BE replaces part of its nuclear with biomass power.

## B2 - Hydrogen supply, sensitivities (`B2_hydrogen_supply`)

*Caption: Hydrogen supply in NL and BE by source in 2050 for Mixed resolution, National CO2 caps, 10 repr. days, Optimistic CCS and With FR + LU (refinery hydrogen excluded).*

**What we see**
- **LH2 imports** are at the limit in all five scenarios: NL ~23 TWh, BE ~20 TWh.
- **Electrolysis (NL only):** Mixed resolution 28, National CO2 caps 25, 10 repr. days 46, Optimistic CCS 9, With FR + LU 16 TWh.
- **Net pipeline import (BE only):** With FR + LU 26, 10 repr. days 13, National CO2 caps 2, Mixed resolution 1, Optimistic CCS 0 TWh.

**Why**
- **Optimistic CCS:** industry uses gas with capture instead of hydrogen, so little electrolysis is needed.
- **10 repr. days:** there are more hours with surplus wind and solar, which makes electrolysis cheaper to run.
- **With FR + LU:** BE glass and ammonia routes change (see B5), and BE takes in more hydrogen by pipeline.

## B3 - Electricity consumption, sensitivities (`B3_electricity_consumption`)

*Caption: Electricity use in NL and BE by category in 2050 for Mixed resolution, National CO2 caps, 10 repr. days, Optimistic CCS and With FR + LU.*

**What we see**
- **Almost the same in all five scenarios:** fixed demand (NL 92-97, BE 63-64 TWh) and industry (NL 73-83, BE 71-72 TWh).
- **Storage charging, NL:** 10 repr. days 120 TWh (mostly iron-air batteries), compared with Mixed resolution 18, National CO2 caps 22, With FR + LU 12, Optimistic CCS 5 TWh. BE: 0-5 TWh.
- **Electrolysis (NL only):** 10 repr. days 73, Mixed resolution 45, National CO2 caps 40, With FR + LU 26, Optimistic CCS 14 TWh.
- **Building heat:** 10 repr. days NL 36 and BE 14 TWh, against NL 4-9 and BE 2-3 TWh in the other four scenarios.
- **Refineries (NL):** 10 repr. days 0 TWh, against 5-7 TWh in the other four scenarios.
- **Net export (NL):** Mixed resolution 37, National CO2 caps 37, With FR + LU 34, 10 repr. days 32, Optimistic CCS 20 TWh. BE exports only in Mixed resolution (4 TWh).

**Why**
- **Storage:** with 3 representative days (all other scenarios) the model cannot see weather events that last several days, so long-duration storage has no value. With 10 days it does, and it builds iron-air storage in NL.
- **Refineries:** electricity use is zero in 10 repr. days because the NL+BE refineries are not used (see B5).
- **Building heat:** the higher value in 10 repr. days has not been analysed yet.

## B4 - Hydrogen consumption, sensitivities (`B4_hydrogen_consumption`)

*Caption: Hydrogen use in NL and BE by category in 2050 for Mixed resolution, National CO2 caps, 10 repr. days, Optimistic CCS and With FR + LU (refinery hydrogen excluded).*

**What we see**
- **Industry:**
  - NL: Mixed resolution 15, National CO2 caps 7, 10 repr. days 15, Optimistic CCS 0, With FR + LU 21 TWh.
  - BE: Mixed resolution 21, National CO2 caps 22, 10 repr. days 22, Optimistic CCS 0, With FR + LU 43 TWh.
- **Net pipeline export:**
  - NL: Mixed resolution 35, National CO2 caps 41, 10 repr. days 52, Optimistic CCS 31, With FR + LU 17 TWh.
  - BE: only in Optimistic CCS (20 TWh).
- **Hydrogen turbines (BE only):** 10 repr. days 11 TWh, With FR + LU 2 TWh; none in the other three scenarios.

**Why**
- **Optimistic CCS:** all industry that uses hydrogen in Mixed resolution switches to gas with capture, so the imported LH2 in both NL and BE is passed on to neighbours.
- **With FR + LU:** BE glass moves partly to hydrogen (see B5), so more hydrogen is used inside BE and NL exports less.
- **10 repr. days:** BE hydrogen turbines provide back-up power during longer low-wind periods.

"""
io.open(r"results_2050_analysis\FIGURE_DESCRIPTIONS.md", "w", encoding="utf-8", newline="\n").write(head + a5 + "---\n\n" + b + b5)
