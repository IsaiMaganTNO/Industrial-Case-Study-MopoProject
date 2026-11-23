import sqlite3
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
# all params on CO2 connections (via connection__node etc)
rs=m.execute("""SELECT DISTINCT ec.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE e.name LIKE '%_CO2_%'""").fetchall()
print("classes containing CO2 connection entities:",[r[0] for r in rs])
for cls in [r[0] for r in rs]:
    n=m.execute("""SELECT count(*) FROM parameter_value pv
      JOIN entity e ON e.id=pv.entity_id JOIN entity_class ec ON ec.id=e.class_id
      WHERE ec.name=? AND e.name LIKE '%_CO2_%'""",(cls,)).fetchone()[0]
    print("   %-28s param rows=%d"%(cls,n))
m.close()
