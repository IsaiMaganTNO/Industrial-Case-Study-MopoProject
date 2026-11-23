import pickle
d=pickle.load(open(r"run_logs\hcco2.pkl","rb"))
p=d["prod"]; e=d["emis"]; f=d["fleet"]
print("prod techs containing 'reference':",sorted(set(t for t in p["tech"] if "reference" in t))[:12])
print("\nemis techs containing 'reference':",sorted(set(t for t in e["tech"] if "reference" in t))[:12])
print("\nfleet techs containing 'reference':",sorted(set(t for t in f["tech"] if "reference" in t))[:12])
