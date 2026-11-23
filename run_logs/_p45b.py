import pickle, pandas as pd
A=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))

print("P4  atmosphere level by year (net CO2):")
for tag,D in [("BASELINE",A),("BIDIR   ",B)]:
    a=D["atm"].groupby("year")["level"].sum().round(3)
    print(f"  {tag}: {a.to_dict()}")

# cement tech list taken from the prod frame itself - no regex guessing
def cement_techs(D):
    p=D["prod"]
    return set(p[p["sector"].astype(str)=="cement"]["tech"].astype(str).unique())
CT = cement_techs(A) | cement_techs(B)
print("\ncement techs used (union of both runs):")
print("  ",sorted(CT))

print("\nP5  cement NET intensity, net of capture:")
for tag,D in [("BASELINE",A),("BIDIR   ",B)]:
    print(f"  --- {tag}")
    for y in ["2030","2040","2050"]:
        p=D["prod"]
        c=p[(p["sector"].astype(str)=="cement")&(p["year"].astype(str).str.startswith(y))]
        o=c["output"].sum()
        e=D["emis"]
        ce=e[(e["tech"].astype(str).isin(CT))&(e["year"].astype(str).str.startswith(y))]["co2"].sum()
        n=D["co2net"]
        cc=n[(n["role"].astype(str)=="captured")&(n["tech"].astype(str).isin(CT))
             &(n["year"].astype(str).str.startswith(y))]["co2"].sum()
        if o:
            print(f"     {y}: out={o:7.0f}  gross={ce:8.1f}  capt={cc:8.1f}  NET={ce-cc:8.1f}  net_int={(ce-cc)/o:7.4f}")
