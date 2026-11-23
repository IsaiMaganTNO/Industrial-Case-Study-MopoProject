> **SUPERSEDED IN PART - 2026-10-04.** Sections 6 and 10.3 (add a bioST->atmosphere
> link) are **WRONG and withdrawn**: biomass combustion is net-zero at the stack;
> only BECCS warrants a carbon flow. Section 5 and 10.4 (biomass volume) are
> superseded by `docs/FINDING_biomass_cap.md`, which corrects the units and shows
> the cap **does** bind regionally. A separate claim made in chat that the cap is
> mis-scaled by 365x is also withdrawn - see `TIME_REPRESENTATION.md` section 7.4.
> The flat-load analysis (section 2) and the retraction list (section 9) stand.
# FINDING: Why bioST dominates and VRE is built at exactly zero (IC1, 3-day Group 1)

Status: investigation complete for the primary mechanism; secondary data anomalies flagged.
Baseline run: `checkpoints/Investment_Results.3day_group1.sqlite` (objective 3,250,650.92, OPTIMAL)
Scenario: `baseline_blended_representative` = Base -> wy2009 -> medium_bio -> current -> GA ->
GA_flex0 -> high_CO2 -> flex_buildings -> flex_buildings_wy2009_cu -> flex_industry

## 1. The observation

2050 investment outcome:

| Technology | GW built | Share of 2050 generation |
|---|---|---|
| bioST (biomass steam) | 31.736 | 89.7% |
| wind-on-SP277-HH100 | 5.775 (NLC2 only) | 10.1% |
| solar-PV-no-tracking | 0.000 | 0% |
| wind-off-FO | 0.000 | 0% |

This is not a cost ranking problem. Measured LCOE at 2050 capex with technology-specific
discount rates (`tools/lcoe_compare.py`), capex identical in all 17 regions:

| Technology | capex | LCOE |
|---|---|---|
| solar-PV-no-tracking | 269.5 | **0.0183** |
| wind-on-SP277-HH100 | 934 | **0.0288** |
| wind-off-FO | 2855 | **0.0504** |
| bioST | 1056 (20 y, fuel 0.0388) | **0.0548** |
| nuclear-3 | 6948 (r=0.095) | 0.1098 |
| CCGT-H2 | 896 | 0.2865 |

**Every VRE technology beats bioST on energy cost.** The model builds the expensive one anyway.

## 2. The mechanism: the load is flat, and VRE cannot serve a flat load without storage

2050 hourly system load across the 72 representative hours:

- min 29.07, max 38.32, mean 34.09
- **peak/mean = 1.12**

For comparison the *raw input* 8760 series is realistic: per-node peak/mean 1.43,
system 1.37. The 3-day clustering trims this to 1.22 while still capturing 89.6% of
the annual peak. So clustering flattens the profile somewhat, but it is not the
main cause.

The main cause is that **~47% of 2050 load is industrial process draw that is
literally constant** - min equals max in every hour:

| Process | Constant draw |
|---|---|
| (EL)PEA | 2.478 |
| MOE | 2.401 |
| Diaphragm | 1.085 |
| other-industrial-sectors | 0.917 |
| (NG)PEA-MEA | 0.717 |
| (NG)DRI-EAF-MEA | 0.540 |

This creates a ~29 MW floor in every single hour of the year. A flat floor is a
baseload requirement. Solar at a representative-day CF of 0.154 and onshore wind
at 0.330 cannot serve a baseload floor; bioST, dispatchable with a free-at-the-margin
fuel endowment, can.

Consistent corroborating evidence: **the batteries never cycle.** `battery-storage`
and `battery-storage-iron-air` are 0.000 everywhere, in every period, in every region.
A model with a flat load has no arbitrage spread to monetise, so it builds no storage -
and without storage it has no way to use VRE beyond the instantaneous floor.

Representative-day capacity factors (wy2009) for reference, with bias vs the annual mean:

| Resource | rep-day CF | bias |
|---|---|---|
| solar | 0.154 | 1.11x (favourable) |
| wind onshore | 0.330 | 0.92x |
| wind offshore | 0.679 | 1.27x (favourable) |

Note the rep-day sampling is *biased in favour of* solar and offshore wind, and they
are still not built. The sampling is not hiding VRE value; it is slightly flattering it.

