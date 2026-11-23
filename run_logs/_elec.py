import pickle, pandas as pd
pd.set_option("display.width",108)
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
s=B["supply"]
e=s[s["carrier"].astype(str)=="electricity"]
t=e.pivot_table(index="tech",columns="year",values="energy",aggfunc="sum").fillna(0).round(0)
t=t.loc[t.sum(axis=1)>0].sort_values("2050",ascending=False)
print("ELECTRICITY SUPPLY by tech (GWh):")
print(t.to_string())
print("\nshares 2030 / 2050:")
for y in ["2030","2050"]:
    col=t[y]; tot=col.sum()
    print(f"  {y}: total={tot:,.0f}")
    for k,v in col.sort_values(ascending=False).head(6).items():
        print(f"      {k:28s} {v:10,.0f}  {v/tot*100:5.1f}%")
