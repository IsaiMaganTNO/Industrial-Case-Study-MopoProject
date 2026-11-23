import pickle, pandas as pd
A=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
print("industrial output by FUEL (prod frame), 2050:")
for tag,D in [("BASELINE",A),("BIDIR   ",B)]:
    p=D["prod"]; p=p[p["year"].astype(str).str.startswith("2050")]
    g=p.groupby(p["fuel"].astype(str))["output"].sum().sort_values(ascending=False).round(1)
    print(f"  --- {tag}"); print(g.to_string())
    print()
print("CEMENT output by fuel, 2050:")
for tag,D in [("BASELINE",A),("BIDIR   ",B)]:
    p=D["prod"]; p=p[(p["year"].astype(str).str.startswith("2050"))&(p["sector"].astype(str)=="cement")]
    print(f"  {tag}: {p.groupby(p['fuel'].astype(str))['output'].sum().round(1).to_dict()}")
