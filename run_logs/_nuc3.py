import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.nodac.sqlite")
for r in c.execute("select ec.id,ec.name,ec.dimension_count from entity_class ec where ec.name in ('investment_group','unit__investment_group')"): print(r)
for r in c.execute("select * from entity_class_dimension where entity_class_id=(select id from entity_class where name='unit__investment_group')"): print(r)
e=c.execute("select id from entity where name='nuclear-3_BEC1__nuclear-3'").fetchone()[0]
print(c.execute("select * from entity_element where entity_id=?",(e,)).fetchall())
print([d[1] for d in c.execute("pragma table_info(entity)")])
print(c.execute("select pv.type, typeof(pv.value), cast(pv.value as text) from parameter_value pv join entity e on e.id=pv.entity_id where e.name='nuclear-3' ").fetchall())
print(c.execute("select pd.id from parameter_definition pd join entity_class ec on ec.id=pd.entity_class_id where pd.name='investment_count_total_max_cumulative' and ec.name='investment_group'").fetchall())
