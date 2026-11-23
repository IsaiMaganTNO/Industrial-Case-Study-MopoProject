import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite")
q="""select e.name,pd.name,a.name,substr(cast(pv.value as text),1,120),pv.type from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id join entity_class ec on ec.id=e.class_id where ec.name='unit' and e.name like 'DAC%'"""
for r in c.execute(q): print(r)
print(c.execute("select count(*) from entity e join entity_class ec on ec.id=e.class_id where ec.name='unit' and e.name like 'DAC%'").fetchone())
for r in c.execute("select e.name,a.name,cast(pv.value as text) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where pd.name='availability_factor' and (e.name like 'LNG%' or e.name like 'gas-extraction%')"): print(r)
