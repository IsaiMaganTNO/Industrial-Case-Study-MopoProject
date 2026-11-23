import pickle, pandas as pd
new=pickle.load(open(r"run_logs\gascap.pkl","rb"))
old=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
print("=== co2net (capture/removal roles) by role, year ===")
for lbl,d in [("base",old),("gascap",new)]:
    c=d["co2net"]
    print(f"--- {lbl}")
    print(c.groupby(["role","year"])["co2"].sum().unstack().fillna(0).round(0).to_string())
print()
print("=== DAC + top capture techs 2050 ===")
for lbl,d in [("base",old),("gascap",new)]:
    c=d["co2net"]; c=c[c.year==2050]
    g=c.groupby("tech")["co2"].sum().sort_values()
    print(f"  {lbl} most-negative(capture):", g.head(6).round(0).to_dict())
