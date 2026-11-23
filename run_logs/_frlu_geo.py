import json, glob
for p in glob.glob(r"geodata\*.geojson") + glob.glob(r"**\BE_NL_IC1_NWEU_w_FR_LU.geojson", recursive=True):
    g = json.load(open(p, encoding="utf8")); f = g["features"]
    keys = list(f[0]["properties"].keys())
    ids = [str(x["properties"].get("id", x["properties"].get(keys[0]))) for x in f]
    print(p, len(f), keys[:5], ids[:30])
