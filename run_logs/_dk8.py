import sqlite3,json
for f in [r"checkpoints\Final_SpineOpt_Model.tiny.3day.mixedres.sqlite"]:
  c=sqlite3.connect(f)
  q="""select e.name,a.name,pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where e.name='atmosphere' and pd.name like 'storage_investment_count%'"""
  for r in c.execute(q): print(r)
  q="""select e.name,pd.name,a.name,pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative a on a.id=pv.alternative_id where e.name like 'CO2-storage%' and pd.name like '%cost%'"""
  for r in list(c.execute(q))[:6]: print(r)
