import pickle, pandas as pd
pd.set_option("display.width",200)
new=pickle.load(open(r"run_logs\gascap.pkl","rb"))
old=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
print("=== EMISSIONS by category (emis frame, co2) ===")
for lbl,d in [("base",old),("gascap",new)]:
    e=d["emis"]
    print(f"--- {lbl}")
    print(e.groupby(["category","year"])["co2"].sum().unstack().fillna(0).round(0).to_string())
print()
print("=== TOTAL net CO2 by year ===")
for lbl,d in [("base",old),("gascap",new)]:
    print(f"  {lbl}:", d["emis"].groupby("year")["co2"].sum().round(0).to_dict())
