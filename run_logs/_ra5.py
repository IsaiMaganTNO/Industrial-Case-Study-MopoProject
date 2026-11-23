import pandas as pd
p = r"data-pipelines/europe/_ines-builder/region_transformation.xlsx"
m = pd.read_excel(p,"OFF3_map")
sel = m[m.PECD1.isin(["DE","DK","NO","UK","BE","NL"])]
print(sel[["source","PECD1","IC1"]].to_string())
for s in ["PECD1_IC1","IC1_PECD1"]:
    d = pd.read_excel(p,s)
    print("==",s,list(d.columns),len(d))
    print(d.head(8).to_string())
    print(d[d.source.astype(str).isin(["DE","DK","NO","UK"])|d.target.astype(str).isin(["DE","DK","NO","UK"])].to_string())
