# FINDING: Gas supply - capacity is CORRECT; the defect is 100% year-round load factor

> **See also `FINDING_gas_volumes_and_transit.md`**, which measures actual consumption
> (434/624/662 TWh), proves in-model transit is exactly 0.0 TWh, and shows the source
> capacity is a **transit-capable terminal send-out** figure - a better-founded criticism
> than anything in this file. It also corrects the `gas-extraction` vs storage distinction.

Run `3day_co2bidir`. Scripts: `run_logs/_gas*.py`, `_gnote.py`, `_gorig.py`, `_gdiv.py`,
`_glf.py`, `_gbudget.py`, `_gretract.py`.

> ## RETRACTION (2026-10-07)
> An earlier version of this file claimed the builder **replicated national gas capacity
> into every NUTS3 region**, giving an "8.60x overstatement" and a 77 TWh correct ceiling.
> **That claim is WRONG and is fully withdrawn.** The IC1 values are national totals
> **already divided by region count**. Verified against the upstream European dataset
> `data/Gas/Gas_Sectors_Dataset.xlsx`, which uses real country codes:
>
> | tech | country | national GWh/d | /n regions | IC1 value | ratio |
> |---|---|---:|---:|---:|---:|
> | LNG-terminal | BE (8) | 669.000 | 83.6250 | 83.6250 | **1.0000** |
> | LNG-terminal | NL (9) | 860.300 | 95.5889 | 95.5889 | **1.0000** |
> | gas-extraction | NL (9) | 284.548 | 31.6164 | 31.6164 | **1.0000** |
> | bio-diges-up | NL (9) | 8.519 | 0.9466 | 0.9466 | **1.0000** |
>
> Model total methane = **662.1 TWh = exactly 1.0000x** the national ceiling. No
> replication, no double counting. The disaggregation was done deliberately in building the
> IC1 placeholder.
>
> **Blind-spot postmortem (6th instance of the recurring pattern).** I observed identical
> values across regions and concluded "national total replicated" without testing the
> equally consistent hypothesis "national total *divided* and therefore equal". The single
> query that would have settled it - comparing against the upstream national dataset
> sitting in the same folder - was not run. The column header `To Country` was treated as
> corroborating evidence when it is merely an unchanged legacy header.
> **Rule: when values are suspiciously uniform, compute the implied national aggregate and
> compare it with the source before alleging a multiplication error.**

## 1. Where the gas comes from (unchanged, verified)
Two sources only, feeding `CH4_*` via the global `fossil-CH4` node:

| tech | 2030 | 2040 | 2050 |
|---|---:|---:|---:|
| `LNG-terminal` | 434,134 | 558,199 | 558,199 |
| `gas-extraction` (NL only) | 0 | 66,234 | 103,864 |
| **total GWh** | 434,134 | 624,433 | **662,062** |

Carbon booked upstream at the gate (0.2/unit), per `FINDING_upstream_carbon_gate.md`.
**Blind spot closed:** `CH4_DE/FR/UK/LU` have **no feeders at all** (only `storage_active`),
so the 12 cross-border CH4 connections cannot inject gas. `supply` captures 100% of methane.
(Inspection only - no trade component modified.)

## 2. The real defect: 100% load factor, every hour of every year
Observed supply equals nameplate x 8760 **exactly in all 17 regions** (`_glf.py`):

| | 2030 | 2040 | 2050 |
|---|---:|---:|---:|
| BE (% of LNG capacity) | **100.0%** | **100.0%** | **100.0%** |
| NL (% of LNG+extraction) | 45.5% | 91.0% | **100.0%** |

There is **no `availability_factor`, no profile, no annual energy budget** on these units -
only `capacity_per_unit`, `vom_cost` and fixed investment counts. The cap is a pure hourly
power limit.

Why this is wrong in the real world:
- **LNG terminals do not run flat out all year.** Actual EU LNG terminal utilisation is
  typically ~40-65%, limited by cargo scheduling, send-out ramping and tank management.
  Belgium at a sustained 100% of 669 GWh/d (244 TWh/yr) is not physically credible -
  that is roughly BE's *entire* annual gas consumption delivered via Zeebrugge alone.
