import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
for t in ["paper-production-alternative","pulp-production-alternative","(BM)NH3"]:
    rs=c.execute("""SELECT DISTINCT e.name FROM entity e
      JOIN entity_class ec ON ec.id=e.class_id
      WHERE ec.name='node__to_unit' AND e.name LIKE ?""",("%"+t+"%",)).fetchall()
    fuels=sorted(set(n.split("__")[0].rsplit("_",1)[0] for (n,) in rs))
    print("%-30s inputs: %s"%(t[:30],fuels))
c.close()
