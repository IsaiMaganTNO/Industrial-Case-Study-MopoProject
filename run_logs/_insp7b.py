import pickle,pandas as pd
pd.set_option("display.width",92)
for tag,f in [("3day",r"run_logs\hcco2.pkl"),("7day",r"run_logs\hcco2_7day.pkl")]:
    d=pickle.load(open(f,"rb")); p=d["prod"]
    print("==",tag,"prod cols:",list(p.columns))
    break
