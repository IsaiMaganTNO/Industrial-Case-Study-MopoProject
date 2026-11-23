import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
e=b["emis"]
q=e[e["year"]==2050]
tot=q["co2"].sum(); pos=q[q["co2"]>0]["co2"].sum(); neg=q[q["co2"]<0]["co2"].sum()
print("2050 NET=%.1f GROSS+=%.1f GROSS-=%.1f"%(tot,pos,neg))
for t in ("LNG-terminal","gas-extraction"):
    r=e[e["tech"]==t]
    print("%-16s %s"%(t,{y:round(r[r["year"]==y]["co2"].sum(),0) for y in (2030,2040,2050)}))
print("\nshare of gross 2050: LNG+extraction = %.1f%%"%
  (100*(e[(e["year"]==2050)&(e["tech"].isin(["LNG-terminal","gas-extraction"]))]["co2"].sum())/pos))
