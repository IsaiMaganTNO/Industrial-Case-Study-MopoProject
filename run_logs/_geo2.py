import json, collections
d = json.load(open(r"verification/IC_NWEU.geojson", encoding="utf-8"))
fs = d["features"]
rows = []
for f in fs:
    p = f["properties"]
    rows.append((p["id"], p["country"], p["cluster_id"], p["level"],
                 p["area_km2"], p["per_km2"]))
rows.sort(key=lambda r: (str(r[1]), str(r[0])))
for i, c, cl, lv, a, pk in rows:
    astr = "%12.1f" % a if isinstance(a, (int, float)) else "%12s" % "NULL"
    pstr = "%9.1f" % pk if isinstance(pk, (int, float)) else "%9s" % "NULL"
    print("%-6s %-3s %-24s %-10s %s %s" % (i, c, str(cl)[:24], lv, astr, pstr))
print()
print("by country:", dict(collections.Counter(str(r[1]) for r in rows)))
print("by level  :", dict(collections.Counter(str(r[3]) for r in rows)))
print("null area :", sum(1 for r in rows if r[4] is None))
print("unique ids:", len({r[0] for r in rows}), "of", len(rows))
print("crs       :", d.get("crs", "ABSENT -> assume EPSG:4326"))
