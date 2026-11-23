import sys, os, re, glob, collections; sys.path.insert(0, "tools")
import pandas as pd
from postprocess import load_weights, unpack_flow
from spinedb_api import DatabaseMapping
exec(open(r"run_logs\_use_all.py", encoding="utf8").read().split("NODE =")[0].split("R = {",1)[0])
R = eval("{" + open(r"run_logs\_use_all.py", encoding="utf8").read().split("R = {",1)[1].split("}\n",1)[0] + "}", {"F": "final_runs_pessimistic_ccs"})
EN = re.compile(r"^elec_((?:NL|BE)C\d+|NL|BE)$")
rows = []
for k, (gi, go) in R.items():
    w = load_weights(glob.glob(gi)[0]); dem = collections.Counter(); xb = collections.Counter()
    with DatabaseMapping("sqlite:///" + os.path.abspath(glob.glob(go)[0])) as db:
        for v in db.get_parameter_value_items(entity_class_name="report__node__stochastic_scenario", parameter_definition_name="demand"):
            m = EN.match(v["entity_byname"][1])
            if not m: continue
            for y, x in unpack_flow(v, w): dem[(m.group(1)[:2], int(y))] += x / 1e3
        for v in db.get_parameter_value_items(entity_class_name="report__connection__node__direction__stochastic_scenario", parameter_definition_name="connection_flow"):
            conn, n, d = v["entity_byname"][1:4]
            m = EN.match(n)
            if not m: continue
            ends = re.findall(r"((?:NL|BE)C\d+|(?<![A-Z])(?:NL|BE|DE|DK|NO|UK|FR|LU)(?![A-Z]))", conn)
            cs = {e[:2] for e in ends}
            if len(cs) < 2 and not any(e[:2] not in ("NL","BE") for e in ends): continue  # internal NL-NL / BE-BE
            if cs <= {"NL","BE"} and len(cs) == 1: continue
            other = [e[:2] for e in ends if e[:2] != m.group(1)[:2]]
            if not other: continue
            o = other[0]
            if o in ("NL","BE"): continue   # NL<->BE counted as internal to NL+BE
            sgn = -1 if d == "from_node" else 1  # from_node = leaving NL/BE node (export)
            for y, x in unpack_flow(v, w): xb[(m.group(1)[:2], int(y))] += sgn * x / 1e3
    for (c, y), val in dem.items(): rows.append((k, "elec", c, "demand (buildings, transport, other)", y, val))
    for (c, y), val in xb.items(): rows.append((k, "elec", c, "net import", y, val))
    print(k, "dem2050", round(sum(v for (c,y),v in dem.items() if y==2050),1), "netimp2050", round(sum(v for (c,y),v in xb.items() if y==2050),1), flush=True)
pd.DataFrame(rows, columns=["run","carrier","cn","tech","year","twh"]).to_pickle(r"run_logs\_elec_dem_xb_all.pkl"); print("saved")
