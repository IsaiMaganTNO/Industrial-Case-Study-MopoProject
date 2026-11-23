# ANALYSIS - Pessimistic CCS vs base CCS, and pessimistic runs compared (2026-10-13)

Pessimistic CCS = `low_CO2` storage caps + high-cost CO2 tariffs (pipelines x6, injection x1.2-4.7, shipping unchanged).
Unless marked "whole model", figures are NL+BE only (`run_logs/ccs_metrics_NLBE.csv`), 2050. Cross-border (XB) flows are in TWh (energy) or Mt (CO2).
Plots: see section 4.

## 1. Headline
| Pair | Base obj | Pessimistic obj | Delta | Stored CO2 2050 (whole model) |
|---|---|---|---|---|
| IC1 (nb_v2 -> nb_ccslow) | 3,644,339 | 3,829,096 | +184,757 (+5.1%) | 27.2 -> 10.5 Mt |
| Country (nb_ctry -> nb_ctry_ccslow) | 3,602,609 | 3,777,356 | +174,747 (+4.9%) | 27.2 -> 10.5 Mt |
| Mixed-res (mr_fix -> mr_ccslow) | 7,073,666 | 7,618,824 | +545,158 (+7.7%) | 356 -> 130 Mt |

All runs still reach net zero in 2050, and the storage caps bind in every pessimistic run.

**Main finding:** the extra cost is mostly investment to *avoid* emitting, not the CO2 tariffs themselves.
- In the NL+BE runs, unit investment rises by about +160k, while the transport cost change is under 0.3k.
- Mixed-res is the exception: transport tariffs (+25k) and storage investment (+35k) do become visible.

## 2. Pessimistic vs base, per resolution

### 2a. IC1 (Standalone)
- Storage moves to NLC6 only (10.5 Mt). NLC1 and NLC5 are not used in 2050.
- **What replaces storage:** offshore wind rises from 318 to 454 TWh (new NSNL031/032 sites, plus NSNL011 growing from 2.8 to 9.8 GW).
  - Electrolytic H2 goes from 64 to 149 TWh (PEM 12 -> 25 GW).
  - Methanation rises 3.9 -> 13.4 GW (CO2 reused instead of stored).
  - Nuclear rises 9.1 -> 11.0 GW.
  - There are more heat pumps; bio-boilers disappear.
- **Industry:** almost unchanged. Ammonia goes from 80% to 98% biomass gasification (gas SMR+CCS drops out). Polyethylene shifts slightly from H2 to electricity routes.
- **CO2 captured by source:** unchanged except ammonia (1.1 -> 0.1 Mt). SMR+CC H2 still captures 16 Mt. The cut in storage is absorbed because captured CO2 is used in e-fuels / methanation rather than stored.

### 2b. Country-level
- The same pattern, but stronger in heat and gas.
  - Offshore wind rises from 315 to 446 TWh; electrolytic H2 from 26 to 94 TWh (PEM 5 -> 17 GW); methanation 2.8 -> 8.4 GW.
  - Gas boilers fall from 13.8 to 4.0 GW and unabated fossil heat from 31 to 5 TWh. Heat pumps rise to 116 TWh (air HP 21 -> 30 GW).
  - Unabated REF-SMR (6.6 GW) and CCGT-H2 (1.2 GW) disappear, which removes the 1.1 Mt residual SMR emission noted in the earlier Country-level analysis.
- **Industry:** some routes change.
  - Glass fibre and float go fully electric.
  - Steel shifts towards molten-oxide electrolysis (57 -> 64%).
  - Olefins: 7.8% via a methanol route ((COEL)MeOH)O-MEA.
- **Exports:** H2 exports to the rest of the model rise (2050: 104 -> 151 TWh). Note that at country level the "export" is to merged nodes and does not leave the NL+BE system. CH4 is unchanged.
- Nuclear stays at 6.0 GW.

### 2c. Mixed resolution (whole model)
- **Storage collapses:**
  - DE 60 -> 0 (the NSDE011 low cap is 0).
  - UK 164 -> 52.5.
  - DK 36.5 -> 11.
  - NO 69 -> 56.
  - NL 27 -> 10.5.
- Cross-border CO2 shipping/piping into the UK and NO falls sharply. NL+BE net CO2 exports drop from 185 to 43 Mt in 2050.
- **Removals shrink:** DAC captures 139 Mt in NL+BE in mr_fix but only 5 Mt in mr_ccslow. Whole-model negative emissions in "other" go from -52 to -27 Mt.
  - Because the 2050 budget is 0, the remaining positive emissions must fall by the same amount.
- **Gas largely leaves the system:**
  - Whole-model methane use falls by 1.0 PWh.
  - Plain REF-SMR (164 GW) is replaced by SMR with carbon capture, REF-SMR-MEA (187 GW). SMR+CC, CCGT+CC (20 GW) and BECCS digesters disappear.
  - Gas boilers fall 156 -> 23 GW.
