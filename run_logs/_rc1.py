import pandas as pd
p=r"data-pipelines/europe/_ines-builder/region_transformation.xlsx"
d=pd.read_excel(p,"PECD2_PECD1")
print("cols",list(d.columns),"rows",len(d))
sel=d[d.target.astype(str).isin(["DE","DK","NO","UK"])]
print(sel.to_string())
print("\nsum of capacity per target:")
print(sel.groupby("target")[["capacity","potential","area","population"]].sum().to_string())
