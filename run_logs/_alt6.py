import pickle,pandas as pd
d=pickle.load(open(r"run_logs\hcco2.pkl","rb"))
p=d["prod"]
f={"aluminium-primary-production-alternative":1.444697,
"other-chemicals-production-alternative":0.687791,
"pharmaceuticals-production-alternative":0.555711,
"other-non-ferrous-metals-production-alternative":0.130915,
"ceramics-and-other-non-metalic-minerals-production-alternative":0.048216,
"machinery-equipment-production-alternative":0.024870,
"transport-equipment-production-alternative":0.022496}
print("%-56s %6s %10s %10s"%("unbooked family w/ nonzero factor","year","output","missedCO2"))
tot={}
for fam,v in f.items():
    for y in (2030,2040,2050):
        o=p[(p["tech"]==fam)&(p["year"]==y)]["output"].sum()
        if o>0:
            print("%-56s %6d %10.2f %10.2f"%(fam[:56],y,o,o*v))
            tot[y]=tot.get(y,0)+o*v
print("\nTOTAL missed CO2 by year:",{k:round(v,2) for k,v in sorted(tot.items())})
