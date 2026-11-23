import pandas as pd, json, collections
o = open(r"run_logs\_frlu_probe.out", "w", encoding="utf8"); P = lambda *a: (print(*a, file=o), o.flush())
V = "verification\\"
for f in ["global_constraints_industry_case_study.xlsx", "global_constraints_industry_case_study_FR_LU.xlsx"]:
    x = pd.read_excel(V + f, sheet_name=None, header=None)
    P("=====", f, "sheets:", list(x))
    for s, df in x.items():
        P("--", s, df.shape); P(df.head(40).to_string())
for f in ["BE_NL_IC1_NWEU_w_FR_LU.geojson", "IC_NWEU.geojson"]:
    g = json.load(open(V + f, encoding="utf8"))
    feats = g["features"]; P("=====", f, "features", len(feats), "crs", g.get("crs"))
    P("props keys", list(feats[0]["properties"]))
    for ft in feats: P({k: v for k, v in ft["properties"].items()}, ft["geometry"]["type"])
g0 = json.load(open(r"geodata\IC1_NWEU.geojson", encoding="utf8"))
P("===== geodata/IC1_NWEU.geojson", len(g0["features"]), list(g0["features"][0]["properties"]))
for ft in g0["features"]: P(ft["properties"])
o.close()
