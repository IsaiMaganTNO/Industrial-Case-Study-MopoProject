import sqlite3,re
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
base=lambda n: re.sub(r"_(NL|BE)C\d+$","",n)
# all units
units=set()
for (n,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec
 ON ec.id=e.class_id WHERE ec.name='unit'"""): units.add(n)
# units with ANY atmosphere ratio
atm=set()
for (n,) in c.execute("""SELECT e.name FROM entity e JOIN entity_class ec
 ON ec.id=e.class_id WHERE ec.name='unit_flow__unit_flow'
 AND e.name LIKE '%__atmosphere__%'"""):
    atm.add(n.split("__")[0])
alt=[u for u in units if "alternative" in u]
print("alternative units total:",len(alt))
print("  of which WITH atmosphere link:",len([u for u in alt if u in atm]))
print("  of which WITHOUT:",len([u for u in alt if u not in atm]))
fams={}
for u in alt:
    if u not in atm: fams[base(u)]=fams.get(base(u),0)+1
for f,n in sorted(fams.items()): print("   %-62s %3d"%(f[:62],n))
