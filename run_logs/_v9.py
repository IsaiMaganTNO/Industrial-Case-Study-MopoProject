import pickle, pandas as pd
pd.set_option("display.width",92)
A=pickle.load(open(r"run_logs\vre15.pkl","rb"))
B=pickle.load(open(r"run_logs\gascap.pkl","rb"))
o=A["obj"]
print("OBJ frame cols:",list(o.columns)); print(o.head(20).to_string()[:1200])
