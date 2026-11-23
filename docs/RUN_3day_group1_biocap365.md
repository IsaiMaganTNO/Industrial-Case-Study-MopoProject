# RUN DEFINITION: 3day_group1_biocap365

Date: 2026-10-04. Input DB: `checkpoints/Final_SpineOpt_Model.tiny.3day.group1.biocap365.sqlite`
Created by: `tools/patch_biomass_cap_div365.py` from
`checkpoints/Final_SpineOpt_Model.tiny.3day.group1.sqlite` (the Group 1 baseline).

## 1. Purpose

Test whether the 365x-inflated biomass resource is what suppresses VRE investment.
Baseline Group 1 built `bioST` to 31.74 GW (89.7% of 2050 generation) with solar
and offshore wind at **exactly zero**.

## 2. What this patch changes - and ONLY this

204 `parameter_value` rows, all on `biomass-stock_*` entities (17 nodes x 3
alternatives + Base), divided by **365**:

| parameter | rows |
|---|---|
| `storage_investment_count_max_cumulative` | 51 |
| `storage_investment_count_initial_cumulative` | 51 |
| `storage_investment_count_fix_cumulative` | 51 |
| `storage_state_fix` (time series; NaNs preserved) | 51 |

Verified by full row-level diff against the baseline: **exactly 204 rows differ,
and every one belongs to the `biomass-stock` family.** Row count identical
(31,470 both).

Resulting endowment (NL+BE, 17 regions):

| alternative | before | after |
|---|---|---|
| low_bio | 17,409.1 | 47.70 |
| **medium_bio** (active) | **24,899.4** | **68.22** |
| high_bio | 29,998.9 | 82.19 |

These match `checkpoints/Final_SpineOpt_Model.tiny.5rep.biofix.sqlite`
(47.7 / 68.2 / 82.2) to 1 d.p. - an independent corroboration, since that DB was
produced separately.

## 3. Justification for /365

SpineOpt debits long-term storage with a delta formulation
(`constraint_node_state_longterm_trajectory.jl`), weighting each representative
block by `representative_block_coefficient`. In this model those coefficients are
[0.276185, 0.436662, 0.287153] and **sum to exactly 1.000000**, whereas the
representative-day weights used to annualise *flows* sum to **365.000**.

Measured on `biomass-stock_BEC1` -> `bio_BEC1`, 2050:

| quantity | value |
|---|---|
| fuel delivered (weighted annual) | 397,144.6 |
| stock debited (`node_state_longterm`) | 1,088.07 |
| **ratio** | **365.0** |

The same /365 correction is **already applied to the `atmosphere` CO2 cap in this
same database** (165.40 -> 0.45315068, 36.80 -> 0.10082192). This patch makes
biomass consistent with that precedent.

Upstream sanity check: `annual_production` for NL+BE `medium_bio` is 86,173,831
MWh/yr (`biomass_DB.py` line 264 converts PJ -> MWh via `*277777.77`), and
`scenario_run.py:biomass_limitations()` applies
`biomass_potential_realistic: 0.5` -> **~43 TWh/yr** intended. Literature for
NL+BE is ~100-150 TWh/yr technical potential, so ~43 TWh/yr is conservative but
defensible.

## 4. What is CARRIED OVER from the baseline (unchanged, deliberately)

| feature | state | note |
|---|---|---|
| **Cross-border elec connections** | **PRISTINE** | initial sum **26.060**, asserted by an in-script guard. The `noxborder` experiment is **NOT** carried over. |
| `atmosphere` CO2 cap | /365-patched | inherited from `tiny.3day.co2rebuild`; 2030 0.45315 / 2041 0.10082 / 2050 **0.0** |
| Forced retirement | 467 `investment_count_fix_cumulative` rows | the "Group 1" retirement scenario |
| `CH4-geo-formation` | untouched | same latent 365x defect, but never binds (floors at exactly 90% of full) |
| Representative days | 05-14 / 09-10 / 12-24, weights 100.807 / 159.382 / 104.811 | sum 365.000 |
| Scenario | `baseline_blended_representative` | Base -> wy2009 -> medium_bio -> current -> GA -> GA_flex0 -> high_CO2 -> flex_buildings -> flex_buildings_wy2009_cu -> flex_industry |

