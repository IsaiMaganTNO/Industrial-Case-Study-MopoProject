import pandas as pd
xl = pd.ExcelFile("data-pipelines/europe/_ines-builder/region_transformation.xlsx")
need = ["PECD2_PECD1", "PECD1_PECD2", "PECD2_IC1", "IC1_PECD2",
        "PECD2_NUTS3", "NUTS3_PECD2", "PECD1_IC1", "IC1_PECD1"]
print("%-14s %s" % ("sheet", "present"))
for s in need:
    print("%-14s %s" % (s, "YES" if s in xl.sheet_names else "** MISSING **"))
print()
d = xl.parse("PECD1_IC1")
print("PECD1_IC1 shape:", d.shape, list(d.columns))
sub = d[d.source.astype(str).str.startswith(("DE","DK","NO","UK"))]
print("rows DE/DK/NO/UK as source:", len(sub))
print(sub.head(10).to_string())
