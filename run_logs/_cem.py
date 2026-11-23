import pickle, pandas as pd
pd.set_option("display.width",108)
A=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
print("P3/P5  2050 CEMENT by route x region")
for tag,D in [("BASELINE",A),("BIDIR   ",B)]:
    p=D["prod"]; c=p[(p["sector"].astype(str)=="cement")&(p["year"].astype(str).str.contains("2050"))]
    t=c.pivot_table(index="tech",columns="region",values="output",aggfunc="sum").fillna(0).round(1)
    t=t.loc[t.sum(1)>0]
    print(f"\n--- {tag}"); print(t.to_string())
    unab=c[~c["tech"].astype(str).str.contains("MEA|Oxy|CaL",na=False)]["output"].sum()
    print(f"    unabated cement 2050 = {unab:,.1f}")
