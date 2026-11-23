import sqlite3
def units(p, like="%-existing_%"):
    c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
    r = c.execute("""SELECT e.name FROM entity e JOIN entity_class ec
                     ON ec.id=e.class_id WHERE ec.name='unit' AND e.name LIKE ?""",
                  (like,)).fetchall()
    c.close()
    return {x[0] for x in r}
v = units("checkpoints/Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite")
print("vre15 existing units:", len(v))
# the two candidate fleets, as seen in INES_DB
old = units("backups/spinetoolbox-items-pre-mixedres/items/ines_db/INES_DB.sqlite")
new = units(".spinetoolbox/items/ines_db/INES_DB.sqlite")
print("INES backup(OLD random draw):", len(old))
print("INES current(2nd random draw):", len(new))
print()
print("vre15 == backup fleet ?", v == old)
print("vre15 == current fleet ?", v == new)
print("vre15 - backup :", sorted(v - old)[:6])
print("backup - vre15 :", sorted(old - v)[:6])
# key probes
for probe in ["nuclear-3-existing_NLC7", "SCPC-existing_NLC7",
              "CCGT-existing_BEC4", "CCGT-existing_NLC1"]:
    print("  %-28s vre15=%-5s backup=%-5s current=%s" %
          (probe, probe in v, probe in old, probe in new))
