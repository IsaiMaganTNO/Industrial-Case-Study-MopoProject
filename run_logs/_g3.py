import pickle, pandas as pd
pd.set_option("display.width", 95)

def cc(r):
    r = str(r)
    return "BE" if r.startswith("BE") else ("NL" if r.startswith("NL") else r)

for tag in ["co2bidir", "vre15"]:
    d = pickle.load(open("run_logs/%s.pkl" % tag, "rb"))
    m = d["supply"]
    m = m[m.carrier == "methane"].copy()
    m["ctry"] = m.region.map(cc)
    print("===", tag, "TWh")
    g = m.groupby(["tech", "ctry", "year"]).energy.sum().div(1000).unstack().round(1)
    print(g.to_string())
    print("-- regions supplying LNG --")
    l = m[m.tech == "LNG-terminal"]
    print(l.groupby(["region", "year"]).energy.sum().div(1000).unstack().round(1).to_string())
    print()
