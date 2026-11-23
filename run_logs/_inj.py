import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
ins=c.execute("""SELECT DISTINCT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='node__to_unit' AND e.name LIKE '%CO2-injection%'""").fetchall()
print("CO2-injection inputs:",[n.split('__')[0] for (n,) in ins][:8])
outs=c.execute("""SELECT DISTINCT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  WHERE ec.name='unit__to_node' AND e.name LIKE 'CO2-injection%'""").fetchall()
print("CO2-injection outputs:",[n.split('__',1)[1] for (n,) in outs][:8])
rat=c.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE pd.name='flow_ratio_equality_coefficient' AND e.name LIKE 'CO2-injection%'""").fetchall()
for n,v in rat[:6]: print("   RATIO",n[:70],"=",v[:12])
c.close()
