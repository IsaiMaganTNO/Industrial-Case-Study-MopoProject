import json, collections
p = r"verification/IC_NWEU.geojson"
d = json.load(open(p, encoding="utf-8"))
print("type", d.get("type"))
fs = d.get("features", [])
print("features", len(fs))
keys = collections.Counter()
for f in fs:
    for k in (f.get("properties") or {}):
        keys[k] += 1
print("property keys:", dict(keys))
geoms = collections.Counter(f.get("geometry", {}).get("type") for f in fs)
print("geom types:", dict(geoms))
print("--- first 3 features ---")
for f in fs[:3]:
    print(json.dumps(f.get("properties"), ensure_ascii=False))
