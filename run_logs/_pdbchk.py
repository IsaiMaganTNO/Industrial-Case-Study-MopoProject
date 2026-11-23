import sqlite3, hashlib
def dump(p):
    c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
    ents = sorted(c.execute("""SELECT ec.name, e.name FROM entity e
                   JOIN entity_class ec ON ec.id=e.class_id""").fetchall())
    vals = sorted(c.execute("""SELECT pd.name, e.name, pv.value
                   FROM parameter_value pv
                   JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
                   JOIN entity e ON e.id=pv.entity_id""").fetchall())
    c.close()
    h = hashlib.md5(repr(ents).encode()).hexdigest()[:12]
    hv = hashlib.md5(repr(vals).encode()).hexdigest()[:12]
    return ents, vals, h, hv

old = "backups/spinetoolbox-items-pre-mixedres/items/power_db/power_db.sqlite"
new = ".spinetoolbox/items/power_db/power_db.sqlite"
eo, vo, ho, hvo = dump(old)
en, vn, hn, hvn = dump(new)
print("OLD entities %d md5 %s | values %d md5 %s" % (len(eo), ho, len(vo), hvo))
print("NEW entities %d md5 %s | values %d md5 %s" % (len(en), hn, len(vn), hvn))
print("ENTITIES IDENTICAL:", eo == en)
print("VALUES   IDENTICAL:", vo == vn)