## 3. Why NLC2 is the sole exception

NLC2 has the best wind resource in the model (CF **0.616**, next best NLC5 at 0.535).
It builds onshore wind to its investment-group cap of 5.7748 **exactly** - i.e. it is
cap-bound, not economics-bound. Wherever VRE is good enough to beat the flat-load
problem, the model maxes it out. That is the proof that VRE is buildable and that
nothing is deactivating it (`entity_alternative` has zero rows for VRE units).

## 4. The 2050 energy balance (for the record)

Generation 35.386 = unit draws 16.043 + node demand 18.269 + losses 1.074 (3%). Closes.

Block-weighted annual totals (rep-day weights 05-14: 100.807, 09-10: 159.382,
12-24: 104.811; 24 h each):

- Total 2050 load **302.0 TWh** (node demand 161.5 + industrial draw 140.5)
- Generation 309.5 TWh
- bioST: 646.5 TWh biomass x 0.43 efficiency = **278.0 TWh electricity**, 368.5 TWh waste heat

## 5. Secondary finding: the biomass volume is not physically plausible

Total biomass consumption, block-weighted:

| Period | Total TWh | of which bioST |
|---|---|---|
| 2030 | 98.2 | 0.4 |
| 2041 | 722.1 | 310.1 |
| 2050 | **1,043.0** | 646.5 |

Literature puts realistic NL+BE biomass potential at ~100-150 TWh. 2030 is consistent.
**2050 is roughly 7x too high.** The endowment parameterisation permits it:
low_bio 17,409.1 / medium_bio 24,899.4 / high_bio 29,998.9 storage-state units
(ratios 0.70 / 1.00 / 1.20); largest regions under medium_bio are BEC6 5146.9,
BEC2 2764.5, BEC3 2737.0, NLC3 2471.0.

Biomass is **not forced**: system-wide consumption is 68.8% (2030), 53.4% (2041),
66.8% (2050) of endowment - never 100%, and the fraction is non-monotonic. Ten of
seventeen regions leave their 2050 stock entirely untouched (BEC4, BEC7, BEC8, NLC1,
NLC2, NLC3, NLC5, NLC7, NLC9). All 17 `user_constraint` entities are `heatpump-ratio_*`;
none touch biomass. The model *chooses* this biomass volume.

## 6. Secondary finding: bioST has no atmosphere link

`bioST` has exactly one input (`bio_*`) and one output (`elec_*`). A search for any
entity matching `%bio%atmos%` returns zero rows. **Biomass combustion CO2 is entirely
absent from the emissions accounting.**

By contrast the fossil wiring is correct: `CCGT_NLC6` -> elec only;
`CCGT+CC_NLC6` -> elec + `CO2_NLC6`. The CO2 cap binds at **0.0000 in 2050**, which
drives all fossil generation to zero.

So the 2050 system is: CO2-capped to zero, which eliminates fossil; biomass is
zero-rated so it is unconstrained by the cap; and the flat load makes biomass more
valuable than cheaper VRE. bioST wins by default.

## 7. Data anomalies flagged, not resolved

1. **NLC5 onshore-wind investment-group cap = 0.2887** despite NLC5 having the
   second-best wind CF in the model (0.535). Neighbouring caps are an order of
   magnitude larger (NLC1 4.62, NLC2 5.7748). Probable data error.
2. **`NLC3_HC_DE` `connection_flow_cost` = 0.0004** vs siblings 0.0112-0.0123 (~30x cheap).
3. **External nodes** (`elec_DE/FR/NO/UK/DK/LU`) carry only `storage_active` and
   `storage_longterm_active` - no demand, no generators, no state bounds. `node_state`
   goes negative (DE -19.28, FR -13.25). Bounded in practice only by border capacity.
4. **`existing_connections` has default 1.0 and zero rows**, so every connection has an
   irreducible 1.0 of capacity that investment-count parameters cannot remove. See the
   cross-border test below.
5. Model power unit assumed GW; this rests only on the 161.5 vs ~205 TWh real NL+BE
   cross-check and should be confirmed from the source pipeline.

## 8. Cross-border test (falsification attempt)

