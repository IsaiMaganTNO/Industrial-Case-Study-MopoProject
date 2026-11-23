import pickle, pandas as pd
A=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
print("P4 net CO2 (atmosphere) by year:")
for tag,D in [("BASELINE",A),("BIDIR   ",B)]:
    a=D["atm"].groupby("year")["co2"].sum() if "co2" in D["atm"].columns else D["atm"].sum()
    print(f"  {tag}: {dict((str(k)[:4],round(v,3)) for k,v in a.items())}")
print("\nP5 cement NET intensity (gross - captured)/output:")
for tag,D in [("BASELINE",A),("BIDIR   ",B)]:
    out=[]
    for y in ["2030","2040","2050"]:
        p=D["prod"]; c=p[(p["sector"].astype(str)=="cement")&(p["year"].astype(str).str.contains(y))]
        o=c["output"].sum()
        e=D["emis"]; ce=e[(e["tech"].astype(str).str.contains("CEM2|LC3",na=False))&(e["year"].astype(str).str.contains(y))]["co2"].sum()
        n=D["co2net"]; cc=n[(n["role"].astype(str)=="captured")&(n["tech"].astype(str).str.contains("CEM2|LC3",na=False))&(n["year"].astype(str).str.contains(y))]["co2"].sum()
        out.append(f"{y}: out={o:7.0f} gross={ce:8.1f} capt={cc:8.1f} NET={(ce-cc):8.1f} int={(ce-cc)/o:.4f}" if o else f"{y}: n/a")
    print(f"  {tag}"); [print("     ",x) for x in out]
