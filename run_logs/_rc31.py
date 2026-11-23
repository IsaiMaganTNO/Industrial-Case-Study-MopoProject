import pandas as pd
pd.set_option("display.width",250); pd.set_option("display.max_columns",30)
for s in ["technology","storage"]:
    a=pd.read_excel(r"backups\data-pre-mixedres\Energy_Conversion\assumptions.xlsx",sheet_name=s)
    b=pd.read_excel(r"data\Energy_Conversion\assumptions.xlsx",sheet_name=s)
    print("=====",s,"OLD"); print(a.iloc[:,:8].to_string())
    print("=====",s,"NEW"); print(b.iloc[:,:8].to_string())
