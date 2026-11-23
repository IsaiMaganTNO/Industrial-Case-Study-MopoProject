import pickle, pandas as pd
pd.set_option("display.width",92)
A=pickle.load(open(r"run_logs\vre15.pkl","rb"))
B=pickle.load(open(r"run_logs\gascap.pkl","rb"))
print("=== vre15 obj ==="); print(A["obj"].to_string())
pen=[i for i in A["obj"].index if "penalt" in str(i).lower()]
print("PENALTY ENTRIES:",pen, [A["obj"][i] for i in pen])
