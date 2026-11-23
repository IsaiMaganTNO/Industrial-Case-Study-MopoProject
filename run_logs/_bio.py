import pickle, pandas as pd
A=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
for tag,D in [("BASELINE",A),("BIDIR   ",B)]:
    s=D["supply"]
    bio=s[s["carrier"].astype(str).str.contains("bio",case=False,na=False)]
    g=bio.groupby("year")["energy"].sum().round(1)
    print(f"{tag} TOTAL bio supply by year: {g.to_dict()}")
print()
# DAC and overall capture comparison
for tag,D in [("BASELINE",A),("BIDIR   ",B)]:
    n=D["co2net"]; cap=n[n["role"].astype(str)=="captured"]
    g=cap.groupby("year")["co2"].sum().round(1)
    print(f"{tag} total captured by year: {g.to_dict()}")
print()
for tag,D in [("BASELINE",A),("BIDIR   ",B)]:
    n=D["co2net"]; cap=n[(n["role"].astype(str)=="captured")&(n["year"].astype(str).str.startswith("2050"))]
    top=cap.groupby("tech")["co2"].sum().sort_values(ascending=False).head(8).round(1)
    print(f"--- {tag} 2050 capture by tech"); print(top.to_string()); print()
