import pandas as pd, glob, os
T={"DE","DK","NO","UK"}
df=pd.read_csv("data/Transport/fleet.csv")
cc=df["Country code"].astype(str).str.strip()
print("fleet.csv Country code values:", sorted(set(cc))[:40])
print("  targets:", sorted(set(cc)&T))
f2=pd.read_csv("data/Transport/fleets_per_scenario.csv")
print("\nfleets_per_scenario cols:", list(f2.columns)[:8])
c2=f2.iloc[:,0].astype(str).str.strip()
print("  col0 values:", sorted(set(c2))[:40], "| targets:", sorted(set(c2)&T))
# industry
for p in ["data/Industry/production_JRC_IDEES_nuts3.xlsx","data/Industry/technology_catalogue_ind_nuts0_nuts3.xlsx"]:
    xl=pd.ExcelFile(p); print("\n####",os.path.basename(p),"sheets",xl.sheet_names[:6])
    d=pd.read_excel(p,xl.sheet_names[0],nrows=500)
    print("   cols:",[str(c)[:18] for c in d.columns[:10]])
    for col in d.columns[:5]:
        v=set(str(x).strip() for x in d[col].dropna().unique()[:800])
        t=v&T
        nuts=[x for x in v if len(x)>=4 and x[:2] in ("DE","DK","NO","UK")]
        if t or nuts: print("   col",col,"targets",sorted(t)[:6],"nutsish",sorted(nuts)[:8])
