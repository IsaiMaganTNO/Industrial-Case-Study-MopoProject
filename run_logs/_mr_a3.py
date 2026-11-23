import pickle, pandas as pd
pd.set_option("display.width",250)
M=pickle.load(open(r"run_logs\mixedres.pkl","rb")); V=pickle.load(open(r"run_logs\vre15.pkl","rb"))
def ctry(r): r=str(r); return r[:2] if len(r)>2 and r[2]=="C" else r
print("atm level mixed:", M["atm"].to_dict("records"))
print("atm level vre15:", V["atm"].to_dict("records"))
for nm,F in [("vre15",V),("mixed",M)]:
    e=F["emis"].copy(); e["c"]=e.region.map(ctry)
    print(f"\n=== {nm}: net CO2 to atmosphere by country (Mt)")
    print((e.groupby(["c","year"]).co2.sum().unstack()/1e3).round(2).to_string())
    print("   TOTAL:", (e.groupby("year").co2.sum()/1e3).round(2).to_dict())
    cs=F["co2store"]; print(f"   stored by reservoir (Mt):"); print((cs.groupby(["reservoir","year"]).co2.sum().unstack(fill_value=0)/1e3).round(2).to_string())
e=M["emis"].copy(); e["c"]=e.region.map(ctry)
print("\n=== mixed 2050 top +/- emitters (Mt)")
g=e[e.year==2050].groupby(["tech","c"]).co2.sum()/1e3
print(g.sort_values().head(8).round(2).to_string()); print(g.sort_values().tail(10).round(2).to_string())
