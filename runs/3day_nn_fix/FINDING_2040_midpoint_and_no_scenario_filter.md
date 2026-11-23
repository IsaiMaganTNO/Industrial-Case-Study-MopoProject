# FINDING - 2040 inputs are midpoints, and the solve uses no scenario filter (2026-10-09)
Scripts: `run_logs/_ts1.py`-`_ts10.py`. Model `tiny.3day.nodac_nuc`, results `Investment_Results.3day_nodac_nuc`.

## 1. The 2040 timestamp was explained earlier, not fixed
- Yearly inputs are stamped 2030 / **2041** / 2050. The investment slice is 2040-01-01, so SpineOpt uses the **midpoint** of the 2030 and 2041 values (report_v2 `_pick`, reproduced to 3e-8).
- Proof (storage): NSNL012 2040 available = 0.0178 = (0 + 0.0356)/2. NSNL031 = 0.00685.
- Scope: about 5,500 yearly values carry a 2041 key: unit_investment_cost 1119, demand_fraction 1384, storage_state_max 612, investment_count_max_cumulative 532, vom_cost 284, flow_ratio_equality_coefficient 361, CO2/bio caps 312, and others. No hourly data sits on 2041.
- Effect: every 2040 input is halfway back to 2030. Costs for the 2040 build are too high (about 11% on investment), 2040 storage/caps are about half, and the 2040 CO2 cap is (0.453 + 0.101)/2 instead of 0.101. 2050 inputs are correct.

## 2. No scenario filter: the highest-id alternative wins
`solve_tiny_gurobi.jl` passes a bare DB URL, so ALL alternatives are loaded and the last one wins.
| Item | Intended (scenario) | Actually used |
|---|---|---|
| CO2 storage | high_CO2 | **medium_CO2** (NSNL031 0.00685 in 2040) |
| Flex fixed | GA_flex0 | **GA_flex20** (elec_BEC1 bus-DR 1e-4) |
| fossil-CH4 | inactive | **limited_fossil-CH4 ACTIVE and binding** (state 1.0e6 in 2040, 5.0e5 in 2050 = cap) |
| nuclear-3 | none | limited_nuclear-3 total 120/150/180 (likely not binding) |
| bio, weather, demand | medium_bio, wy2009, GA, current | same by coincidence (highest id) |
This applies to every Gurobi run made with this script, not only nodac_nuc.
