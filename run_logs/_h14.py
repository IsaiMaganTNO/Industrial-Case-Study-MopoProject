import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
e=b["emis"]
for t in ("LH2-terminal","LNG-terminal","SMR+CC","PEM"):
    q=e[e["tech"]==t]
    if len(q): print("%-14s co2 %s"%(t,{y:round(q[q["year"]==y]["co2"].sum(),1) for y in (2030,2040,2050)}))
    else: print("%-14s absent from emis"%t)
# SMR+CC capture credited?
cn=b["co2net"]
print("\nco2net roles:",sorted(set(str(x) for x in cn["role"]))[:6])
q=cn[(cn["year"]==2050)&(cn["tech"].astype(str).str.contains("SMR"))]
print("SMR rows in co2net 2050:",len(q), q["co2"].sum() if len(q) else "")
