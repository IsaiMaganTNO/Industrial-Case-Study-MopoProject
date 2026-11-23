import sqlite3,re
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
fams=["alumina-production-reference","aluminium-secondary-production-reference",
"alumina-production-alternative","steel-electric-arc-finishing-reference",
"steel-electric-arc-rolling-reference","steel-integrated-steelworks-finishing-reference",
"steel-integrated-steelworks-rolling-reference"]
for f in fams:
    n=c.execute("SELECT COUNT(*) FROM entity WHERE name LIKE ?",(f+"\\_%",)).fetchone()[0]
    n2=c.execute("SELECT COUNT(*) FROM entity WHERE name LIKE ?",(f+"_%",)).fetchone()[0]
    print("%-50s entities=%d"%(f[:50],n2))
