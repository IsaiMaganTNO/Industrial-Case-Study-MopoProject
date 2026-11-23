import pandas as pd
x=r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx"
df=pd.read_excel(x,sheet_name="ind_process_routes_co2_emission")
m=df[df["Industry"].astype(str).str.contains("alumin|alumina",case=False)]
print(m[["Industry","emission","unit","2030","2040","2050"]].to_string(index=False))
