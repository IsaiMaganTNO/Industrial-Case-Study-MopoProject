import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
for nd in ("global-H2","fossil-CH4"):
    rows=c.execute("""SELECT pd.name,cast(pv.value as text) FROM parameter_value pv
      JOIN entity e ON e.id=pv.entity_id JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      WHERE e.name=?""",(nd,)).fetchall()
    print("=== %s === params: %d"%(nd,len(rows)))
    for p,v in rows[:8]: print("    %-30s %s"%(p[:30],v[:26]))
