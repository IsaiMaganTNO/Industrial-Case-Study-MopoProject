import pickle, pandas as pd
pd.set_option("display.width", 95)
for tag in ["co2bidir", "vre15"]:
    d = pickle.load(open("run_logs/%s.pkl" % tag, "rb"))
    s = d["supply"]
    m = s[s.carrier == "methane"]
    print("===", tag, "methane rows", len(m), "TWh total by year")
    print(m.groupby("year").energy.sum().div(1000).round(1).to_string())
    print("-- techs --")
    t = m.groupby(["tech", "year"]).energy.sum().div(1000).unstack().round(1)
    print(t.to_string())
    print()
