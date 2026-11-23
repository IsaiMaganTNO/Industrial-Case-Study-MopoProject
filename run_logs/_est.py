import pickle,pandas as pd
d=pickle.load(open(r"run_logs\hcco2.pkl","rb"))
p=d["prod"]; e=d["emis"]
fac={"aluminium-primary-production-reference":1.8419,
"other-chemicals-production-reference":0.8177,"pharmaceuticals-production-reference":0.7536,
"other-non-ferrous-metals-production-reference":0.6137,
"other-industrial-sectors_production-reference":0.3428,
"food-beverages-tobacco-production-reference":0.2570,"paper-production-reference":0.2486,
"leather-and-textile-production-reference":0.2217,"pulp-production-reference":0.2049,
"ceramics-and-other-non-metalic-minerals-production-reference":0.1756,
"machinery-equipment-production-reference":0.1449,
"transport-equipment-production-reference":0.1388,
"wood-and-wood-products_production-reference":0.0899,
"printing-and-media-production-reference":0.0503,"(LN+EL)O":0.0}
print("%-48s %10s %10s %10s"%("family","out2050","oldCO2","newCO2est"))
to=tn=0.0
for f,v in sorted(fac.items(),key=lambda z:-z[1]):
    out=p[(p["tech"]==f)&(p["year"]==2050)]["output"].sum()
    old=e[(e["tech"]==f)&(e["year"]==2050)]["co2"].sum()
    new=out*v
    to+=old; tn+=new
    if out>0 or old>0: print("%-48s %10.1f %10.1f %10.1f"%(f[:48],out,old,new))
print("%-48s %10s %10.1f %10.1f  (delta %+.1f)"%("TOTAL","",to,tn,tn-to))
