import pickle,pandas as pd
d=pickle.load(open(r"run_logs\retireall.pkl","rb"))
net=d["co2net"]
u=net[(net.role!="captured")&(net.year==2040)].groupby("tech")["co2"].sum().sort_values(ascending=False)
print("2040 'used / injected' by tech:"); print(u.round(1).to_string())
print("\n2040 co2pipe:"); print(d["co2pipe"][d["co2pipe"].year==2040].to_string())
