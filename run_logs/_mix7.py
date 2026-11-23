import pickle,pandas as pd
res={}
for tag,f in [("3day",r"run_logs\hcco2.pkl"),("7day",r"run_logs\hcco2_7day.pkl")]:
    d=pickle.load(open(f,"rb")); p=d["prod"]
    e=p[(p["sector"]=="electricity")&(p["year"]==2050)]
    if e.empty: e=p[(p["year"]==2050)]
    g=e.groupby("tech")["output"].sum().sort_values(ascending=False)
    res[tag]=g[g>1.0]
t3,t7=res["3day"],res["7day"]
ks=list(dict.fromkeys(list(t7.index[:16])+list(t3.index[:16])))
s3,s7=t3.sum(),t7.sum()
print("2050 electricity  3day tot=%.0f  7day tot=%.0f"%(s3,s7))
print("%-26s %10s %6s %10s %6s"%("tech","3day","%","7day","%"))
for k in ks:
    a=t3.get(k,0.0); b=t7.get(k,0.0)
    print("%-26s %10.0f %5.1f%% %10.0f %5.1f%%"%(k[:26],a,100*a/s3 if s3 else 0,
          b,100*b/s7 if s7 else 0))