- **`gas-extraction` 103.9 TWh in 2050 is the bigger problem.** This is the NL national
  284.5 GWh/d figure, which is a **2025-vintage production capacity**. Groningen **closed
  in October 2023**; remaining NL production is small offshore and declining fast. Letting
  it run at 100% LF to 2050 is counterfactual regardless of capacity treatment.
- The source column is literally `Capacity 2030 (GWh/d)` with `Year = 2025` - a **single
  static value with no decline trajectory**, reused unchanged for 2030/2040/2050.

**Consequence:** gas supply is binding in BE in all three milestones and in NL by 2050.
The model would burn more gas if allowed, and CCGT+CC's 39.2% 2050 share rests on a fuel
supply that is available with perfect, unrealistic reliability.

## 3. The volume budget exists but is inert
`limited_fossil-CH4` sets `storage_state_max` on `fossil-CH4`:

| | 2030 | 2040 | 2050 | 2060 |
|---|---:|---:|---:|---:|
| budget (TWh) | 2500 | 1000 | 500 | 500 |
| actual use (TWh) | 434 | 624 | 662 | - |

The alternative is **not** in the active scenario
(`baseline_blended_representative_periods` = Base, wy2009, medium_bio, current, GA,
GA_flex0, high_CO2, flex_buildings, flex_buildings_wy2009_current, flex_industry).
Note it would **not bind in 2030** (2500 >> 434) but **would bind hard in 2040 (1000 < ...)
marginally and in 2050 (500 << 662, a 25% cut)**. Same inert-cap pattern as
`limited_nuclear-3`.

## 4. Can we go from national to IC1 figures properly? Yes - partly already done
- **Capacity split: already done**, uniformly by region count. The honest criticism is not
  the magnitude but the **uniformity**: every BE region gets 1/8 of a national LNG
  capacity, including landlocked ones. LNG terminals are physically at **Zeebrugge (BE)**
  and **Rotterdam/Eemshaven (NL)**; gas extraction is concentrated in the **north-east NL /
  Groningen** area. The dataset contains no siting column, so this cannot be fixed from
  `CH4_Production` alone.
- **Usable data that IS present:** `CH4_Storage` carries per-region `Capacity (TWh)`,
  `Injection (GWh/d)` and `Withdrawal (GWh/d)` (BE 1.10375 TWh, 11.0175 inj, 21.2075 wdr) -
  real seasonal-deliverability physics, already regionalised the same way. This is the
  natural basis for a seasonal/utilisation constraint.
- **Not present:** any utilisation factor, load-duration profile, siting/coordinates, or
  post-2025 production decline. Those must come from outside (ENTSOG TYNDP send-out
  profiles, GTS/EBN production outlooks, ALSI utilisation history).

## 5. Recommended fixes, in order of defensibility
1. **Add an `availability_factor` to `LNG-terminal` and `gas-extraction`** - the smallest,
   best-targeted fix. Even a flat 0.55-0.65 for LNG is far more defensible than 1.0.
   Patch `unit` level in the model DB (mirrors existing patch tooling).
2. **Apply a decline trajectory to `gas-extraction`** towards ~0 by 2050 (Groningen closed).
   Currently static from a 2025 value.
3. **Activate `limited_fossil-CH4`** as a scenario sensitivity - it is already authored and
   bites meaningfully in 2050 (500 vs 662 TWh).
4. **Raise siting with data authors** - concentrate LNG in coastal regions rather than
   spreading it uniformly; ask whether `Year = 2025` capacity was intended to be static to
   2050, and whether the `To Country` header should be relabelled to avoid the exact
   misreading documented in the retraction above.

**Prediction to register before any such run:** with LNG availability 0.6 + extraction
decline, CCGT+CC 2050 share falls below 39.2%; H2/CCGT-H2 and/or wind rise; CO2 pipeline
throughput and DAC use fall; objective rises. If CCGT+CC share is unmoved, the gas limit
was not actually binding and SS2 is wrong.

## 6. Caveats
- Real-world LNG utilisation (~40-65%) and the Groningen closure date are from memory and
  should be sourced (ALSI/GIE, EBN) before external quotation. The **100% LF result itself
  is computed from model data and is exact**, independent of those figures.
- The 100% LF equality was checked for all 17 regions in 2050 and the BE/NL aggregates in
  all three milestones.
- Whether `bio-diges-up` biomethane adds on top of the 662 TWh is not resolved here; it does
  not appear under `supply` carrier `methane`.
