import sqlite3, json, collections
def dump(p):
    c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
    rows = c.execute("""SELECT pd.name, e.name, pv.value FROM parameter_value pv
                   JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
                   JOIN entity e ON e.id=pv.entity_id
                   WHERE pd.name='units_existing'""").fetchall()
    c.close()
    out = collections.defaultdict(float)
    fam = collections.defaultdict(float)
    for _, ent, val in rows:
        d = json.loads(val.decode("utf-8") if isinstance(val, bytes) else val)
        tech, reg = ent.split("__")
        ctry = reg[:2]
        for y, v in d["data"]:
            out[(ctry, y)] += (v or 0)
            fam[(tech.replace("-existing", ""), ctry, y)] += (v or 0)
    return out, fam
oa, of = dump("backups/spinetoolbox-items-pre-mixedres/items/power_db/power_db.sqlite")
na, nf = dump(".spinetoolbox/items/power_db/power_db.sqlite")
print("=== NATIONAL TOTAL existing capacity (MW) ===")
print("%-14s %12s %12s %10s" % ("country/year", "OLD", "NEW", "diff"))
for k in sorted(set(oa) | set(na)):
    a, b = oa.get(k, 0), na.get(k, 0)
    print("%-14s %12.1f %12.1f %+10.1f" % ("%s %s" % k, a, b, b - a))
print()
print("=== BY TECH (MW) ===")
print("%-22s %12s %12s %10s" % ("tech/ctry/year", "OLD", "NEW", "diff"))
for k in sorted(set(of) | set(nf)):
    a, b = of.get(k, 0), nf.get(k, 0)
    if abs(b - a) > 0.05:
        print("%-22s %12.1f %12.1f %+10.1f" % ("%s %s %s" % k, a, b, b - a))
