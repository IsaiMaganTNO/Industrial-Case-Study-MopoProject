import pickle, pandas as pd
new=pickle.load(open(r"run_logs\gascap.pkl","rb"))
old=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
print("=== P3/P4 fleet: offshore wind + nuclear + CCGT ===")
for lbl,d in [("BASE",old),("GASCAP",new)]:
    fl=d["fleet"]
    sub=fl[fl.tech.str.contains("wind-off|nuclear|CCGT",case=False,na=False)]
    g=sub.groupby(["tech","year"])["units"].sum().unstack().fillna(0)
    print(f"--- {lbl} (GW)"); print(g.round(2).to_string())
print()
print("=== P5 atmosphere / net CO2 ===")
for lbl,d in [("BASE",old),("GASCAP",new)]:
    print(f"  {lbl}: ", d["atm"].to_dict("records"))
print()
print("=== P6 CO2 pipeline throughput ===")
for lbl,d in [("BASE",old),("GASCAP",new)]:
    cp=d["co2pipe"]
    print(f"  {lbl}: ", cp.groupby("year")["co2"].sum().round(0).to_dict())
