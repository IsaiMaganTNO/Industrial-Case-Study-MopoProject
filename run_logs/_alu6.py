import pandas as pd
x=r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx"
df=pd.read_excel(x,sheet_name="ind_process_routes_co2_emission")
print("emission row types:",sorted(set(df["emission"].astype(str))))
cap=df[df["emission"].astype(str)=="co2_capture"]
print("co2_capture rows:",len(cap))
print("any aluminium capture:",len(cap[cap["Industry"].astype(str).str.contains("alumin",case=False)]))
e=df[df["emission"].astype(str)=="co2_emission"]
alt=e[e["Industry"].astype(str).str.contains("alternative")].copy()
ref=e[e["Industry"].astype(str).str.contains("-reference")].copy()
ref["k"]=ref["Industry"].str.replace("-reference","",regex=False)
alt["k"]=alt["Industry"].str.replace("-alternative","",regex=False)
m=alt.merge(ref,on="k",suffixes=("_alt","_ref"))
m["cut"]=100*(1-m["2050_alt"]/m["2050_ref"].replace(0,float("nan")))
print("\n%-44s %9s %9s %7s"%("family","ref2050","alt2050","cut%"))
for _,r in m.sort_values("cut").iterrows():
    print("%-44s %9.4f %9.4f %7.1f"%(r["k"][:44],r["2050_ref"],r["2050_alt"],r["cut"]))
