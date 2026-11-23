import pickle, pandas as pd
B=pickle.load(open("run_logs/hcco2.pkl","rb"))
print("== fleet by category ==")
print(B["fleet"].groupby(["category","year"]).units.sum().unstack().fillna(0).round(2).to_string())
print()
print("== H2 by tech ==")
s=B["supply"]; h=s[s.carrier=="hydrogen"]
print(h.groupby(["tech","year"]).energy.sum().unstack().fillna(0).round(0).to_string())
print()
print("== heat by tech ==")
ht=s[s.carrier=="heat"]
print(ht.groupby(["tech","year"]).energy.sum().unstack().fillna(0).round(0).to_string())
