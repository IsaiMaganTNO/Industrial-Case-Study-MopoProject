import glob, os, sys, pickle, collections; sys.path.insert(0, "tools"); import postprocess as P
import numpy as np, pandas as pd
from spinedb_api import DatabaseMapping, from_database
f = "1_IC1_NLBE_17zones"
db = glob.glob(rf"final_runs_pessimistic_ccs\{f}\output\*.sqlite")[0]
w = P.load_weights(glob.glob(rf"final_runs_pessimistic_ccs\{f}\input\*.sqlite")[0])
S = collections.defaultdict(dict)
with DatabaseMapping("sqlite:///" + os.path.abspath(db)) as d:
    ents = {e["id"]: e for e in d.get_entity_items()}
    for v in d.get_parameter_value_items():
        p = v["parameter_definition_name"]
        if p not in ("capacity_per_connection", "connection_flow"): continue
        _, conn, node, dr, _ = ents[v["entity_id"]]["entity_byname"]
        val = from_database(v["value"], v["type"])
        s = pd.Series(np.asarray(val.values, float), index=pd.to_datetime([str(i) for i in val.indexes]))
        s = s[s.index.year == 2050]
        S[(conn, node, dr)][p] = s
rows = []
for (conn, node, dr), dd in S.items():
    if dr != "from_node" or "connection_flow" not in dd: continue
    fl = dd["connection_flow"]; cap = dd.get("capacity_per_connection")
    if cap is None: cap = S.get((conn, node, "to_node"), {}).get("capacity_per_connection")
    wt = np.array([w.get(str(t)[:10], 0) for t in fl.index], float)
    rows.append(dict(conn=conn, node=node, flow_TWh=(fl.values * wt).sum() / 1e6,
                     cap=None if cap is None else cap.reindex(fl.index).max(),
                     fl=fl, capS=None if cap is None else cap.reindex(fl.index), wt=wt))
pickle.dump(rows, open(r"run_logs\_congestion_IC1.pkl", "wb"))
df = pd.DataFrame([{k: r[k] for k in ("conn", "node", "flow_TWh", "cap")} for r in rows])
df["car"] = df.conn.str.split("_").str[1]
print(df.groupby("car").agg(n=("conn", "size"), cap_missing=("cap", lambda x: x.isna().sum()), TWh=("flow_TWh", "sum")).round(1))
print(df.sort_values("flow_TWh", ascending=False).head(12).round(2).to_string())
