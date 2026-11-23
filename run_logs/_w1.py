import sqlite3,json
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
c=sqlite3.connect(db)
for n,p,v in c.execute("""SELECT e.name,pd.name,cast(pv.value as text) FROM parameter_value pv
JOIN entity e ON e.id=pv.entity_id JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
WHERE pd.name LIKE '%CO2_content%' OR pd.name LIKE '%co2_content%'"""):
    print("%-22s %-16s %s"%(n[:22],p[:16],v[:30]))
