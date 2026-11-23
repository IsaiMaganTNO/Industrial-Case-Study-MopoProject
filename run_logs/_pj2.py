import json, collections
d = json.load(open(".spinetoolbox/project.json", encoding="utf-8"))
items = d.get("items", {})
print("items", len(items))
print("types:", dict(collections.Counter(v.get("type") for v in items.values())))
print()
print("=== Data Stores: url/path ===")
for n, v in sorted(items.items()):
    if v.get("type") == "Data Store":
        u = v.get("url", {})
        db = u.get("database")
        if isinstance(db, dict):
            db = db.get("path", db)
        print("%-24s %-10s %s" % (n[:24], u.get("dialect"), db))
