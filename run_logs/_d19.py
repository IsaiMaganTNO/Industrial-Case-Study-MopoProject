import pandas as pd
NEW=r"verification\Data - IC1 and PECD1\Industry\technology_catalogue_ind_nuts0_nuts3_update.xlsx"
OLD=r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx"
a=pd.read_excel(NEW,sheet_name="ind_process_routes_co2_capture")
b=pd.read_excel(OLD,sheet_name="ind_process_routes_co2_capture")
print("NEW cols:",list(a.columns))
key=a.columns[0]
sa,sb=set(a[key].astype(str)),set(b[key].astype(str))
print("\nroutes only in NEW:",sorted(sa-sb))
print("routes only in OLD:",sorted(sb-sa))
print("\nNEW head:"); print(a.head(6).to_string()[:700])
