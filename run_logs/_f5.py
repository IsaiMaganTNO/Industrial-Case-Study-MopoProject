import sqlite3
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.sqlite"
c=sqlite3.connect(db)
row=c.execute("""select e.id,e.name from entity e join entity_class ec on ec.id=e.class_id
 where ec.name='unit_flow__unit_flow' and e.name like 'SCPC-existing%atmosphere%' limit 1""").fetchone()
print("entity:",row)
for r in c.execute("""select ee.position,e2.name,ec.name from entity_element ee
 join entity e2 on e2.id=ee.element_id join entity_class ec on ec.id=e2.class_id
 where ee.entity_id=? order by ee.position""",(row[0],)):
    print("  ",r)
print()
print("paramdef:",c.execute("""select pd.id,ec.name from parameter_definition pd
 join entity_class ec on ec.id=pd.entity_class_id where pd.name='flow_ratio_equality_coefficient'""").fetchall())
print("alts:",c.execute("select id,name from alternative").fetchall())
pv=c.execute("select type,typeof(value),value,alternative_id from parameter_value where entity_id=?",(row[0],)).fetchall()
print("pv:",pv)
