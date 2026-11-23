import json
a = json.load(open(r"geodata\IC1_NWEU.geojson", encoding="utf8")); b = json.load(open(r"verification\BE_NL_IC1_NWEU_w_FR_LU.geojson", encoding="utf8"))
print("A top keys", [k for k in a if k != "features"], a.get("crs"))
print("B top keys", [k for k in b if k != "features"], b.get("crs"))
for f in a["features"][16:]: print("A", f["properties"], f["geometry"]["type"])
for f in b["features"]: print("B", f["properties"], f["geometry"]["type"])
