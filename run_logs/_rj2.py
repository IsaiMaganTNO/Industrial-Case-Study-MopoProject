import sqlite3,collections
# Check EU DBs: are the 4 countries stored as plain 'DE' region entities in *__region classes?
for lab,p in [("heat",r"EU_case\.spinetoolbox\items\heat_db\heat_db.sqlite"),
              ("transport",r"EU_case\.spinetoolbox\items\transport_db\transport_db.sqlite"),
              ("industry",r"EU_case\.spinetoolbox\items\industry_db\industry_db.sqlite"),
              ("other_ind",r"EU_case\.spinetoolbox\items\other_industry_db\Other_Industry_DB.sqlite")]:
    c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
    print("==",lab)
    for ecn in [r[0] for r in c.execute("SELECT name FROM entity_class")]:
        if not ecn.endswith("region"): continue
        n=c.execute("""SELECT count(*) FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name=?""",(ecn,)).fetchone()[0]
        ex=[r[0] for r in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
            WHERE ec.name=? AND (e.name LIKE '%DE' OR e.name LIKE '%UK') LIMIT 3""",(ecn,))]
        print("   %-48s n=%-5d sample=%s"%(ecn,n,ex))
    c.close()