- **Replacements:**
  - Biomass heat +181 TWh (bio-boilers 24 -> 132 GW). Biomass is now used for combustion instead of BECCS.
  - Offshore wind +371 TWh, solar +28 TWh, onshore wind +17 TWh.
  - PEM 4.6 -> 33 GW; nuclear 0 -> 8.2 GW (all in NL+BE).
- **Within NL+BE:**
  - Heat pumps drop from 209 to 43 TWh while bio heat rises from 6 to 87 TWh and gas heat from 91 to 6 TWh.
  - Electricity from bio (87 -> 14 TWh) and CCS-equipped power (82 -> 0) drop; nuclear ("other" electricity, 1 -> 91 TWh) takes over.
- **Industry (NL+BE):**
  - Cement switches from CEM2-(Afm)MEA to oxy-fuel + CCS.
  - Glass partly moves from gas+CC to electric and H2 furnaces.
  - Polyethylene now has H2/electric routes.
  - Ammonia stays gas SMR + CCS.
  - Steel stays gas DRI-EAF + CCS.

### 2d. Common mechanism
1. Captured CO2 is still produced at roughly the same level by industry: cement, steel, chemicals and SMR H2 (about 30-45 Mt in NL+BE).
2. With storage capped, the outlet becomes **utilisation** (methanation / e-fuels), which needs much more electrolytic H2.
3. That H2 needs large amounts of extra **offshore wind**, with nuclear helping in the IC1 and mixed-res runs.
4. Heat moves away from gas, either to heat pumps (NL+BE-only runs) or to biomass (mixed-res, where biomass from other countries is available and BECCS no longer has storage).
5. Industrial routes are robust in IC1. They change more at country level and in mixed-res.

## 3. Pessimistic runs compared with each other

### 3a. IC1 pessimistic vs Country pessimistic (nb_ccslow vs nb_ctry_ccslow)
| Metric (NL+BE, 2050) | IC1 pess. | Country pess. |
|---|---|---|
| Objective | 3,829,096 | 3,777,356 (-1.4%) |
| CO2 stored | 10.5 (NLC6 only) | 10.5 (NLC1 8.0 + NLC5 2.5) |
| Offshore wind (TWh) | 454 | 446 |
| Electrolytic H2 (TWh) / PEM (GW) | 149 / 25.4 | 94 / 17.1 |
| Methanation (GW) | 13.4 | 8.4 |
| Nuclear (GW) | 11.0 | 6.0 |
| Heat pumps / unabated fossil heat (TWh) | 80 / 42 | 116 / 5 |
| Gas boilers (GW) | 18.6 | 4.0 |
| Battery storage (GW) | 6.1 | 11.7 |
| H2 net export (TWh) | 0 | 151 |
| Steel MOE share | 57% | 64% |
| Glass fibre/float | H2-heavy | 100% electric |

**Interpretation:**
- The copper-plate country model makes it cheaper to move electricity and H2, so less electrolysis capacity is needed. Pessimistic CCS therefore costs about the same in both (+4.9% vs +5.1%), and the gap between resolutions (-1.4%) is roughly the same as with base CCS (-1.1%).
- The resolution affects *which* site stores CO2 (NLC6 in IC1, NLC1/NLC5 at country level). Country level also decarbonises heat further by electrifying it, whereas IC1 keeps gas boilers and builds more nuclear and methanation.

### 3b. IC1 pessimistic vs Mixed-res pessimistic (nb_ccslow vs mr_ccslow, NL+BE part)
| Metric (NL+BE, 2050) | IC1 pess. | Mixed-res pess. |
|---|---|---|
| NL+BE net CO2 (Mt) | 0 | 90 (balanced by removals/budget elsewhere; 6-country total = 0) |
| CO2 stored in NL+BE (Mt) | 10.5 | 10.5 |
| CO2 net export (Mt) | 0 | 43 (to UK 37, NO 6) |
| DAC capture (Mt) | 0 | 5.3 |
| Offshore wind (TWh) | 454 | 247 |
| Electrolytic H2 (TWh) / PEM (GW) | 149 / 25.4 | 27 / 7.0 |
| Methanation (GW) | 13.4 | 0 |
| Nuclear (GW) | 11.0 | 8.2 |
| Heat: HP / bio / gas (TWh) | 80 / 0 / 42 | 43 / 87 / 6 |
| Methane use (TWh) | 130 | 458 |
| Industry | MOE steel 57%, biomass NH3 98%, H2/electric glass | gas DRI+CCS steel 100%, gas SMR+CCS NH3 100%, glass 50% gas+CC |

