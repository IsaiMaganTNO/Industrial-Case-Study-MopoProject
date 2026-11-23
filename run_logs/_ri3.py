import sqlite3,collections
def info(p):
    c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
    cls=collections.Counter(r[0] for r in c.execute("SELECT ec.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id"))
    ecs=set(r[0] for r in c.execute("SELECT name FROM entity_class"))
    pds=set(r[0] for r in c.execute("SELECT name FROM parameter_definition"))
    alts=set(r[0] for r in c.execute("SELECT name FROM alternative"))
    c.close(); return cls,ecs,pds,alts
pairs=[("heat_db",r".spinetoolbox\items\heat_db\heat_db.sqlite",r"EU_case\.spinetoolbox\items\heat_db\heat_db.sqlite"),
 ("transport_db",r".spinetoolbox\items\transport_db\transport_db.sqlite",r"EU_case\.spinetoolbox\items\transport_db\transport_db.sqlite"),
 ("industry_db",r".spinetoolbox\items\industry_db\industry_db.sqlite",r"EU_case\.spinetoolbox\items\industry_db\industry_db.sqlite"),
 ("other_industry_db",r".spinetoolbox\items\other_industry_db\other_industry_db.sqlite",r"EU_case\.spinetoolbox\items\other_industry_db\Other_Industry_DB.sqlite")]
for lab,a,b in pairs:
    ca,ea,pa,aa=info(a); cb,eb,pb,ab=info(b)
    print("=== %s"%lab)
    print("  entity_class  IC1-only:",sorted(ea-eb)," EU-only:",sorted(eb-ea))
    print("  param         IC1-only:",sorted(pa-pb)," EU-only:",sorted(pb-pa))
    print("  alt IC1:",sorted(aa))
    print("  alt EU :",sorted(ab))
