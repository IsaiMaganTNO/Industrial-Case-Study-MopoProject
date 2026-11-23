# Appendix: technical overview of the model runs

| Group | Run | Solver | Rows (M) | Columns (M) | Non-zeros (M) | Rows after presolve (M) | Columns after presolve (M) | Build time | Solve time | Total run time | Peak RAM (GB) | Termination | Objective (M EUR) | Run date |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | NL+BE regional clusters | Gurobi 13.0.3 | 2.75 | 3.17 | 6.54 | 0.36 | 0.56 | 1h 08m | 0h 11m | 1h 24m | 53.9 | Optimal | 3,941,040 | 2026-10-16 |
| A | NL+BE country level | Gurobi 13.0.3 | 2.46 | 2.50 | 5.78 | 0.33 | 0.38 | 0h 59m | 0h 03m | 1h 06m | 51.2 | Optimal | 3,774,842 | 2026-10-16 |
| A/B | Mixed resolution | Gurobi 13.0.3 | 3.56 | 3.97 | 8.53 | 0.48 | 0.70 | 1h 59m | 0h 18m | 2h 23m | 59.0 | Optimal | 7,606,649 | 2026-10-16 |
| B | National CO2 caps | Gurobi 13.0.3 | 3.59 | 4.00 | 8.60 | 0.48 | 0.72 | 2h 09m | 0h 24m | 2h 39m | 65.9 | Optimal | 7,784,577 | 2026-10-27 |
| B | 10 repr. days | Gurobi 13.0.3 | 11.80 | 12.97 | 28.26 | 1.59 | 2.31 | 9h 02m | 27h 31m | 36h 41m | 102.0 | Optimal | 8,418,436 | 2026-10-22 |
| B | Optimistic CCS | Gurobi 13.0.3 | 3.56 | 3.97 | 8.53 | 0.48 | 0.70 | 2h 14m | 0h 25m | 2h 45m | 68.2 | Optimal | 7,190,084 | 2026-10-28 |
| B | With FR + LU | Xpress 9.7 | 3.92 | 4.32 | 9.41 | 0.53 | 0.74 | 0h 55m | 4h 08m | 5h 05m | n/a | Optimal | 9,251,098 | 2026-11-02 |

Notes:
- All runs are linear programmes solved to optimality, with an optimality tolerance of 1e-6. The objective is the total discounted system cost over 2030-2060 (three investment years, each representing 10 years, 5% discount rate) for the whole modelled area. The model units are GWh and M EUR, so the objective is in M EUR. Objectives can only be compared between runs with the same geographical scope: the two NL+BE-only runs, and the runs with neighbouring countries. The objective values from the solver logs match the total costs in the output databases.
- Model size is the size of the linear programme passed to the solver, before and after presolve.
- Build time is the time SpineOpt needs to build the optimisation model from the input database. Solve time is the time the solver needs, including writing results. Total run time also includes reading the input data.
- Gurobi runs: Gurobi 13.0.3, barrier method followed by crossover, up to 8 threads, on a local workstation (10 cores, 20 logical processors). Peak RAM is the memory in use at the end of the run.
- With FR + LU: solved with FICO Xpress 9.7 on a separate server (up to 96 threads, 383 GB memory available), because Gurobi was not available. Build and solve times are therefore not directly comparable with the other runs, and the peak RAM was not logged.
- All runs except "10 repr. days" use 3 representative days per investment year. "10 repr. days" uses 10, which makes the model about 3.3 times larger and the run about 15 times longer than the Mixed resolution run.
