import pickle
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
f=B["fleet"]; print("fleet cols:",list(f.columns))
print("\nsample techs:",sorted(set(f["tech"].astype(str)))[:40])
print("\ncategories:",sorted(set(f["category"].astype(str)))[:12])
print("\nyears:",sorted(set(f["year"].astype(str))))
i=B["inv"]; print("\ninv cols:",list(i.columns))
