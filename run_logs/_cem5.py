import pickle
d=pickle.load(open(r"run_logs\hcco2_7day.pkl","rb"))
f=d["fleet"]
for fam in ["CEM2-(Afm)MEA","CEM2-(Afm)","EU-mix-2018","LC3-(Afm)MEA","(NG)DRI-EAF","(NG)DRI-EAF-MEA"]:
    g=f[f["tech"]==fam].groupby("year")["units"].sum()
    print("%-18s %s"%(fam[:18],{int(k):round(v,2) for k,v in g.items()}))
print()
p=d["prod"]
for fam in ["CEM2-(Afm)MEA","CEM2-(Afm)","EU-mix-2018"]:
    g=p[p["tech"]==fam].groupby("year")["output"].sum()
    print("%-18s out %s"%(fam[:18],{int(k):round(v,1) for k,v in g.items()}))
