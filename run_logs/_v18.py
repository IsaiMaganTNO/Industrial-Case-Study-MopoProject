import pickle, pandas as pd
pd.set_option("display.width",92)
A=pickle.load(open(r"run_logs\vre15.pkl","rb"))
B=pickle.load(open(r"run_logs\gascap.pkl","rb"))
for tag,F in [("gascap",B),("vre15",A)]:
    c=F["co2net"]
    print("===",tag,"co2net by role/year (kt)")
    print(c.groupby(["role","year"]).co2.sum().unstack(fill_value=0).round(0).to_string())
    print("  NET:", c.groupby("year").co2.sum().round(0).to_dict())
    print("  atm:", F["atm"].to_string().replace("\n"," | ")[:200])
