import pickle,pandas as pd
out={}
for tag,f in [("3day",r"run_logs\hcco2.pkl"),("7day",r"run_logs\hcco2_7day.pkl")]:
    d=pickle.load(open(f,"rb")); s=d["supply"]
    e=s[(s["carrier"]=="electricity")&(s["year"]==2050)]
    g=e.groupby("tech")["energy"].sum().sort_values(ascending=False)
    out[tag]=g
a,b=out["3day"],out["7day"]
sa,sb=a.sum(),b.sum()
print("2050 ELEC total  3day=%.0f  7day=%.0f  (%+.1f%%)"%(sa,sb,100*(sb-sa)/sa))
ks=list(dict.fromkeys(list(b.index)+list(a.index)))
print("%-24s %9s %6s %9s %6s"%("tech","3day","%","7day","%"))
for k in ks:
    x=a.get(k,0.0); y=b.get(k,0.0)
    if max(x,y)<50: continue
    print("%-24s %9.0f %5.1f%% %9.0f %5.1f%%"%(k[:24],x,100*x/sa,y,100*y/sb))
vre=["wind-on","solar","wind-off","RoR"]
f=lambda t,s:100*sum(v for k,v in t.items() if any(k.startswith(p) for p in vre))/s
print("\nVRE share  3day=%.1f%%   7day=%.1f%%"%(f(a,sa),f(b,sb)))
