import pandas as pd
f=r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx"
x=pd.ExcelFile(f)
for sh in ["ind_process_routes_co2_emission","ind_process_routes_co2_capture"]:
    d=x.parse(sh)
    al=d[d.apply(lambda r:r.astype(str).str.contains("alumin",case=False).any(),axis=1)]
    print("%-36s aluminium rows=%d"%(sh,len(al)))
    if len(al): print(al.to_string()[:600])
    print("   sector_ids:",sorted(d["sector_id"].astype(str).unique())[:20])
