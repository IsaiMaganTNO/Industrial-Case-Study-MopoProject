import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite"
c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
rs=c.execute("""SELECT e.name,pd.name,cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE e.name LIKE '%oil-eng%' AND e.name LIKE '%atmosphere%'""").fetchall()
print("oil-eng atmosphere rows:",len(rs))
for n,p,v in rs[:6]: print("  ",n[:60],p,v[:40])
c.close()
