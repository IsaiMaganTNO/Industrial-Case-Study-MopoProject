import sys, os, glob, re, collections; sys.path.insert(0, "tools"); import postprocess as P
from spinedb_api import DatabaseMapping
F = r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK"
db = glob.glob(F + r"\output\*.sqlite")[0]; w = P.load_weights(glob.glob(F + r"\input\*.sqlite")[0])
t = collections.Counter()
with DatabaseMapping("sqlite:///" + os.path.abspath(db)) as d:
    ents = {e["id"]: e for e in d.get_entity_items()}
    for v in d.get_parameter_value_items():
        if v["parameter_definition_name"] != "connection_flow": continue
        _, conn, node, dr, _ = ents[v["entity_id"]]["entity_byname"]
        m = re.match(r"^([A-Z]{2})[A-Z0-9]*_(bio|MeOH|HC)_([A-Z]{2})[A-Z0-9]*$", conn)
        if not m or m[1] == m[3] or dr != "from_node": continue
        src = node.split("_")[-1][:2]; dst = m[3] if src == m[1] else m[1]
        t[(m[2], src, dst)] += sum(x for y, x in P.unpack_flow(v, w) if y == 2050) / 1e3
for k, x in sorted(t.items()):
    if abs(x) > .05: print(k, round(x, 2), "TWh")
