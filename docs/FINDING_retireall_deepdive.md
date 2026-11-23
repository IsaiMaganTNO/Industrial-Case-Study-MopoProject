# FINDING: retireall deep-dive  electrolysers, batteries, H2 and sector coverage

Run: `Investment_Results.3day_retireall.sqlite`, OPTIMAL, objective 3,368,121,
`objective_objective_penalties = 0.00`. Cache: `run_logs/retireall.pkl`.

## 1. Electrolysers are NOT blocked  they are outcompeted ~3x

17 `PEM_<region>` units exist and are fully investable: capex series
2030 2740.50 -> 2041 1577.62 -> 2050 613.71, `fom_cost` 0.00136957,
`investment_count_max_cumulative` 1000.0, `lifetime_economic` 25Y,
`discount_rate_technology_specific` 0.08, efficiency
`flow_ratio_equality_coefficient` 0.622 (1.608 MWh elec per MWh H2).

**New PEM investment in every year: zero.** The only "electrolysis"-classified
fleet is 0.151 units of `Diaphragm` (chlor-alkali, 5 regions) which is fixed
endowment, not H2 production.

PEM capex at 2050 (613.71) is *below* SMR+CC (1057.32), so capex is not the
cause. The cause is the marginal electricity price. In 2050 `CCGT+CC` supplies
100,800 and is the price-setter:

| | per MWh H2 |
|---|---|
| marginal electricity (CCGT+CC, eta 0.4857, gas 0.015, vom 0.01035) | 0.0680 |
| PEM fuel 0.0680/0.622 = 0.1093 + capex 0.0073 | **0.1166** |
| SMR+CC fuel 0.015/0.69 = 0.0217 + capex+FOM 0.0180 | **0.0397** |

PEM is **2.93x** more expensive. Even priced at the *cheapest* VRE LCOE
(wind-on 0.01748) PEM lands at 0.0369 vs SMR+CC 0.0397  only marginally
better, and that assumes 0.9 CF on wind-only power, which the 3-day
representative structure cannot deliver. With a realistic CF the advantage
vanishes. **Electrolysis absence is an economic result, not a data defect.**

Root driver: gas at `vom_cost` 0.015 with no carbon price on the *abated*
route, so CCS gas is cheap both as power and as H2 feedstock.

## 2. Batteries exist and are never built

34 storage units (17 `battery-storage`, 17 `battery-storage-iron-air`) plus
their 34 companion nodes, all investable:
`storage_investment_cost` 2050 = 151.70 (Li-ion) / 11.58 (iron-air),
`storage_investment_count_max_cumulative` 10000.0, `storage_state_max` 1.0.

`node_state` results contain **only 5 nodes**: the two CO2 reservoirs and three
demand-response nodes (`car-DR` 0.07, `truck-DR` 0.01, `bus-DR` 0.00 in 2050).
Zero battery state in any year.

Interpretation: with 3 representative days and no inter-day chronology, intra-day
VRE surplus is small and the firm fleet (CCGT+CC 100.8, oil-eng 43.0) covers the
residual. **This is a time-representation artefact and should be flagged as a
limitation, not a result.** Any storage conclusion from this run is invalid.

## 3. H2 usage grew ~1600x, but it is blue and imported

Total hydrogen supply: 2030 **53.9** -> 2040 **35,950.4** -> 2050 **86,942.3**.

Sources 2050: `SMR+CC` 44,441.4 (51%) + `LH2-terminal` imports 42,500.9 (49%).
SMR+CC is partly sunk (endowment 6.25 units) but **does build new: 5.073 units
in 2050**. Import terminals are capped at endowment
(`max_cumulative` == `initial_cumulative`, 4.852 units total) so imports are
maxed out and cannot expand  SMR+CC is the true swing supplier.

Consumers 2050: `(H2)DRI-EAF` 1325.0, `(H2)-CC_gfl` 231.4, `(H2)-CC_gco` 81.9,
`(H2)-CC_gfi` 57.2 (output units, not fuel input).

Note `REF-SMR-MEA` grows 0 -> 12.768 -> 37.000 units (refinery SMR retrofitted
with amine capture)  the largest single new-build in the hydrogen-production
category.

## 4. All sectors do move  including the 13 previously unchecked

The 14 scaffolding families all flip reference -> alternative, reaching
**100% alternative and exactly 0.000 reference units in 2050**: ceramics,
food-beverages-tobacco, leather-and-textile, machinery-equipment,
other-chemicals, other-industrial-sectors, other-non-ferrous-metals,
pharmaceuticals, printing-and-media, transport-equipment, wood-and-wood-products,
aluminium-primary, pulp, paper.

Caveat: these are **scaffolding-tier** units with a single generic
`*-production-alternative` counterpart. The flip is mechanical (the patch forces
it) and carries no technology content. Only the **priced tier** (24 units) gives
an economically meaningful route choice.

Priced-tier 2050 route mix (% of sector output):

| sector | 2030 | 2050 |
|---|---|---|
| cement | EU-mix 100% | biomass 80.6%, alt-fuel-mix 19.4% |
| ammonia | NG 100% | NG 53.8%, biomass 46.2% |
| olefins | NG 100% | NG 79.5%, methanol 20.5% |
| glass (float/fibre) | NG 100% | NG 75%, H2 25% |
| glass (container) | NG 100% | NG 94%, H2 6% |
| steel (primary) | coal 100% | NG 89.3%, H2 10.7% |
| chlorine (control) | elec 100% | elec 100% (unchanged) |
| steel (secondary) (control) | scrap 100% | scrap 100% (unchanged) |

Both controls unchanged, as predicted.

## 5. Net CO2 hits exactly zero in 2050

System total: 2030 **165,400** -> 2040 **36,800** -> 2050 **-0.0**.
The `other` category swings to **-17,066** (DAC + bio-CCS) to offset residual
`hydrogen production` 13,380 and `industry: CCS-equipped` 3,409.
`industry: reference process` and `boilers (other fuels)` both reach 0.

## Open / unresolved

- Unabated `CCGT` 0.0 -> 4,513.3 and `oil-eng` 26.5 -> 43,035.7 in 2050 still
  unexplained; `oil-eng` vom 0.00521 at eta 0.35 is suspiciously cheap.
- `DAC` 9.78 units with zero `atmosphere` flow (pre-existing).
- Storage result is not usable (see S2).
