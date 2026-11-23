import pickle, pandas as pd
A=pickle.load(open("run_logs/retireall.pkl","rb"))
B=pickle.load(open("run_logs/hcco2.pkl","rb"))
print("== unabated fossil detail 2050 (fleet units) ==")
for lbl,d in (("retireall",A),("hcco2",B)):
    f=d["fleet"]; m=f[(f.year==2050)&(f.category=="unabated fossil")]
    print(lbl, m.groupby("tech").units.sum().round(3).to_dict())
print()
print("== oil-boiler / printing / LN+EL O presence ==")
for lbl,d in (("retireall",A),("hcco2",B)):
    f=d["fleet"]
    m=f[f.tech.str.contains("oil-boiler|printing|LN\\+EL",regex=True,na=False)]
    print(lbl, m.groupby(["tech","year"]).units.sum().round(3).to_dict())
print()
print("== heat supply 2050 by tech (top 8) ==")
for lbl,d in (("retireall",A),("hcco2",B)):
    s=d["supply"]; h=s[(s.carrier=="heat")&(s.year==2050)]
    print(lbl, h.groupby("tech").energy.sum().sort_values(ascending=False).head(8).round(1).to_dict())
