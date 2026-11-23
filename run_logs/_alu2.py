import pandas as pd
x=r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx"
df=pd.read_excel(x,sheet_name="ind_process_routes_co2_emission")
print("cols:",list(df.columns))
m=df[df.apply(lambda r: r.astype(str).str.contains("alumin",case=False).any(),axis=1)]
print(m.to_string())
