import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
# alternatives / scenario membership for nuclear
print("alternatives present:")
for (n,) in c.execute("SELECT name FROM alternative"): print("   ",n)
print("\nnuclear-3 param rows by alternative:")
for a,p,cnt in c.execute("""SELECT al.name,pd.name,COUNT(*) FROM parameter_value pv
  JOIN entity e ON e.id=pv.entity_id JOIN alternative al ON al.id=pv.alternative_id
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  WHERE e.name LIKE 'nuclear-3\_%' ESCAPE '\' GROUP BY al.name,pd.name"""):
    print("   %-22s %-34s %d"%(a[:22],p[:34],cnt))
