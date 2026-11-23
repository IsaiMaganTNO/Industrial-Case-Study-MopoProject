import pandas as pd
d=pd.ExcelFile(r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx").parse("ind_process_routes_co2_emission")
for n in ["CEM2-(Afm)","CEM2-(Afm)MEA","LC3-(Afm)MEA","(NG)DRI-EAF","REF-SMR"]:
    r=d[d["Industry"].astype(str)==n]
    if len(r): print("%-16s to_node=%-22s unit=%-14s 2050=%.4f"%(
        n,r.iloc[0]["to_node"],r.iloc[0]["unit"],r.iloc[0]["2050"]))
    else: print("%-16s NOT IN SHEET"%n)
