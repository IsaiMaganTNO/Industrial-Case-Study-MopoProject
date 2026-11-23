import sqlite3, json
def dump(p):
    c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
    rows = c.execute("""SELECT pd.name, e.name, pv.value FROM parameter_value pv
                   JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
                   JOIN entity e ON e.id=pv.entity_id""").fetchall()
    c.close()
    return {(r[0], r[1]): r[2] for r in rows}
o = dump("backups/spinetoolbox-items-pre-mixedres/items/power_db/power_db.sqlite")
n = dump(".spinetoolbox/items/power_db/power_db.sqlite")
def parse(b):
    d = json.loads(b.decode("utf-8") if isinstance(b, bytes) else b)
    return {k: v for k, v in d["data"]}
diff = sorted(k for k in o if o[k] != n[k])
print("%-26s %-6s %12s %12s" % ("entity", "year", "OLD", "NEW"))
for k in diff:
    a, b = parse(o[k]), parse(n[k])
    for y in sorted(set(a) | set(b)):
        va, vb = a.get(y), b.get(y)
        if va != vb:
            print("%-26s %-6s %12.4f %12.4f" % (k[1][:26], y, va or 0, vb or 0))
