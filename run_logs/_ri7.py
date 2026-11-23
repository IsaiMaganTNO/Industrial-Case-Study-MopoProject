import sqlite3,collections
c=sqlite3.connect(r"file:EU_case/.spinetoolbox/items/industry_db/industry_db.sqlite?mode=ro",uri=True)
rows=list(c.execute("""SELECT pd.name,e.name,pv.value FROM parameter_value pv
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id JOIN entity e ON e.id=pv.entity_id
 WHERE pd.name='demand'"""))
c.close()
print("EU industry demand rows:",len(rows))
for pn,en,v in rows:
    if en.endswith("__DE") or en.endswith("__UK"):
        print("   ",en[:60],str(v)[:110]); 
print()
c=sqlite3.connect(r"file:.spinetoolbox/items/industry_db/industry_db.sqlite?mode=ro",uri=True)
rows=list(c.execute("""SELECT e.name,pv.value FROM parameter_value pv
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id JOIN entity e ON e.id=pv.entity_id
 WHERE pd.name='demand'"""))
c.close()
print("IC1 industry demand rows:",len(rows))
for en,v in rows[:3]: print("   ",en[:60],str(v)[:110])
