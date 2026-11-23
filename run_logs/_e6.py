import pickle, pandas as pd
new=pickle.load(open(r"run_logs\gascap.pkl","rb"))
old=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
print("=== DAC specifically (co2net) ===")
for lbl,d in [("base",old),("gascap",new)]:
    c=d["co2net"]; dac=c[c.tech.str.contains("DAC",case=False,na=False)]
    print(f"  {lbl}:", dac.groupby("year")["co2"].sum().round(0).to_dict())
print()
print("=== gross emissions vs captured, 2050 ===")
for lbl,d in [("base",old),("gascap",new)]:
    e=d["emis"]; e50=e[e.year==2050]
    pos=e50[e50.co2>0]["co2"].sum(); neg=e50[e50.co2<0]["co2"].sum()
    print(f"  {lbl}: gross+ {pos:12,.0f}   gross- {neg:12,.0f}   net {pos+neg:10,.0f}")
