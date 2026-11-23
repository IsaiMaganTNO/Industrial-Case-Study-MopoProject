> **SUPERSEDED 2026-10-04 by `docs/FINDING_biomass_cap_365x_CONFIRMED.md`.**
> Sections 3-6 of this file are WRONG. I measured `node_state_longterm` at
> milestone boundaries, which aliases away the per-representative-day refill.
> Using `node_state`, the stock is drained to exactly 0.00 on EVERY
> representative day and the effective annual availability is **365.0x** the
> authored cap. The source trace (`biomass_DB.py` line 264, PJ -> MWh) gives an
> intended NL+BE cap of ~43 TWh/yr after `biomass_potential_realistic: 0.5`.
> The "no scaling bug / ~9,088 TWh / 11.5% used" conclusion below is retracted.
> Section 0(a) - biomass CO2 is net-zero, no atmosphere link needed - still STANDS.
# FINDING: biomass availability cap in IC1 - what it actually is

Date: 2026-10-04. Status: **arithmetic verified; provenance of the magnitude UNRESOLVED.**
Run: Group 1, 3-day, `reports_3day_group1/` (objective 3,250,650.92).
Supersedes my earlier claims in this session. Read sections 6 and 7 before acting.

## 0. Two corrections to things I said earlier today

**(a) I claimed biomass CO2 should be added to the cap. WRONG - withdrawn.**
Biomass combustion is net-zero at the stack under standard energy-sector
accounting; the carbon is booked in LULUCF at harvest. A negative flow belongs
only on BECCS. `bioST` having no atmosphere link is **correct modelling**, not a
defect. `docs/WHY_NOT_atmosphere_commodity.md` and
`docs/FINDING_fuel_based_emissions.md` are the relevant prior work.

**(b) I claimed the biomass cap is mis-scaled by ~365x ("42x too loose"). WRONG - withdrawn.**
This directly contradicted `TIME_REPRESENTATION.md` section 7.4, which had already
examined `biomass-stock_BEC1` (cap 1,088.07, `state_max` **1**, 1.5 days of
headroom) and concluded **"already per-period -> leave"**. That conclusion stands.
I made the claim without reading the docs. Specific errors:

1. I compared *weighted annual flow* (1,043) against the *stock endowment*
   (24,899). Different units. Meaningless ratio.
2. I said "the cap never binds". **False** - see section 3.
3. My per-region ">100% of endowment" table divided a 72-hour flow sum by a
   stock level. Garbage.

## 1. Where the limit lives

17 `biomass-stock_*` nodes, one per NUTS3 region. Parameters:

| parameter | alternative | role |
|---|---|---|
| `storage_investment_count_initial_cumulative` | low/medium/high_bio | the endowment |
| `storage_investment_count_max_cumulative` | low/medium/high_bio | same value |
| `storage_investment_count_fix_cumulative` | low/medium/high_bio | same value |
| `storage_state_max` | Base | **1.0** |
| `storage_state_fix` | low/medium/high_bio | refill schedule |
| `storage_active`, `storage_longterm_active` | Base | `5` = true |

Effective cap = `storage_state_max` x `storage_investment_count_max_cumulative`
(per `FINDING_import_export_caps.md` section 3 - **not** `node_state_cap`, which
does not exist and whose empty query was previously misread as "uncapped").

Endowment totals, summed over the 17 regions:

| alternative | stock units per period |
|---|---|
| `low_bio` | 17,409.1 |
| `medium_bio` **(active)** | 24,899.4 |
| `high_bio` | 29,998.9 |

Ratios 0.70 / 1.00 / 1.20. Largest regions under `medium_bio`: BEC6 5,146.9,
BEC2 2,764.5, BEC3 2,737.0, NLC3 2,471.0. Smallest: NLC5 131.9, BEC7 267.9.

## 2. The refill schedule - per milestone, not cumulative

`storage_state_fix` on `biomass-stock_NLC6` (`medium_bio`):

```
2029-12-31T23:00  393.31      2040-12-31T23:00  393.31      2049-12-31T23:00  393.31
2030-01-01T00:00  nan         2041-01-01T00:00  nan         2050-01-01T00:00  nan
```

The stock is **re-granted in full at the start of each milestone period** and is
`nan` (= unconstrained, free to deplete) in between. So the endowment is a
**per-period** allowance, not a budget shared across 2030/2041/2050.

`operations_y*` resolution is **365D** (verified), so there is **one draw-down per
year** - the condition described in `TIME_REPRESENTATION.md` section 7.1.

## 3. The cap DOES bind - regionally

`node_state_longterm` on `biomass-stock_*`, 2050:

| region | endowment | 2050 end state |
|---|---|---|
| `biomass-stock_BEC1` | 1,088.07 | **0.00** (exhausted) |
| `biomass-stock_NLC4` | 1,689.88 | **0.00** (exhausted) |
| `biomass-stock_BEC2` | 2,764.48 | 2,685.02 (3% used) |
| `biomass-stock_NLC6` | 393.31 | 393.31 (untouched) |
| `biomass-stock_NLC5` | 131.95 | 131.95 (untouched) |

Trajectory for BEC1: 962.94 (2030) -> refill -> 220.97 (2041) -> refill -> **0.00** (2050).
NLC4: 1,545.93 -> 578.50 -> **0.00**.

**Two regions hit exactly zero.** This matches `FINDING_import_export_caps.md`
section 3 ("the biomass fix is working and binds hard"). My "never binds" claim
is retracted.

