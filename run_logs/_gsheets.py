import pandas as pd
pd.set_option("display.width",200)
f=r"data\Gas\Gas_Sectors_Dataset_IC1_placeholder.xlsx"
xl=pd.ExcelFile(f)
for s in ["CH4_Storage","Technology_Costs","Technology_Conversion"]:
    d=xl.parse(s)
    print("#"*90); print(s, d.shape, list(d.columns))
    print(d.head(12).to_string()[:2000])
