import pickle, glob, os, numpy as np
from spinedb_api import DatabaseMapping, from_database
rows = pickle.load(open(r"run_logs\_congestion_IC1.pkl","rb"))
r = [x for x in rows if x["conn"]=="NLC2_elec_NLC3"][0]
print(r["fl"].describe()); print(r["capS"].describe())
db = glob.glob(r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\output\*.sqlite")[0]
with DatabaseMapping("sqlite:///" + os.path.abspath(db)) as d:
    for v in d.get_parameter_value_items():
        if v["parameter_definition_name"] in ("connections_invested_available","connections_invested") and "NLC2_elec_NLC3" in v["entity_byname"]:
            x = from_database(v["value"], v["type"]); print(v["parameter_definition_name"], list(zip(map(str,x.indexes), x.values))[:6])
mdl = glob.glob(r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\input\*.sqlite")[0]
with DatabaseMapping("sqlite:///" + os.path.abspath(mdl)) as d:
    for v in d.get_parameter_value_items():
        if "NLC2_elec_NLC3" in v["entity_byname"]:
            x = from_database(v["value"], v["type"]); print(v["entity_class_name"], v["parameter_definition_name"], v["entity_byname"], str(x)[:120])
