import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
ns=[r[0] for r in c.execute("SELECT name FROM parameter_definition")]
print([n for n in ns if 'initial' in n.lower()])
c.close()
