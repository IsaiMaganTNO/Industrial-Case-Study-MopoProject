import geopandas as gpd
off=gpd.read_file(r"geodata\offshore.geojson")
for r in off.itertuples():
    if r.id in ("NSNL012","NSNL031","NSUK011","NSUK012","NSUK041","NSUK042","NSUK052","ATUK031","NSDKW12"):
        p=r.geometry.representative_point(); print(r.id, round(p.x,2), round(p.y,2))
