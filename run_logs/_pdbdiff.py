import sqlite3
def dump(p):
    c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
    rows = c.execute("""SELECT pd.name, ec.name, e.name, a.name, pv.value, pv.type
                   FROM parameter_value pv
                   JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
                   JOIN entity e ON e.id=pv.entity_id
                   JOIN entity_class ec ON ec.id=e.class_id
                   JOIN alternative a ON a.id=pv.alternative_id""").fetchall()
    c.close()
    return {(r[0], r[1], r[2], r[3]): (r[4], r[5]) for r in rows}
o = dump("backups/spinetoolbox-items-pre-mixedres/items/power_db/power_db.sqlite")
n = dump(".spinetoolbox/items/power_db/power_db.sqlite")
print("keys old %d new %d  same keyset %s" % (len(o), len(n), set(o) == set(n)))
diff = [k for k in o if k in n and o[k] != n[k]]
print("CHANGED VALUES:", len(diff))
for k in diff[:25]:
    a = o[k][0]; b = n[k][0]
    sa = a.decode("utf-8", "replace")[:46] if isinstance(a, bytes) else str(a)[:46]
    sb = b.decode("utf-8", "replace")[:46] if isinstance(b, bytes) else str(b)[:46]
    print("  %s | %s | %s" % (k[0], k[2][:28], k[3]))
    print("      OLD", sa)
    print("      NEW", sb)
