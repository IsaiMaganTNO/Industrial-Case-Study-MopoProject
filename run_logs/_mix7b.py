import pickle,pandas as pd
out={}
for tag,f in [("3day",r"run_logs\hcco2.pkl"),("7day",r"run_logs\hcco2_7day.pkl")]:
    d=pickle.load(open(f,"rb")); s=d["supply"]
    s=s.drop_duplicates(subset=["tech","region","year","carrier","vintage"])
    e=s[(s["carrier"]=="electricity")&(s["year"]==2050)]
    out[tag]=e.groupby("tech")["energy"].sum().sort_values(ascending=False)
a,b=out["3day"],out["7day"]
sa,sb=a.sum(),b.sum()
print("2050 ELEC  3day=%.0f GWh   7day=%.0f GWh"%(sa,sb))
ks=list(dict.fromkeys(list(b.index)+list(a.index)))
print("%-20s %10s %6s %10s %6s"%("tech","3day","%","7day","%"))
for k in ks:
    x=a.get(k,0.0); y=b.get(k,0.0)
    if max(x,y)<1: continue
    print("%-20s %10.0f %5.1f%% %10.0f %5.1f%%"%(k[:20],x,100*x/sa,y,100*y/sb))
