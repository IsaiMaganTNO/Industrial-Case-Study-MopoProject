import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
for fam in ("LH2-terminal","LNG-terminal"):
    n=c.execute("""SELECT COUNT(*) FROM entity e JOIN entity_class ec ON ec.id=e.class_id
      WHERE ec.name='unit_flow__unit_flow' AND e.name LIKE ? AND e.name LIKE '%atmosphere%'""",
      (fam+"%",)).fetchone()[0]
    print("%-14s atmosphere ratio rows: %d"%(fam,n))
# what feeds LH2-terminal?
print("\nLH2-terminal inputs:")
for (x,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='node__to_unit' AND e.name LIKE '%__LH2-terminal%' LIMIT 6"""): print("   ",x)
