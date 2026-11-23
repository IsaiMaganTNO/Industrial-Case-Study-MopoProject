import sqlite3, collections, os

stores = {
 "vre_db":          ".spinetoolbox/items/vre_db/vre_db.sqlite",
 "rdemand_db":      ".spinetoolbox/items/rdemand_db/rdemand_db.sqlite",
 "transmission_db": ".spinetoolbox/items/transmission_db/transmission_db.sqlite",
 "heat_db":         ".spinetoolbox/items/heat_db/heat_db.sqlite",
 "power_db":        ".spinetoolbox/items/power_db/power_db.sqlite",
 "gas_db":          ".spinetoolbox/items/gas_db/gas_db.sqlite",
 "biomass_db":      ".spinetoolbox/items/biomass_db/biomass_db.sqlite",
 "industry_db":     ".spinetoolbox/items/industry_db/industry_db.sqlite",
 "transport_db":    ".spinetoolbox/items/transport_db/transport_db.sqlite",
 "hydro_db":        ".spinetoolbox/items/hydro_db/hydro_db.sqlite",
}

def classify(n):
    if n.startswith(("BEC", "NLC")):
        return "IC1"
    if len(n) == 4 and n[:2].isalpha() and n[2:].isalnum():
        return "PECD2-like"
    if len(n) == 2 and n.isalpha():
        return "country"
    return "other"

for tag, p in stores.items():
    if not os.path.exists(p):
        print("%-16s MISSING" % tag); continue
    c = sqlite3.connect("file:%s?mode=ro" % p, uri=True)
    try:
        rows = c.execute("""SELECT e.name FROM entity e JOIN entity_class ec
                            ON ec.id=e.class_id WHERE ec.name='region'""").fetchall()
    except Exception as e:
        rows = []
    c.close()
    names = sorted(x[0] for x in rows)
    k = collections.Counter(classify(n) for n in names)
    tgt = sorted(n for n in names if n[:2] in ("DE","DK","NO","UK"))
    print("%-16s regions=%3d  %s" % (tag, len(names), dict(k)))
    print("      DE/DK/NO/UK: %s" % (tgt[:14] if tgt else "NONE"))
