import sys, os, glob, re, pandas as pd; sys.path.insert(0, "tools"); import postprocess as P
from spinedb_api import DatabaseMapping
RUNS = {"IC1": "1_IC1_NLBE_17zones", "CTRY": "2_CountryLevel_NLBE"}
res = {}
for k, f in RUNS.items():
    db = glob.glob(rf"final_runs_pessimistic_ccs\{f}\output\*.sqlite")[0]
    mdl = glob.glob(rf"final_runs_pessimistic_ccs\{f}\input\*.sqlite")
    w = P.load_weights(mdl[0]) if mdl else None
    tot = {}
    with DatabaseMapping("sqlite:///" + os.path.abspath(db)) as d:
        ents = {e["id"]: e for e in d.get_entity_items()}
        for v in d.get_parameter_value_items():
            if v["entity_class_name"] != "report__unit__node__direction__stochastic_scenario" or v["parameter_definition_name"] != "unit_flow": continue
            bn = ents[v["entity_id"]]["entity_byname"]
            if bn[3] != "from_node" or not bn[2].lower().startswith("elec"): continue
            if not re.search(r"_(NL|BE)", bn[2]) and bn[2].split("_")[-1][:2] not in ("NL", "BE"): continue
            for y, x in P.unpack_flow(v, w):
                if y == 2050:
                    t = re.sub(r"_[A-Z]{2}[A-Za-z0-9]*$", "", bn[1]); tot[t] = tot.get(t, 0) + x
    res[k] = pd.Series(tot) / 1e3
t = pd.DataFrame(res).fillna(0); t["diff"] = t.CTRY - t.IC1
pd.set_option("display.width", 200)
print(t[t[["IC1","CTRY"]].max(axis=1) > 1].sort_values("IC1", ascending=False).round(1).to_string())
print("TOTAL TWh", t.sum().round(1).to_dict())
