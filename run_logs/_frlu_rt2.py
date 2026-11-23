import pandas as pd
d = pd.read_excel(r"data-pipelines\europe\_ines-builder\region_transformation.xlsx", sheet_name="OFF3_map")
print(d[d.PECD1.isin(["DE","DK","NO","UK","BE","NL"])].to_string())
print(pd.read_excel(r"data-pipelines\europe\_ines-builder\region_transformation.xlsx", sheet_name="IC1").id.tolist())
