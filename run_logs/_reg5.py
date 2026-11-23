import pandas as pd
xl = pd.ExcelFile("data-pipelines/europe/_ines-builder/region_transformation.xlsx")
print("all sheets:", xl.sheet_names)
print()
for s in ["PECD1", "PECD2"]:
    d = xl.parse(s)
    print("=== %s shape=%s cols=%s" % (s, d.shape, list(d.columns)))
    if "country" in d.columns:
        for c in ["DE","DK","NO","UK","BE","NL"]:
            ids = d[d.country == c].id.tolist()
            print("   %-3s n=%2d %s" % (c, len(ids), ids[:9]))