System-wide depletion, however, is small:

| year | depleted | endowment | % |
|---|---|---|---|
| 2030 | 269.1 | 24,899.4 | **1.1%** |
| 2041 | 1,978.5 | 24,899.4 | **7.9%** |
| 2050 | 2,857.4 | 24,899.4 | **11.5%** |

**Binding regionally, slack system-wide.** Both statements are true and not in
conflict. The resolution is that biomass moves between regions over `*_bio_*`
connections (a near-complete 17x17 mesh), so whether a regional cap binds depends
on transport capacity as well as local endowment. BEC1 and NLC4 are the two
largest *generation* hubs (193% and 301% self-sufficiency), and they exhaust
their local stock while 10 other regions leave theirs completely untouched.

## 4. Unit conversion - and its single load-bearing assumption

Empirically, in **all three periods to 4 significant figures**:

```
weighted annual energy / stock depleted = 365.0
unweighted 72-h flow   / stock depleted = 3.00   (= the 3 representative days)
```

So **1 stock unit == 365 GWh/yr of fuel**, i.e. one unit sustains 1 GW-equivalent
drawn once per day for a year. On that basis:

| | stock units | implied TWh/yr |
|---|---|---|
| `low_bio` | 17,409.1 | ~6,354 |
| `medium_bio` | 24,899.4 | **~9,088** |
| `high_bio` | 29,998.9 | ~10,950 |
| 2050 consumption | 2,857.4 | 1,043.0 |

> **Load-bearing assumption:** this rests on the model power unit being **GW**,
> which has *never been verified from the source pipeline*. It is currently
> supported only by the 2050 node demand of 161.5 TWh being the right order of
> magnitude against real NL+BE electricity demand (~205 TWh/yr). If the unit is
> not GW, every TWh figure in this document scales. **Do not quote these TWh
> numbers externally until the unit is traced.** This is open item 1.

## 5. The implausibility, stated carefully

| year | biomass consumed |
|---|---|
| 2030 | 98.2 TWh |
| 2041 | 722.2 TWh |
| 2050 | **1,043.0 TWh** |

NL+BE sustainable biomass potential in the literature is **~100-150 TWh/yr**.
2030 sits inside that range. **2041 and 2050 do not**, by a factor of ~5-7.
For scale, 1,043 TWh of primary biomass is ~5x the two countries' entire annual
electricity demand.

If the section-4 conversion holds, the authored `medium_bio` cap of ~9,088 TWh/yr
is **~60-90x** a defensible NL+BE potential. The cap is therefore not binding at
the system level for any realistic configuration, which is why consumption can
climb to 1,043 TWh and still return a clean OPTIMAL.

**This is a magnitude-of-input problem, not a time-representation problem.**
Do NOT "fix" it by dividing by 365 - `TIME_REPRESENTATION.md` section 7.4
specifically warns that for `state_max = 1` nodes this would push the cap below
one period's consumption and likely make the model infeasible.

## 6. OPEN: why is the cap this large? (prime suspect: EU-case values)

~9,088 TWh/yr is implausible for two countries but is **not** implausible for
**pan-European** biomass potential. `SESSION_HANDOVER.md` section 4 records:
*"The EU case assumes 50% of technical potential - worth matching"*, and
`EU_CASE_MIGRATION.md` records `biomass_potential_realistic: 0.5`.

Hypothesis to test: the IC1 `biomass-stock_*` endowments carry **EU-scale
potential** rather than values downscaled to the 17 NL+BE NUTS3 regions - i.e.
a missing or mis-applied regional allocation step.

Not yet tested. Required: locate where `storage_investment_count_initial_cumulative`
for `biomass-stock_*` is authored upstream and compare against the EU_case DB.
`TIME_REPRESENTATION.md` section 7.4 already asked for exactly this trace:
*"This is an inference from the data, not something verified against a
specification. If you can trace where `biomass-stock` availability is authored
upstream, confirm it."* **It has still never been done.** It is the single
highest-value open item.

## 7. Open items, ranked

1. **Verify the model power unit (GW?) from the source pipeline.** Everything in
   section 4 and 5 depends on it.
2. **Trace `biomass-stock` endowment provenance upstream**; compare with EU_case.
   Tests the section-6 hypothesis.
3. Only then decide whether to re-author the cap to a literature-consistent
   100-150 TWh/yr for NL+BE.
4. `NLC5` onshore-wind investment-group cap 0.2887 despite the 2nd-best wind CF
   in the model (0.535). Probable data error, unrelated to biomass.

## 8. Method note

In this session I asserted and then retracted: forced biomass consumption;
unbounded foreign nodes; VRE blocked by investment caps; CO2 cap excluding VRE;
unrealistic demand data; a `.values.max()` scaling bug; biomass CO2 missing from
the cap; and a 365x biomass cap mis-scaling. Eight retractions.

Two distinct failure modes:
- **Absence of evidence treated as evidence of absence** - a query returns 0 rows
  and I conclude the thing does not exist, without checking the parameter name
  exists in `parameter_definition`. (`connection_capacity` vs
  `capacity_per_connection`; `node_state_cap`.)
- **NOT READING THE EXISTING DOCS.** The 365x claim and the biomass-CO2 claim
  were both already answered in `TIME_REPRESENTATION.md` and
  `WHY_NOT_atmosphere_commodity.md`. Weeks of prior work was re-litigated and
  contradicted because I did not spend five minutes reading `docs/` first.

**Read `docs/` before forming any hypothesis about this model.**

