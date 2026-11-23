import pickle, pandas as pd
pd.set_option("display.width",108)
A=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
print("2050 CO2 captured by REGION (role='captured'):")
for tag,D in [("BASELINE",A),("BIDIR   ",B)]:
    n=D["co2net"]; c=n[(n["role"].astype(str)=="captured")&(n["year"].astype(str).str.startswith("2050"))]
    c=c.copy(); c["ctry"]=c["region"].astype(str).str[:2]
    g=c.groupby("ctry")["co2"].sum().round(1)
    print(f"  {tag}: {g.to_dict()}   TOTAL={c['co2'].sum():,.1f}")
print()
print("2050 INJECTION into geological storage (role contains used/injected):")
for tag,D in [("BASELINE",A),("BIDIR   ",B)]:
    n=D["co2net"]; c=n[n["year"].astype(str).str.startswith("2050")]
    inj=c[c["tech"].astype(str).str.contains("injection",case=False,na=False)]
    g=inj.groupby("tech")["co2"].sum().round(1).sort_values()
    print(f"  --- {tag}"); print(g.to_string())
