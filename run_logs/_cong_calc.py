import pickle, glob, os, collections, numpy as np, pandas as pd
from spinedb_api import DatabaseMapping, from_database
F = r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones"
db = glob.glob(F + r"\output\*.sqlite")[0]; mdl = glob.glob(F + r"\input\*.sqlite")[0]
inp = collections.defaultdict(dict)
with DatabaseMapping("sqlite:///" + os.path.abspath(mdl)) as d:
    for v in d.get_parameter_value_items():
        p = v["parameter_definition_name"]
        if p in ("capacity_per_connection","investment_count_max_cumulative","investment_count_initial_cumulative","connection_capacity","number_of_connections","initial_connections_invested_available"):
            x = from_database(v["value"], v["type"]); inp[v["entity_byname"][0]][p] = x if isinstance(x,(int,float)) else str(x)[:60]
avail = {}
with DatabaseMapping("sqlite:///" + os.path.abspath(db)) as d:
    for v in d.get_parameter_value_items():
        if v["parameter_definition_name"] == "connections_invested_available":
            x = from_database(v["value"], v["type"]); avail[v["entity_byname"][1]] = dict(zip([str(i)[:4] for i in x.indexes], x.values))
rows = pickle.load(open(r"run_logs\_congestion_IC1.pkl","rb"))
out = []
for r in rows:
    c = r["conn"]; car = c.split("_")[1]
    if car not in ("elec","H2","CO2","CH4"): continue
    i = inp.get(c, {}); cap1 = i.get("capacity_per_connection")
    n = avail.get(c, {}).get("2050", i.get("investment_count_initial_cumulative", 1))
    mx = i.get("investment_count_max_cumulative")
    fl, wt = r["fl"].values, r["wt"]; ok = wt > 0
    capT = (cap1 or np.nan) * (n if n else 1)
    out.append(dict(conn=c, car=car, frm=r["node"], cap1=cap1, n2050=n, nmax=mx, capGW=capT,
                    avgflow=(fl*wt).sum()/wt[ok].sum(), sat=(wt*((fl >= .99*capT) & ok)).sum()/wt[ok].sum() if capT==capT and capT>0 else np.nan))
d = pd.DataFrame(out); d.to_pickle(r"run_logs\_cong_IC1.pkl")
pd.set_option("display.width", 220)
print(d.groupby("car").agg(n=("conn","size"), nocap=("cap1", lambda x: x.isna().sum()), atmax=("n2050", "count")))
for car in ("elec","H2","CO2","CH4"):
    print(car); print(d[d.car==car].sort_values("sat", ascending=False).head(12).round(2).to_string())
