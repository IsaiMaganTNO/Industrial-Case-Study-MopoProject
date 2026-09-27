import pandas as pd
p = "data/Gas/Gas_Sectors_Dataset_IC1_placeholder.xlsx"
df = pd.read_excel(p, sheet_name="Technology_Costs")
print("cols:", list(df.columns))
print("shape:", df.shape)
c0 = df.columns[0]
m = df[df[c0].astype(str).str.contains("diges", case=False, na=False)]
print(m.to_string())
