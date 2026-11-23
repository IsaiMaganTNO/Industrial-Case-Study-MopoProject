import pandas as pd
full=r"data/Gas/Gas_Sectors_Dataset.xlsx"
s=pd.read_excel(full,"Technology_Conversion")
bad=s[s[["2030","2040","2050"]].isna().any(axis=1)]
print("Technology_Conversion rows with NaN years:", len(bad))
print(bad.to_string())
# gas_import tech_conversion uses row.iloc[3..5]; check it guards
import re
src=open(r"data-pipelines/europe/_gas/gas_import.py",encoding="utf-8").read()
i=src.find("def tech_conversion")
print("\n---- tech_conversion body ----")
print(src[i:i+1200])
