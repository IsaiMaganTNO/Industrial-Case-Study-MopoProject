import geopandas as gpd
g = gpd.read_file(r"data/geodata/onshore_plus_ic.geojson")
print("features", len(g), "cols", list(g.columns), "crs", g.crs)
print(g.groupby("level").size().to_string())
for lv in sorted(set(g["level"])):
    ids = sorted(g[g.level==lv]["id"].astype(str))
    print("\nLEVEL %s n=%d" % (lv, len(ids)))
    print("  ", ids[:40])
    print("   targets present:", [i for i in ids if i in ("DE","DK","NO","UK")])
