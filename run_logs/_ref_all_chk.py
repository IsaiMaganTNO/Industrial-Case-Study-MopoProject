import pickle, collections
r = pickle.load(open(r"run_logs\_hc_supply_all.pkl", "rb"))
for k, a in r.items():
    t = collections.Counter()
    for (tech, c, y), v in a.items(): t[(y, c, tech)] += v
    print(k, {f"{y} {c} {tech}": round(v, 1) for (y, c, tech), v in sorted(t.items()) if v > 1})
