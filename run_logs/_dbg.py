import pickle, pandas as pd
A=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
print("atm columns:",list(A["atm"].columns))
print(A["atm"].head(6).to_string())
print("\ncement techs present (baseline 2050):")
p=A["prod"]; print(sorted(p[(p["sector"].astype(str)=="cement")]["tech"].astype(str).unique()))
print("\nemis 'sector' available?",list(A["emis"].columns))
