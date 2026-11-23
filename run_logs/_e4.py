import pickle, pandas as pd
pd.set_option("display.width",200)
new=pickle.load(open(r"run_logs\gascap.pkl","rb"))
old=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
print("=== CEMENT: tech mix + net CO2 by year ===")
for lbl,d in [("base",old),("gascap",new)]:
    p=d["prod"]; c=p[p.sector=="cement"]
    print(f"--- {lbl} production by tech")
    print(c.groupby(["tech","year"])["output"].sum().unstack().fillna(0).round(0).to_string())
    e=d["emis"]; ce=e[e.tech.isin(c.tech.unique())]
    print(f"    cement net CO2:", ce.groupby("year")["co2"].sum().round(1).to_dict())
print()
print("=== BIOMASS use (supply frame has no biomass carrier; use prod fuel) ===")
for lbl,d in [("base",old),("gascap",new)]:
    p=d["prod"]
    print(f"  {lbl}:", p[p.fuel=="biomass"].groupby("year")["output"].sum().round(0).to_dict())