Hypothesis tested: cheap imports from unbounded foreign nodes suppress domestic VRE.

`tools/patch_no_xborder_elec.py` produced
`checkpoints/Final_SpineOpt_Model.tiny.3day.noxborder.sqlite`, zeroing 57 rows
(`investment_count_initial_cumulative`, `_max_cumulative`, `_fix_new`) on 19 cross-border
elec connections. Verified: cross-border initial sum 26.06 -> 0.00, with 79 elec-connection
rows left intact in both DBs (domestic and non-elec untouched).

Run: 83.7 min, OPTIMAL, objective **3,252,760** vs baseline **3,250,650.92** (+0.06%).

2050 result deltas:

| Technology | baseline | no-xborder |
|---|---|---|
| bioST | 31.736 | **31.962** (+0.225) |
| wind-on-SP277-HH100 | 5.775 | **5.415** (-0.360) |
| solar-PV-no-tracking | 0.000 | **0.000** |
| wind-off-FO | 0.000 | **0.000** |
| RoR / MOE / REF-SMR | 0.070 / 0.605 / 80.390 | unchanged |

**Caveat on patch efficacy.** Gross cross-border flow fell 62.7 -> 33.7 TWh, not to zero,
because of anomaly (7.4): `existing_connections` defaults to 1.0 with no rows to override,
and `capacity_per_connection` = 1.0 remains on all 19 links. Each border therefore keeps
1.0 of permanent capacity (19 x 1.0 = 19.0 vs the original 26.06 - proportional to the
observed flow reduction). To eliminate borders fully the patch must *insert*
`existing_connections = 0.0` rows, not merely zero investment counts.

The test is therefore a ~46% border reduction rather than an elimination. The conclusion
nevertheless stands: halving interconnection moved the objective by 0.06% and left solar
and offshore wind at *exactly* zero. Net flow was -0.0 in both runs (perfectly balanced
churn), so borders were never providing net energy in the first place.

## 9. Theories proposed and retracted

Recorded deliberately, because each was stated before the falsifying test was run.

1. **Forced biomass consumption / "use-it-or-lose-it".** Retracted: consumption is
   53-69% of endowment and varies by period; 10 regions leave stock untouched; no
   biomass `user_constraint` exists.
2. **Unbounded free foreign nodes acting as an infinite battery.** Retracted: borders
   are capped (`capacity_per_connection` = 1.0 on 19 links; FR_elec_BEC7 runs at 99.4%
   utilisation).
3. **Investment caps blocking VRE.** Retracted: caps exist but are large; NLC1 has
   CF 0.497 and cap 4.62 and still builds zero. Only NLC2 is cap-bound.
4. **CO2 cap structured to exclude VRE.** Retracted: the cap is a simple emissions
   limit; VRE is unaffected by it.
5. **Unrealistic demand input data.** Retracted: raw 8760 series are realistic
   (peak/mean 1.43 per node, 1.37 system). The flatness is introduced by constant
   *industrial process* load plus clustering, not by bad demand data.
6. **Missing `.values.max()` scaling bug in `demand_flex()`.** Retracted: industry
   `demand` is a scalar, so the buildings-branch `.values.max()` is correctly absent.
   Verified: `storage_state_max / demand` = exactly 0.200000 for all 187 nodes
   (= flex_industry 0.1 x comfort_industry 2.0). `flex_industry` is correctly implemented.

Common failure mode across all six: treating a zero-row query as proof of absence
without first confirming the parameter name exists in `parameter_definition`. The
`connection_capacity` / `capacity_per_connection` name error was the single largest
source of wrong conclusions.

## 10. Recommended next steps

1. Re-run the border test with `existing_connections = 0.0` inserted, to close the caveat.
2. Investigate the NLC5 wind cap (0.2887) - likely a data error suppressing the
   second-best wind site in the model.
3. Add the missing bioST -> atmosphere link so biomass CO2 enters the cap, then re-run.
   This is the single change most likely to change the headline result.
4. Constrain the biomass endowment to a literature-consistent 100-150 TWh for NL+BE.
5. Confirm the GW power unit from the source pipeline.
6. Consider whether constant industrial process load should carry *any* demand-side
   flexibility; at present it is a hard baseload floor that structurally advantages
   dispatchable generation.

