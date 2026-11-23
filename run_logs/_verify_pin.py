import sqlite3, hashlib, json, collections
from spinedb_api import DatabaseMapping, from_database

def vals(p):
    c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
    r = sorted(c.execute("""SELECT pd.name, e.name, pv.value FROM parameter_value pv
        JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
        JOIN entity e ON e.id=pv.entity_id""").fetchall())
    c.close()
    return r

src = "backups/spinetoolbox-items-pre-mixedres/items/power_db/power_db.sqlite"
dst = ".spinetoolbox/items/power_db/power_db.sqlite"
a, b = vals(src), vals(dst)
print("baseline md5:", hashlib.md5(repr(a).encode()).hexdigest()[:12])
print("pinned   md5:", hashlib.md5(repr(b).encode()).hexdigest()[:12])
print("FULL Power_DB IDENTICAL:", a == b)

# Spine API read-back
with DatabaseMapping("sqlite:///" + dst) as db:
    rows = [x for x in db.query(db.parameter_value_sq)]
    pd_ = {x.id: x.name for x in db.query(db.parameter_definition_sq)}
    ent = {x.id: x.name for x in db.query(db.entity_sq)}
    tot = collections.defaultdict(float)
    n = 0
    for r in rows:
        if pd_.get(r.parameter_definition_id) != "units_existing":
            continue
        pv = from_database(r.value, r.type)
        name = ent[r.entity_id]
        tech, reg = name.split("__")
        n += 1
        for i, v in zip(pv.indexes, pv.values):
            tot[(reg[:2], str(i))] += float(v or 0)
print()
print("Spine API read OK, units_existing series:", n)
print("%-12s %12s" % ("key", "MW"))
for k in sorted(tot):
    print("%-12s %12.0f" % ("%s %s" % k, tot[k]))
