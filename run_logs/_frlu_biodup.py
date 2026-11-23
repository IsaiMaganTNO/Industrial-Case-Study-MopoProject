import pandas as pd
b = pd.read_excel(r"backups/pre-frlu/region_transformation_IC1.xlsx.pre-frlu", sheet_name="NUTS3_IC1")
n = pd.read_excel(r"data-pipelines/europe/region_transformation_IC1.xlsx", sheet_name="NUTS3_IC1")
print("dups before", b.source.duplicated().sum(), "after", n.source.duplicated().sum())
print("new rows dup?", n.iloc[len(b):].source.isin(b.source).sum())
print(b[b.source.duplicated(keep=False)].sort_values("source").head(6).to_string())
