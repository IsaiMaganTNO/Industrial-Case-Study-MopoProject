import pandas as pd
p = r"data-pipelines/europe/_ines-builder/region_transformation.xlsx"
x = pd.ExcelFile(p)
print(x.sheet_names)
off = pd.read_excel(p,"OFF3")
print("OFF3 cols",list(off.columns),"rows",len(off))
print(off[off.country.isin(["DE","DK","NO","UK","BE","NL"])].groupby("country").size())
m = pd.read_excel(p,"OFF3_map")
print("OFF3_map cols",list(m.columns),"rows",len(m))
print(m.head(10).to_string())
