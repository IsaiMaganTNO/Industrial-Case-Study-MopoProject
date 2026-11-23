import pickle, pandas as pd
B=pickle.load(open("run_logs/hcco2.pkl","rb"))
A=pickle.load(open("run_logs/retireall.pkl","rb"))
print("== onshore/solar headroom check 2050 (units built) ==")
for lbl,d in (("retireall",A),("hcco2",B)):
    f=d["fleet"]; m=f[(f.year==2050)&(f.tech.str.contains("wind-on-SP277|solar-PV-no"))]
    print(f"-- {lbl} --")
    print(m.groupby("tech").units.sum().round(3).to_dict())
    print("   regions w/ onshore:", m[m.tech.str.contains("wind-on")].region.nunique(),
          " solar:", m[m.tech.str.contains("solar")].region.nunique())
print()
print("== offshore new investment hcco2 ==")
i=B["inv"]; print(i[i.tech.str.contains("wind-off")].to_string())
