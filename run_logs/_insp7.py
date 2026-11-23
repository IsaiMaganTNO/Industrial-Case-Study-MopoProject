import pickle,sys
d=pickle.load(open(r"run_logs\hcco2_7day.pkl","rb"))
print(type(d))
if isinstance(d,dict):
    for k in list(d)[:25]: print("  key:",k, type(d[k]))
