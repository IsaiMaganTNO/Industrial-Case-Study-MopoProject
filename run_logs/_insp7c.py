import pickle,pandas as pd
d=pickle.load(open(r"run_logs\hcco2_7day.pkl","rb")); p=d["prod"]
print("sectors:",sorted(p["sector"].dropna().unique())[:20])
print("years:",sorted(p["year"].dropna().unique()))
print("outputs:",sorted(p["output"].dropna().unique())[:20] if p["output"].dtype==object else "numeric")
