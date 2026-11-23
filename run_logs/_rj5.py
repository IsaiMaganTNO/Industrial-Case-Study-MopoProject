import sqlite3,collections
c=sqlite3.connect(r"file:EU_case/.spinetoolbox/items/hydro_db/hydro_db.sqlite?mode=ro",uri=True)
rs=sorted(r[0] for r in c.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name='region'"))
print("EU hydro regions:",rs)
rows=list(c.execute("""SELECT pd.name,e.name FROM parameter_value pv
 JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id JOIN entity e ON e.id=pv.entity_id"""))
c.close()
for cc in ("DE","DK","NO","UK"):
    n=[r for r in rows if r[1].split("__")[-1]==cc]
    print("  %s hydro values: %d  params=%s"%(cc,len(n),sorted(set(r[0] for r in n))))
c=sqlite3.connect(r"file:.spinetoolbox/items/hydro_db/hydro_db.sqlite?mode=ro",uri=True)
print("\nIC1 hydro regions:",sorted(r[0] for r in c.execute("SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id WHERE ec.name='region'")))
c.close()
