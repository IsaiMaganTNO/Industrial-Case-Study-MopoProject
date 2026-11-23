import pandas as pd
for tag,p in [("OLD",r"backups\data-pre-mixedres\Energy_Conversion\assumptions.xlsx"),("NEW",r"data\Energy_Conversion\assumptions.xlsx")]:
    x=pd.ExcelFile(p); print(tag,"sheets:",x.sheet_names)
old=pd.ExcelFile(r"backups\data-pre-mixedres\Energy_Conversion\assumptions.xlsx")
new=pd.ExcelFile(r"data\Energy_Conversion\assumptions.xlsx")
for s in old.sheet_names:
    if s not in new.sheet_names: print("sheet gone:",s); continue
    a=old.parse(s); b=new.parse(s)
    print("sheet %-28s old%s new%s %s"%(s,a.shape,b.shape,"SAME" if a.equals(b) else "DIFFERS"))
