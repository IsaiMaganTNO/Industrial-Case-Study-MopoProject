import sqlite3, hashlib

def vals(p):
    c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
    r = sorted(c.execute("""SELECT pd.name, e.name, a.name, pv.value
          FROM parameter_value pv
          JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
          JOIN entity e ON e.id=pv.entity_id
          JOIN alternative a ON a.id=pv.alternative_id""").fetchall())
    c.close()
    return r

base = "backups/spinetoolbox-items-pre-mixedres/items/ines_db/INES_DB.sqlite"
cur = ".spinetoolbox/items/ines_db/INES_DB.sqlite"
a, b = vals(base), vals(cur)
print("baseline rows %d md5 %s" % (len(a), hashlib.md5(repr(a).encode()).hexdigest()[:12]))
print("rebuilt  rows %d md5 %s" % (len(b), hashlib.md5(repr(b).encode()).hexdigest()[:12]))
print("ALL PARAMETER VALUES IDENTICAL:", "PASS" if a == b else "FAIL")
if a != b:
    da = {(x[0], x[1], x[2]): x[3] for x in a}
    db_ = {(x[0], x[1], x[2]): x[3] for x in b}
    diff = [k for k in set(da) & set(db_) if da[k] != db_[k]]
    print("differing shared keys:", len(diff))
    import collections
    print("by parameter:", collections.Counter(k[0] for k in diff).most_common(12))
    for k in diff[:6]:
        print("   ", k[0], "|", k[1][:34])
