import pandas as pd,glob
f=r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx"
xl=pd.ExcelFile(f)
print("sheets:",[s for s in xl.sheet_names if "co2" in s.lower() or "emis" in s.lower()])
d=xl.parse("ind_process_routes_co2_emission")
print("cols:",list(d.columns)[:8],"rows:",len(d))
c0=d.columns[0]
pats=["alumin","leather","machinery","other-chemicals","printing","transport-equipment",
      "food","pharma","wood","pulp","ceramics","paper","other-industrial","non-ferrous"]
for p in pats:
    sub=d[d[c0].astype(str).str.contains(p,case=False,na=False)]
    print("   %-22s rows=%d  %s"%(p,len(sub),list(sub[c0].head(3))))
