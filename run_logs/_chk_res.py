import sqlite3
db=r"checkpoints\Investment_Results.3day_hcco2.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
ns=[r[0] for r in c.execute("SELECT name FROM parameter_definition")]
print("params with 'state':",[n for n in ns if 'state' in n.lower()])
rs=c.execute("""SELECT e.name,pd.name FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE e.name LIKE '%atmosphere%' LIMIT 20""").fetchall()
for r in rs: print(r)
c.close()
