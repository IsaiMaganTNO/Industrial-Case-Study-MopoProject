import pandas as pd
f=r"data\Gas\Gas_Sectors_Dataset_IC1_placeholder.xlsx"
xl=pd.ExcelFile(f)
print("sheets:",xl.sheet_names)
for s in xl.sheet_names:
    d=xl.parse(s)
    if any(("LNG" in str(c) or "extract" in str(c).lower()) for c in d.columns) or d.astype(str).apply(lambda col: col.str.contains("LNG|extraction",case=False,na=False)).any().any():
        print("---",s, d.shape, list(d.columns)[:12])
        print(d.head(20).to_string()[:1800])
