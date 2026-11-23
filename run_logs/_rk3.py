import sqlite3
for lab,p in [("IC1",r".spinetoolbox\items\other_industry_db\other_industry_db.sqlite"),("EU",r"EU_case\.spinetoolbox\items\other_industry_db\Other_Industry_DB.sqlite")]:
    c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
    print(lab,[x[0] for x in c.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name='technology' AND e.name LIKE '%wood%'")])
    print("  IC1-only techs vs EU:",[x[0] for x in c.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name='technology'")][:0])
    c.close()
