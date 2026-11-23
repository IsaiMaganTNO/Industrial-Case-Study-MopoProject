import pandas as pd
o = open(r"run_logs\_frlu_probe3.out", "w", encoding="utf8"); P = lambda *a: (print(*a, file=o), o.flush())
E = "data-pipelines\\europe\\"
for f in [E + "_ines-builder\\CO2_data_IC1.xlsx", r"verification\CO2_data_IC1_low_cost.xlsx"]:
    x = pd.read_excel(f, sheet_name=None)
    P("=====", f)
    n = x["network"]; P(n[n["from"].isin(["FR", "LU"]) | n["to"].isin(["FR", "LU"])].to_string())
    s = x["network_to_storage"]; P(s[s["from"].isin(["FR", "LU"])].to_string())
    st = x["storage"]; P(st[st["node"].isin(["FR", "LU"])].to_string())
    P("storage nodes", sorted(st["node"].unique()))
    P("net nodes", sorted(set(n["from"]) | set(n["to"])))
r = pd.read_excel(E + "_ines-builder\\region_transformation.xlsx", sheet_name=None)
P("===== IC1 sheet (_ines-builder)"); P(r["IC1"].to_string())
P("PECD1 FR/LU"); P(r["PECD1"][r["PECD1"].astype(str).apply(lambda c: c.isin(["FR", "LU", "DE"])).any(axis=1)].to_string())
for s in ["PECD1_IC1", "IC1_PECD1"]:
    d = r[s]; P(s); P(d[d.astype(str).apply(lambda c: c.isin(["FR", "LU", "DE", "UK"])).any(axis=1)].to_string())
P("NUTS3_IC1 targets", r["NUTS3_IC1"]["target"].value_counts().to_dict())
r2 = pd.read_excel(E + "region_transformation_IC1.xlsx", sheet_name="NUTS3_IC1")
P("europe/region_transformation_IC1 NUTS3_IC1 targets", r2["target"].value_counts().to_dict())
o.close()
