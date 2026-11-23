import sqlite3, json
c = sqlite3.connect(r".spinetoolbox\items\power_db\power_db.sqlite")
for e, p, t in c.execute("""select e.name, pd.name, substr(cast(pv.value as text),1,150) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
  join entity e on e.id=pv.entity_id where e.name like '%existing__FR' and pd.name in ('units_existing','capacity','existing_capacity','units','capacity_existing')"""): print(e, p, t)
print([r[0] for r in c.execute("select distinct pd.name from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id where e.name='nuclear-3-existing__FR'")])
