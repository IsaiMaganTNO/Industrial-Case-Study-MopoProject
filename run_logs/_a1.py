import pickle, pandas as pd
pd.set_option("display.width",95)
d = pickle.load(open("run_logs/retireall.pkl","rb"))
sup, fl, sto = d["supply"], d["fleet"], d["sto"]
print("== carriers ==")
print(sup.groupby(["carrier","year"]).energy.sum().unstack().round(1))
print("== H2 supply by tech ==")
h2 = sup[sup.carrier.str.contains("h2|hydrog",case=False,na=False)]
print(h2.groupby(["tech","year"]).energy.sum().unstack().round(1))
print("== fleet categories ==")
print(fl.groupby(["category","year"]).units.sum().unstack().round(2))
