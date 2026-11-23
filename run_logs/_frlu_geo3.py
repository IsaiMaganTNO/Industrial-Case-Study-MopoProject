import json, copy
a = json.load(open(r"geodata\IC1_NWEU.geojson", encoding="utf8")); b = json.load(open(r"verification\BE_NL_IC1_NWEU_w_FR_LU.geojson", encoding="utf8"))
tmpl = a["features"][17]["properties"]
for f in b["features"]:
    if f["properties"]["id"] in ("FR", "LU"):
        p = f["properties"]; n = copy.deepcopy(f)
        n["properties"] = {"id": p["id"], "cluster_id": None, "country": p["country"], "level": "IC1", "uuid": p["uuid"], "area_km2": None, "per_km2": p["per_km2"]}
        a["features"].append(n)
a["name"] = "IC1_NWEU_FRLU"
json.dump(a, open(r"geodata\IC1_NWEU_FRLU.geojson", "w", encoding="utf8"))
c = json.load(open(r"geodata\IC1_NWEU_FRLU.geojson", encoding="utf8")); print(len(c["features"]), [f["properties"]["id"] for f in c["features"]])
