import pickle, pandas as pd
B=pickle.load(open("run_logs/hcco2.pkl","rb"))
s=B["supply"]
print("== carriers by year (GWh) ==")
print(s.groupby(["carrier","year"]).energy.sum().unstack().round(0).to_string())
print()
print("== electricity by year ==")
e=s[s.carrier=="electricity"]
print(e.groupby(["tech","year"]).energy.sum().unstack().fillna(0).round(0).sort_values(2050,ascending=False).head(10).to_string())
print()
print("== emissions by category ==")
print(B["emis"].groupby(["category","year"]).co2.sum().unstack().round(0).to_string())
print()
print("== CO2 injected ==")
cs=B["co2store"]; print(cs.groupby(["injector","year"]).co2.sum().unstack().round(1).to_string())
