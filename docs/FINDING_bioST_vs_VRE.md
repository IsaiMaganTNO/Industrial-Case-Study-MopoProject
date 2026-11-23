# FINDING: Why bioST dominates 2050 electricity (and VRE does not)

Status: **investigation log, partly unresolved.** Date: 2026-10-04.
Run under analysis: Group 1 forced-retirement, 3-day model, objective 3,250,650.92
(`reports_3day_group1/`, input `checkpoints/Final_SpineOpt_Model.tiny.3day.group1.sqlite`).

All figures are block-weighted annual energy (weights 100.807 / 159.382 / 104.811
for 14 May / 10 Sep / 24 Dec), unless stated. Model power unit inferred as GW.

---

## 1. The headline anomaly

2050 electricity generation:

| tech | TWh/yr | share |
| --- | ---: | ---: |
| `bioST` | 278.0 | 89.7% |
| `wind-on-SP277-HH100` | ~31 | 10.2% |
| `RoR` | ~0.3 | 0.1% |
| `solar-PV-no-tracking` | **0.0** | 0% |
| `wind-off-F{B,O}-SP370-HH155` | **0.0** | 0% |

Existing solar (44.5 GW) and existing onshore wind retire to zero by 2050 with no
replacement. New onshore wind is built in **exactly one region (NLC2)**.

## 2. Biomass volumes are implausible

| year | total biomass use | `bioST` share | `bioST` elec out |
| --- | ---: | ---: | ---: |
| 2030 | 98.2 TWh | 0.4 TWh (0.4%) | 0.2 TWh |
| 2041 | 722.1 TWh | 310.1 TWh (42.7%) | 133.4 TWh |
| 2050 | **1,043.0 TWh** | **646.5 TWh (62.0%)** | **278.0 TWh** |

- 2030 (98.2 TWh) matches literature for NL+BE (~100-150 TWh). 2050 is **~7x too high**.
- `bioST` efficiency is **0.430** (`flow_ratio_equality_coefficient`), so 646.5 TWh
  biomass yields 278.0 TWh electricity and **368.5 TWh is rejected as waste heat**.
- Endowment totals (`storage_investment_count_initial_cumulative`, stock units, NOT TWh):
  `low_bio` 17,409.1 / `medium_bio` 24,899.4 / `high_bio` 29,998.9 (ratios 0.70 / 1.00 / 1.20).
- Only ~67% of the endowment is ever consumed, so the resource limit **never binds**.

## 3. Load is flat, and that is what forces firm capacity

2050 total load = **302.0 TWh**, of which:
- node `demand` 161.5 TWh (constant across 2030/2041/2050)
- industrial process draw **140.5 TWh** (grows 89.0 -> 114.4 -> 140.5)

Hourly (mean MW): min 29.07, max 38.32, mean 34.09 -> **peak/mean = 1.12**.
The floor is 76% of peak in every hour. Largest industrial sinks are *perfectly*
flat (min == max): `(EL)PEA` 2.478, `MOE` 2.401, `Diaphragm` 1.085,
`other-industrial-sectors` 0.917, `(NG)PEA-MEA` 0.717, `(NG)DRI-EAF-MEA` 0.540.

Solar at CF 0.154 cannot serve that floor; no storage is built anywhere.

## 4. Costs do NOT explain the outcome

LCOE on the actual representative days (wy2009, each unit own discount rate):

| unit | capex 2050 | life | CF | fuel/MWh | LCOE |
| --- | ---: | ---: | ---: | ---: | ---: |
| `solar-PV-no-tracking` | 269.5 | 40 | 0.154 | 0 | **0.0183** |
| `wind-on-SP277-HH100` | 933.9 | 30 | 0.330 | 0 | **0.0288** |
| `wind-off-FO-SP370-HH155` | 2,855.1 | 30 | 0.599 | 0 | **0.0504** |
| `bioST` | 1,056.2 | 20 | 1.00 | 0.0388 | **0.0548** |
| `nuclear-3` | 6,948.2 | 40 | 1.00 | 0.0221 | 0.1098 |
| `CCGT-H2` | 896.5 | 25 | 1.00 | 0.2745 | 0.2865 |

**All three VRE options are cheaper per MWh than `bioST`.** Once `bioST` exists its
marginal cost is fuel+VOM = 0.0388 + 0.0023 = **0.0411/MWh**, which is what new VRE
must beat to displace *energy* (not capacity).

## 5. Hypotheses TESTED AND REJECTED

Recorded so they are not re-investigated:

