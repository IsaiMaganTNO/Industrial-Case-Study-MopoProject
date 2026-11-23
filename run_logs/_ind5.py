import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
for t in ["paper-production-alternative","(BM)NH3","pulp-production-alternative",
          "aluminium-primary-production-reference","CEM2-(Afm)"]:
    rs=c.execute("""SELECT count(*) FROM parameter_value pv
      JOIN entity e ON e.id=pv.entity_id
      WHERE e.name LIKE ? AND e.name LIKE '%atmosphere%'""",("%"+t+"%",)).fetchone()[0]
    inp=c.execute("""SELECT DISTINCT e.name FROM entity e
      WHERE e.name LIKE ? AND e.name LIKE '%atmosphere%' LIMIT 3""",("%"+t+"%",)).fetchall()
    print("%-42s atm rows=%d"%(t[:42],rs))
    for (n,) in inp: print("        ",n[:78])
c.close()
