import sqlite3
pairs = [("INES_DB",
          "backups/spinetoolbox-items-pre-mixedres/items/ines_db/INES_DB.sqlite",
          ".spinetoolbox/items/ines_db/INES_DB.sqlite"),
         ("SpineOpt_target",
          "backups/spinetoolbox-items-pre-mixedres/items/spineopt_target/SpineOpt_target.sqlite",
          ".spinetoolbox/items/spineopt_target/SpineOpt_target.sqlite")]
q = """SELECT ec.name, e.name FROM entity e
       JOIN entity_class ec ON ec.id = e.class_id"""
for tag, old, new in pairs:
    print("=" * 70)
    print(tag)
    a = sqlite3.connect("file:%s?mode=ro" % old, uri=True)
    b = sqlite3.connect("file:%s?mode=ro" % new, uri=True)
    sa = set(a.execute(q).fetchall())
    sb = set(b.execute(q).fetchall())
    a.close(); b.close()
    add = sb - sa
    rem = sa - sb
    print("  ADDED  %d" % len(add))
    for c, n in sorted(add):
        print("     +", c, "|", n)
    print("  REMOVED %d" % len(rem))
    for c, n in sorted(rem):
        print("     -", c, "|", n)
