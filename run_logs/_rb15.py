import pandas as pd
full=r"data/Gas/Gas_Sectors_Dataset.xlsx"; plc=r"data/Gas/Gas_Sectors_Dataset_IC1_placeholder.xlsx"
for s in ["H2_Network","Technology_Conversion"]:
    a=pd.read_excel(full,s); b=pd.read_excel(plc,s)
    print("==",s)
    print("  full cols:", list(a.columns))
    print("  plc  cols:", list(b.columns))
    print("  extra in full:", [c for c in a.columns if c not in b.columns])
    print("  extra in plc :", [c for c in b.columns if c not in a.columns])
a=pd.read_excel(full,"Technology_Conversion"); b=pd.read_excel(plc,"Technology_Conversion")
print("\nTechnology_Conversion full:"); print(a.head(25).to_string())
