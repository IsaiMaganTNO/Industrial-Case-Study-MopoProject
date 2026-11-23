import pandas as pd, numpy as np
NEW=r"verification\Data - IC1 and PECD1\Industry\technology_catalogue_ind_nuts0_nuts3_update.xlsx"
OLD=r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx"
a=pd.ExcelFile(NEW); b=pd.ExcelFile(OLD)
print("NEW sheets:",a.sheet_names)
print("OLD sheets:",b.sheet_names)
print("only in NEW:",[s for s in a.sheet_names if s not in b.sheet_names])
print("only in OLD:",[s for s in b.sheet_names if s not in a.sheet_names])
for s in a.sheet_names:
    if s not in b.sheet_names: continue
    da,db=a.parse(s),b.parse(s)
    tag="SAME shape" if da.shape==db.shape else "DIFF shape"
    print(f"  {s:36} NEW{str(da.shape):12} OLD{str(db.shape):12} {tag}")
