import pandas as pd
x=r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx"
d=pd.read_excel(x,sheet_name="ind_process_routes_co2_capture")
print("rows:",len(d),"cols:",list(d.columns)[:8])
nz=d[d["2050"]>0]
print("non-zero 2050 capture rows:",len(nz))
print(nz[["Industry","to_node","unit","2050"]].head(14).to_string(index=False))
