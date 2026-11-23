import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
e=b["emis"]; p=b["prod"]
ts=sorted(set(str(t) for t in e["tech"]))
print("emis techs matching CCGT/SMR/OCGT/DAC/gas-boiler:")
for t in ts:
    if any(k in t for k in ("CCGT","SMR","OCGT","DAC","gas-boiler")): print("   ",t)
print("\nprod 2050 for those:")
for t in sorted(set(str(x) for x in p["tech"])):
    if any(k in t for k in ("CCGT","SMR","OCGT","DAC","gas-boiler")):
        o=p[(p["tech"]==t)&(p["year"]==2050)]["output"].sum()
        if o>1: print("    %-28s %10.1f"%(t[:28],o))
