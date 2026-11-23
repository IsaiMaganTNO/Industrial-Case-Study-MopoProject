# Final runs - NL+BE decarbonisation with limited CO2 storage (pessimistic CCS)

All three runs: OPTIMAL (Gurobi), zero penalties, no DAC, NL storage 2.5 / 10.5 / 16 Mt/yr.

| Folder | Set-up | Objective |
|---|---|---|
| `1_IC1_NLBE_17zones` | NL+BE, 17 IC1 zones | 3,941,040 |
| `2_CountryLevel_NLBE` | NL+BE, one node per country | 3,774,840 |
| `3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK` | NL+BE 17 zones + DE, DK, NO, UK (one node each), shared CO2 target | 7,606,649 |

Each folder: `input/` (SpineOpt model DB), `output/` (results DB), solve log, `README_run.md` (technical notes).

Deck: `NLBE_resolution_and_scope.pdf` (`python tools/make_deck_final3.py <out.pdf>`; needs caches `run_logs/<run>{,_NLBE,_xbbio}.pkl`).
