import pickle, pandas as pd
d=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
for k,v in d.items():
    if hasattr(v,"columns"): print(f"{k:10s} {list(v.columns)}")
