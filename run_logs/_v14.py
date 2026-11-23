import pickle, pandas as pd
A=pickle.load(open(r"run_logs\vre15.pkl","rb"))
f=A["fleet"]
caps={"wind-on-SP277-HH100":{"BE":3.60,"NL":7.20},
      "solar-PV-no-tracking":{"BE":12.766,"NL":33.50}}
for t,cc in caps.items():
    d=f[f.tech==t].copy(); d["ctry"]=d.region.str[:2]
    g=d[d.year==2050].groupby("ctry").units.sum()
    for k,v in cc.items():
        print(f"{t:24} {k} 2050={g.get(k,0):.4f} cap={v:.4f} ratio={g.get(k,0)/v:.5f}")
n=f[f.tech=="nuclear-3"].copy(); n["ctry"]=n.region.str[:2]
print("\nnuclear by country/year:")
print(n.groupby(["ctry","year"]).units.sum().round(3).to_string())
