# Representative periods: description for the report

## Concept
Optimising every hour of every investment year (3 x 8,760 hours) is computationally too heavy for a model with 21 or more regions, many sectors and a full CO2 chain. We therefore represent each year by a small set of representative days. Each day is modelled at hourly resolution and given a weight (the number of real days it stands for). The weights of all representative days in a year add up to 365, so their weighted operating costs and flows represent a full year.

## Selecting the days with TulipaClustering
The representative days are selected with TulipaClustering.jl, in the same way as in the Pan-EU workflow:
1. All demand and availability profiles of the model (wind, solar, run-of-river, hydro inflow, electricity demand, cooling, heat and transport demand) are exported, scaled to 0-1 and grouped into a small set of aggregate profiles.
2. The year (weather year 2009) is split into 365 periods of 24 hours.
3. TulipaClustering selects the representative days using the convex-hull method with a Euclidean distance. The selected days are actual days from the weather year.
4. For every day of the year, TulipaClustering computes convex weights: each real day is described as a weighted combination of the representative days. Adding these weights over the year gives the number of days each representative day stands for.

The selected days and their weights are written back into the SpineOpt database as temporal blocks: one block per representative day per investment year, with hourly resolution.

## How we use them in the runs
- Main runs (all A runs and the B sensitivities except "10 repr. days"): 3 representative days per investment year: 14 May (weight 104.6 days), 10 September (146.3 days) and 24 December (114.1 days). The same calendar days are used for 2030, 2040 and 2050 (2040 uses 2041 dates to avoid the leap year).
- "10 repr. days" sensitivity: 10 representative days per year, taken from the Pan-EU case's TulipaClustering result for weather year 2009 (weights from 13.6 to 62.2 days). Apart from the time representation, the model is identical to the Mixed resolution run.
- Each investment year (2030, 2040, 2050) represents 10 years in the objective function.
- Storage: within each representative day, storage operates hour by hour, with cyclic start and end conditions per day. Seasonal storage and annual budgets (for example the CO2 cap, CO2 storage and biomass availability) are tracked with SpineOpt's long-term storage formulation at the level of the investment year.
- Not blended: SpineOpt can link representative days into a chronological sequence over the year (blended representative periods, as in the Pan-EU description), which allows energy to be shifted between seasons. In our runs each year is mapped to its representative days in a single step, without this chronological sequence. Long-duration storage can therefore shift energy within a representative day, but not between seasons.

## Practical lessons
- Annual budgets must be consistent with the weights. Limits that apply to a full year must be scaled to the time steps the model actually solves. We found that unscaled limits could be off by a factor of up to 365 without any error message, and corrected this as a standard patch.
- The number of representative days affects results. Going from 3 to 10 days raised the objective by 10.7%. It moved building heat from biomass to heat pumps, increased offshore wind and electrolysis, and led to investment in iron-air (multi-day) storage. Three days are enough for the main trends, but storage and flexibility results should be read with this in mind.
- Computational cost: the 10-day run had about 11.8 million rows and 13.0 million columns and took about 37 hours with Gurobi (peak about 102 GB RAM). This is much longer than the 3-day runs.

## Suggested report text
"Each investment year is represented by a set of representative days with hourly resolution, selected with TulipaClustering.jl using the convex-hull method on the normalised demand and renewable profiles of weather year 2009. Each representative day is weighted by the number of days it represents, with weights summing to 365 per year. The main runs use three representative days per year; a sensitivity run uses ten days taken from the Pan-European case. Storage operates hourly within each representative day, while annual constraints such as the CO2 cap and biomass availability are applied at the level of the investment year. Unlike the blended formulation, the representative days are not linked chronologically, so seasonal storage shifting is not represented. Increasing the number of representative days from three to ten increases total system cost by about 11% and leads to more heat pumps, more offshore wind and electrolysis, and investment in long-duration storage."
