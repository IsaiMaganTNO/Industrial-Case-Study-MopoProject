import geopandas as gpd, json, os
for p in [r"geodata/IC1.geojson", r"verification/IC_NWEU.geojson"]:
    g = gpd.read_file(p)
    print("==", p, os.path.getsize(p), "feat", len(g), "cols", list(g.columns))
    print(g.groupby("level").id.apply(list).to_string())
    print("crs", g.crs)
cfgs = [r"data-pipelines/europe/_power/config.json"]
for c in cfgs:
    if os.path.exists(c):
        d=json.load(open(c))
        print("geolevel =", d.get("geolevel"))
