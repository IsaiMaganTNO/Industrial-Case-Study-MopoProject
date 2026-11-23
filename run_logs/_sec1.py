import pickle,pandas as pd
d=pickle.load(open(r"run_logs\hcco2_7day.pkl","rb"))
p=d["prod"]; e=d["emis"]
secs=sorted(p["sector"].dropna().unique())
print("%-18s %22s %22s %22s"%("sector","2030 out/CO2/int","2040","2050"))
for s in secs:
    cells=[]
    for y in (2030,2040,2050):
        q=p[(p["sector"]==s)&(p["year"]==y)]
        out=q["output"].sum()
        techs=set(q[q["output"]>0.5]["tech"])
        co2=e[(e["year"]==y)&(e["tech"].isin(techs))]["co2"].sum()
        cells.append("%7.0f %7.0f %5.3f"%(out,co2,co2/out if out else 0))
    print("%-18s %s"%(s[:18]," | ".join(cells)))
