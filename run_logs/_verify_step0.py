import sqlite3, hashlib

def fp(p):
    c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
    e = c.execute("SELECT count(*) FROM entity").fetchone()[0]
    v = c.execute("SELECT count(*) FROM parameter_value").fetchone()[0]
    ents = sorted(c.execute("""SELECT ec.name, e.name FROM entity e
          JOIN entity_class ec ON ec.id=e.class_id""").fetchall())
    ex = sorted(x[1] for x in ents if x[0] == "unit" and "-existing_" in x[1])
    c.close()
    return e, v, ents, ex

base = "backups/spinetoolbox-items-pre-mixedres/items/ines_db/INES_DB.sqlite"
cur = ".spinetoolbox/items/ines_db/INES_DB.sqlite"
be, bv, bents, bex = fp(base)
ce, cv, cents, cex = fp(cur)

print("BASELINE (vre15 fleet) : entity %5d  pval %5d  existing-units %3d" % (be, bv, len(bex)))
print("UNPINNED drift run     : entity 14982  pval 21008  existing-units 205")
print("PINNED rebuild (now)   : entity %5d  pval %5d  existing-units %3d" % (ce, cv, len(cex)))
print()
print("entity count match :", "PASS" if ce == be else "FAIL")
print("pval   count match :", "PASS" if cv == bv else "FAIL")
print("existing-unit SET  :", "PASS" if cex == bex else "FAIL")
print("FULL entity SET    :", "PASS" if cents == bents else "FAIL")
if cents != bents:
    a, b = set(bents), set(cents)
    print("   added  :", sorted(b - a)[:8])
    print("   removed:", sorted(a - b)[:8])
print()
for probe in ["nuclear-3-existing_NLC7", "SCPC-existing_NLC7",
              "CCGT-existing_BEC4", "CCGT-existing_NLC1"]:
    print("  %-26s baseline=%-5s rebuilt=%s" % (probe, probe in bex, probe in cex))
