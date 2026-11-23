import pandas as pd
x=pd.ExcelFile(r"data-pipelines\europe\region_transformation_IC1.xlsx")
d=x.parse("NUTS3_IC1")
print(d.shape, list(d.columns)); print(d.head(4).to_string())
print("\nderived nuts2 -> targets (BE/NL):")
d["n2"]=d["source"].astype(str).str[:4]
g=d.groupby("n2")["target"].nunique()
print("nuts2 count:",len(g)," multi-target:",(g>1).sum())
print(d.groupby("n2")["target"].apply(lambda s:sorted(set(s))).head(12).to_string())
