import pickle, pandas as pd
A=pickle.load(open(r"run_logs\vre15.pkl","rb"))
B=pickle.load(open(r"run_logs\gascap.pkl","rb"))
for tag,F in [("gascap",B),("vre15",A)]:
    s=F["supply"]
    g=s.groupby(["carrier","year"]).energy.sum().unstack(fill_value=0)/1e3
    print("===",tag,"(TWh)"); print(g.round(1).to_string())
