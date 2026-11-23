import pandas as pd, re
o = open(r"run_logs\_frlu_probe2.out", "w", encoding="utf8"); P = lambda *a: (print(*a, file=o), o.flush())
E = "data-pipelines\\europe\\"
files = [E + "_ines-builder\\region_transformation.xlsx", E + "region_transformation_IC1.xlsx", E + "region_transformation.xlsx",
         E + "_industry-aidres\\region_transformation_IC1.xlsx", E + "_ines-builder\\CO2_data_IC1.xlsx",
         r"verification\CO2_data_IC1_low_cost.xlsx", r"verification\CO2_data_IC1_high_cost.xlsx"]
for f in files:
    try:
        x = pd.read_excel(f, sheet_name=None, header=None)
    except Exception as e:
        P("ERR", f, e); continue
    P("=====", f, list(x))
    for s, df in x.items():
        txt = df.astype(str)
        hits = {}
        for c in ("FR", "LU", "DE", "UK"):
            m = txt.apply(lambda col: col.str.contains(rf"(?<![A-Za-z]){c}(?![a-z])", regex=True)).values.sum()
            hits[c] = int(m)
        P("--", s, df.shape, "cells mentioning", hits)
        if "IC1" in s or "CO2" in f:
            P(df.head(8).to_string()[:1500])
o.close()
