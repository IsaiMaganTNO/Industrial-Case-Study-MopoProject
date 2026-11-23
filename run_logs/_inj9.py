import sqlite3
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
# any connection moving CO2 between regions?
rs=m.execute("""SELECT DISTINCT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='connection' AND e.name LIKE '%CO2%'""").fetchall()
print("CO2 connections:",len(rs))
for (n,) in rs[:12]: print("   ",n[:76])
# which regions host a CO2-injection unit at all
u=m.execute("""SELECT DISTINCT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='unit' AND e.name LIKE 'CO2-injection%'""").fetchall()
print("\ninjection units:",[n for (n,) in u])
m.close()
