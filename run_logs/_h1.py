import pickle
b=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
p=b["prod"]; f=b["fleet"]
ts=sorted(set(str(t) for t in p["tech"]))
print("prod techs w/ PEM/Alk/SOEC/electrolys:")
for t in ts:
    if any(k.lower() in t.lower() for k in ("PEM","alkal","SOEC","electroly")): print("   ",t)
print("\nfleet techs same:")
for t in sorted(set(str(t) for t in f["tech"])):
    if any(k.lower() in t.lower() for k in ("PEM","alkal","SOEC","electroly")): print("   ",t)
