import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
for n,v in c.execute("""SELECT e.name,pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
WHERE e.name LIKE 'aluminium-primary-production-%__atmosphere__%production%'"""):
    print(n[:56]); print("   ",json.loads(bytes(v).decode())["data"])
print("\nunit__to_node atmosphere link count:",
 c.execute("""SELECT COUNT(*) FROM entity e JOIN entity_class ec ON ec.id=e.class_id
 WHERE ec.name='unit__to_node' AND e.name LIKE '%__atmosphere'""").fetchone()[0])
