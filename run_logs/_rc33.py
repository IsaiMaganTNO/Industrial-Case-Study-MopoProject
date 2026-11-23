import pandas as pd
pd.set_option("display.width",260); pd.set_option("display.max_columns",30)
for s in ["Technology_Conversion","Technology_Costs"]:
    a=pd.read_excel(r"backups\data-pre-mixedres\Gas\Gas_Sectors_Dataset.xlsx",sheet_name=s)
    b=pd.read_excel(r"data\Gas\Gas_Sectors_Dataset.xlsx",sheet_name=s)
    print("=====",s,"OLD"); print(a.iloc[:,:6].to_string())
    print("=====",s,"NEW"); print(b.iloc[:,:6].to_string())
