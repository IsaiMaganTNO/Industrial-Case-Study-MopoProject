# FINDING - CO2 storage potentials are 365x too loose (2026-10-09, verified against SpineOpt source)

## Data
- **Source:** `EU_case/data/Gas/CCS_storage_scenarios_mopo.xlsx`, copied unchanged into `CO2_data*.xlsx`.
- **What the values mean:** potential in Mtpa per site and year (low/medium/high). The values are **cumulative capacity, not increments**: DK high = 0 / 25.5 / 25.5 means 25.5 Mt/yr in both 2040 and 2050.
- **Conversion** (`ines_target.py`, around line 1535): `storage_investment_count_fix_cumulative = Mtpa` units x `storage_state_max = 1000` kt. The cumulative reading is correct; DK `storages_invested_available` is 0 / 0 / 25.5.

## How SpineOpt applies the cap (source: SpineOpt 1NRBB)
- **Trajectory** (`constraint_node_state_longterm_trajectory.jl`):
  `state_longterm[t_after] = state_longterm[t_before] + sum(coef_blk * (node_state[last] - node_state[first]))`
  - Each long-term step adds one weighted representative day (the block coefficients sum to 1), i.e. annual flow / 365.
  - Verified: ATUK031 rises by 370.4 in 2050 = 135.2 Mt / 365.
- **Cap** (`constraint_node_state_capacity.jl`, longterm=true): `state_longterm[t] <= storage_state_max * storages_invested_available`, checked at every long-term time slice.
- **Long-term slices per period:** 2030-01-01 | 2040-01-02 (reset) | 2041 | 2049 | 2050.
  - 2049 is a gap slice: its value is interpolated between 2041 and 2050 (e.g. 9,630 = 360 + 9,270), not a real 8-year accumulation.
  - So the state counts at most one or two years of injection in day-units, and the cap acts as an **annual-rate cap in day-units**.
  - Dividing by 365 turns the data's Mtpa into exactly that.
- **Atmosphere budget:** treated the same way (already /365; binds at 3,140.7 in 2030). The two are now consistent.

## Before the fix

| site | data Mtpa | stored 2050 | cap in day-units | used |
|---|---:|---:|---:|---:|
| CO2-storage-DK | 25.5 | 242.7 Mt | 25,500 | 665 |
| ATUK031 | 10 | 135.2 Mt | 10,000 | 370 (the 2050 slice shows 10,000 via the gap slice) |
| NSNL031 | 6.2 | 78.0 Mt (vre15: 73.5) | 6,200 | 214 |

## Caveat
- The gap slices (2049) can absorb slack, so the cap is not a perfectly clean "per year" limit.
- After the fix the cap is roughly 1 year x Mtpa. This is the intended reading of the data.

## Fix
- **Tool:** `tools/patch_co2_storage_div365.py`. It divides `storage_investment_count_fix_cumulative` by 365 on `CO2-storage-*` nodes for all CO2 alternatives.
- **Safety:** refuses to run twice; the cross-border guard is checked as unchanged.
- **Now standard patch #9.**
