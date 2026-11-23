import pandas as pd
o=pd.ExcelFile(r"backups\data-pre-mixedres\Gas\Gas_Sectors_Dataset.xlsx")
n=pd.ExcelFile(r"data\Gas\Gas_Sectors_Dataset.xlsx")
print("OLD",o.sheet_names); print("NEW",n.sheet_names)
for s in o.sheet_names:
    if s not in n.sheet_names: print("gone",s); continue
    a=o.parse(s); b=n.parse(s)
    print("%-30s old%s new%s %s"%(s,a.shape,b.shape,"SAME" if a.equals(b) else "DIFFERS"))
