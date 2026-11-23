import geopandas as gpd, pandas as pd
g = gpd.read_file(r"geodata/IC1.geojson")[["id","area_km2","per_km2"]]
x = pd.read_excel(r"data-pipelines/europe/_ines-builder/region_transformation.xlsx","IC1")
m = g.merge(x, on="id", suffixes=("_geo","_xls"))
m["d_area"] = (m.area_km2_geo - m.area_km2_xls).abs()
bad = m[m.d_area > 1.0]
print("regions where geojson and Excel area_km2 disagree by >1 km2:", len(bad))
print(bad[["id","area_km2_geo","area_km2_xls","per_km2_geo","per_km2_xls"]].to_string())
