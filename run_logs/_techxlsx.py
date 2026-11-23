import pandas as pd
cols = ["Baseline: NL+BE, 17 zones", "Lower resolution: NL+BE, 1 node per country", "With neighbours: NL+BE 17 zones + DE, DK, NO, UK"]
rows = [
 ("Model construction time", "min", 70, 61, 121),
 ("  of which constraints", "min", 46, 41, 85),
 ("  of which variables", "min", 20, 17, 32),
 ("Model solve time (Gurobi)", "min", 10.7, 2.2, 17.1),
 ("Writing results", "min", 1.2, 1.0, 1.5),
 ("Total run time", "min", 85.3, 66.5, 143.6),
 ("Variables (columns)", "million", 31.7, 25.0, 39.7),
 ("Constraints (rows)", "million", 2.75, 2.46, 3.56),
 ("Non-zero coefficients", "million", 6.5, 5.8, 8.5),
 ("Variables after presolve", "million", 0.56, 0.38, 0.70),
 ("Constraints after presolve", "million", 0.36, 0.33, 0.48),
 ("Barrier iterations", "-", 77, 76, 86),
 ("Peak RAM", "GB", 54, 51, 59),
 ("Input database size", "MB", 208, 153, 208),
 ("Results database size", "MB", 134, 116, 172),
 ("Objective (total system cost)", "M EUR", 3941, 3775, 7607),
 ("Solution status", "-", "Optimal", "Optimal", "Optimal"),
]
df = pd.DataFrame(rows, columns=["Item", "Unit"] + cols)
notes = pd.DataFrame({"Common set-up": [
 "Linear program (no integer variables); SpineOpt + Gurobi 13.0.3, 8 threads",
 "Workstation: 10 cores / 20 threads, 144 GB RAM",
 "Investment years: 2030, 2040, 2050",
 "3 representative days per year, hourly resolution, weighted to a full year",
 "Objective of 'With neighbours' covers six countries; not comparable with NL+BE-only costs"]})
out = r"final_runs_pessimistic_ccs\Technical_details_runs.xlsx"
with pd.ExcelWriter(out) as w:
    df.to_excel(w, sheet_name="Technical details", index=False)
    notes.to_excel(w, sheet_name="Common set-up", index=False)
print(pd.read_excel(out).shape, out)
