import pandas as pd, numpy as np
NEW=r"verification\Data - IC1 and PECD1\Industry\technology_catalogue_ind_nuts0_nuts3_update.xlsx"
OLD=r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx"
KEYS=["sector_id","Industry","to_node","emission"]
a=pd.read_excel(NEW,sheet_name="ind_process_routes_co2_capture")
b=pd.read_excel(OLD,sheet_name="ind_process_routes_co2_capture")
m=a.merge(b,on=KEYS,suffixes=("_new","_old"),how="inner")
print("shared rows:",len(m))
diff=[]
for y in ["2025","2030","2040","2050"]:
    d=m[~np.isclose(m[y+"_new"].fillna(-9),m[y+"_old"].fillna(-9))]
    if len(d): diff.append((y,len(d)))
print("shared rows with CHANGED capture values:",diff if diff else "NONE - pure superset")
# production sheets
for s in ["ind_production_2018_nuts0","ind_production_30_50_nuts0"]:
    x=pd.read_excel(NEW,sheet_name=s); y=pd.read_excel(OLD,sheet_name=s)
    k=list(x.columns[:3])
    sx=set(map(tuple,x[k].astype(str).values)); sy=set(map(tuple,y[k].astype(str).values))
    print(f"\n{s}: only-NEW {len(sx-sy)} -> {sorted(sx-sy)[:6]}")
