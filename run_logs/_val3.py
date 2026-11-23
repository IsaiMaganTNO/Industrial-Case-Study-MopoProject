import pandas as pd
d=pd.ExcelFile(r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx").parse("ind_process_routes_co2_emission")
s=d[d["Industry"].astype(str).str.contains("ceramic",case=False,na=False)]
print(s[["Industry","to_node","unit","2050"]].to_string())
