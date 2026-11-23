import sys, os, re, glob, collections, pickle; sys.path.insert(0, "tools")
import pandas as pd
from postprocess import load_weights, unpack_flow
from spinedb_api import DatabaseMapping
F = "final_runs_pessimistic_ccs"
R = {
 "IC1":  (rf"{F}\1_IC1_NLBE_17zones\input\*.sqlite", rf"{F}\1_IC1_NLBE_17zones\output\*.sqlite"),
 "CTRY": (rf"{F}\2_CountryLevel_NLBE\input\*.sqlite", rf"{F}\2_CountryLevel_NLBE\output\*.sqlite"),
 "MR":   (rf"{F}\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\*.sqlite", rf"{F}\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\output\*.sqlite"),
 "S1":   (r"runs\ctryco2B_mr\*.sqlite", rf"{F}\5_MixedRes_CountryCO2caps_emitter_credit\output\*.sqlite"),
 "S2":   (r"runs\rp10_mr_noblend\*.sqlite", r"runs\rp10_mr_noblend\output\*.sqlite"),
 "S3":   (rf"{F}\6_MixedRes_OptimisticCCS\input\*.sqlite", rf"{F}\6_MixedRes_OptimisticCCS\output\*.sqlite"),
 "S4":   (r"runs\3day_mr_frlu_v4\input\*.v4.sqlite", r"xpress_server_v4\*.sqlite"),
}
NODE = re.compile(r"^(elec|H2)_((?:NL|BE)C\d+|NL|BE)$")
rows = []
for k, (gi, go) in R.items():
    w = load_weights(glob.glob(gi)[0]); agg = collections.Counter()
    with DatabaseMapping("sqlite:///" + os.path.abspath(glob.glob(go)[0])) as db:
        for v in db.get_parameter_value_items(entity_class_name="report__unit__node__direction__stochastic_scenario", parameter_definition_name="unit_flow"):
            u, n, d = v["entity_byname"][1:4]
            m = NODE.match(n)
            if not m or d != "from_node": continue
            car, reg = m.groups()
            tech = re.sub(r"_((?:NL|BE)C\d+|NL|BE)$", "", u)
            for y, x in unpack_flow(v, w): agg[(car, reg[:2], tech, int(y))] += x / 1e3
    rows += [(k, *key, val) for key, val in agg.items()]
    t = collections.Counter()
    for (car, c, tech, y), val in agg.items():
        if y == 2050: t[car] += val
    print(k, {c: round(v, 1) for c, v in t.items()}, flush=True)
df = pd.DataFrame(rows, columns=["run", "carrier", "cn", "tech", "year", "twh"])
df.to_pickle(r"run_logs\_use_elec_h2_all.pkl"); print("saved", len(df))

