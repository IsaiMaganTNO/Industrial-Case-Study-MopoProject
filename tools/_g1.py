import pandas as pd
p = "data/Gas/Gas_Sectors_Dataset_IC1_placeholder.xlsx"
xl = pd.ExcelFile(p)
print("sheets:", xl.sheet_names)
