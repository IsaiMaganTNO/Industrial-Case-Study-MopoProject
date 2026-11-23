import pickle, pandas as pd
pd.set_option("display.width",108)
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
s=B["supply"].copy()
s["year"]=s["year"].astype(str)
e=s[s["carrier"].astype(str)=="electricity"]
t=e.pivot_table(index="tech",columns="year",values="energy",aggfunc="sum").fillna(0).round(0)
t=t.loc[t.sum(axis=1)>0]
t=t.sort_values(t.columns[-1],ascending=False)
print("ELECTRICITY SUPPLY by tech (GWh):"); print(t.to_string())
for y in t.columns:
    tot=t[y].sum(); print(f"\n{y}: total={tot:,.0f}")
    for k,v in t[y].sort_values(ascending=False).head(5).items():
        if v>0: print(f"    {k:28s} {v:11,.0f}  {v/tot*100:5.1f}%")
