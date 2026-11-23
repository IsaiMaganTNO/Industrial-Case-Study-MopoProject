import pandas as pd
p = r"data-pipelines/europe/_ines-builder/region_transformation.xlsx"
x = pd.ExcelFile(p)
print("SHEETS", len(x.sheet_names))
ic1 = pd.read_excel(p, "IC1")
print("IC1 cols", list(ic1.columns), "rows", len(ic1))
print(ic1.to_string())
p1 = pd.read_excel(p, "PECD1")
print("PECD1 cols", list(p1.columns), "rows", len(p1))
sel = p1[p1.iloc[:,0].astype(str).isin(["DE","DK","NO","UK"])]
print(sel.to_string())