1. **"Biomass must be consumed (use-it-or-lose-it)"** - FALSE. System-wide only
   68.8% / 53.4% / 66.8% of the endowment is used in 2030/2041/2050, and the
   fraction varies by period. 10 of 17 regions leave their 2050 stock *untouched*
   (`BEC4`, `BEC7`, `BEC8`, `NLC1`, `NLC2`, `NLC3`, `NLC5`, `NLC7`, `NLC9`).
   `storage_state_fix` re-grants the stock at each milestone but `NaN` in between
   means *unconstrained*, and there is no `storage_state_min` / `cyclic_condition`
   / `frac_state_loss` on any `biomass-stock_*` node.
2. **"Foreign zones are unbounded free batteries"** - FALSE. Cross-border links are
   capacity-limited: `capacity_per_connection` = 1.0 on all 19, with
   `investment_count_initial_cumulative` 0.7-2.7 per link. My "0 rows" result came
   from querying a **non-existent** parameter name (`connection_capacity`; the real
   name is `capacity_per_connection`). See `FINDING_import_export_caps.md`.
3. **"VRE is blocked by investment caps"** - FALSE as a general claim. All VRE has
   `investment_count_max_cumulative` = 1000 and `unit__investment_group` caps have
   large headroom in most regions (e.g. `solar-PV_NLC3` 35.9 unused).
4. **"Zero CO2 cap excludes everything except bioST"** - explains why *fossil* is
   zero, does NOT explain zero VRE (VRE is also carbon-free and cheaper).
5. **"Electricity demand data is unrealistic"** - FALSE. Raw `demand` series are
   8760-hour profiles with **peak/mean 1.43**, which is realistic. The 3-day sample
   reduces this to 1.22 and captures 89.6% of annual peak - real but secondary.
6. **"`flex_industry` has a unit-conversion bug"** - FALSE. Ratio
   `storage_state_max / demand` is **exactly 0.200000 on all 187 nodes** =
   `flex_industry (0.1) * comfort_industry (2.0)`. The industry branch of
   `demand_flex()` omits `.values.max()` only because industry `demand` is a
   **scalar**, whereas heat demand is a time series. Code is correct.
7. **"`bioST` is a CHP by-product"** - FALSE. `bioST_NLC6` has exactly one input
   (`bio_NLC6`) and one output (`elec_NLC6`).

## 6. Confirmed structural facts

- `bioST` has **no atmosphere link at all** - no `flow_ratio_equality_coefficient`
  to any atmosphere node (searched `%bio%atmos%`, 0 rows). Biomass combustion is
  booked as **exactly zero CO2**, not net-zero-with-a-tracked-flow. Compare
  `CCGT+CC_NLC6` which outputs to `CO2_NLC6`. With the 2050 CO2 cap binding at
  **0.0000**, this makes `bioST` structurally exempt where fossil is excluded.
  Related to `FINDING_co2_gateway_accounting.md`.
- `bioST` exists in 18 units (17 regions + `bioST-existing_NLC8`).
- 9 of 17 regions generate **zero** electricity in 2050 and import everything.
  Generation concentrates in NLC2 (327% self-sufficiency), NLC4 (301%), BEC1 (193%).
- NLC2 has the **highest onshore wind CF in the model** (0.616 vs 0.535 next best)
  and is built **exactly to its group cap** of 5.7748. The second-best site NLC5
  (CF 0.535) has a group cap of only **0.2887** - effectively nothing.
- Cross-border trade nets to ~zero (mean -0.162 MW) but supplies **7-11% of load at
  the six highest-load hours**, where `bioST` is pinned at its full 31.74 GW.

## 7. OPEN

Why VRE investment is **exactly 0.000** in all 17 regions despite being cheaper per
MWh remains **unexplained**. The flat-load / firm-capacity argument is the most
consistent story but is **inference, not proof**: it explains why *some* `bioST` is
needed, not why solar is not built to displace biomass *energy* during sunlit hours.
A pure corner solution is not what an LP normally produces when mixed solutions exist.

Discriminating test not yet run: fix 1 unit of `solar-PV-no-tracking_NLC5` via
`investment_count_fix_new`, re-solve, read objective delta.

## 8. In-flight test

`checkpoints/Final_SpineOpt_Model.tiny.3day.noxborder.sqlite` - all 19 cross-border
ELECTRICITY connections disabled (`investment_count_initial_cumulative`,
`_max_cumulative`, `_fix_new` all zeroed; 57 rows). Patch:
`tools/patch_no_xborder_elec.py`. Expect `bioST` to grow ~4 MW; **not** expected to
produce solar, since at 01:00 on 14 May the system is net *exporting* 6.34 MW.

## 9. Method warning

Five claims in this session were asserted and then retracted. Every failure had the
same shape: **a query returned 0 rows and absence of evidence was treated as evidence
of absence.** Before concluding anything from an empty result, enumerate
`parameter_definition` and confirm the parameter name exists.