## 5. Relationship to `tools/patch_biomass_stock.py` - DO NOT RUN BOTH

That earlier script diagnoses the same 365x symptom but attributes it to
`storage_state_fix` refilling, and remedies it by REMOVING the refill and
MULTIPLYING by `HORIZON_YEARS = 10` (its docstring flags the x10 as
`*** A GUESS ***`). That does not address the coefficient normalisation and
would leave the cap ~36.5x too loose. **This script supersedes it.**

## 6. Predictions (recorded BEFORE the run, so they can falsify)

1. `bioST` capacity collapses from 31.74 GW.
2. Biomass consumption 2050 falls from 1,043 TWh toward ~43 TWh.
3. Some VRE appears. **If solar and offshore wind are STILL exactly zero, the
   biomass cap was not the cause** and the flat-load hypothesis
   (`FINDING_biomass_dominance_zero_vre.md` section 2, peak/mean 1.12) becomes
   the leading explanation.
4. Objective rises above the baseline 3,250,650.92.

## 7. Checks to run on completion

- `objective_objective_penalties` **must be 0.00** - `atmosphere` carries
  `balance_penalty = 10000`, so an over-tight cap yields a paid-for violation
  that still reports OPTIMAL (`TIME_REPRESENTATION.md` section 7.5).
- Confirm `node_state_longterm` on `biomass-stock_*` no longer bottoms at 0.00
  on every representative day.
- Re-derive weighted biomass TWh and compare against the ~43 TWh/yr target.
- Check whether the model goes infeasible: if a region cannot meet demand with
  1/365th of the former biomass, that is a real signal, not a bug.

## 8. Outstanding caveat

The model power unit (assumed **GW**) is still unverified from the pipeline. The
energy-side trace (PJ -> MWh) is solid, but all TWh figures remain contingent on
that assumption.

## 9. RESULT (completed 2026-10-04) - hypothesis CONFIRMED

OPTIMAL, 82.4 min, objective **3,334,510** vs baseline 3,250,651 (**+2.6%**).
`objective_objective_penalties = 0.00`, so the result is real abatement, not slack.

All four predictions in section 6 held, including the falsification test (#3):

| prediction | outcome |
|---|---|
| 1. `bioST` collapses | **31.736 -> 0.000 GW** |
| 2. Biomass falls toward ~43 TWh | **1,043 -> 24.9 TWh** |
| 3. Some VRE appears (else biomass was NOT the cause) | **solar 0 -> 46.7 GW (10 regions); wind 5.8 -> 26.0 GW (6 regions)** |
| 4. Objective rises | **+2.6%** |

Full analysis, CSVs and plots: `reports_3day_biocap365/`.

**Key nuance:** gas+CCS becomes the largest firm source (100 TWh) and CO2 capture
triples. The flat-load finding (peak/mean 1.12) was real but was NOT the cause of
zero VRE - it explains why ~130 TWh of firm capacity is needed, not why VRE was
absent. Biomass was the cause.

**Two new anomalies found, unresolved:** `oil-eng` generates 26.5 TWh with **no CO2
output wired at all**, and `DAC` builds 11.9 GW but operates at **zero flow**. Both
need fixing before publication; neither invalidates the headline.

### 9.1 CORRECTION to the oil-eng anomaly (2026-10-04)

The `oil-eng` "no CO2 output" flag in the first write-up is **RETRACTED**. This
model books emissions **upstream at fuel supply**, not at combustion. `oil-eng`
draws `HC_*`, which is supplied by `REF-SMR` (704.2 TWh) and `REF-SMR-MEA`
(329.7 TWh), both of which DO emit to `atmosphere`. 17 technologies share this
pattern (`CCGT`, `OCGT`, `SMR`, `gas-boiler`, `nuclear-3`, ...); 84 technologies
emit to `atmosphere`. Consistent with `docs/FINDING_fuel_based_emissions.md`.

Decisive cross-check: 2050 gross emissions == captured CO2 **exactly**
(164,362.6 both sides) and net `atmosphere` lands on 0.000000 - impossible if a
26.5 TWh emitter were unaccounted.

`DAC` building 11.877 GW at zero `atmosphere` flow remains **open**.
