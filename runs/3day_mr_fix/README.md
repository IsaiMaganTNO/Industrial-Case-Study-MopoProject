# Run 3day_mr_fix - mixed resolution (NL+BE IC1 zones + DE/DK/NO/UK country level)

Status: OPTIMAL, penalties 0, objective 7,073,666 (141.6 min, Gurobi, 52.7 GB RAM).
Same assumptions as `runs/3day_nb_v2` (scenario filter, 2040 restamp, storage /365, noDAC/LNG, nuclear caps).
Difference: 4 extra countries at country resolution, and one CO2 budget shared by all 6 countries (3,141 / 698 / 0 Mt over the modelled years).

## Contents
- `input/Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite` - solved model (moved out of checkpoints/)
- `output/Investment_Results.3day_mr_fix.sqlite` - results
- `logs/` - `3day_mr_fix_solve.out`, `gurobi_solver.log`, `mr_fix.pkl` (all regions), `mr_fix_NLBE.pkl` (NL+BE incl. their offshore zones), `mr_fix_xb.pkl` (cross-border flows)
- `plots/summary_NLBE/` - 9 curated plots, NL+BE only (directly comparable with `runs/3day_nb_v2/plots/summary`)
- `plots/summary_6country/` - same 9 plots for all 6 countries
- `plots/postprocess/` - full postprocess set + PDF
- `plots/report_v2/` - report_v2 set + PDF

Results and interpretation: `RESULT_3day_mr_fix.md`.

## Reproduce plots
```
python tools/filter_pkl_countries.py runs/3day_mr_fix/logs/mr_fix.pkl mr_fix_NLBE.pkl NL,BE
python tools/plot_run_summary.py mr_fix_NLBE.pkl <out> --title "..."
python tools/plot_run_summary.py runs/3day_mr_fix/logs/mr_fix.pkl <out> --regions "^((BE|NL)C\d|DE|DK|NO|UK)"
python tools/postprocess.py <output.sqlite> -o <dir> -m <input.sqlite>
python tools/report_v2.py   <output.sqlite> -o <dir> -m <input.sqlite>
```

- `plots/compare_nb_v2/` - 10 NL+BE comparison plots vs `3day_nb_v2` (see its README)
- `SLIDES_Standalone_vs_Interconnected.pdf` - 19-slide deck for colleagues (`python tools/make_slides.py <out.pdf>`). Display names: **Standalone** = 3day_nb_v2, **Interconnected** = 3day_mr_fix. Uses `plots/compare_named`, `plots/summary_named_*`.

