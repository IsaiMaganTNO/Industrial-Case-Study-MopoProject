import sqlite3
c=sqlite3.connect(r"file:.spinetoolbox/items/industry_db/industry_db.sqlite?mode=ro",uri=True)
for t in ["entity","entity_class","entity_element","entity_class_dimension","parameter_value","parameter_definition","alternative"]:
    print("==",t,[ (r[1],r[2],r[3]) for r in c.execute("PRAGMA table_info(%s)"%t)])
print("\nsample entity_element:",c.execute("SELECT * FROM entity_element LIMIT 3").fetchall())
print("sample multi-dim entity:",c.execute("""SELECT e.id,e.class_id,e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='technology__region' LIMIT 2""").fetchall())
c.close()
