import geopandas as gpd, json
cfg=json.load(open(r"data/Energy_Conversion/config.json"))
geolevel=cfg["geolevel"]
print("config geolevel:", geolevel)
for p in [r"geodata/IC1.geojson", r"geodata/IC1_NWEU.geojson"]:
    g=gpd.read_file(p)
    f=g[g["level"]==geolevel]                 # exactly power_DB.py L116
    regions=f["id"].to_list()                 # exactly L117
    print("%-30s total=%-3d after filter=%-3d" % (p,len(g),len(f)))
    print("    regions:", regions)
