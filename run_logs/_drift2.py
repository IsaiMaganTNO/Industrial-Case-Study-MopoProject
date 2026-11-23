import sqlite3, collections, re
pairs = [("OLD", "backups/spinetoolbox-items-pre-mixedres/items/ines_db/INES_DB.sqlite"),
         ("NEW", ".spinetoolbox/items/ines_db/INES_DB.sqlite")]
res = {}
for tag, p in pairs:
    c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
    rows = c.execute("""SELECT e.name FROM entity e JOIN entity_class ec
                        ON ec.id=e.class_id WHERE ec.name='unit'""").fetchall()
    c.close()
    ex = [r[0] for r in rows if "-existing_" in r[0]]
    fam = collections.Counter(n.split("-existing_")[0] for n in ex)
    res[tag] = (len(rows), len(ex), fam)
    print(tag, "units total", len(rows), "existing", len(ex))
print()
print("%-22s %6s %6s %6s" % ("existing family", "OLD", "NEW", "diff"))
keys = sorted(set(res["OLD"][2]) | set(res["NEW"][2]))
for k in keys:
    a = res["OLD"][2].get(k, 0); b = res["NEW"][2].get(k, 0)
    print("%-22s %6d %6d %+6d %s" % (k, a, b, b - a, "" if a == b else "<<<"))
