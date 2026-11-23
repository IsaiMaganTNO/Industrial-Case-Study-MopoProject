import sys, os, glob, collections, pickle; sys.path.insert(0, "tools")
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
res = {}
for k, (gi, go) in R.items():
    inp, out = glob.glob(gi), glob.glob(go)
    print(k, inp[:1], out[:1], flush=True)
    w = load_weights(inp[0]); agg = collections.Counter()
    with DatabaseMapping("sqlite:///" + os.path.abspath(out[0])) as db:
        for v in db.get_parameter_value_items(entity_class_name="report__unit__node__direction__stochastic_scenario", parameter_definition_name="unit_flow"):
            bn = v["entity_byname"]
            if bn[3] != "to_node" or not bn[2].startswith("HC"): continue
            reg = bn[2].split("_")[-1][:2] if "_" in bn[2] else bn[1].split("_")[-1][:2]
            for y, x in unpack_flow(v, w): agg[(bn[1].rsplit("_", 1)[0], reg, y)] += x / 1e3
    res[k] = agg
    print("  NL+BE 2050:", {t: round(v, 1) for (t, c, y), v in agg.items() if c in ("NL", "BE") and y == 2050 and v > .1}, flush=True)
pickle.dump(res, open(r"run_logs\_hc_supply_all.pkl", "wb")); print("saved")

