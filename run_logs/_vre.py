import pickle
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
f=B["fleet"]
vre=sorted(t for t in set(f["tech"].astype(str)) if any(k in t.lower() for k in ("solar","pv","wind")))
print("VRE techs in fleet:",vre)
print()
print("units column stats for solar/wind:")
sel=f[f["tech"].astype(str).isin(vre)]
print(sel.head(6).to_string())
print("\nregions:",sorted(set(sel["region"].astype(str))))
