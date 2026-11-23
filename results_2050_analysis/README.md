# 2050 analysis - NL+BE industrial decarbonisation, all runs
- `FINDINGS.md` - run descriptions, KPI table, comparisons A and B, notes per figure
- `figures/` - 20 PNGs. File name = `<n>_<figure>_<group>_<years>.png`
  - group `A` = baseline runs: NL+BE 17 zones / NL+BE 1 node per country / With neighbours
  - group `B` = sensitivity runs: With neighbours / National CO2 caps / 10 repr. days / Optimistic CCS / With FR + LU
  - years `all` = 2030, 2040, 2050; `2050` = 2050 only
  - figures: 1 industry routes (incl. refinery), 2 electricity mix NL/BE, 3 energy panels, 4 H2 and electricity balance, 5 CO2 capture and destination
- `data/` - CSV behind each figure + `kpi_2050.csv`
- `scripts/` - copies of `make_report_2050.py`, `build_frlu_v4.py`, `preflight.jl`
Regenerate: `.\.venv\Scripts\python.exe tools\make_report_2050.py`
