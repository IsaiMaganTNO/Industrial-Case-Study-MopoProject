import pandas as pd
x=pd.ExcelFile(r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx")
print("sheets:",x.sheet_names)
for s in ["ind_production_30_50_nuts3","ind_production_30_50_nuts0"]:
    d=x.parse(s)
    print("\n--",s,d.shape,list(d.columns)[:6])
    col=[c for c in d.columns if str(c).lower() in ("nuts3","country_code","nuts0")]
    print("   region cols:",col)
    for c in col:
        v=sorted(set(d[c].astype(str)))
        pre=sorted(set(z[:2] for z in v))
        print("   %s n=%d prefixes=%s"%(c,len(v),pre[:40]))
