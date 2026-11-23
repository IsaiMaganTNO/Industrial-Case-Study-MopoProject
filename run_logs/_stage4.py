import pandas as pd
p = "data-pipelines/europe/_ines-builder/region_transformation.xlsx"
xl = pd.ExcelFile(p)
print("sheets:", len(xl.sheet_names))
hit = [s for s in xl.sheet_names if "PECD2" in s or "PECD1" in s]
print("PECD sheets:", hit)
for s in ["PECD2_PECD1"]:
    if s in xl.sheet_names:
        d = xl.parse(s)
        print()
        print("===", s, d.shape)
        print("columns:", list(d.columns))
        sub = d[d.iloc[:, 1].astype(str).str.startswith(("DE", "DK", "NO", "UK"))]
        print("rows for DE/DK/NO/UK:", len(sub))
        print(sub.head(25).to_string())
