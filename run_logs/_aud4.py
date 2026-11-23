import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
e=b["emis"]
for f in ["CCGT","CCGT+CC","CCGT-existing","OCGT","SMR","SMR+CC","DAC","gas-boiler","gas-boiler-existing"]:
    r=e[e["tech"]==f]
    s={y:round(r[r["year"]==y]["co2"].sum(),1) for y in (2030,2040,2050)}
    print("%-22s %s"%(f,s))
