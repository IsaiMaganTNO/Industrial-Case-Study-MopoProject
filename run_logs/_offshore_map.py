import geopandas as gpd, pandas as pd
o = gpd.read_file(r"geodata\offshore.geojson"); print(o.columns.tolist())
o = o[o.iloc[:, 0].astype(str).str.contains("NSNL0|NSBE0") | o.apply(lambda r: any("NSNL0" in str(x) or "NSBE0" in str(x) for x in r.values), axis=1)]
o["lon"], o["lat"] = o.geometry.to_crs(3035).centroid.to_crs(4326).x, o.geometry.to_crs(3035).centroid.to_crs(4326).y
print(o.drop(columns="geometry").round(2).to_string())
x = pd.ExcelFile(r"data-pipelines\europe\_ines-builder\region_transformation.xlsx"); print(x.sheet_names)
for sh in x.sheet_names:
    d = x.parse(sh).astype(str)
    m = d[d.apply(lambda r: r.str.contains("NSNL0|NSBE0").any(), axis=1)]
    if len(m): print("==", sh); print(m.head(20).to_string())
