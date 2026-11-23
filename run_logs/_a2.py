import pickle, pandas as pd
pd.set_option("display.width",95)
d = pickle.load(open("run_logs/retireall.pkl","rb"))
sto, fl = d["sto"], d["fleet"]
print("== storage node_state by node/year ==")
print(sto.groupby(["node","year"]).units.sum().unstack().round(2).to_string())
print()
print("== electrolysis fleet detail ==")
print(fl[fl.category=="electrolysis"].to_string())
print()
print("== e-fuels detail ==")
print(fl[fl.category=="e-fuels / green chemicals"].groupby(["tech","year"]).units.sum().unstack().round(3).to_string())
