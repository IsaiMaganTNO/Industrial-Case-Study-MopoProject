import sys, os, glob, re, collections, pandas as pd; sys.path.insert(0, "tools"); import postprocess as P
from spinedb_api import DatabaseMapping
F = r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones"
db = glob.glob(F + r"\output\*.sqlite")[0]; w = P.load_weights(glob.glob(F + r"\input\*.sqlite")[0])
gen = collections.Counter(); use = collections.Counter(); off = collections.Counter(); pem = collections.Counter()
with DatabaseMapping("sqlite:///" + os.path.abspath(db)) as d:
    ents = {e["id"]: e for e in d.get_entity_items()}
    for v in d.get_parameter_value_items():
        if v["parameter_definition_name"] != "unit_flow": continue
        _, u, n, dr, _ = ents[v["entity_id"]]["entity_byname"]
        if not n.startswith("elec_"): continue
        z = n[5:]
        x = sum(val for y, val in P.unpack_flow(v, w) if y == 2050) / 1e3
        if dr == "to_node":
            gen[z] += x
            if "wind-off" in u: off[z] += x
        else:
            use[z] += x
            if u.startswith("PEM"): pem[z] += x
t = pd.DataFrame({"gen": gen, "offshore": off, "use": use, "PEM_use": pem}).fillna(0)
t["net_export"] = t.gen - t.use
d = pd.read_pickle(r"run_logs\_cong_IC1.pkl"); d = d[d.car == "elec"]
d["a"], d["b"] = d.conn.str.split("_").str[0], d.conn.str.split("_").str[2]
# flows are reported from the 'from' node of each direction entry
d["src"] = d.frm.str[5:]; d["dst"] = d.apply(lambda r: r.b if r.src == r.a else r.a, axis=1)
full = d[d.sat >= .9]
t["full_out"] = full.groupby("src").size(); t["full_in"] = full.groupby("dst").size()
print(t.fillna(0).round(1).sort_values("net_export", ascending=False).to_string())
print(full[["src", "dst", "sat"]].round(2).to_string())
