import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
p=b["prod"]
cons=["(H2)DRI-EAF","(H2)FT-DC","(H2)MeOH-DC","(H2)NH3","(H2)PE","(H2)PEA",
"CCGT-H2","OCGT-H2","REF(H2)","fuelcell","methanation","((BM+H2)MeOH)O",
"(H2)_gco","(H2)_gfi","(H2)_gfl","(H2)-CC_gco","(H2)-CC_gfi","(H2)-CC_gfl",
"(EL)PE","(EL)_gco","(EL)_gfl","(EL)-CC_gco"]
print("H2-CONSUMING units: output by year")
for t in cons:
    q=p[p["tech"]==t]
    if not len(q): continue
    d={y:round(q[q["year"]==y]["output"].sum(),0) for y in (2030,2040,2050)}
    if any(d.values()): print("   %-16s %s"%(t,d))
