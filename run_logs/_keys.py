import pickle, pandas as pd
d = pickle.load(open("run_logs/retireall.pkl","rb"))
for k,v in d.items():
    if isinstance(v,pd.DataFrame):
        print(k, v.shape, list(v.columns))
