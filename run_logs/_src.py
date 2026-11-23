import pandas as pd
p=r"data-pipelines\europe\_ines-builder\CO2_data_IC1.xlsx"
xl=pd.ExcelFile(p)
print("SHEETS:",xl.sheet_names)
for s in xl.sheet_names:
    d=xl.parse(s)
    print(f"\n=== {s}  shape={d.shape}")
    print("cols:",list(d.columns))
    print(d.head(12).to_string()[:1800])