**Interpretation:**
- Even with the pessimistic caps, the interconnected system still has about 120 Mt of storage outside NL+BE (NO, UK, DK). NL+BE therefore keeps gas-based industry with CCS and exports CO2, instead of building the e-fuel / methanation chain.
- Each interconnected system weighs its own budget: NL+BE emits 90 Mt "net" in the mixed-res run, offset elsewhere in the 6-country budget.
- Pessimistic CCS hurts the interconnected case more in relative terms (+7.7% vs +5.1%), because it relied far more on storage (356 Mt). But NL+BE itself changes *less* drastically in its industry than IC1 does; its main change is in heat (biomass) and power (nuclear instead of gas+CCS).

## 4. Plots (`tools/plot_compare_nlbe.py`, 11 PNGs each: power mix, capacity, CO2, gas, flows, flow map, costs, emission accounting, nuclear/biomass)
- `runs/3day_nb_ccslow/plots/cmp_vs_base/` - IC1 base vs pessimistic
- `runs/3day_nb_ctry_ccslow/plots/cmp_vs_base/` - Country base vs pessimistic
- `runs/3day_mr_ccslow/plots/cmp_vs_base/` - Mixed-res base vs pessimistic (NL+BE)
- `runs/3day_nb_ctry_ccslow/plots/cmp_vs_ic1_pess/` - IC1 pess. vs Country pess.
- `runs/3day_mr_ccslow/plots/cmp_vs_ic1_pess/` - IC1 pess. vs Mixed-res pess.

## 5. Caveats
- 3 representative days per year. Storage and seasonal effects (caverns, biomass) are coarse.
- NL+BE attribution in mixed-res is an accounting view; only the 6-country budget is constrained.
- Non-NL low caps are not yet verified against the spreadsheet.
- "Electricity: other" mainly reflects nuclear (check if exact attribution is needed).

## CORRECTION 2026-10-13 ~18:40 - DAC is NOT fully disabled (free default unit)
- `patch_nodac_lng.py` set `investment_count_max_cumulative = 0` for all DAC_* units (no *new* DAC). That is in place in all six runs.
- But no unit has an explicit `existing_units`, and the SpineOpt default is **1.0**. Each DAC_* unit has `capacity_per_unit = 1.0` on its CO2 output, so every region gets **one free existing DAC unit**. Up to 1 CO2 unit/h, about 8.76 Mt/yr per region, with no investment cost.
- Evidence (`run_logs/_free1.py`-`_free3.py`): units_invested = 0 for all DAC, yet DAC_NLC1 in mr_fix runs at max 1.0, mean 0.60 per hour.

DAC capture (Mt) per run:

| Run | 2030 | 2040 | 2050 |
|---|---|---|---|
| nb_v2 | 0.10 | 0 | 0 |
| nb_ctry | 0.36 | 0 | 0 |
| nb_ccslow | 0.33 | 0 | 0 |
| nb_ctry_ccslow | 0.25 | 0 | 0 |
| mr_fix | 0 | 142.9 | 172.6 (21 regions, ~8 Mt each) |
| mr_ccslow | 0 | 26.6 | 14.9 |

- Consequence: the NL+BE-only runs are essentially unaffected (DAC <0.4 Mt, 2030 only). **mr_fix and mr_ccslow are contaminated.** DAC is a large free negative-emission source there, which inflates storage use (356 Mt) and the mr pessimistic-vs-base deltas. The mr conclusions in this document should not be shared until the runs are redone with DAC `existing_units = 0`.

## UPDATE 2026-10-14 - Mixed resolution re-run with DAC fixed (`3day_mr_ccslow_dac0`)
- This run supersedes `3day_mr_ccslow`. OPTIMAL, 138 min, objective 7,623,391 (+0.06% vs the free-DAC run), penalties 0, DAC = 0.
- NL+BE 2050 numbers barely change vs the free-DAC run:
  - Net CO2 93 Mt; 10.5 Mt stored; 40 Mt CO2 exported (NL->UK 24, BE->UK 15).
  - Electrolysis 29 TWh; offshore wind 249 TWh; methane 475 TWh.
  - Heat: pumps 37, bio 87, gas 6 TWh. Nuclear 8.4 GW.
  - Industry: steel 100% gas DRI+CCS; ammonia 100% gas SMR+CCS; cement 58% biomass oxy-fuel (BECCS).
- Section 3b conclusions stand. Metrics for the three pessimistic runs: `run_logs/ccs_metrics_pess_NLBE.csv`.
- Decks (`tools/make_slides_pess.py {ctry|mr|combined} out.pdf`):
  - `runs/3day_nb_ctry_ccslow/SLIDES_Pess_IC1_vs_CountryLevel.pdf` (16 p.)
  - `runs/3day_mr_ccslow_dac0/SLIDES_Pess_IC1_vs_MixedRes.pdf` (16 p.)
  - `reports/pessimistic_ccs/SLIDES_Pess_Resolution_vs_Scope.pdf` (10 p.)
