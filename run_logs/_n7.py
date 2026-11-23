import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
print("ACTIVE alternatives in scenario(s):")
for s,a,r in c.execute("""SELECT sc.name,al.name,sa.rank FROM scenario_alternative sa
  JOIN scenario sc ON sc.id=sa.scenario_id JOIN alternative al ON al.id=sa.alternative_id
  ORDER BY sc.name,sa.rank"""):
    print("   %-20s rank %-3s %s"%(s[:20],r,a))
