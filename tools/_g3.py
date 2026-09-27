import pandas as pd
p = "data/Gas/Gas_Sectors_Dataset_IC1_placeholder.xlsx"
df = pd.read_excel(p, sheet_name="Technology_Costs")
pd.set_option("display.width", 200)
print(df[["technologie","commodity","capex 2030 (M€/MW)","fom 2030 (€/MW/y)","vom 2030 (€/MWh)","lifetime"]].to_string())
