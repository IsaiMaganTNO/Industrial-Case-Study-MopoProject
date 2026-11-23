import pickle, pandas as pd
A=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
s=B["supply"]
print("supply carriers:",sorted(set(s["carrier"].astype(str))))
print()
for tag,D in [("BASELINE",A),("BIDIR   ",B)]:
    s=D["supply"]
    bio=s[s["carrier"].astype(str).str.lower().str.startswith("bio")]
    if len(bio)==0:
        print(f"{tag}: NO bio rows in supply frame")
    else:
        print(f"{tag} bio energy by year: {bio.groupby('year')['energy'].sum().round(1).to_dict()}")
