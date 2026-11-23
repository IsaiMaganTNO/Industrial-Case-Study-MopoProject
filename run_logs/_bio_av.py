import sys, os, glob, re; sys.path.insert(0, "tools"); import postprocess as P
from spinedb_api import DatabaseMapping
import pandas as pd
pd.set_option("display.width", 220); pd.set_option("display.max_rows", 300)
RUNS = {"IC1": "1_IC1_NLBE_17zones", "CTRY": "2_CountryLevel_NLBE", "MR": "3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK"}
KEEP = re.compile(r"^(CH4|HC|aviation|int-aviation|biomass|bio|MeOH)")
for k, f in RUNS.items():
    out = glob.glob(rf"final_runs_pessimistic_ccs\{f}\output\*.sqlite")[0]; inp = glob.glob(rf"final_runs_pessimistic_ccs\{f}\input\*.sqlite")[0]
    w = P.load_weights(inp); rows = []
    with DatabaseMapping("sqlite:///" + os.path.abspath(out)) as d:
        ents = {e["id"]: e for e in d.get_entity_items()}
        for v in d.get_parameter_value_items():
            cls, par = v["entity_class_name"], v["parameter_definition_name"]
            if par not in ("unit_flow", "connection_flow"): continue
            bn = ents[v["entity_id"]]["entity_byname"]
            if len(bn) < 4: continue
            node = bn[2]; nb = node.rsplit("_", 1)[0]
            if not KEEP.match(nb): continue
            reg = node.rsplit("_", 1)[-1] if "_" in node else ""
            for y, x in P.unpack_flow(v, w):
                if y == 2050 and abs(x) > 1e-9:
                    rows.append(dict(kind=par, obj=bn[1], node=nb, reg=reg, cn=reg[:2], dir=bn[3], v=x))
    df = pd.DataFrame(rows); df.to_pickle(rf"run_logs\_flows2050_{k}.pkl")
    print("=====", k, len(df))
    df["obj_g"] = df.obj.str.replace(r"_(NLC\d|BEC\d|NL|BE|DE|DK|NO|UK)(__.*)?$", "", regex=True)
    nlbe = df[df.cn.isin(["NL", "BE"])]
    for n in ["CH4", "HC", "aviation", "int-aviation"]:
        q = nlbe[nlbe.node == n]
        if q.empty: continue
        t = q.groupby(["kind", "dir", "obj_g"]).v.sum().div(1e3).round(2)
        print("--", n); print(t[t.abs() >= .05].to_string())
    q = nlbe[nlbe.node.str.startswith("bio")]
    print("-- bio* nodes"); print(q.groupby(["node", "kind", "dir", "obj_g"]).v.sum().div(1e3).round(2).loc[lambda s: s.abs() >= .05].to_string())
