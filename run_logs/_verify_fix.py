import sqlite3, hashlib, json, collections

def dump(p):
    c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
    ents = sorted(c.execute("""SELECT ec.name, e.name FROM entity e
                   JOIN entity_class ec ON ec.id=e.class_id""").fetchall())
    vals = sorted(c.execute("""SELECT pd.name, e.name, pv.value
                   FROM parameter_value pv
                   JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
                   JOIN entity e ON e.id=pv.entity_id""").fetchall())
    c.close()
    return ents, vals

paths = {
 "PRE_backup": "backups/spinetoolbox-items-pre-mixedres/items/power_db/power_db.sqlite",
 "FIX_run1":   "run_logs/power_db.fix_run1.sqlite",
 "FIX_run2":   ".spinetoolbox/items/power_db/power_db.sqlite",
}
D = {}
for k, p in paths.items():
    e, v = dump(p)
    D[k] = (e, v)
    print("%-11s entities %4d md5 %s | values %4d md5 %s" % (
        k, len(e), hashlib.md5(repr(e).encode()).hexdigest()[:12],
        len(v), hashlib.md5(repr(v).encode()).hexdigest()[:12]))

print()
print("P1 DETERMINISM (run1 vs run2 values identical):",
      "PASS" if D["FIX_run1"][1] == D["FIX_run2"][1] else "FAIL")
print("P5 entity set unchanged vs pre-fix:",
      "PASS" if D["PRE_backup"][0] == D["FIX_run2"][0] else "FAIL")

def agg(vals):
    out = collections.defaultdict(float)
    for pd_, ent, val in vals:
        if pd_ != "units_existing":
            continue
        d = json.loads(val.decode("utf-8") if isinstance(val, bytes) else val)
        tech, reg = ent.split("__")
        for y, mw in d["data"]:
            out[(reg[:2], y)] += (mw or 0)
            out[(tech.replace("-existing", ""), reg[:2], y)] += (mw or 0)
    return out

a_pre = agg(D["PRE_backup"][1]); a_new = agg(D["FIX_run2"][1])
print()
print("=== NATIONAL TOTALS (MW) ===")
print("%-12s %12s %12s" % ("key", "PRE(random)", "FIXED"))
for k in [("BE","y2030"),("BE","y2040"),("BE","y2050"),
          ("NL","y2030"),("NL","y2040"),("NL","y2050")]:
    print("%-12s %12.0f %12.0f" % ("%s %s" % k, a_pre.get(k,0), a_new.get(k,0)))
print()
print("=== KEY TECHS (MW) ===")
for k in [("nuclear-3","BE","y2030"),("nuclear-3","BE","y2040"),
          ("nuclear-3","NL","y2030"),
          ("SCPC","NL","y2030"),("SCPC","BE","y2030"),
          ("CCGT","NL","y2030"),("CCGT","BE","y2030")]:
    print("%-22s %12.0f %12.0f" % (" ".join(k), a_pre.get(k,0), a_new.get(k,0)))
