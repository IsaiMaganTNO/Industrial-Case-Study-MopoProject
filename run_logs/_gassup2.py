import pickle
d=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
for k in ["supply","prod"]:
    f=d[k]; print(k, f.columns.tolist())
s=d["supply"]
print("\ncarriers:",sorted(s["carrier"].unique()))
m=s[s.carrier=="methane"]
print("methane techs:",sorted(m["tech"].unique()))
print("methane regions:",sorted(m["region"].unique()))
print("\n2050 methane total:",round(m[m.year==2050]["energy"].sum(),1))
