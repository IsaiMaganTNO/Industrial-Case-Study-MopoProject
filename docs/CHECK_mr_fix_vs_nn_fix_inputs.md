# CHECK - is mr_fix comparable to nn_fix? (2026-10-09)
Scripts: `run_logs/_cmp1.py`-`_cmp4.py`. NL+BE parameter diff, in-scenario alternatives only.

## Same (patches/assumptions)
LNG 1.0 (17 NL+BE terminals); DAC cap 0; NL extraction 0; storage /365; NL+BE nuclear caps; 2040 restamp; scenario filter; same 3 representative days.

## Different by design (expected with the larger system)
- CO2 budget is system-wide: atmosphere 3.141 / 0.698 / 0 (6 countries) vs 0.453 / 0.101 / 0 (NL+BE only).
- Neighbours bring extra sinks/sources: 14 more storage sites (DK 25.5 Mtpa), Norwegian gas pipelines, CO2 pipelines to DE/DK/NO/UK, UK nuclear 6/11/13.

## Different but NOT intended (the mixedres build is a fresh pipeline build)
| Item | Magnitude |
|---|---|
| Biomass endowment NL+BE (medium_bio) | 118.0 vs 68.2 (+73%); BEC7 x5, NLC6 x4.8 |
| Biomass flow cost | up to +73% |
| Investment costs (170 values) | <=1% (e.g. SMR+CC +0.4%, bio-digester +-1%) |
| bio-digester+CC CH4 yield | 0.600 vs 0.545 |
| Demand, availability, vom/fom | about 0.2% or less (rounding) |
| harber-bosch_* units (17) | only present in mixedres |
Cause: nn_fix comes from the older vre15 chain (biomass fix, gas cap, VRE onshore patch); mixedres was rebuilt from the updated pipeline.
