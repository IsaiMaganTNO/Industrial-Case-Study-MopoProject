import sqlite3, hashlib

def fp(p):
    c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
    e = c.execute("SELECT count(*) FROM entity").fetchone()[0]
    v = c.execute("SELECT count(*) FROM parameter_value").fetchone()[0]
    ents = sorted(c.execute("""SELECT ec.name, e.name FROM entity e
          JOIN entity_class ec ON ec.id=e.class_id""").fetchall())
    vals = sorted(c.execute("""SELECT pd.name, e.name, a.name, pv.value
          FROM parameter_value pv
          JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
          JOIN entity e ON e.id=pv.entity_id
          JOIN alternative a ON a.id=pv.alternative_id""").fetchall())
    c.close()
    return e, v, ents, vals

base = "backups/spinetoolbox-items-pre-mixedres/items/spineopt_target/SpineOpt_target.sqlite"
cur = ".spinetoolbox/items/spineopt_target/SpineOpt_target.sqlite"
be, bv, bents, bvals = fp(base)
ce, cv, cents, cvals = fp(cur)
print("BASELINE          : entity %5d  pval %5d" % (be, bv))
print("CONTAMINATED run  : entity 21034  pval 24877")
print("PINNED rebuild    : entity %5d  pval %5d" % (ce, cv))
print()
print("entity count  :", "PASS" if ce == be else "FAIL")
print("pval count    :", "PASS" if cv == bv else "FAIL")
print("entity SET    :", "PASS" if cents == bents else "FAIL")
print("baseline vals md5:", hashlib.md5(repr(bvals).encode()).hexdigest()[:12])
print("rebuilt  vals md5:", hashlib.md5(repr(cvals).encode()).hexdigest()[:12])
print("ALL VALUES    :", "PASS" if bvals == cvals else "FAIL")
if bvals != cvals:
    import collections
    da = {(x[0], x[1], x[2]): x[3] for x in bvals}
    db_ = {(x[0], x[1], x[2]): x[3] for x in cvals}
    diff = [k for k in set(da) & set(db_) if da[k] != db_[k]]
    print("  differing:", len(diff))
    print("  by param:", collections.Counter(k[0] for k in diff).most_common(10))
