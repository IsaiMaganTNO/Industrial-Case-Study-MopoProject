import pickle, pandas as pd
pd.set_option("display.width",110)
d=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
s=d["supply"]
m=s[s["carrier"]=="methane"]
print("=== methane supply by tech/year (sum energy) ===")
print(m.groupby(["tech","year"])["energy"].sum().unstack().fillna(0).round(1).to_string())
print()
print("=== methane supply by region/year ===")
print(m.groupby(["region","year"])["energy"].sum().unstack().fillna(0).round(1).to_string())
print()
pr=d["prod"]
print("=== CCGT+CC production (electricity) by year ===")
cc=pr[pr["tech"].str.contains("CCGT",na=False)]
print(cc.groupby(["tech","year"])["value"].sum().unstack().fillna(0).round(1).to_string() if "value" in pr.columns else pr.columns.tolist())
