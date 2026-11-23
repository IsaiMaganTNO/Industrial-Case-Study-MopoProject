import pandas as pd
o = open(r"run_logs\_gc_read.out", "w", encoding="utf8")
X = pd.read_excel(r"verification\global_constraints_industry_case_study.xlsx", sheet_name=None, header=None)
for k, d in X.items():
    print("=== SHEET", k, d.shape, file=o); print(d.head(60).to_string(), file=o)
o.close()
