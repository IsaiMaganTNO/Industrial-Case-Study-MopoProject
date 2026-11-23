# FINDING: Offshore wind is exactly zero because it is simply more expensive

Status: **explained** (3-day Group 1, both `group1` baseline and `biocap365`).
Supersedes the speculative framing in `RUN_3day_group1_biocap365.md` section 8,
which listed this as "the clearest remaining open question".

## 1. The question

Offshore wind is built at **exactly 0.000** in every region, in every milestone,
in **both** the baseline and the corrected-biomass run - even though correcting
the biomass cap moved solar from 0 to 46.7 GW and onshore wind from 5.8 to
26.0 GW. If the biomass defect was suppressing VRE, why did offshore not move?

## 2. It is not a structural block

Offshore is fully wired and investable. For `wind-off-FB-SP370-HH155_NSNL012`:

| Parameter | Value |
|---|---|
| `investment_count_max_cumulative` (unit) | 1000.0 |
| `investment_count_total_max_cumulative` (resource node) | 6.1267 |
| `capacity_per_unit` (`__elec_NLC2`) | 1.0 |
| `availability_factor` | 8760-h series, present for wy1995/wy2008/wy2009 |
| `unit_investment_cost` | 5734.7 / 3596.4 / 1920.5 (2030/2041/2050) |

57 offshore entities exist across 12 resource nodes, connected to coastal
`elec_*` nodes. Total offshore group cap is **124.557 units** - the *largest*
of the three VRE families (onshore 48.992, solar 196.019). Nothing is fixed to
zero and no cap is zero.

## 3. It is economics, and the margin is wide

Levelised cost at 2050 investment costs, 7% discount rate, 30-year life
(CRF = 0.08059), using capacity factors measured on the actual representative
days:

| Technology (NLC2 / NSNL012) | inv cost 2050 | CF on rep days | CF annual | LC (model units/MWh) | vs offshore |
|---|---:|---:|---:|---:|---:|
| `wind-off-FB-SP370-HH155` | 1920.53 | 0.6633 | 0.5368 | **0.03252** | 1.000 |
| `wind-on-SP277-HH100` | 933.91 | 0.6159 | 0.4757 | **0.01748** | **0.538** |
| `solar-PV-no-tracking` | 269.49 | 0.1544 | 0.1480 | **0.02273** | **0.699** |

Offshore costs **2.06x** onshore per unit of capacity and only earns **1.08x**
the energy on the rep days, so it lands at **1.86x** onshore and **1.43x**
solar per delivered MWh. That is not a marginal gap that noise or a slightly
different rep-day sample would close.

Note this comparison is **biased in favour of offshore**: its rep-day CF
(0.6633) is well above its annual CF (0.5368), because the three sampled days
are windy. On a full-year run offshore would look *worse*, not better.

## 4. Why the order of build is exactly what we observe

The model exhausts cheap options before reaching offshore, and it never gets
there:

- **Onshore wind: 5 of 17 regions are at their cap** (BEC3, NLC1, NLC2, NLC3,
  NLC5 - all `built == cap` to 3 decimals). Onshore is the cheapest option and
  is built out wherever the resource allows.
- **Solar: 11 of 17 regions still have headroom.** Only 46.663 of 196.019 units
  are taken. Solar is the second-cheapest option and is **not** exhausted.

This is the decisive observation. **Offshore would only be selected after solar
runs out, and solar has 149 units of unused headroom.** There is no
circumstance in this run where the optimiser would reach for a source at 1.43x
the cost of one it has not finished using.

## 5. What this does NOT say

- It does **not** say offshore wind is uneconomic in reality. The result
  depends on `unit_investment_cost` (offshore 1920.5 vs onshore 933.9 in 2050),
  which I have not validated against literature, and on the **unverified
  assumption that the power unit is GW**.
- It does **not** generalise past 3 representative days. Offshore's real
  advantage is a flatter, less correlated output profile - exactly the property
  a 3-day model cannot price. The sampled days flatter offshore on CF while
  erasing the inter-day persistence that is its actual value.
- It is **not** the same mechanism as the biomass defect. There is no defect
  here: no mis-scaled parameter, no missing row, no wrong cap. Offshore is
  correctly specified and correctly rejected on cost **within this model's
  assumptions**.

## 6. How to test it

If offshore is merely expensive rather than blocked, forcing it should be
feasible and should cost a predictable, small amount. Two checks:

1. Set `investment_count_total_max_cumulative` to 0 on all **solar** resource
   nodes and re-solve. Prediction: offshore becomes non-zero. If it stays at
   exactly zero, this explanation is **wrong** and something structural is
   blocking it.
2. Cut offshore `unit_investment_cost` by ~45% (to ~1050, below onshore-adjusted
   parity) and re-solve. Prediction: offshore enters before solar is exhausted.

Neither has been run. Until one is, section 3-4 is an argument from the input
parameters and the solved fleet, not a demonstrated causal result.

---

## 10. SUPERSEDED by `FINDING_hc_co2_unpriced.md` (2026-10-04)

The levelised-cost analysis in this document is still correct, but its
**conclusion was falsified** by the `hcco2` run.

Claim here: offshore stays at zero because solar has headroom in 11/17 regions,
so the model never exhausts the cheaper option.

Observed in `hcco2` (identical VRE data, only HC emissions added):
`wind-off-FB-SP370-HH155_NSNL011` builds **1.719 units / 10,187 GWh in 2050**,
while solar is still built in the same **11** regions.

So solar headroom was never the binding reason. Offshore was being undercut by
`oil-eng`, which burned HC with **no CO2 coefficient at all** and so acted as an
unpriced escape valve from the CO2 cap. Pricing HC at 0.24 t/MWh removed it and
offshore entered immediately.

The falsification test proposed in S8 (zero the solar caps) is superseded - the
decisive variable was emissions pricing, not VRE competition.
