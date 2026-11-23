import sqlite3,collections
c=sqlite3.connect(r"file:.spinetoolbox/items/biomass_db/biomass_db.sqlite?mode=ro",uri=True)
print("classes:",collections.Counter(r[0] for r in c.execute("SELECT ec.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id")))
print("params:",collections.Counter(r[0] for r in c.execute("SELECT pd.name FROM parameter_value pv JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id")))
for r in list(c.execute("""SELECT pd.name,e.name,a.name,pv.value FROM parameter_value pv
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id JOIN entity e ON e.id=pv.entity_id
 JOIN alternative a ON a.id=pv.alternative_id"""))[:12]:
    print("  ",r[0],"|",r[1][:34],"|",r[2],"|",str(r[3])[:80])
