import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite"
c=sqlite3.connect(db)
ts=[r[0] for r in c.execute("select name from sqlite_master where type='table' order by 1")]
for t in ts: print("  ",t)
