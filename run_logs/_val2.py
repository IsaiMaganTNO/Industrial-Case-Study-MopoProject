import pandas as pd,sqlite3,re
d=pd.ExcelFile(r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx").parse("ind_process_routes_co2_emission")
fams=["aluminium-primary-production-reference","ceramics-and-other-non-metalic-minerals-production",
"food-beverages-tobacco-production-reference","leather-and-textile-production-reference",
"machinery-equipment-production-reference","other-chemicals-production-reference",
"other-industrial-sectors_production-reference","other-non-ferrous-metals-production-reference",
"paper-production-reference","pharmaceuticals-production-reference",
"printing-and-media-production-reference","pulp-production-reference",
"transport-equipment-production-reference","wood-and-wood-products_production-reference","(LN+EL)O"]
print("%-50s %-24s %-12s %s"%("family","to_node","unit","2050"))
for f in fams:
    r=d[d["Industry"].astype(str)==f]
    if len(r):
        print("%-50s %-24s %-12s %.4f"%(f[:50],r.iloc[0]["to_node"],r.iloc[0]["unit"],r.iloc[0]["2050"]))
    else: print("%-50s MISSING"%f[:50])
print()
print("distinct units col:",d["unit"].unique())
