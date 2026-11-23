import sqlite3
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
for cls in ["connection__from_node","connection__node__node"]:
    rs=m.execute("""SELECT e.name,pd.name,cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id JOIN entity_class ec ON ec.id=e.class_id
      WHERE ec.name=? AND e.name LIKE '%_CO2_%' LIMIT 6""",(cls,)).fetchall()
    print("==",cls)
    for n,p,v in rs: print("   %-40s %-26s %s"%(n[:40],p[:26],v[:22]))
m.close()
