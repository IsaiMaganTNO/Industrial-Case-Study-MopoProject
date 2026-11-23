import sys, os, glob, collections; sys.path.insert(0, "tools"); import postprocess as P
from spinedb_api import DatabaseMapping
F = r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones"
db = glob.glob(F + r"\output\*.sqlite")[0]; mdl = glob.glob(F + r"\input\*.sqlite")[0]; w = P.load_weights(mdl)
t = collections.Counter()
with DatabaseMapping("sqlite:///" + os.path.abspath(db)) as d:
    ents = {e["id"]: e for e in d.get_entity_items()}
    for v in d.get_parameter_value_items():
        if v["parameter_definition_name"] != "unit_flow": continue
        _, u, n, dr, _ = ents[v["entity_id"]]["entity_byname"]
        if "wind-off" not in u or dr != "to_node": continue
        t[(u, n)] += sum(x for y, x in P.unpack_flow(v, w) if y == 2050) / 1e3
for k, x in sorted(t.items(), key=lambda kv: -kv[1]):
    if x > 0.1: print(f"{x:7.1f} TWh  unit={k[0]}  -> node={k[1]}")
print("total", round(sum(t.values()), 1))
# input side: offshore-related connections and nodes
with DatabaseMapping("sqlite:///" + os.path.abspath(mdl)) as d:
    names = [e["name"] for e in d.get_entity_items(entity_class_name="connection")]
    nodes = [e["name"] for e in d.get_entity_items(entity_class_name="node")]
print("offshore-like nodes:", [n for n in nodes if "OFF" in n.upper() or "NS" in n.upper()][:30])
print("elec connections with offshore ends:", [c for c in names if "elec" in c and ("OFF" in c.upper())][:30])
