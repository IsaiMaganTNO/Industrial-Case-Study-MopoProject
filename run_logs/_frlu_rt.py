import pandas as pd
x = pd.read_excel(r"data-pipelines\europe\_ines-builder\region_transformation.xlsx", sheet_name=None)
for k, d in x.items(): print(k, d.shape, list(d.columns)[:8])
for k, d in x.items():
    if k.endswith("_map"):
        print("==", k); print(d[d.isna().any(axis=1)].head(20).to_string())
        print(d[d.astype(str).apply(lambda r: r.str.contains("FR|LU").any(), axis=1)].to_string())
