import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
q="""SELECT e.name FROM entity e WHERE e.name LIKE '%atmosphere%'
AND e.name LIKE '%alumin%'"""
r=[x[0] for x in c.execute(q)]
print("aluminium atmosphere entities:",len(r))
for n in r: print("  ",n)
q2="""SELECT COUNT(*) FROM entity e WHERE e.name LIKE '%alternative%'
AND e.name LIKE '%atmosphere%'"""
print("\nalternative routes booked to atmosphere:",c.execute(q2).fetchone()[0])
q3="""SELECT COUNT(*) FROM entity e WHERE e.name LIKE '%-reference%'
AND e.name LIKE '%atmosphere%'"""
print("reference routes booked to atmosphere:",c.execute(q3).fetchone()[0])
