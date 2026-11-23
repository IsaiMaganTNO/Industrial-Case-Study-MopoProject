import sys, os, collections, pickle; sys.path.insert(0, "tools")
from postprocess import load_weights, unpack_flow
from spinedb_api import DatabaseMapping
R = {"IC1": r"1_IC1_NLBE_17zones", "CTRY": r"2_CountryLevel_NLBE", "MR": r"3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK"}
res = {}
for k, d in R.items():
    base = os.path.join("final_runs_pessimistic_ccs", d)
    out = [f for f in os.listdir(base + r"\output") if f.endswith(".sqlite")][0]
    inp = [f for f in os.listdir(base + r"\input") if f.endswith(".sqlite")][0]
    w = load_weights(os.path.join(base, "input", inp)); agg = collections.Counter()
    with DatabaseMapping("sqlite:///" + os.path.abspath(os.path.join(base, "output", out))) as db:
        ents = {e["id"]: e for e in db.get_entity_items()}
        for v in db.get_parameter_value_items():
            if v["entity_class_name"] != "report__unit__node__direction__stochastic_scenario" or v["parameter_definition_name"] != "unit_flow": continue
            bn = ents[v["entity_id"]]["entity_byname"]
            if bn[3] != "to_node" or not bn[2].startswith("HC"): continue
            reg = bn[2].split("_")[-1][:2] if "_" in bn[2] else bn[1].split("_")[-1][:2]
            for y, x in unpack_flow(v, w): agg[(bn[1].rsplit("_", 1)[0], reg, y)] += x / 1e3
    res[k] = agg
    print("==", k); [print(kk, round(vv, 1)) for kk, vv in sorted(agg.items()) if vv > .1]
pickle.dump(res, open(r"run_logs\_hc_supply.pkl", "wb"))
