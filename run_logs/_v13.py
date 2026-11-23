import pickle, pandas as pd
pd.set_option("display.width",92)
A=pickle.load(open(r"run_logs\vre15.pkl","rb"))
f=A["fleet"]
for t in ["wind-on-SP277-HH100","solar-PV-no-tracking","nuclear-3"]:
    d=f[f.tech==t]
    g=d.groupby(["region","year"]).units.sum().unstack(fill_value=0)
    print("===",t); print(g.round(3).to_string())
